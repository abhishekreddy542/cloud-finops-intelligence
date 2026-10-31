import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from src.database import get_engine, initialize_database, optimize_database

def generate_enterprise_focus_dataset(start_date="2025-01-01", days=365, random_seed=42):
    """
    Generates authentic multi-cloud billing telemetry conforming to the official
    FinOps Open Cost & Usage Specification (FOCUS™ 1.0) standard.
    
    Synthesizes native billing schemas from:
      - AWS Cost and Usage Report (CUR 2.0)
      - Google Cloud BigQuery Detailed Billing Export
      - Azure Cost Management Export / Cost Details API
    
    Joined with continuous telemetry from AWS CloudWatch, Azure Monitor, and GCP Cloud Operations.
    """
    np.random.seed(random_seed)
    base = datetime.strptime(start_date, "%Y-%m-%d")
    date_list = [base + timedelta(days=i) for i in range(days)]
    
    providers = ["AWS", "Azure", "Google Cloud"]
    departments = ["AI/ML Research", "Data Platform", "Core Engineering", "Customer Portal", "Finance & Analytics"]
    
    # Provider-Specific Real-World Architecture Catalogs
    cloud_catalog = {
        "AWS": {
            "account_id": "942182019482",
            "account_name": "abhi-aws-enterprise-prod",
            "services": [
                {
                    "name": "AmazonEC2",
                    "category": "Compute",
                    "sku": "m6i.4xlarge On Demand",
                    "sku_id": "AWS-EC2-M6I-4XLARGE-US-EAST-1",
                    "resource_prefix": "arn:aws:ec2:us-east-1:942182019482:instance/i-0",
                    "res_type": "Virtual Machine",
                    "unit": "Hours",
                    "base_cost": 210.0
                },
                {
                    "name": "AmazonS3",
                    "category": "Storage",
                    "sku": "Standard Storage S3 US-East-1",
                    "sku_id": "AWS-S3-STANDARD-US-EAST-1",
                    "resource_prefix": "arn:aws:s3:::abhi-data-lake-",
                    "res_type": "Object Storage Bucket",
                    "unit": "GB",
                    "base_cost": 95.0
                },
                {
                    "name": "AmazonRDS",
                    "category": "Database",
                    "sku": "db.r6i.2xlarge Multi-AZ PostgreSQL",
                    "sku_id": "AWS-RDS-POSTGRES-R6I-2XLARGE",
                    "resource_prefix": "arn:aws:rds:us-east-1:942182019482:db:abhi-db-",
                    "res_type": "Relational Database",
                    "unit": "Hours",
                    "base_cost": 165.0
                },
                {
                    "name": "AmazonEKS",
                    "category": "Containers",
                    "sku": "EKS Managed Cluster Control Plane",
                    "sku_id": "AWS-EKS-CLUSTER-PLANE",
                    "resource_prefix": "arn:aws:eks:us-east-1:942182019482:cluster/abhi-k8s-",
                    "res_type": "Managed Kubernetes",
                    "unit": "Hours",
                    "base_cost": 130.0
                },
                {
                    "name": "AmazonCloudFront",
                    "category": "Network",
                    "sku": "CloudFront Global Data Transfer Out",
                    "sku_id": "AWS-CF-DATA-TRANSFER-OUT",
                    "resource_prefix": "arn:aws:cloudfront::942182019482:distribution/E2",
                    "res_type": "CDN & Egress",
                    "unit": "GB",
                    "base_cost": 115.0
                },
                {
                    "name": "AmazonEC2-Snapshots",
                    "category": "Storage",
                    "sku": "EBS:SnapshotUsage & AMI Machine Images",
                    "sku_id": "AWS-EBS-SNAPSHOT-US-EAST-1",
                    "resource_prefix": "arn:aws:ec2:us-east-1:942182019482:snapshot/snap-",
                    "res_type": "EBS Volume Snapshot & AMI",
                    "unit": "GB-Mo",
                    "base_cost": 85.0
                }
            ],
            "regions": [("us-east-1", "US East (N. Virginia)"), ("eu-central-1", "Europe (Frankfurt)"), ("ap-south-1", "Asia Pacific (Mumbai)")]
        },
        "Azure": {
            "account_id": "sub-a1b2c3d4-e5f6-7890",
            "account_name": "abhi-azure-production-sub",
            "services": [
                {
                    "name": "Microsoft.Compute",
                    "category": "Compute",
                    "sku": "Standard_D16s_v5 General Purpose",
                    "sku_id": "AZ-VM-D16S-V5-EASTUS",
                    "resource_prefix": "/subscriptions/sub-a1b2c3d4/resourceGroups/rg-abhi/providers/Microsoft.Compute/virtualMachines/vm-",
                    "res_type": "Virtual Machine",
                    "unit": "Hours",
                    "base_cost": 205.0
                },
                {
                    "name": "Microsoft.Storage",
                    "category": "Storage",
                    "sku": "Hot LRS Block Blob Storage",
                    "sku_id": "AZ-BLOB-HOT-LRS-EASTUS",
                    "resource_prefix": "/subscriptions/sub-a1b2c3d4/resourceGroups/rg-abhi/providers/Microsoft.Storage/storageAccounts/sa",
                    "res_type": "Blob Storage Container",
                    "unit": "GB",
                    "base_cost": 90.0
                },
                {
                    "name": "Microsoft.Sql",
                    "category": "Database",
                    "sku": "Azure SQL Database General Purpose 8-vCore",
                    "sku_id": "AZ-SQL-GP-8VCORE",
                    "resource_prefix": "/subscriptions/sub-a1b2c3d4/resourceGroups/rg-abhi/providers/Microsoft.Sql/servers/sql-",
                    "res_type": "Managed SQL Server",
                    "unit": "Hours",
                    "base_cost": 160.0
                },
                {
                    "name": "Microsoft.ContainerService",
                    "category": "Containers",
                    "sku": "AKS Managed Kubernetes Cluster",
                    "sku_id": "AZ-AKS-MANAGED-CLUSTER",
                    "resource_prefix": "/subscriptions/sub-a1b2c3d4/resourceGroups/rg-abhi/providers/Microsoft.ContainerService/managedClusters/aks-",
                    "res_type": "Container Cluster",
                    "unit": "Hours",
                    "base_cost": 125.0
                },
                {
                    "name": "Microsoft.Network",
                    "category": "Network",
                    "sku": "Standard Internet Egress Bandwidth",
                    "sku_id": "AZ-NET-EGRESS-BANDWIDTH",
                    "resource_prefix": "/subscriptions/sub-a1b2c3d4/resourceGroups/rg-abhi/providers/Microsoft.Network/bandwidth/egress-",
                    "res_type": "Network Transit",
                    "unit": "GB",
                    "base_cost": 110.0
                },
                {
                    "name": "Microsoft.Compute/snapshots",
                    "category": "Storage",
                    "sku": "Standard Managed Disk Snapshots & Compute Gallery Images",
                    "sku_id": "AZ-DISK-SNAPSHOTS-EASTUS",
                    "resource_prefix": "/subscriptions/sub-a1b2c3d4/resourceGroups/rg-abhi/providers/Microsoft.Compute/snapshots/snap-",
                    "res_type": "Disk Snapshot & Machine Image",
                    "unit": "GB",
                    "base_cost": 82.0
                }
            ],
            "regions": [("eastus", "East US (Virginia)"), ("westeurope", "West Europe (Netherlands)"), ("centralindia", "Central India (Pune)")]
        },
        "Google Cloud": {
            "account_id": "01A2B3-4C5D6E-7F8A9B",
            "account_name": "abhi-cloud-tech-prod-project",
            "services": [
                {
                    "name": "Compute Engine",
                    "category": "Compute",
                    "sku": "N2 Custom Instance Core running in Iowa",
                    "sku_id": "GCP-COMPUTE-N2-STANDARD-16",
                    "resource_prefix": "//compute.googleapis.com/projects/abhi-cloud-tech-prod/zones/us-central1-a/instances/n2-node-",
                    "res_type": "Compute Instance",
                    "unit": "Hours",
                    "base_cost": 200.0
                },
                {
                    "name": "Cloud Storage",
                    "category": "Storage",
                    "sku": "Standard Storage US Multi-region",
                    "sku_id": "GCP-STORAGE-STANDARD-US",
                    "resource_prefix": "//storage.googleapis.com/abhi-cloud-lake-",
                    "res_type": "Cloud Storage Bucket",
                    "unit": "GB",
                    "base_cost": 88.0
                },
                {
                    "name": "Cloud SQL",
                    "category": "Database",
                    "sku": "Cloud SQL for PostgreSQL 8 vCPU 32GB",
                    "sku_id": "GCP-SQL-POSTGRES-8VCPU",
                    "resource_prefix": "//cloudsql.googleapis.com/projects/abhi-cloud-tech-prod/instances/sql-",
                    "res_type": "Cloud SQL Instance",
                    "unit": "Hours",
                    "base_cost": 155.0
                },
                {
                    "name": "Google Kubernetes Engine",
                    "category": "Containers",
                    "sku": "GKE Autopilot Enterprise Cluster",
                    "sku_id": "GCP-GKE-AUTOPILOT-ENTERPRISE",
                    "resource_prefix": "//container.googleapis.com/projects/abhi-cloud-tech-prod/locations/us-central1/clusters/gke-",
                    "res_type": "Kubernetes Engine",
                    "unit": "Hours",
                    "base_cost": 120.0
                },
                {
                    "name": "Cloud Interconnect & CDN",
                    "category": "Network",
                    "sku": "Network Internet Egress from Iowa",
                    "sku_id": "GCP-NET-EGRESS-INTERNET-US",
                    "resource_prefix": "//compute.googleapis.com/projects/abhi-cloud-tech-prod/global/networks/vpc-egress-",
                    "res_type": "Internet Egress",
                    "unit": "GB",
                    "base_cost": 105.0
                },
                {
                    "name": "Compute Engine - Snapshots & Images",
                    "category": "Storage",
                    "sku": "Persistent Disk Snapshot & Custom Machine Image Storage",
                    "sku_id": "GCP-COMPUTE-SNAPSHOT-IMAGE-US",
                    "resource_prefix": "//compute.googleapis.com/projects/abhi-cloud-tech-prod/global/snapshots/snap-",
                    "res_type": "Persistent Disk Snapshot & Machine Image",
                    "unit": "GB",
                    "base_cost": 80.0
                }
            ],
            "regions": [("us-central1", "US Central (Iowa)"), ("europe-west3", "Europe (Frankfurt)"), ("asia-south1", "Asia South (Mumbai)")]
        }
    }

    records = []
    
    for current_date in date_list:
        day_str = current_date.strftime("%Y-%m-%d")
        next_day_str = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
        day_of_week = current_date.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        day_idx = (current_date - base).days
        trend_factor = 1.0 + (0.00085 * day_idx) # Organic corporate workload growth
        
        # Monthly billing period bounds (FOCUS 1.0)
        billing_period_start = current_date.replace(day=1).strftime("%Y-%m-%d")
        if current_date.month == 12:
            billing_period_end = current_date.replace(year=current_date.year + 1, month=1, day=1).strftime("%Y-%m-%d")
        else:
            billing_period_end = current_date.replace(month=current_date.month + 1, day=1).strftime("%Y-%m-%d")
        
        issuer_map = {
            "AWS": "Amazon Web Services, Inc.",
            "Azure": "Microsoft Corporation",
            "Google Cloud": "Google LLC"
        }
        
        for dept in departments:
            # Departmental budget multiplier
            dept_mult = {
                "AI/ML Research": 2.25,
                "Data Platform": 1.85,
                "Core Engineering": 1.45,
                "Customer Portal": 1.05,
                "Finance & Analytics": 0.70
            }[dept]
            
            for prov_name, prov_info in cloud_catalog.items():
                for srv in prov_info["services"]:
                    # Select primary region
                    region_idx = np.random.choice([0, 1, 2], p=[0.60, 0.25, 0.15])
                    region_id, region_name = prov_info["regions"][region_idx]
                    
                    # Compute realistic continuous telemetry
                    base_unit_cost = srv["base_cost"] * dept_mult * trend_factor * np.random.uniform(0.92, 1.08)
                    
                    if is_weekend and dept != "Data Platform":
                        base_unit_cost *= np.random.uniform(0.68, 0.84)
                        
                    # Quantities
                    consumed_qty = round(base_unit_cost * np.random.uniform(9.0, 14.5), 1)
                    is_snapshot_srv = any(k in srv["name"].lower() for k in ["snapshot", "image"])
                    if is_snapshot_srv:
                        avg_cpu = float(np.random.uniform(0.0, 1.5))
                        max_cpu = float(np.random.uniform(0.0, 3.5))
                        mem_gb = 0.0
                        storage_tb = round(np.random.uniform(18.0, 68.0) * trend_factor, 2)
                        egress_gb = round(np.random.uniform(2.0, 35.0), 1)
                    else:
                        avg_cpu = float(np.clip(np.random.normal(48, 12) if not is_weekend else np.random.normal(24, 7), 5.0, 94.0))
                        max_cpu = float(np.clip(avg_cpu + np.random.uniform(12, 28), avg_cpu, 99.5))
                        mem_gb = round(consumed_qty * np.random.uniform(2.5, 4.0), 1)
                        storage_tb = round(np.random.uniform(2.5, 55.0) * trend_factor, 2)
                        egress_gb = round(np.random.uniform(40.0, 850.0) * (1.6 if is_weekend else 1.0), 1)
                    
                    # Anomaly injection flags
                    is_anomaly = 0
                    anomaly_type = "None"
                    waste_cost = 0.0
                    billed_cost = base_unit_cost
                    
                    # Anomaly 1: Zombie / Idle GPU or Compute Cluster
                    if (day_idx in range(60, 68) or day_idx in range(210, 218)) and srv["category"] == "Compute" and dept == "AI/ML Research":
                        is_anomaly = 1
                        anomaly_type = "Idle/Zombie GPU/Compute Cluster"
                        billed_cost *= 2.85
                        avg_cpu = float(np.random.uniform(3.5, 8.0))
                        max_cpu = float(np.random.uniform(10.0, 18.0))
                        waste_cost = billed_cost * 0.75
                        
                    # Anomaly 2: Runaway Network Data Egress
                    elif day_idx in [124, 125, 290, 291] and srv["category"] == "Network":
                        is_anomaly = 1
                        anomaly_type = "Unexpected Data Egress Surge"
                        egress_gb *= 8.6
                        billed_cost *= 3.45
                        waste_cost = billed_cost * 0.68
                        
                    # Anomaly 3: Storage Sprawl / Orphan Disks
                    elif (day_idx % 45 == 0) and srv["category"] == "Storage" and not is_snapshot_srv:
                        is_anomaly = 1
                        anomaly_type = "Unattached Volumes & Orphan Snapshots"
                        billed_cost *= 1.82
                        waste_cost = billed_cost * 0.46
                        
                    # Anomaly 4: Stale Machine Images & Unattached Disk Snapshots (AWS AMIs, Azure Disk Snapshots, GCP Custom Images)
                    elif (day_idx in range(40, 48) or day_idx in range(180, 188) or day_idx in range(310, 318)) and is_snapshot_srv:
                        is_anomaly = 1
                        anomaly_type = "Orphan Snapshots & Stale Machine Images"
                        billed_cost *= 2.65
                        storage_tb = float(np.random.uniform(55.0, 140.0))
                        waste_cost = billed_cost * 0.85 # 85% waste from abandoned backups & stale VM images
                        
                    # Pricing & Commitments
                    pricing_cat = "On-Demand"
                    effective_cost = billed_cost
                    list_cost = billed_cost * 1.05
                    
                    if avg_cpu > 40 and not is_anomaly:
                        pricing_cat = "CommitmentDiscount"
                        effective_cost = billed_cost * 0.72 # 28% commitment discount applied
                        
                    # Canonical Resource ID
                    res_hash = uuid.uuid4().hex[:8]
                    res_id = f"{srv['resource_prefix']}{dept.lower().replace('/', '-').replace(' ', '-')}-{res_hash}"
                    res_name = f"{prov_name.lower()[:3]}-{srv['name'].lower()[:6]}-{res_hash}"
                    
                    records.append({
                        "RecordId": f"REC-{day_idx:03d}-{prov_name[:3]}-{res_hash}",
                        "ChargePeriodStart": day_str,
                        "ChargePeriodEnd": next_day_str,
                        "BillingPeriodStart": billing_period_start,
                        "BillingPeriodEnd": billing_period_end,
                        "BillingCurrency": "USD",
                        "PricingCurrency": "USD",
                        "ProviderName": "AWS" if prov_name == "AWS" else "Azure" if prov_name == "Azure" else "GCP",
                        "InvoiceIssuer": issuer_map.get(prov_name, "Cloud Service Provider"),
                        "BillingAccountId": prov_info["account_id"],
                        "BillingAccountName": prov_info["account_name"],
                        "SubAccountId": f"sub-{dept.lower()[:4]}-{prov_info['account_id'][:6]}",
                        "SubAccountName": f"{dept.lower().replace('/', '-').replace(' ', '-')}-prod",
                        "RegionId": region_id,
                        "RegionName": region_name,
                        "ServiceName": srv["name"],
                        "ServiceCategory": srv["category"],
                        "ResourceId": res_id,
                        "ResourceName": res_name,
                        "ResourceType": srv["res_type"],
                        "SkuId": srv["sku_id"],
                        "SkuDescription": srv["sku"],
                        "ConsumedQuantity": round(consumed_qty, 1),
                        "ConsumedUnit": srv["unit"],
                        "BilledCost": round(billed_cost, 2),
                        "EffectiveCost": round(effective_cost, 2),
                        "ListCost": round(list_cost, 2),
                        "PricingCategory": pricing_cat,
                        "ChargeCategory": "Usage",
                        "ChargeClass": "Original",
                        "ChargeFrequency": "Usage-Based",
                        "TagCostCenter": dept,
                        "TagEnvironment": "Production" if dept != "AI/ML Research" else "Research-Lab",
                        "TagOwner": f"lead.{dept.lower()[:4]}@abhicloudtech.com",
                        "AvgCpuUtilizationPct": round(avg_cpu, 1),
                        "MaxCpuUtilizationPct": round(max_cpu, 1),
                        "MemoryAllocatedGB": round(mem_gb, 1),
                        "StorageAllocatedTB": round(storage_tb, 2),
                        "NetworkEgressGB": round(egress_gb, 1),
                        "IsAnomaly": is_anomaly,
                        "AnomalyType": anomaly_type,
                        "EstWasteCostUSD": round(waste_cost, 2)
                    })
                    
    df = pd.DataFrame(records)
    return df

