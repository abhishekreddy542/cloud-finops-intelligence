import numpy as np
import pandas as pd

class FinOpsOptimizer:
    """
    FinOps Recommendation Engine & Executive Financial Impact Calculator.
    Aligned with FinOps Foundation Standards (Inform -> Optimize -> Operate).
    Dynamically computes cost recovery portfolios and engineering action priorities.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def generate_savings_portfolio(self) -> dict:
        if self.df.empty:
            return {
                "Annual_Run_Rate_USD": 0.0,
                "Total_Annual_Savings_USD": 0.0,
                "Savings_Percentage": 0.0,
                "Idle_Cleanup_Savings_USD": 0.0,
                "Right_Sizing_Savings_USD": 0.0,
                "Commitment_Discounts_Savings_USD": 0.0,
                "Storage_Optimization_Savings_USD": 0.0,
                "FinOps_Maturity_Score": 50,
                "FinOps_Maturity_Stage": "Walk"
            }

        # Analyze recent operational window (latest quarter or full set if short)
        unique_dates = self.df["Date"].nunique()
        recent_days = max(14, unique_dates // 3)
        sorted_dates = sorted(self.df["Date"].unique())
        cutoff_date = sorted_dates[-recent_days]
        recent_df = self.df[self.df["Date"] >= cutoff_date]
        
        days_in_window = recent_df["Date"].nunique()
        if days_in_window == 0:
            days_in_window = 1
            
        total_recent_spend = recent_df["DailyCost_USD"].sum()
        annualized_run_rate = (total_recent_spend / days_in_window) * 365
        
        # 1. Idle & Zombie compute cleanup (<15% CPU and high daily spend)
        idle_mask = (recent_df["Avg_CPU_Utilization_Pct"] < 15) & (recent_df["DailyCost_USD"] > 100)
        idle_annual_savings = (recent_df[idle_mask]["DailyCost_USD"].sum() / days_in_window) * 365 * 0.70
        
        # 2. Right-sizing underutilized instances (15% - 35% utilization)
        underutilized_mask = (recent_df["Avg_CPU_Utilization_Pct"] >= 15) & (recent_df["Avg_CPU_Utilization_Pct"] < 35)
        right_sizing_annual_savings = (recent_df[underutilized_mask]["DailyCost_USD"].sum() / days_in_window) * 365 * 0.30
        
        # 3. Reserved Instances (RI) & Compute Savings Plans for steady state workloads (35% - 75% CPU)
        steady_mask = (recent_df["Avg_CPU_Utilization_Pct"] >= 35) & (recent_df["Avg_CPU_Utilization_Pct"] <= 75)
        commitment_annual_savings = (recent_df[steady_mask]["DailyCost_USD"].sum() / days_in_window) * 365 * 0.28
        
        # 4. Storage tiering & orphan disk deletion
        storage_mask = recent_df["Service"].str.contains("Storage|Blob|S3", case=False, na=False)
        storage_annual_savings = (recent_df[storage_mask]["DailyCost_USD"].sum() / days_in_window) * 365 * 0.20
        
        total_annual_savings = idle_annual_savings + right_sizing_annual_savings + commitment_annual_savings + storage_annual_savings
        savings_percentage = (total_annual_savings / annualized_run_rate * 100) if annualized_run_rate > 0 else 0.0
        
        # FinOps Maturity Level Score (0 to 100)
        avg_cpu = recent_df["Avg_CPU_Utilization_Pct"].mean() if not recent_df.empty else 50.0
        waste_ratio = (total_annual_savings / annualized_run_rate) if annualized_run_rate > 0 else 0.2
        maturity_score = int(np.clip(100 - (waste_ratio * 140) + (avg_cpu * 0.4), 35, 95))
        
        if maturity_score < 55:
            maturity_stage = "Crawl (Reactive / High Waste)"
        elif maturity_score < 78:
            maturity_stage = "Walk (Proactive / Developing Governance)"
        else:
            maturity_stage = "Run (Optimized / Continuous Unit Economics)"
            
        return {
            "Annual_Run_Rate_USD": round(annualized_run_rate, 2),
            "Total_Annual_Savings_USD": round(total_annual_savings, 2),
            "Savings_Percentage": round(savings_percentage, 1),
            "Idle_Cleanup_Savings_USD": round(idle_annual_savings, 2),
            "Right_Sizing_Savings_USD": round(right_sizing_annual_savings, 2),
            "Commitment_Discounts_Savings_USD": round(commitment_annual_savings, 2),
            "Storage_Optimization_Savings_USD": round(storage_annual_savings, 2),
            "FinOps_Maturity_Score": maturity_score,
            "FinOps_Maturity_Stage": maturity_stage
        }
        
    def get_actionable_recommendations_table(self) -> pd.DataFrame:
        """
        Returns prioritized action list for FinOps committee and engineering leaders.
        """
        if self.df.empty:
            return pd.DataFrame()

        latest_date = self.df["Date"].max()
        latest_df = self.df[self.df["Date"] == latest_date].copy()
        
        recs = []
        for _, row in latest_df.iterrows():
            if row["Avg_CPU_Utilization_Pct"] < 15 and row["DailyCost_USD"] > 120:
                recs.append({
                    "Priority": "P1 - Critical",
                    "Department": row["Department"],
                    "Cloud_Provider": row["CloudProvider"],
                    "Resource_Service": row["Service"],
                    "Issue_Identified": f"Severely underutilized ({row['Avg_CPU_Utilization_Pct']}% CPU)",
                    "Action_Required": "Downsize instance size or schedule weekend auto-shutdown",
                    "Est_Monthly_Savings_USD": round(row["DailyCost_USD"] * 30 * 0.55, 2),
                    "Implementation_Effort": "Low (1-2 Hours)"
                })
            elif any(k in row["Service"] for k in ["Egress", "Bandwidth"]) and row["Data_Egress_GB"] > 500:
                recs.append({
                    "Priority": "P2 - High",
                    "Department": row["Department"],
                    "Cloud_Provider": row["CloudProvider"],
                    "Resource_Service": row["Service"],
                    "Issue_Identified": f"High internet data egress ({row['Data_Egress_GB']} GB/day)",
                    "Action_Required": "Enable CloudFront CDN edge caching or private VPC Peering",
                    "Est_Monthly_Savings_USD": round(row["DailyCost_USD"] * 30 * 0.35, 2),
                    "Implementation_Effort": "Medium (1 Sprint)"
                })
            elif any(k in row["Service"] for k in ["Storage", "Blob", "S3"]) and row["Storage_TB"] > 15:
                recs.append({
                    "Priority": "P3 - Medium",
                    "Department": row["Department"],
                    "Cloud_Provider": row["CloudProvider"],
                    "Resource_Service": row["Service"],
                    "Issue_Identified": f"Large static storage volume ({row['Storage_TB']} TB)",
                    "Action_Required": "Implement lifecycle transition rule to Glacier / Archive tier",
                    "Est_Monthly_Savings_USD": round(row["DailyCost_USD"] * 30 * 0.40, 2),
                    "Implementation_Effort": "Low (Config update)"
                })
                
        rec_df = pd.DataFrame(recs)
        if not rec_df.empty:
            rec_df = rec_df.sort_values(by="Est_Monthly_Savings_USD", ascending=False).reset_index(drop=True)
        return rec_df
