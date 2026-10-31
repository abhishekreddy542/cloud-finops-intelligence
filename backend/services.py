import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np
from src.database import load_focus_dataframe
from src.data_generator import seed_database_and_export_csv
from src.anomaly_detection import FinOpsAnomalyDetector
from src.forecasting import FinOpsForecaster
from src.optimizer import FinOpsOptimizer

import json
import datetime

class FinOpsService:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), "..", "data", "cloud_enterprise_billing_telemetry.csv")
        self.models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
        os.makedirs(self.models_dir, exist_ok=True)
        self.detector_path = os.path.join(self.models_dir, "anomaly_detector_isolation_forest.joblib")
        self.forecaster_path = os.path.join(self.models_dir, "spend_forecaster_histgradient.joblib")
        self.metadata_path = os.path.join(self.models_dir, "model_metadata.json")
        self.df = None
        self.analyzed_df = None
        self.detector = None
        self.forecaster = None
        self.forecast_metrics = {}
        self.load_and_train()
        
    def load_and_train(self):
        # 1. Load from SQLite FinOps Data Warehouse or fallback to CSV
        try:
            print("[*] Loading multi-cloud billing telemetry from SQLite warehouse...")
            self.df = load_focus_dataframe()
            if self.df.empty:
                raise ValueError("Database table empty")
            print(f"[+] Loaded {len(self.df):,} FOCUS records from finops_warehouse.db")
        except Exception as e:
            print(f"[!] SQLite warehouse query error ({e}). Falling back to CSV...")
            if not os.path.exists(self.data_path):
                os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
                seed_database_and_export_csv()
            self.df = pd.read_csv(self.data_path)
            
        # 2. Anomaly Detection: Load persisted artifact or fit & persist
        if os.path.exists(self.detector_path):
            try:
                print(f"[*] Loading pre-trained Anomaly Detector artifact from {self.detector_path} (Warm Start)...")
                self.detector = FinOpsAnomalyDetector.load(self.detector_path)
                self.analyzed_df = self.detector.predict(self.df)
                print(f"[+] Successfully loaded pre-trained detector ({len(self.detector.model.estimators_)} trees)")
            except Exception as e:
                print(f"[!] Error loading detector artifact ({e}), re-fitting...")
                self.detector = FinOpsAnomalyDetector()
                self.analyzed_df = self.detector.fit_predict(self.df)
                self.detector.save(self.detector_path)
        else:
            print("[*] No serialized detector artifact found. Fitting and serializing to models/...")
            self.detector = FinOpsAnomalyDetector()
            self.analyzed_df = self.detector.fit_predict(self.df)
            self.detector.save(self.detector_path)
            print(f"[+] Serialized Anomaly Detector to {self.detector_path}")
        
        # 3. Spend Forecaster: Load persisted artifact or train & persist
        if os.path.exists(self.forecaster_path):
            try:
                print(f"[*] Loading pre-trained Forecaster artifact from {self.forecaster_path} (Warm Start)...")
                self.forecaster = FinOpsForecaster.load(self.forecaster_path)
                self.forecast_metrics = getattr(self.forecaster, "metrics", {})
                print(f"[+] Successfully loaded pre-trained forecaster (MAPE: {self.forecast_metrics.get('mape', 'N/A')}%)")
            except Exception as e:
                print(f"[!] Error loading forecaster artifact ({e}), re-training...")
                self.forecaster = FinOpsForecaster()
                self.forecast_metrics = self.forecaster.train_and_evaluate(self.analyzed_df)
                self.forecaster.save(self.forecaster_path)
        else:
            print("[*] No serialized forecaster artifact found. Training and serializing to models/...")
            self.forecaster = FinOpsForecaster()
            self.forecast_metrics = self.forecaster.train_and_evaluate(self.analyzed_df)
            self.forecaster.save(self.forecaster_path)
            print(f"[+] Serialized Spend Forecaster to {self.forecaster_path}")

        # 4. Persist Model Metadata Summary
        self._write_model_metadata()
        print("[+] FinOps Service initialized with persistent MLOps model registry.")

    def _write_model_metadata(self):
        try:
            det_size = os.path.getsize(self.detector_path) if os.path.exists(self.detector_path) else 0
            fore_size = os.path.getsize(self.forecaster_path) if os.path.exists(self.forecaster_path) else 0
            
            meta = {
                "organization": "Abhi Cloud Tech",
                "lead_architect": "Abhishek",
                "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "dataset_records": len(self.df) if self.df is not None else 0,
                "models": {
                    "anomaly_detection": {
                        "algorithm": "Calibrated Multivariate Isolation Forest",
                        "status": "Production Active",
                        "artifact_path": "models/anomaly_detector_isolation_forest.joblib",
                        "artifact_size_bytes": det_size,
                        "artifact_size_mb": round(det_size / (1024 * 1024), 2),
                        "contamination": getattr(self.detector, "contamination", 0.0184),
                        "estimators": 200,
                        "features": getattr(self.detector, "iso_features", [])
                    },
                    "spend_forecasting": {
                        "algorithm": "Residual HistGradientBoosting with Deterministic Ridge Trend & Fourier Seasonality",
                        "status": "Production Active",
                        "artifact_path": "models/spend_forecaster_histgradient.joblib",
                        "artifact_size_bytes": fore_size,
                        "artifact_size_mb": round(fore_size / (1024 * 1024), 2),
                        "quantiles": [0.05, 0.50, 0.95],
                        "metrics": self.forecast_metrics
                    }
                }
            }
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
        except Exception as e:
            print(f"[!] Warning: Could not write model metadata: {e}")

    def get_model_registry(self):
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"status": "Metadata not found"}

    def get_scoped_dataframe(self, providers=None, departments=None):
        if self.analyzed_df is None or self.analyzed_df.empty:
            return pd.DataFrame()
        df = self.analyzed_df.copy()
        if providers:
            df = df[df["CloudProvider"].isin(providers)]
        if departments:
            df = df[df["Department"].isin(departments)]
        return df

    def get_overview_kpis(self, providers=None, departments=None):
        scoped_df = self.get_scoped_dataframe(providers, departments)
        optimizer = FinOpsOptimizer(scoped_df)
        portfolio = optimizer.generate_savings_portfolio()
        
        total_spend = float(scoped_df["DailyCost_USD"].sum()) if not scoped_df.empty and "DailyCost_USD" in scoped_df else 0.0
        if not scoped_df.empty and "detected_anomaly" in scoped_df:
            anomalies = scoped_df[scoped_df["detected_anomaly"] == 1]
            anomalous_waste = float(anomalies["cost_spike_usd"].sum()) if "cost_spike_usd" in anomalies else 0.0
            anomaly_count = int(len(anomalies))
        else:
            anomalous_waste = 0.0
            anomaly_count = 0
            
        avg_cpu = float(scoped_df["Avg_CPU_Utilization_Pct"].mean()) if not scoped_df.empty and "Avg_CPU_Utilization_Pct" in scoped_df else 0.0
        
        return {
            "total_spend_ytd": round(total_spend, 2),
            "annual_run_rate": portfolio["Annual_Run_Rate_USD"],
            "identifiable_annual_savings": portfolio["Total_Annual_Savings_USD"],
            "savings_percentage": portfolio["Savings_Percentage"],
            "anomalous_waste_usd": round(anomalous_waste, 2),
            "anomaly_incident_count": anomaly_count,
            "average_cpu_utilization": round(avg_cpu, 1),
            "finops_maturity_score": portfolio["FinOps_Maturity_Score"],
            "finops_maturity_stage": portfolio["FinOps_Maturity_Stage"]
        }

    def get_spend_trends(self, providers=None, departments=None):
        scoped_df = self.get_scoped_dataframe(providers, departments)
        if scoped_df.empty:
            return {
                "daily_trend": [],
                "daily_by_provider": [],
                "anomalies_summary": [],
                "provider_breakdown": []
            }
        
        # 1. Overall daily total
        daily_total = scoped_df.groupby("Date").agg({
            "DailyCost_USD": "sum",
            "detected_anomaly": "max"
        }).reset_index()
        
        # 2. Granular daily spend per cloud provider (for multi-color timeline)
        daily_by_prov = scoped_df.groupby(["Date", "CloudProvider"]).agg({
            "DailyCost_USD": "sum",
            "detected_anomaly": "max"
        }).reset_index()
        
        # 3. Anomaly callout list with provider metadata
        anom_records = scoped_df[scoped_df["detected_anomaly"] == 1][[
            "Date", "CloudProvider", "Department", "Service", "DailyCost_USD", "cost_spike_usd", "anomaly_severity"
        ]].sort_values(by="DailyCost_USD", ascending=False).to_dict(orient="records")
        
        # 4. Total provider breakdown
        provider_share = scoped_df.groupby("CloudProvider")["DailyCost_USD"].sum().reset_index()
        
        return {
            "daily_trend": daily_total.to_dict(orient="records"),
            "daily_by_provider": daily_by_prov.to_dict(orient="records"),
            "anomalies_summary": anom_records[:15],
            "provider_breakdown": provider_share.to_dict(orient="records")
        }

    def get_department_analytics(self, providers=None, departments=None):
        scoped_df = self.get_scoped_dataframe(providers, departments)
        if scoped_df.empty:
            return {
                "department_spend": [],
                "top_services": [],
                "efficiency_scatter": []
            }
        
        # Spend per dept by provider
        dept_prov = scoped_df.groupby(["Department", "CloudProvider"])["DailyCost_USD"].sum().reset_index()
        
        # Top services
        top_services = scoped_df.groupby("Service")["DailyCost_USD"].sum().reset_index().sort_values(by="DailyCost_USD", ascending=False).head(8)
        
        # Sample for scatter efficiency
        sample_size = min(400, len(scoped_df))
        sample = scoped_df.sample(sample_size, random_state=42)[
            ["Date", "CloudProvider", "Department", "Service", "DailyCost_USD", "Avg_CPU_Utilization_Pct", "vCPU_Hours"]
        ]
        
        return {
            "department_spend": dept_prov.to_dict(orient="records"),
            "top_services": top_services.to_dict(orient="records"),
            "efficiency_scatter": sample.to_dict(orient="records")
        }

    def get_anomalies(self, providers=None, departments=None, severity=None, limit=None):
        scoped_df = self.get_scoped_dataframe(providers, departments)
        if scoped_df.empty or "detected_anomaly" not in scoped_df:
            return []
            
        anom_df = scoped_df[scoped_df["detected_anomaly"] == 1].copy()
        
        if severity and severity.upper() != "ALL":
            anom_df = anom_df[anom_df["anomaly_severity"] == severity.upper()]
            
        # Chronological sort (newest events first) with high spend precedence
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        anom_df["sev_rank"] = anom_df["anomaly_severity"].map(severity_order).fillna(4)
        anom_df = anom_df.sort_values(by=["Date", "sev_rank", "DailyCost_USD"], ascending=[False, True, False])
        
        desired_cols = [
            "Date", "CloudProvider", "Department", "Service", "RegionName", "ResourceId",
            "DailyCost_USD", "cost_spike_usd", "anomaly_severity", "root_cause_diagnosis"
        ]
        cols = [c for c in desired_cols if c in anom_df.columns]
        
        if limit is not None and limit > 0:
            anom_df = anom_df.head(limit)
            
        return anom_df[cols].to_dict(orient="records")

    def get_forecast(self, horizon_days=60, workload_growth=15.0, finops_savings=10.0):
        if self.forecaster is None:
            return {
                "metrics": {},
                "historical": [],
                "forecast": [],
                "projected_total_usd": 0.0
            }
            
        forecast_df = self.forecaster.generate_future_forecast(
            days_ahead=horizon_days,
            workload_growth_pct=workload_growth,
            finops_savings_pct=finops_savings
        )
        
        # Latest 60 days of actuals for historical context
        if self.analyzed_df is not None and not self.analyzed_df.empty and "DailyCost_USD" in self.analyzed_df:
            hist_agg = self.analyzed_df.groupby("Date")["DailyCost_USD"].sum().reset_index().tail(60)
            hist_list = hist_agg.to_dict(orient="records")
        else:
            hist_list = []
        
        total_proj = round(float(forecast_df["Forecasted_Spend_USD"].sum()), 2) if not forecast_df.empty and "Forecasted_Spend_USD" in forecast_df else 0.0
        return {
            "metrics": self.forecast_metrics,
            "historical": hist_list,
            "forecast": forecast_df.to_dict(orient="records"),
            "projected_total_usd": total_proj
        }

    def get_optimization_portfolio(self, providers=None, departments=None):
        scoped_df = self.get_scoped_dataframe(providers, departments)
        opt = FinOpsOptimizer(scoped_df)
        portfolio = opt.generate_savings_portfolio()
        action_table = opt.get_actionable_recommendations_table()
        
        return {
            "portfolio": portfolio,
            "action_matrix": action_table.to_dict(orient="records")
        }

# Global singleton
finops_service = FinOpsService()