def seed_database_and_export_csv():
    """Generates FOCUS 1.0 records, populates SQLite finops_warehouse.db, and exports CSV"""
    initialize_database()
    engine = get_engine()
    
    print("\n" + "=" * 65)
    print("[*] Generating FinOps Open Cost & Usage Specification (FOCUS 1.0) Dataset...")
    print("=" * 65)
    
    df = generate_enterprise_focus_dataset(days=365)
    print(f"Generated {len(df):,} normalized multi-cloud records across 365 days.")
    
    # Write to SQLite
    print("Inserting records into SQLite table 'unified_focus_billing'...")
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM unified_focus_billing;"))
        conn.commit()
    df.to_sql("unified_focus_billing", engine, if_exists="append", index=False)
    optimize_database()
    print("[+] Records successfully indexed and query plans optimized in 'data/finops_warehouse.db'!")
    
    # Export backward-compatible CSV with standard columns for immediate caching
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    csv_path = os.path.join(data_dir, "cloud_enterprise_billing_telemetry.csv")
    
    # Create the unified CSV format
    csv_df = df.copy()
    csv_df["Date"] = csv_df["ChargePeriodStart"]
    csv_df["CloudProvider"] = csv_df["ProviderName"]
    csv_df["Department"] = csv_df["TagCostCenter"]
    csv_df["Service"] = csv_df["ServiceName"] + " (" + csv_df["ServiceCategory"] + ")"
    csv_df["DailyCost_USD"] = csv_df["BilledCost"]
    csv_df["vCPU_Hours"] = csv_df["ConsumedQuantity"]
    csv_df["Memory_GB_Hours"] = csv_df["MemoryAllocatedGB"]
    csv_df["Avg_CPU_Utilization_Pct"] = csv_df["AvgCpuUtilizationPct"]
    csv_df["Storage_TB"] = csv_df["StorageAllocatedTB"]
    csv_df["Data_Egress_GB"] = csv_df["NetworkEgressGB"]
    csv_df["Is_Anomaly"] = csv_df["IsAnomaly"]
    csv_df["Anomaly_Type"] = csv_df["AnomalyType"]
    csv_df["Est_Waste_Cost_USD"] = csv_df["EstWasteCostUSD"]
    
    def recommend(row):
        if row["Is_Anomaly"] == 1:
            return f"Immediate Alert: Remediate {row['Anomaly_Type']}"
        elif row["Avg_CPU_Utilization_Pct"] < 20:
            return "Downsize underutilized instances"
        elif row["Avg_CPU_Utilization_Pct"] > 80:
            return "Well-optimized (Consider Reserved Capacity)"
        else:
            return "Shift to 1-Year Savings Plan"
            
    csv_df["FinOps_Recommendation"] = csv_df.apply(recommend, axis=1)
    csv_df["Potential_Savings_USD"] = np.where(
        csv_df["Is_Anomaly"] == 1, 
        csv_df["Est_Waste_Cost_USD"],
        np.where(csv_df["Avg_CPU_Utilization_Pct"] < 20, csv_df["DailyCost_USD"] * 0.35, csv_df["DailyCost_USD"] * 0.20)
    ).round(2)
    
    try:
        csv_df.to_csv(csv_path, index=False)
        print(f"[+] CSV Export generated at: {csv_path}")
    except PermissionError:
        alt_path = os.path.join(data_dir, "cloud_enterprise_billing_telemetry_latest.csv")
        csv_df.to_csv(alt_path, index=False)
        print(f"[!] '{csv_path}' is open in another application (e.g. Excel). Generated latest snapshot at: {alt_path}")
    print("=" * 65 + "\n")
    return df

if __name__ == "__main__":
    seed_database_and_export_csv()
