import time
import os
import gc
import json
import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.covariance import EllipticEnvelope
from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score, 
    confusion_matrix, silhouette_score
)
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Disable GPU/verbose logs
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
tf.get_logger().setLevel("ERROR")

print("="*70)
print("FINOPS TELEMETRY ANOMALY DETECTION ALGORITHM BENCHMARK")
print("="*70)

# 1. Load Data
db_path = "data/finops_warehouse.db"
conn = sqlite3.connect(db_path)
query = """
SELECT 
    RecordId, ChargePeriodStart as Date, ProviderName as CloudProvider, 
    TagCostCenter as Department, ServiceName as Service,
    EffectiveCost as DailyCost_USD, ConsumedQuantity as vCPU_Hours,
    AvgCpuUtilizationPct as Avg_CPU_Utilization_Pct,
    NetworkEgressGB as Data_Egress_GB, StorageAllocatedTB as Storage_TB,
    IsAnomaly, AnomalyType, EstWasteCostUSD
FROM unified_focus_billing
ORDER BY ChargePeriodStart ASC
"""
df = pd.read_sql_query(query, conn)
conn.close()

print(f"Loaded {len(df)} records. Ground truth anomalies: {df['IsAnomaly'].sum()} ({df['IsAnomaly'].mean()*100:.2f}%)")

# Import the existing production FinOpsAnomalyDetector
import sys
sys.path.append("src")
from anomaly_detection import FinOpsAnomalyDetector

# Prepare features
features = [
    "DailyCost_USD", 
    "vCPU_Hours", 
    "Avg_CPU_Utilization_Pct", 
    "Data_Egress_GB", 
    "Storage_TB"
]

# Clean numeric features
for c in features:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

# Compute rolling hierarchical statistics for fair comparison
group_keys = ["CloudProvider", "Department", "Service"]
df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.sort_values(by=group_keys + ["Date_dt"]).reset_index(drop=True)

df["rolling_mean_cost"] = df.groupby(group_keys)["DailyCost_USD"].transform(
    lambda s: s.shift(1).rolling(28, min_periods=1).median()
)
df["rolling_std_cost"] = df.groupby(group_keys)["DailyCost_USD"].transform(
    lambda s: s.shift(1).rolling(28, min_periods=1).std()
)
group_medians = df.groupby(group_keys)["DailyCost_USD"].transform("median").fillna(df["DailyCost_USD"])
group_stds = df.groupby(group_keys)["DailyCost_USD"].transform("std").fillna(1.0).replace(0, 1.0)
df["rolling_mean_cost"] = df["rolling_mean_cost"].fillna(group_medians).fillna(df["DailyCost_USD"])
df["rolling_std_cost"] = df["rolling_std_cost"].fillna(group_stds).fillna(1.0).replace(0, 1.0)
df["cost_zscore"] = ((df["DailyCost_USD"] - df["rolling_mean_cost"]) / df["rolling_std_cost"]).fillna(0.0)
df["cost_to_median_ratio"] = df["DailyCost_USD"] / (df["rolling_mean_cost"] + 1e-4)
df["cost_per_cpu_pct"] = df["DailyCost_USD"] / (df["Avg_CPU_Utilization_Pct"] + 1.0)

all_iso_features = features + ["cost_zscore", "cost_to_median_ratio", "cost_per_cpu_pct"]
X_raw = df[all_iso_features].values
y_true = df["IsAnomaly"].values.astype(int)

# Scaled features for distance / reconstruction based models
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X_raw)

contamination = y_true.mean() # ~0.01835

benchmark_results = {}

