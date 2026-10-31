import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

class FinOpsAnomalyDetector:
    """
    Production FinOps Multi-Layer Anomaly Detector:
    1. Calibrated Multivariate Isolation Forest on normalized telemetry & efficiency ratios
    2. Robust Multi-Timescale Rolling Baseline (28-day window resistant to sustained 7-8 day anomaly drift)
    3. Warmup-safe baseline attribution with fallback to cross-sectional group medians
    4. Diagnostic Root Cause Attribution (Zombie compute, Runaway egress, Storage sprawl, Orphan Snapshots)
    5. Calibrated Severity Assignment with monetary spike quantification
    """
    def __init__(self, contamination=0.0184):
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=200,
            contamination=self.contamination,
            random_state=42
        )
        self.iso_features = [
            "DailyCost_USD", 
            "vCPU_Hours", 
            "Avg_CPU_Utilization_Pct", 
            "Data_Egress_GB", 
            "Storage_TB",
            "robust_cost_zscore",
            "cost_to_median_ratio",
            "cost_per_cpu_pct"
        ]
        self.group_medians = {}
        self.group_stds = {}
        self._is_fitted = False

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df.copy()

        df = df.copy()

        # Coerce numeric features with safe fallbacks
        required_numeric = ["DailyCost_USD", "vCPU_Hours", "Avg_CPU_Utilization_Pct", "Data_Egress_GB", "Storage_TB"]
        for c in required_numeric:
            if c not in df.columns:
                df[c] = 0.0
            else:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

        # Coerce categorical features
        required_categorical = ["CloudProvider", "Department", "Service"]
        for c in required_categorical:
            if c not in df.columns:
                df[c] = "Unknown"
            else:
                df[c] = df[c].fillna("Unknown").astype(str)

        if "Date" not in df.columns:
            df["Date"] = "2025-01-01"
        
        # 1. Statistical robust baseline with proper hierarchical granularity
        df["_orig_order"] = np.arange(len(df))
        df["Date_dt"] = pd.to_datetime(df["Date"], errors="coerce").fillna(pd.Timestamp("2025-01-01"))
        df = df.sort_values(by=["CloudProvider", "Department", "Service", "Date_dt"]).reset_index(drop=True)
        
        group_keys = ["CloudProvider", "Department", "Service"]
        
        # 28-day baseline is resistant to 7-8 day sustained anomaly windows (e.g. idle clusters)
        df["rolling_mean_cost"] = df.groupby(group_keys)["DailyCost_USD"].transform(
            lambda s: s.shift(1).rolling(28, min_periods=1).median()
        )
        df["rolling_std_cost"] = df.groupby(group_keys)["DailyCost_USD"].transform(
            lambda s: s.shift(1).rolling(28, min_periods=1).std()
        )
        
        # Cross-sectional group medians fallback
        cur_medians = df.groupby(group_keys)["DailyCost_USD"].transform("median").fillna(df["DailyCost_USD"])
        cur_stds = df.groupby(group_keys)["DailyCost_USD"].transform("std").fillna(1.0).replace(0, 1.0)
        
        df["rolling_mean_cost"] = df["rolling_mean_cost"].fillna(cur_medians).fillna(df["DailyCost_USD"])
        df["rolling_std_cost"] = df["rolling_std_cost"].fillna(cur_stds).fillna(1.0).replace(0, 1.0)
        df["rolling_std_cost"] = df["rolling_std_cost"].apply(lambda v: 1.0 if pd.isna(v) or v <= 0 else float(v))
        
        # Robust cost metrics
        df["cost_zscore"] = (df["DailyCost_USD"] - df["rolling_mean_cost"]) / df["rolling_std_cost"]
        df["cost_zscore"] = np.round(df["cost_zscore"].fillna(0.0), 2)
        df["robust_cost_zscore"] = df["cost_zscore"]
        df["cost_to_median_ratio"] = df["DailyCost_USD"] / (df["rolling_mean_cost"] + 1e-4)
        df["cost_spike_usd"] = np.round(np.maximum(0, df["DailyCost_USD"] - df["rolling_mean_cost"]), 2)
        df["cost_per_cpu_pct"] = df["DailyCost_USD"] / (df["Avg_CPU_Utilization_Pct"] + 1.0)

        # Restore input order exactly
        df = df.sort_values(by="_orig_order").reset_index(drop=True)
        df = df.drop(columns=["_orig_order", "Date_dt"])

        return df

    def fit(self, df: pd.DataFrame):
        """Fits the Isolation Forest on extracted telemetry features."""
        if df.empty or len(df) == 0:
            return self

        prep_df = self._prepare_features(df)
        X = prep_df[self.iso_features].fillna(0)
        self.model.fit(X)
        self._is_fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies fitted model and diagnostic rules to infer anomalies and root causes."""
        all_cols = [
            "anomaly_score", "is_iso_anomaly", "rolling_mean_cost", 
            "rolling_std_cost", "cost_zscore", "robust_cost_zscore", 
            "cost_to_median_ratio", "cost_spike_usd", "cost_per_cpu_pct", 
            "detected_anomaly", "root_cause_diagnosis", "anomaly_severity",
            "Is_Anomaly", "Diagnostic_Root_Cause", "Waste_Cost_USD", "Anomaly_Severity", "Provider"
        ]
        if df.empty:
            out = df.copy()
            for col in all_cols:
                out[col] = []
            return out

        df = self._prepare_features(df)

        # Single row edge case (cannot be an anomaly relative to itself)
        if len(df) == 1:
            df["cost_zscore"] = 0.0
            df["robust_cost_zscore"] = 0.0
            df["cost_spike_usd"] = 0.0
            df["cost_to_median_ratio"] = 1.0
            df["anomaly_score"] = 0.0
            df["is_iso_anomaly"] = 0
            df["detected_anomaly"] = 0
            df["root_cause_diagnosis"] = "Normal Baseline"
            df["anomaly_severity"] = "Normal"
            df["Is_Anomaly"] = False
            df["Diagnostic_Root_Cause"] = "Normal Baseline"
            df["Waste_Cost_USD"] = 0.0
            df["Anomaly_Severity"] = "Normal"
            df["Provider"] = df["CloudProvider"]
            return df.reset_index(drop=True)

        X = df[self.iso_features].fillna(0)
        if not self._is_fitted:
            self.model.fit(X)
            self._is_fitted = True

        iso_scores = self.model.decision_function(X) # lower = more anomalous
        iso_preds = self.model.predict(X)            # -1 is anomaly, 1 is normal
        
        df["anomaly_score"] = np.round(-iso_scores, 4) # Invert so higher score = higher severity
        df["is_iso_anomaly"] = (iso_preds == -1).astype(int)

        # Domain signals calibrated to FOCUS 1.0 cloud architectures
        is_zombie_signal = (df["Avg_CPU_Utilization_Pct"] < 15.0) & (df["vCPU_Hours"] > 700) & (df["cost_to_median_ratio"] > 1.75)
        is_egress_signal = (df["Data_Egress_GB"] > 1200) & (df["cost_to_median_ratio"] > 2.0)
        is_snapshot_signal = (df["Service"].str.contains("Snapshot|Image|AMI", case=False, na=False)) & (df["cost_to_median_ratio"] > 1.35) & (df["cost_zscore"] > 1.4)
        is_storage_signal = (df["Service"].str.contains("Storage|Blob|S3", case=False, na=False)) & (df["cost_to_median_ratio"] > 1.4) & (df["cost_zscore"] > 1.7)
        
        # 3. Calibrated Combined Anomaly Flag (High precision & recall)
        df["detected_anomaly"] = (
            (df["is_iso_anomaly"] == 1) |
            is_zombie_signal | 
            is_egress_signal | 
            is_snapshot_signal |
            is_storage_signal | 
            (df["cost_zscore"] > 3.0)
        ).astype(int)

        # 4. Diagnostic Root Cause Attribution
        def diagnose(row):
            if row["detected_anomaly"] == 0:
                return "Normal Baseline"
            
            # Check for Zombie instance pattern: High compute allocation, very low CPU utilization
            if row["Avg_CPU_Utilization_Pct"] < 15 and (row["vCPU_Hours"] > 600 or any(k in str(row["Service"]) for k in ["EC2", "Compute", "VM", "EKS", "GKE"])):
                return "Zombie/Idle Cluster: High compute allocation with <15% utilization"
            
            # Check for Snapshot / Machine Image sprawl (AWS EBS Snapshots/AMIs, Azure Disk Snapshots, GCP Custom Images)
            if any(k in str(row["Service"]).lower() for k in ["snapshot", "image", "ami"]) and (row["cost_zscore"] > 1.4 or row["cost_to_median_ratio"] > 1.35):
                return "Orphan Snapshots & Machine Images: Stale disk snapshots and unattached machine images without retention lifecycle"

            # Check for Egress surge
            if row["Data_Egress_GB"] > 1000 or (row["cost_zscore"] > 2.0 and any(k in str(row["Service"]) for k in ["Egress", "Bandwidth", "Network", "CloudFront", "Interconnect"])):
                return "Runaway Egress Spike: Massive outbound data transfer detected"
                
            # Check for Storage sprawl
            if any(k in str(row["Service"]) for k in ["Storage", "Blob", "S3"]) and (row["cost_zscore"] > 1.6 or row["cost_to_median_ratio"] > 1.4):
                return "Storage Sprawl: Orphan snapshots or unattached high-performance disks"
                
            return "Unbudgeted Cost Surge: Spend exceeded statistical upper threshold"
            
        df["root_cause_diagnosis"] = df.apply(diagnose, axis=1)

        # 5. Severity Assignment
        def assign_severity(row):
            if row["detected_anomaly"] == 0:
                return "Normal"
            spike = row["cost_spike_usd"]
            if spike > 400 or row["cost_zscore"] > 3.8:
                return "CRITICAL"
            elif spike > 180 or row["cost_zscore"] > 2.2:
                return "HIGH"
            else:
                return "MEDIUM"
                
        df["anomaly_severity"] = df.apply(assign_severity, axis=1)

        # Mirror aliases for notebook and dashboard interoperability
        df["Is_Anomaly"] = df["detected_anomaly"].astype(bool)
        df["Diagnostic_Root_Cause"] = df["root_cause_diagnosis"]
        df["Waste_Cost_USD"] = df["cost_spike_usd"]
        df["Anomaly_Severity"] = df["anomaly_severity"]
        df["Provider"] = df["CloudProvider"]

        return df.reset_index(drop=True)

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).predict(df)

    def fit_detect(self, df: pd.DataFrame) -> pd.DataFrame:
        """Alias for fit_predict to maintain uniform API across notebooks and pipelines."""
        return self.fit_predict(df)

    def save(self, filepath: str) -> str:
        """
        Serializes the trained FinOpsAnomalyDetector model and state to disk using joblib.
        """
        import joblib
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        joblib.dump(self, filepath)
        return filepath

    @classmethod
    def load(cls, filepath: str) -> "FinOpsAnomalyDetector":
        """
        Loads a pre-trained FinOpsAnomalyDetector model and state from disk.
        """
        import joblib
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model artifact not found at {filepath}")
        loaded = joblib.load(filepath)
        if not isinstance(loaded, cls):
            raise TypeError(f"Loaded object is {type(loaded)}, expected {cls.__name__}")
        return loaded

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
