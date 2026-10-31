"""
Abhi Cloud Tech - Production MLOps Model Serialization Pipeline
Lead Architect: Abhishek

This script demonstrates and executes the offline model training, evaluation,
and serialization pipeline. It loads the multi-cloud FOCUS 1.0 dataset from the
SQLite warehouse, trains the production models, and persists their binary artifacts
to the `models/` directory using joblib.

Artifacts Produced:
1. models/anomaly_detector_isolation_forest.joblib
2. models/spend_forecaster_histgradient.joblib
3. models/model_metadata.json
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.database import load_focus_dataframe
from src.anomaly_detection import FinOpsAnomalyDetector
from src.forecasting import FinOpsForecaster

def run_model_training_and_serialization():
    print("=" * 80)
    print("Abhi Cloud Tech | Enterprise FinOps MLOps Model Training & Registry Pipeline")
    print("=" * 80)
    
    # Ensure models directory exists
    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # 1. Ingest Data from SQLite Warehouse
    print("\n[Step 1/4] Ingesting multi-cloud telemetry from SQLite warehouse...")
    df = load_focus_dataframe()
    if df.empty:
        raise ValueError("FinOps warehouse database is empty. Please run data generator.")
    print(f"[+] Loaded {len(df):,} FOCUS 1.0 records spanning {df['Date'].nunique()} unique dates.")
    print(f"[+] Cloud Providers: {df['CloudProvider'].unique().tolist()}")
    
    # 2. Train and Serialize Calibrated Isolation Forest Anomaly Detector
    print("\n[Step 2/4] Training Calibrated Multivariate Isolation Forest...")
    detector = FinOpsAnomalyDetector(contamination=0.0184)
    detector_df = detector.fit_predict(df)
    anom_count = int(detector_df['detected_anomaly'].sum())
    total_waste = float(detector_df[detector_df['detected_anomaly'] == 1]['cost_spike_usd'].sum())
    print(f"[+] Anomaly Detection Complete: {anom_count} anomalies identified across multi-cloud.")
    print(f"[+] Total recoverable anomalous waste identified: ${total_waste:,.2f}")
    
    det_artifact_path = os.path.join(models_dir, "anomaly_detector_isolation_forest.joblib")
    detector.save(det_artifact_path)
    det_size_kb = os.path.getsize(det_artifact_path) / 1024
    print(f"[+] Serialized Anomaly Detector artifact to: {det_artifact_path} ({det_size_kb:.1f} KB)")
    
    # 3. Train and Serialize Multi-Quantile HistGradientBoosting Spend Forecaster
    print("\n[Step 3/4] Training Multi-Quantile HistGradientBoosting Forecaster with Deterministic Trend...")
    forecaster = FinOpsForecaster(forecast_horizon_days=30)
    metrics = forecaster.train_and_evaluate(detector_df)
    print(f"[+] Forecasting Model Evaluated:")
    print(f"    - Mean Absolute Percentage Error (MAPE): {metrics.get('mape', 0.0):.2f}%")
    print(f"    - Root Mean Squared Error (RMSE):        ${metrics.get('rmse', 0.0):,.2f}")
    print(f"    - Mean Absolute Error (MAE):             ${metrics.get('mae', 0.0):,.2f}")
    
    fore_artifact_path = os.path.join(models_dir, "spend_forecaster_histgradient.joblib")
    forecaster.save(fore_artifact_path)
    fore_size_kb = os.path.getsize(fore_artifact_path) / 1024
    print(f"[+] Serialized Forecaster artifact to: {fore_artifact_path} ({fore_size_kb:.1f} KB)")
    
    # 4. Generate Model Registry Metadata JSON
    print("\n[Step 4/4] Generating MLOps Registry Metadata...")
    metadata = {
        "organization": "Abhi Cloud Tech",
        "lead_architect": "Abhishek",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "dataset": {
            "record_count": len(df),
            "start_date": str(df["Date"].min()),
            "end_date": str(df["Date"].max()),
            "total_spend_usd": round(float(df["DailyCost_USD"].sum()), 2),
            "cloud_providers": df["CloudProvider"].unique().tolist()
        },
        "registry": {
            "anomaly_detector": {
                "model_class": "FinOpsAnomalyDetector",
                "underlying_estimator": "sklearn.ensemble.IsolationForest",
                "artifact_file": "anomaly_detector_isolation_forest.joblib",
                "artifact_size_bytes": os.path.getsize(det_artifact_path),
                "hyperparameters": {
                    "n_estimators": 200,
                    "contamination": 0.0184,
                    "random_state": 42
                },
                "feature_count": len(detector.iso_features),
                "features": detector.iso_features,
                "anomalies_detected": anom_count,
                "total_waste_usd": round(total_waste, 2)
            },
            "spend_forecaster": {
                "model_class": "FinOpsForecaster",
                "underlying_estimator": "sklearn.ensemble.HistGradientBoostingRegressor + Ridge",
                "artifact_file": "spend_forecaster_histgradient.joblib",
                "artifact_size_bytes": os.path.getsize(fore_artifact_path),
                "hyperparameters": {
                    "learning_rate": 0.03,
                    "max_iter": 180,
                    "max_depth": 4,
                    "l2_regularization": 1.0,
                    "quantiles": [0.05, 0.50, 0.95]
                },
                "performance_metrics": metrics
            }
        }
    }
    
    meta_path = os.path.join(models_dir, "model_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[+] Metadata written to: {meta_path}")
    
    # 5. Verification: Load models back and test inference
    print("\n[Verification] Testing artifact roundtrip (Load & Warm Inference)...")
    loaded_detector = FinOpsAnomalyDetector.load(det_artifact_path)
    loaded_preds = loaded_detector.predict(df.head(20))
    print(f"[+] Loaded detector scored {len(loaded_preds)} test rows in {loaded_preds['detected_anomaly'].sum()} anomalies.")
    
    loaded_forecaster = FinOpsForecaster.load(fore_artifact_path)
    loaded_forecast = loaded_forecaster.generate_future_forecast(days_ahead=7)
    print(f"[+] Loaded forecaster generated 7-day future projections successfully (Day 1: ${loaded_forecast['Forecasted_Spend_USD'].iloc[0]:,.2f})")
    
    print("\n" + "=" * 80)
    print("[SUCCESS] All FinOps models successfully trained, evaluated, and serialized to disk!")
    print("=" * 80)

if __name__ == "__main__":
    run_model_training_and_serialization()