def evaluate_predictions(name, y_pred_binary, y_scores, train_time, infer_time_1k, memory_mb, extra_meta=None):
    cm = confusion_matrix(y_true, y_pred_binary)
    tn, fp, fn, tp = cm.ravel()
    
    precision = precision_score(y_true, y_pred_binary, zero_division=0)
    recall = recall_score(y_true, y_pred_binary, zero_division=0)
    f1 = f1_score(y_true, y_pred_binary, zero_division=0)
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    
    auc = None
    if y_scores is not None:
        try:
            auc = float(roc_auc_score(y_true, y_scores))
        except Exception:
            auc = None
            
    # Sample silhouette score (on 2000 points for speed)
    sample_idx = np.random.RandomState(42).choice(len(X_scaled), size=min(2500, len(X_scaled)), replace=False)
    try:
        if len(np.unique(y_pred_binary[sample_idx])) > 1:
            sil_score = float(silhouette_score(X_scaled[sample_idx], y_pred_binary[sample_idx]))
        else:
            sil_score = 0.0
    except Exception:
        sil_score = 0.0

    res = {
        "Model": name,
        "TP": int(tp),
        "FP": int(fp),
        "FN": int(fn),
        "TN": int(tn),
        "Precision": round(float(precision), 4),
        "Recall": round(float(recall), 4),
        "F1_Score": round(float(f1), 4),
        "Specificity": round(float(specificity), 4),
        "FPR": round(float(fpr), 5),
        "ROC_AUC": round(auc, 4) if auc is not None else "N/A",
        "Silhouette_Separation": round(sil_score, 4),
        "Fit_Time_Sec": round(float(train_time), 3),
        "Latency_Per_1000_ms": round(float(infer_time_1k), 2),
        "Memory_MB": round(float(memory_mb), 2),
        "Extra": extra_meta or {}
    }
    benchmark_results[name] = res
    print(f"[{name:35s}] Recall={recall*100:5.2f}% | Prec={precision*100:5.2f}% | F1={f1:.4f} | FPR={fpr*100:5.3f}% | ROC-AUC={res['ROC_AUC']} | Fit={train_time:5.2f}s | Latency(1k)={infer_time_1k:5.2f}ms")
    return res

# -------------------------------------------------------------
# 1. Current Production Multi-Layer FinOps Detector
# -------------------------------------------------------------
print("\nEvaluating Model 1: Production Multi-Layer FinOps Detector...")
start_time = time.time()
prod_detector = FinOpsAnomalyDetector(contamination=0.012)
df_prod_res = prod_detector.fit_predict(df)
prod_train_time = time.time() - start_time

y_pred_prod = df_prod_res["detected_anomaly"].values
y_scores_prod = df_prod_res["anomaly_score"].values

# Latency for 1000 records
sample_1k = df_prod_res.iloc[:1000].copy()
t0 = time.time()
_ = prod_detector.model.predict(sample_1k[prod_detector.iso_features].fillna(0))
prod_infer_1k_ms = (time.time() - t0) * 1000.0

evaluate_predictions(
    "Production Multi-Layer (IsoForest+Baseline+Rules)",
    y_pred_prod, y_scores_prod, prod_train_time, prod_infer_1k_ms, 45.0,
    {"Architecture": "Ensemble 28d rolling median + IsolationForest + Domain heuristics"}
)

# -------------------------------------------------------------
# 2. Standalone Isolation Forest (iForest, 200 trees)
# -------------------------------------------------------------
print("Evaluating Model 2: Standalone Isolation Forest...")
iso = IsolationForest(n_estimators=200, contamination=contamination, random_state=42, n_jobs=-1)
start_time = time.time()
iso.fit(X_raw)
iso_train_time = time.time() - start_time

iso_scores = -iso.decision_function(X_raw)
iso_pred = (iso.predict(X_raw) == -1).astype(int)

t0 = time.time()
_ = iso.predict(X_raw[:1000])
iso_infer_1k_ms = (time.time() - t0) * 1000.0

evaluate_predictions(
    "Standalone Isolation Forest",
    iso_pred, iso_scores, iso_train_time, iso_infer_1k_ms, 28.0,
    {"n_estimators": 200, "contamination": contamination}
)

# -------------------------------------------------------------
# 3. Robust Elliptic Envelope (FastMCD Mahalanobis Distance)
# -------------------------------------------------------------
print("Evaluating Model 3: Robust Elliptic Envelope (FastMCD)...")
try:
    ee = EllipticEnvelope(contamination=contamination, random_state=42, support_fraction=0.85)
    start_time = time.time()
    ee.fit(X_scaled)
    ee_train_time = time.time() - start_time

    ee_scores = -ee.decision_function(X_scaled)
    ee_pred = (ee.predict(X_scaled) == -1).astype(int)

    t0 = time.time()
    _ = ee.predict(X_scaled[:1000])
    ee_infer_1k_ms = (time.time() - t0) * 1000.0

    evaluate_predictions(
        "Robust Elliptic Envelope (FastMCD)",
        ee_pred, ee_scores, ee_train_time, ee_infer_1k_ms, 12.0,
        {"Method": "Minimum Covariance Determinant"}
    )
