import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_finops_dataset(start_date="2025-01-01", days=365, random_seed=42):
    """
    Generates realistic multi-cloud enterprise billing and telemetry dataset.
    Covers AWS, Azure, and GCP across departments: Engineering, AI/ML, Marketing, Core Banking, Data Platform.
    Includes normal seasonal trends, workload spikes, and realistic cloud waste anomalies:
      - Zombie/Idle compute instances running on weekends/nights
      - Unattached cloud storage volumes & snapshots
      - Runaway query/data egress anomalies
      - Over-provisioned databases
    """
    np.random.seed(random_seed)
    base = datetime.strptime(start_date, "%Y-%m-%d")
    date_list = [base + timedelta(days=i) for i in range(days)]
    
    providers = ["AWS", "Azure", "GCP"]
    departments = ["AI/ML Research", "Data Platform", "Core Engineering", "Customer Portal", "Finance & Analytics"]
    services_by_provider = {
        "AWS": ["EC2 (Compute)", "S3 (Storage)", "RDS (Database)", "EKS (Kubernetes)", "CloudFront (Egress)"],
        "Azure": ["Virtual Machines", "Blob Storage", "Azure SQL", "AKS (Containers)", "Bandwidth"],
        "GCP": ["Compute Engine", "Cloud Storage", "Cloud SQL", "GKE (Kubernetes)", "Cloud Run"]
    }
    
    records = []
    
    for current_date in date_list:
        day_of_week = current_date.weekday() # 0: Mon, ..., 6: Sun
        is_weekend = 1 if day_of_week >= 5 else 0
        day_idx = (current_date - base).days
        trend_factor = 1.0 + (0.0008 * day_idx) # Moderate organic business growth
        
        for dept in departments:
            # Department baseline multipliers
            dept_mult = {
                "AI/ML Research": 2.2,
                "Data Platform": 1.8,
                "Core Engineering": 1.4,
                "Customer Portal": 1.0,
                "Finance & Analytics": 0.7
            }[dept]
            
            for prov in providers:
                services = services_by_provider[prov]
                for srv in services:
                    # Baseline unit cost
                    base_cost = np.random.uniform(80, 220) * dept_mult * trend_factor
                    
                    # Business hour pattern: lower on weekends unless it's batch data pipelines
                    if is_weekend and "Data" not in dept:
                        base_cost *= np.random.uniform(0.65, 0.85)
                    else:
                        base_cost *= np.random.uniform(0.95, 1.15)
                    
                    # Compute hours & resource metrics
                    vCPU_hours = int(base_cost * np.random.uniform(8, 14))
                    memory_gb_hours = int(vCPU_hours * np.random.uniform(2.5, 4.0))
                    avg_cpu_utilization = np.clip(np.random.normal(48, 12) if not is_weekend else np.random.normal(25, 8), 5, 95)
                    storage_tb = round(np.random.uniform(2, 50) * trend_factor, 2)
                    data_egress_gb = round(np.random.uniform(50, 800) * (1.5 if is_weekend else 1.0), 1)
                    
                    # Anomaly injection flags
                    is_anomaly = 0
                    anomaly_type = "None"
                    waste_cost = 0.0
                    
                    # Anomaly 1: Zombie / Idle compute running unmonitored (low CPU but high cost)
                    if (day_idx in range(60, 68) or day_idx in range(210, 218)) and "Compute" in srv and dept == "AI/ML Research":
                        is_anomaly = 1
                        anomaly_type = "Idle/Zombie GPU/Compute Cluster"
                        base_cost *= 2.8
                        avg_cpu_utilization = np.random.uniform(3, 8)
                        waste_cost = base_cost * 0.75
                    
                    # Anomaly 2: Runaway Data Egress / Accidental public scrape
                    elif day_idx in [124, 125, 290, 291] and "Egress" in srv or "Bandwidth" in srv:
                        is_anomaly = 1
                        anomaly_type = "Unexpected Data Egress Surge"
                        data_egress_gb *= 8.5
                        base_cost *= 3.4
                        waste_cost = base_cost * 0.65

                    # Anomaly 3: Unattached Disks / Over-provisioned high-IOPS storage
                    elif (day_idx % 45 == 0) and "Storage" in srv:
                        is_anomaly = 1
                        anomaly_type = "Unattached Volumes & Orphan Snapshots"
                        base_cost *= 1.8
                        waste_cost = base_cost * 0.45
                        
                    # Calculate potential savings opportunity if right-sized
                    if avg_cpu_utilization < 20 and not is_anomaly:
                        right_sizing_opportunity = round(base_cost * 0.35, 2)
                        recommendation = "Downsize underutilized instances"
                    elif is_anomaly:
                        right_sizing_opportunity = round(waste_cost, 2)
                        recommendation = f"Immediate Alert: Remediate {anomaly_type}"
                    elif avg_cpu_utilization > 80:
                        right_sizing_opportunity = 0.0
                        recommendation = "Well-optimized (Consider Reserved Capacity)"
                    else:
                        right_sizing_opportunity = round(base_cost * 0.12, 2)
                        recommendation = "Shift to 1-Year Savings Plan"
                        
                    records.append({
                        "Date": current_date.strftime("%Y-%m-%d"),
                        "CloudProvider": prov,
                        "Department": dept,
                        "Service": srv,
                        "DailyCost_USD": round(base_cost, 2),
                        "vCPU_Hours": vCPU_hours,
                        "Memory_GB_Hours": memory_gb_hours,
                        "Avg_CPU_Utilization_Pct": round(avg_cpu_utilization, 1),
                        "Storage_TB": storage_tb,
                        "Data_Egress_GB": data_egress_gb,
                        "Is_Anomaly": is_anomaly,
                        "Anomaly_Type": anomaly_type,
                        "Est_Waste_Cost_USD": round(waste_cost, 2),
                        "Potential_Savings_USD": right_sizing_opportunity,
                        "FinOps_Recommendation": recommendation
                    })
                    
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "cloud_enterprise_billing_telemetry.csv")
    
    print("Generating comprehensive enterprise multi-cloud FinOps dataset...")
    df = generate_finops_dataset()
    df.to_csv(out_path, index=False)
    print(f"Successfully generated {len(df)} records across 365 days.")
    print(f"Dataset saved to: {out_path}")
    print(df.head())
