import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

class FinOpsAnomalyDetector:
    """
    Production FinOps Multi-Layer Anomaly Detector:
    1. Isolation Forest for multivariate anomaly detection (cost + telemetry metrics)
    2. Dynamic Rolling Z-Score with hierarchical grouping (Provider + Dept + Service)
    3. Root cause diagnostic attribution (Zombie compute, Egress leak, Storage sprawl)
    """
    def __init__(self, contamination=0.03):
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=150,
            contamination=self.contamination,
            random_state=42
        )
        self.feature_cols = [
            "DailyCost_USD", 
            "vCPU_Hours", 
            "Avg_CPU_Utilization_Pct", 
            "Data_Egress_GB", 
            "Storage_TB"
        ]

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Ensure features are present and non-null
        X = df[self.feature_cols].fillna(0)
        
        # 1. Fit Isolation Forest on continuous telemetry features
        self.model.fit(X)
        iso_scores = self.model.decision_function(X) # lower = more anomalous
        iso_preds = self.model.predict(X)            # -1 is anomaly, 1 is normal
        
        df["anomaly_score"] = np.round(-iso_scores, 4) # Invert so higher score = higher severity
        df["is_iso_anomaly"] = (iso_preds == -1).astype(int)
        
        # 2. Statistical rolling baseline with proper hierarchical granularity
        df["Date_dt"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by=["CloudProvider", "Department", "Service", "Date_dt"])
        
        # Rolling 14-day window grouped by granular resource entity
        group_keys = ["CloudProvider", "Department", "Service"]
        df["rolling_mean_cost"] = df.groupby(group_keys)["DailyCost_USD"].transform(
            lambda s: s.shift(1).rolling(14, min_periods=3).mean()
        )
        df["rolling_std_cost"] = df.groupby(group_keys)["DailyCost_USD"].transform(
            lambda s: s.shift(1).rolling(14, min_periods=3).std().fillna(1.0)
        )
        # Fill warm-up periods cleanly
        df["rolling_mean_cost"] = df["rolling_mean_cost"].fillna(df["DailyCost_USD"])
        df["rolling_std_cost"] = df["rolling_std_cost"].fillna(1.0).replace(0, 1.0)
        
        # Cost Z-score & Delta
        df["cost_zscore"] = (df["DailyCost_USD"] - df["rolling_mean_cost"]) / df["rolling_std_cost"]
        df["cost_zscore"] = np.round(df["cost_zscore"].fillna(0), 2)
        df["cost_spike_usd"] = np.round(np.maximum(0, df["DailyCost_USD"] - df["rolling_mean_cost"]), 2)
        
        # Combined anomaly flag (IsoForest OR Z-Score > 2.5)
        df["detected_anomaly"] = ((df["is_iso_anomaly"] == 1) & (df["cost_zscore"] > 1.8)) | (df["cost_zscore"] > 2.8)
        df["detected_anomaly"] = df["detected_anomaly"].astype(int)
        
        # 3. Diagnostic Root Cause Attribution
        def diagnose(row):
            if row["detected_anomaly"] == 0:
                return "Normal Baseline"
            
            # Check for Zombie instance pattern: High cost/vCPU, very low CPU utilization
            if row["Avg_CPU_Utilization_Pct"] < 15 and row["vCPU_Hours"] > 1200:
                return "Zombie/Idle Cluster: High compute allocation with <15% utilization"
            
            # Check for Egress surge
            if row["Data_Egress_GB"] > 1500 or (row["cost_zscore"] > 2.2 and any(k in row["Service"] for k in ["Egress", "Bandwidth"])):
                return "Runaway Egress Spike: Massive outbound data transfer detected"
                
            # Check for Storage sprawl
            if any(k in row["Service"] for k in ["Storage", "Blob", "S3"]) and row["cost_zscore"] > 1.8:
                return "Storage Sprawl: Orphan snapshots or unattached high-performance disks"
                
            return "Unbudgeted Cost Surge: Spend exceeded statistical upper threshold"
            
        df["root_cause_diagnosis"] = df.apply(diagnose, axis=1)
        
        # 4. Severity Assignment
        def assign_severity(row):
            if row["detected_anomaly"] == 0:
                return "Normal"
            spike = row["cost_spike_usd"]
            if spike > 500 or row["cost_zscore"] > 4.0:
                return "CRITICAL"
            elif spike > 200 or row["cost_zscore"] > 2.5:
                return "HIGH"
            else:
                return "MEDIUM"
                
        df["anomaly_severity"] = df.apply(assign_severity, axis=1)
        return df.sort_values(by="Date").reset_index(drop=True)

if __name__ == "__main__":
    import os
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "cloud_enterprise_billing_telemetry.csv")
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        detector = FinOpsAnomalyDetector()
        res = detector.fit_predict(df)
        anomalies = res[res["detected_anomaly"] == 1]
        print(f"Total anomalies detected: {len(anomalies)} / {len(df)}")
        print(anomalies[["Date", "CloudProvider", "Department", "Service", "DailyCost_USD", "cost_spike_usd", "anomaly_severity", "root_cause_diagnosis"]].head(10))