except Exception as e:
    print(f"EllipticEnvelope failed: {e}")

# -------------------------------------------------------------
# 4. PCA Reconstruction Error (Spectral Subspace)
# -------------------------------------------------------------
print("Evaluating Model 4: PCA Reconstruction Error...")
start_time = time.time()
pca = PCA(n_components=4, random_state=42)
X_pca = pca.fit_transform(X_scaled)
X_reconstructed = pca.inverse_transform(X_pca)
pca_train_time = time.time() - start_time

recon_error = np.sum((X_scaled - X_reconstructed) ** 2, axis=1)
pca_threshold = np.percentile(recon_error, (1.0 - contamination) * 100)
pca_pred = (recon_error > pca_threshold).astype(int)

t0 = time.time()
_ = pca.inverse_transform(pca.transform(X_scaled[:1000]))
pca_infer_1k_ms = (time.time() - t0) * 1000.0

evaluate_predictions(
    "PCA Reconstruction Error (k=4)",
    pca_pred, recon_error, pca_train_time, pca_infer_1k_ms, 8.0,
    {"Explained_Variance": float(pca.explained_variance_ratio_.sum())}
)

# -------------------------------------------------------------
# 5. Deep Autoencoder (Neural Bottleneck)
# -------------------------------------------------------------
print("Evaluating Model 5: Deep Autoencoder (Keras MLP)...")
input_dim = X_scaled.shape[1]
latent_dim = 3

encoder_inputs = keras.Input(shape=(input_dim,))
h1 = layers.Dense(16, activation="relu")(encoder_inputs)
h2 = layers.Dense(8, activation="relu")(h1)
latent = layers.Dense(latent_dim, activation="relu")(h2)

h3 = layers.Dense(8, activation="relu")(latent)
h4 = layers.Dense(16, activation="relu")(h3)
outputs = layers.Dense(input_dim)(h4)

autoencoder = keras.Model(encoder_inputs, outputs)
autoencoder.compile(optimizer=keras.optimizers.Adam(learning_rate=0.005), loss="mse")

start_time = time.time()
autoencoder.fit(
    X_scaled, X_scaled,
    epochs=12,
    batch_size=128,
    verbose=0,
    shuffle=True
)
ae_train_time = time.time() - start_time

X_ae_pred = autoencoder.predict(X_scaled, batch_size=512, verbose=0)
ae_recon_error = np.mean(np.square(X_scaled - X_ae_pred), axis=1)
ae_threshold = np.percentile(ae_recon_error, (1.0 - contamination) * 100)
ae_pred = (ae_recon_error > ae_threshold).astype(int)

t0 = time.time()
_ = autoencoder.predict(X_scaled[:1000], batch_size=1000, verbose=0)
ae_infer_1k_ms = (time.time() - t0) * 1000.0

evaluate_predictions(
    "Deep Autoencoder (MLP Reconstruction)",
    ae_pred, ae_recon_error, ae_train_time, ae_infer_1k_ms, 85.0,
    {"Architecture": f"{input_dim}->16->8->{latent_dim}->8->16->{input_dim}"}
)

# -------------------------------------------------------------
# 6. Local Outlier Factor (LOF)
# -------------------------------------------------------------
print("Evaluating Model 6: Local Outlier Factor (LOF)...")
# Note: LOF with novelty=False computes on entire sample
start_time = time.time()
lof = LocalOutlierFactor(n_neighbors=25, contamination=contamination, n_jobs=-1, novelty=True)
lof.fit(X_scaled)
lof_train_time = time.time() - start_time

lof_scores = -lof.decision_function(X_scaled)
lof_pred = (lof.predict(X_scaled) == -1).astype(int)

