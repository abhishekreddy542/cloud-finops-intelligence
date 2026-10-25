import os
import pandas as pd
import numpy as np
from src.data_generator import generate_finops_dataset
from src.anomaly_detection import FinOpsAnomalyDetector
from src.forecasting import FinOpsForecaster
from src.optimizer import FinOpsOptimizer

class FinOpsService:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), "..", "data", "cloud_enterprise_billing_telemetry.csv")
        self.df = None
        self.analyzed_df = None
        self.forecaster = None
        self.forecast_metrics = {}
        self.load_and_train()
        
    def load_and_train(self):
        # 1. Load or generate dataset
        if not os.path.exists(self.data_path):
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            self.df = generate_finops_dataset()
            self.df.to_csv(self.data_path, index=False)
        else:
            self.df = pd.read_csv(self.data_path)
            
        # 2. Run Anomaly Detection
        detector = FinOpsAnomalyDetector()
        self.analyzed_df = detector.fit_predict(self.df)
        
        # 3. Train Forecaster
        self.forecaster = FinOpsForecaster()
        self.forecast_metrics = self.forecaster.train_and_evaluate(self.analyzed_df)
        print("FinOps Service initialized and models cached successfully.")

    def get_scoped_dataframe(self, providers=None, departments=None):
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
        
        total_spend = float(scoped_df["DailyCost_USD"].sum())
        anomalies = scoped_df[scoped_df["detected_anomaly"] == 1]
        anomalous_waste = float(anomalies["cost_spike_usd"].sum())
        avg_cpu = float(scoped_df["Avg_CPU_Utilization_Pct"].mean()) if not scoped_df.empty else 0.0
        
        return {
            "total_spend_ytd": round(total_spend, 2),
            "annual_run_rate": portfolio["Annual_Run_Rate_USD"],
            "identifiable_annual_savings": portfolio["Total_Annual_Savings_USD"],
            "savings_percentage": portfolio["Savings_Percentage"],
            "anomalous_waste_usd": round(anomalous_waste, 2),
            "anomaly_incident_count": int(len(anomalies)),
            "average_cpu_utilization": round(avg_cpu, 1),
            "finops_maturity_score": portfolio["FinOps_Maturity_Score"],
            "finops_maturity_stage": portfolio["FinOps_Maturity_Stage"]
        }

    def get_spend_trends(self, providers=None, departments=None):
        scoped_df = self.get_scoped_dataframe(providers, departments)
        
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
        
        # Spend per dept by provider
        dept_prov = scoped_df.groupby(["Department", "CloudProvider"])["DailyCost_USD"].sum().reset_index()
        
        # Top services
        top_services = scoped_df.groupby("Service")["DailyCost_USD"].sum().reset_index().sort_values(by="DailyCost_USD", ascending=False).head(8)
        
        # Sample for scatter efficiency
        sample = scoped_df.sample(min(400, len(scoped_df)), random_state=42)[
            ["Date", "CloudProvider", "Department", "Service", "DailyCost_USD", "Avg_CPU_Utilization_Pct", "vCPU_Hours"]
        ]
        
        return {
            "department_spend": dept_prov.to_dict(orient="records"),
            "top_services": top_services.to_dict(orient="records"),
            "efficiency_scatter": sample.to_dict(orient="records")
        }

    def get_anomalies(self, providers=None, departments=None, severity=None):
        scoped_df = self.get_scoped_dataframe(providers, departments)
        anom_df = scoped_df[scoped_df["detected_anomaly"] == 1].copy()
        
        if severity and severity != "ALL":
            anom_df = anom_df[anom_df["anomaly_severity"] == severity]
            
        anom_df = anom_df.sort_values(by="DailyCost_USD", ascending=False)
        cols = [
            "Date", "CloudProvider", "Department", "Service", 
            "DailyCost_USD", "cost_spike_usd", "anomaly_severity", "root_cause_diagnosis"
        ]
        return anom_df[cols].head(50).to_dict(orient="records")

    def get_forecast(self, horizon_days=60, workload_growth=15.0, finops_savings=10.0):
        forecast_df = self.forecaster.generate_future_forecast(
            days_ahead=horizon_days,
            workload_growth_pct=workload_growth,
            finops_savings_pct=finops_savings
        )
        
        # Latest 60 days of actuals for historical context
        hist_agg = self.analyzed_df.groupby("Date")["DailyCost_USD"].sum().reset_index().tail(60)
        
        return {
            "metrics": self.forecast_metrics,
            "historical": hist_agg.to_dict(orient="records"),
            "forecast": forecast_df.to_dict(orient="records"),
            "projected_total_usd": round(float(forecast_df["Forecasted_Spend_USD"].sum()), 2)
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
