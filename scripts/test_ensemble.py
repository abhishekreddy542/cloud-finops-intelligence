import json
import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

conn = sqlite3.connect("data/finops_warehouse.db")
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

# Clean numeric features
features = ["DailyCost_USD", "vCPU_Hours", "Avg_CPU_Utilization_Pct", "Data_Egress_GB", "Storage_TB"]
for c in features:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

# Compute rolling stats
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

scaler = RobustScaler()
X_scaled = scaler.fit_transform(X_raw)

# 1. Fit calibrated Isolation Forest with contamination matching warehouse anomaly rate (1.835%)
iso = IsolationForest(n_estimators=200, contamination=0.01835, random_state=42, n_jobs=-1)
iso.fit(X_raw)
iso_scores = -iso.decision_function(X_raw)
iso_pred = (iso.predict(X_raw) == -1).astype(int)

# 2. PCA reconstruction error
pca = PCA(n_components=4, random_state=42)
X_pca = pca.fit_transform(X_scaled)
X_reconstructed = pca.inverse_transform(X_pca)
recon_error = np.sum((X_scaled - X_reconstructed) ** 2, axis=1)

# Normalise scores to [0, 1]
norm_iso_scores = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min())
norm_pca_scores = (recon_error - recon_error.min()) / (recon_error.max() - recon_error.min())

# Blended ensemble score: 0.70 IsoForest + 0.30 PCA
ensemble_score = 0.70 * norm_iso_scores + 0.30 * norm_pca_scores
threshold = np.percentile(ensemble_score, (1.0 - 0.01835) * 100)
ensemble_pred = (ensemble_score > threshold).astype(int)

prec_iso = precision_score(y_true, iso_pred)
rec_iso = recall_score(y_true, iso_pred)
f1_iso = f1_score(y_true, iso_pred)
auc_iso = roc_auc_score(y_true, iso_scores)

prec_ens = precision_score(y_true, ensemble_pred)
rec_ens = recall_score(y_true, ensemble_pred)
f1_ens = f1_score(y_true, ensemble_pred)
auc_ens = roc_auc_score(y_true, ensemble_score)

print(f"Standalone IsoForest: Recall={rec_iso*100:.2f}%, Prec={prec_iso*100:.2f}%, F1={f1_iso:.4f}, AUC={auc_iso:.4f}")
print(f"Ensemble (IsoForest + PCA): Recall={rec_ens*100:.2f}%, Prec={prec_ens*100:.2f}%, F1={f1_ens:.4f}, AUC={auc_ens:.4f}")

# Now test: What if we remove the hard `& (cost_to_median_ratio > 1.5)` constraint from the production model?
# Domain rules directly from telemetry:
is_zombie = (df["Avg_CPU_Utilization_Pct"] < 15.0) & (df["vCPU_Hours"] > 600)
is_egress = (df["Data_Egress_GB"] > 1000)
is_storage = (df["Storage_TB"] > 40) & (df["Avg_CPU_Utilization_Pct"] < 5.0)
is_high_cost = (df["cost_zscore"] > 3.0)

calibrated_combined = (iso_pred == 1) | is_zombie | is_egress | is_storage | is_high_cost
prec_cal = precision_score(y_true, calibrated_combined)
rec_cal = recall_score(y_true, calibrated_combined)
f1_cal = f1_score(y_true, calibrated_combined)
print(f"Calibrated Multi-Layer (IsoForest + Telemetry Domain Rules): Recall={rec_cal*100:.2f}%, Prec={prec_cal*100:.2f}%, F1={f1_cal:.4f}")