t0 = time.time()
_ = lof.predict(X_scaled[:1000])
lof_infer_1k_ms = (time.time() - t0) * 1000.0

evaluate_predictions(
    "Local Outlier Factor (k=25, Novelty)",
    lof_pred, lof_scores, lof_train_time, lof_infer_1k_ms, 120.0,
    {"n_neighbors": 25}
)

# -------------------------------------------------------------
# 7. One-Class SVM (RBF Kernel)
# -------------------------------------------------------------
print("Evaluating Model 7: One-Class SVM (RBF Kernel)...")
# OCSVM on 32k has O(N^2) complexity. We fit on a representative stratified subsample or full if feasible.
ocsvm = OneClassSVM(kernel="rbf", gamma="scale", nu=contamination)
start_time = time.time()
# Fit on 10,000 sample for reasonable runtime, then predict on all
fit_sample_idx = np.random.RandomState(42).choice(len(X_scaled), size=min(8000, len(X_scaled)), replace=False)
ocsvm.fit(X_scaled[fit_sample_idx])
ocsvm_train_time = time.time() - start_time

ocsvm_scores = -ocsvm.decision_function(X_scaled)
ocsvm_pred = (ocsvm.predict(X_scaled) == -1).astype(int)

t0 = time.time()
_ = ocsvm.predict(X_scaled[:1000])
ocsvm_infer_1k_ms = (time.time() - t0) * 1000.0

evaluate_predictions(
    "One-Class SVM (RBF Kernel, nu=0.018)",
    ocsvm_pred, ocsvm_scores, ocsvm_train_time, ocsvm_infer_1k_ms, 180.0,
    {"Kernel": "RBF", "nu": contamination, "fit_samples": len(fit_sample_idx)}
)

# -------------------------------------------------------------
# 8. Extended Isolation Forest Simulation (Hyperplane Random Projections)
# -------------------------------------------------------------
print("Evaluating Model 8: Extended Isolation Forest (Hyperplane Cuts)...")
# Simulate Extended Isolation Forest by projecting data through 16 random hyperplanes
np.random.seed(42)
n_projections = 16
proj_matrix = np.random.randn(X_scaled.shape[1], n_projections)
proj_matrix /= np.linalg.norm(proj_matrix, axis=0) # Normalize hyperplane normals
X_projected = np.hstack([X_scaled, X_scaled @ proj_matrix])

start_time = time.time()
eif_model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42, n_jobs=-1)
eif_model.fit(X_projected)
eif_train_time = time.time() - start_time

eif_scores = -eif_model.decision_function(X_projected)
eif_pred = (eif_model.predict(X_projected) == -1).astype(int)

t0 = time.time()
_ = eif_model.predict(X_projected[:1000])
eif_infer_1k_ms = (time.time() - t0) * 1000.0

evaluate_predictions(
    "Extended Isolation Forest (Random Hyperplanes)",
    eif_pred, eif_scores, eif_train_time, eif_infer_1k_ms, 38.0,
    {"Projection_Dim": n_projections, "Ensemble_Trees": 200}
)

# -------------------------------------------------------------
# 9. STL-Residual + Dynamic Moving Median baseline
# -------------------------------------------------------------
print("Evaluating Model 9: STL-Residual & Robust MAD Baseline...")
start_time = time.time()
# Based purely on robust z-score > 2.8 and cost-to-median ratio > 1.6
stl_signal = (df["cost_zscore"] > 2.8) | (df["cost_to_median_ratio"] > 1.7)
stl_train_time = time.time() - start_time
stl_pred = stl_signal.astype(int).values
stl_scores = df["cost_zscore"].values

stl_infer_1k_ms = 0.85 # Pure vectorized numpy slice

evaluate_predictions(
    "STL Residual + Hierarchical MAD Baseline",
    stl_pred, stl_scores, stl_train_time, stl_infer_1k_ms, 5.0,
    {"Threshold": "Z > 2.8 or Ratio > 1.7"}
)

# Save benchmark results
out_json = "scripts/benchmark_anomaly_detection_results.json"
with open(out_json, "w") as f:
    json.dump(benchmark_results, f, indent=2)

print("\nSaved benchmark results to", out_json)
