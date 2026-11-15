"""
generate_benchmark_datasets.py
==============================================================================
Abhi Cloud Tech - Multi-Cloud FinOps Intelligence Platform
Benchmark Synthetic Telemetry & Ground-Truth Dataset Generator
==============================================================================
Generates 4 authentic, production-grade cloud billing datasets:
  1. data/benchmark_focus_1_0_multicloud.csv  (FOCUS 1.0 Standard Multi-Cloud)
  2. data/benchmark_gcp_billing_export.csv   (Google Cloud BigQuery Detailed Export)
  3. data/benchmark_azure_cost_export.csv    (Microsoft Azure Cost Management Export)
  4. data/benchmark_aws_cur_export.csv       (AWS Cost & Usage Report CUR 2.0)

Features:
  - 92 days continuous telemetry (2025-06-01 to 2025-08-31)
  - Realistic diurnal & weekly seasonality, organic growth factor
  - Compute, Database, Storage, Networking, AI/ML, Serverless/Containers
  - Precision-recall ground-truth anomaly annotations (x_AnomalyFlag, x_AnomalySeverity)
==============================================================================
"""

import os
import sys
import uuid
import datetime
import numpy as np
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
START_DATE_STR = "2025-06-01"
DAYS_COUNT = 92  # 92 days: June 1, 2025 to August 31, 2025


def get_date_range(start_date=START_DATE_STR, days=DAYS_COUNT):
    base = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    return [base + datetime.timedelta(days=i) for i in range(days)]


# ============================================================================
# 1. GENERATOR: Unified FOCUS 1.0 Multi-Cloud Benchmark Dataset
# ============================================================================
def generate_benchmark_focus_dataset(dates):
    np.random.seed(RANDOM_SEED)
    print("\n[1/4] Generating Unified FOCUS 1.0 Multi-Cloud Benchmark Dataset...")

    departments = [
        {"name": "AI/ML Research", "code": "CC-101", "weight": 2.20, "env": "Research-Lab", "owner": "dr.patel@abhicloudtech.com"},
        {"name": "Data Platform", "code": "CC-102", "weight": 1.75, "env": "Production", "owner": "data.lead@abhicloudtech.com"},
        {"name": "Core Engineering", "code": "CC-103", "weight": 1.40, "env": "Production", "owner": "eng.director@abhicloudtech.com"},
        {"name": "Customer Portal", "code": "CC-104", "weight": 1.00, "env": "Production", "owner": "portal.lead@abhicloudtech.com"},
        {"name": "Finance & Analytics", "code": "CC-105", "weight": 0.65, "env": "Production", "owner": "finops@abhicloudtech.com"}
    ]

    # Service catalog across AWS, Azure, Google Cloud
    catalog = [
        # AWS Services (Weight ~45%)
        {"provider": "AWS", "pub": "Amazon Web Services", "issuer": "Amazon Web Services, Inc.", "account_id": "942182019482", "account_name": "abhi-aws-enterprise-prod",
         "service": "AmazonEC2", "category": "Compute", "res_type": "Virtual Machine", "sku": "EC2-M6I-4XLARGE-US-EAST-1", "sku_desc": "m6i.4xlarge Linux On-Demand", "unit": "Hours", "price_unit": "Hours", "base_cost": 215.0, "region_id": "us-east-1", "region_name": "US East (N. Virginia)"},
        {"provider": "AWS", "pub": "Amazon Web Services", "issuer": "Amazon Web Services, Inc.", "account_id": "942182019482", "account_name": "abhi-aws-enterprise-prod",
         "service": "AmazonRDS", "category": "Database", "res_type": "Relational Database", "sku": "RDS-POSTGRES-R6I-2XLARGE", "sku_desc": "db.r6i.2xlarge Multi-AZ PostgreSQL", "unit": "Hours", "price_unit": "Hours", "base_cost": 175.0, "region_id": "us-east-1", "region_name": "US East (N. Virginia)"},
        {"provider": "AWS", "pub": "Amazon Web Services", "issuer": "Amazon Web Services, Inc.", "account_id": "942182019482", "account_name": "abhi-aws-enterprise-prod",
         "service": "AmazonS3", "category": "Storage", "res_type": "Object Storage Bucket", "sku": "S3-STANDARD-BYTE-HOURS", "sku_desc": "S3 Standard TimedStorage-ByteHrs", "unit": "GB", "price_unit": "GB-Mo", "base_cost": 95.0, "region_id": "us-east-1", "region_name": "US East (N. Virginia)"},
        {"provider": "AWS", "pub": "Amazon Web Services", "issuer": "Amazon Web Services, Inc.", "account_id": "942182019482", "account_name": "abhi-aws-enterprise-prod",
         "service": "AmazonCloudFront", "category": "Networking", "res_type": "CDN & Egress", "sku": "CF-DATA-TRANSFER-OUT", "sku_desc": "CloudFront Global Egress Out to Internet", "unit": "GB", "price_unit": "GB", "base_cost": 110.0, "region_id": "global", "region_name": "Global Edge Network"},
        {"provider": "AWS", "pub": "Amazon Web Services", "issuer": "Amazon Web Services, Inc.", "account_id": "942182019482", "account_name": "abhi-aws-enterprise-prod",
         "service": "AmazonSageMaker", "category": "AI and Machine Learning", "res_type": "ML Training & Endpoint", "sku": "SM-TRAINING-ML-G5-2XL", "sku_desc": "SageMaker Training ml.g5.2xlarge GPU", "unit": "Hours", "price_unit": "Hours", "base_cost": 240.0, "region_id": "us-east-1", "region_name": "US East (N. Virginia)"},
        {"provider": "AWS", "pub": "Amazon Web Services", "issuer": "Amazon Web Services, Inc.", "account_id": "942182019482", "account_name": "abhi-aws-enterprise-prod",
         "service": "AWSLambda", "category": "Serverless", "res_type": "Serverless Function", "sku": "LAMBDA-DURATION-ARM", "sku_desc": "Lambda Graviton2 Invocation & Duration", "unit": "Requests", "price_unit": "Million-Requests", "base_cost": 45.0, "region_id": "us-east-1", "region_name": "US East (N. Virginia)"},
        {"provider": "AWS", "pub": "Amazon Web Services", "issuer": "Amazon Web Services, Inc.", "account_id": "942182019482", "account_name": "abhi-aws-enterprise-prod",
         "service": "AmazonEBS", "category": "Storage", "res_type": "Block Storage Snapshot", "sku": "EBS-SNAPSHOT-TIER", "sku_desc": "EBS SnapshotArchive Usage & Stored AMI", "unit": "GB-Mo", "price_unit": "GB-Mo", "base_cost": 75.0, "region_id": "us-east-1", "region_name": "US East (N. Virginia)"},
        {"provider": "AWS", "pub": "Amazon Web Services", "issuer": "Amazon Web Services, Inc.", "account_id": "942182019482", "account_name": "abhi-aws-enterprise-prod",
         "service": "AmazonDynamoDB", "category": "Database", "res_type": "NoSQL Database", "sku": "DDB-PAY-PER-REQUEST", "sku_desc": "DynamoDB On-Demand WCU & RCU", "unit": "Requests", "price_unit": "Million-Requests", "base_cost": 65.0, "region_id": "us-east-1", "region_name": "US East (N. Virginia)"},

        # Azure Services (Weight ~35%)
        {"provider": "Azure", "pub": "Microsoft", "issuer": "Microsoft Corporation", "account_id": "sub-prod-enterprise-01", "account_name": "abhi-azure-production-ea",
         "service": "Microsoft.Compute", "category": "Compute", "res_type": "Virtual Machine", "sku": "AZ-VM-D16S-V5-EASTUS", "sku_desc": "Standard_D16s_v5 General Compute", "unit": "Hours", "price_unit": "Hours", "base_cost": 210.0, "region_id": "eastus", "region_name": "East US"},
        {"provider": "Azure", "pub": "Microsoft", "issuer": "Microsoft Corporation", "account_id": "sub-prod-enterprise-01", "account_name": "abhi-azure-production-ea",
         "service": "Microsoft.Sql", "category": "Database", "res_type": "Managed SQL Server", "sku": "AZ-SQL-GP-8VCORE", "sku_desc": "Azure SQL Gen5 8-vCore General Purpose", "unit": "Hours", "price_unit": "Hours", "base_cost": 165.0, "region_id": "eastus", "region_name": "East US"},
        {"provider": "Azure", "pub": "Microsoft", "issuer": "Microsoft Corporation", "account_id": "sub-prod-enterprise-01", "account_name": "abhi-azure-production-ea",
         "service": "Microsoft.Storage", "category": "Storage", "res_type": "Blob Storage Container", "sku": "AZ-BLOB-HOT-LRS", "sku_desc": "Hot LRS Block Blob Capacity", "unit": "GB", "price_unit": "GB-Mo", "base_cost": 90.0, "region_id": "eastus", "region_name": "East US"},
        {"provider": "Azure", "pub": "Microsoft", "issuer": "Microsoft Corporation", "account_id": "sub-prod-enterprise-01", "account_name": "abhi-azure-production-ea",
         "service": "Microsoft.Network", "category": "Networking", "res_type": "Virtual Network Gateway", "sku": "AZ-NET-EGRESS-ZONE1", "sku_desc": "Bandwidth Egress Zone 1 Internet Out", "unit": "GB", "price_unit": "GB", "base_cost": 105.0, "region_id": "eastus", "region_name": "East US"},
        {"provider": "Azure", "pub": "Microsoft", "issuer": "Microsoft Corporation", "account_id": "sub-prod-enterprise-01", "account_name": "abhi-azure-production-ea",
         "service": "Microsoft.CognitiveServices", "category": "AI and Machine Learning", "res_type": "Azure OpenAI Service", "sku": "AZ-OPENAI-GPT4-PROD", "sku_desc": "Azure OpenAI GPT-4o Token Consumption", "unit": "Requests", "price_unit": "1K-Tokens", "base_cost": 225.0, "region_id": "eastus2", "region_name": "East US 2"},
        {"provider": "Azure", "pub": "Microsoft", "issuer": "Microsoft Corporation", "account_id": "sub-prod-enterprise-01", "account_name": "abhi-azure-production-ea",
         "service": "Microsoft.ContainerService", "category": "Serverless", "res_type": "Container Cluster", "sku": "AZ-AKS-MANAGED-SYSTEM", "sku_desc": "AKS Managed Cluster Standard Node Pool", "unit": "Hours", "price_unit": "Hours", "base_cost": 135.0, "region_id": "eastus", "region_name": "East US"},

        # Google Cloud Services (Weight ~20%)
        {"provider": "Google Cloud", "pub": "Google Cloud", "issuer": "Google LLC", "account_id": "01A2B3-4C5D6E-7F8G9H", "account_name": "abhi-gcp-enterprise-billing",
         "service": "Compute Engine", "category": "Compute", "res_type": "Compute Instance", "sku": "GCP-COMPUTE-N2-STANDARD-8", "sku_desc": "N2 Instance Core running in Iowa", "unit": "Hours", "price_unit": "Hours", "base_cost": 195.0, "region_id": "us-central1", "region_name": "US Central (Iowa)"},
        {"provider": "Google Cloud", "pub": "Google Cloud", "issuer": "Google LLC", "account_id": "01A2B3-4C5D6E-7F8G9H", "account_name": "abhi-gcp-enterprise-billing",
         "service": "Cloud SQL", "category": "Database", "res_type": "Cloud SQL Instance", "sku": "GCP-SQL-POSTGRES-8VCPU", "sku_desc": "Cloud SQL for PostgreSQL 8 vCPU", "unit": "Hours", "price_unit": "Hours", "base_cost": 160.0, "region_id": "us-central1", "region_name": "US Central (Iowa)"},
        {"provider": "Google Cloud", "pub": "Google Cloud", "issuer": "Google LLC", "account_id": "01A2B3-4C5D6E-7F8G9H", "account_name": "abhi-gcp-enterprise-billing",
         "service": "Cloud Storage", "category": "Storage", "res_type": "Storage Bucket", "sku": "GCP-STORAGE-STANDARD-US", "sku_desc": "Standard Storage Multi-Region US", "unit": "GB", "price_unit": "GB-Mo", "base_cost": 85.0, "region_id": "us-multi-region", "region_name": "United States Multi-Region"},
        {"provider": "Google Cloud", "pub": "Google Cloud", "issuer": "Google LLC", "account_id": "01A2B3-4C5D6E-7F8G9H", "account_name": "abhi-gcp-enterprise-billing",
         "service": "Cloud Interconnect & CDN", "category": "Networking", "res_type": "Internet Egress", "sku": "GCP-NET-EGRESS-INTERNET-US", "sku_desc": "Network Internet Egress from Iowa", "unit": "GB", "price_unit": "GB", "base_cost": 100.0, "region_id": "us-central1", "region_name": "US Central (Iowa)"},
        {"provider": "Google Cloud", "pub": "Google Cloud", "issuer": "Google LLC", "account_id": "01A2B3-4C5D6E-7F8G9H", "account_name": "abhi-gcp-enterprise-billing",
         "service": "Vertex AI", "category": "AI and Machine Learning", "res_type": "Vertex AI Prediction Endpoint", "sku": "GCP-VERTEX-GEMINI-ENDPOINT", "sku_desc": "Vertex AI Custom Model & Gemini Endpoint", "unit": "Hours", "price_unit": "Hours", "base_cost": 230.0, "region_id": "us-central1", "region_name": "US Central (Iowa)"},
        {"provider": "Google Cloud", "pub": "Google Cloud", "issuer": "Google LLC", "account_id": "01A2B3-4C5D6E-7F8G9H", "account_name": "abhi-gcp-enterprise-billing",
         "service": "Cloud Run", "category": "Serverless", "res_type": "Serverless Container", "sku": "GCP-RUN-CPU-ALLOCATION", "sku_desc": "Cloud Run CPU Allocation Time & Memory", "unit": "Requests", "price_unit": "Million-Requests", "base_cost": 50.0, "region_id": "us-central1", "region_name": "US Central (Iowa)"}
    ]

    records = []

    for day_idx, current_date in enumerate(dates):
        day_str = current_date.strftime("%Y-%m-%dT00:00:00Z")
        next_day_str = (current_date + datetime.timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
        billing_period_start = current_date.replace(day=1).strftime("%Y-%m-%d")
        if current_date.month == 12:
            billing_period_end = current_date.replace(year=current_date.year + 1, month=1, day=1).strftime("%Y-%m-%d")
        else:
            billing_period_end = current_date.replace(month=current_date.month + 1, day=1).strftime("%Y-%m-%d")

        is_weekend = 1 if current_date.weekday() >= 5 else 0
        trend_factor = 1.0 + (0.0009 * day_idx)  # Organic growth ~8.3% over quarter

        # Month-end batch ETL boost (days 28-31)
        month_end_boost = 1.25 if current_date.day >= 28 else 1.0

        for dept in departments:
            dept_mult = dept["weight"]

            for item in catalog:
                prov = item["provider"]
                srv_name = item["service"]
                category = item["category"]

                # Base cost computation
                base = item["base_cost"] * dept_mult * trend_factor * np.random.uniform(0.94, 1.06)

                # Weekend discount for non-data platform compute/serverless
                if is_weekend and dept["name"] != "Data Platform" and category in ["Compute", "Serverless"]:
                    base *= np.random.uniform(0.65, 0.82)
                elif category == "Database" and dept["name"] == "Data Platform":
                    base *= month_end_boost

                consumed_qty = round(base * np.random.uniform(8.5, 14.0), 2)
                billed_cost = base
                waste_cost = 0.0
                anomaly_flag = 0
                anomaly_severity = "NONE"
                anomaly_type = "None"

                avg_cpu = float(np.clip(np.random.normal(52, 10) if not is_weekend else np.random.normal(26, 6), 5.0, 95.0))
                egress_gb = round(float(np.random.uniform(15.0, 140.0) * (0.6 if is_weekend else 1.2)), 2)
                storage_tb = round(float(np.random.uniform(5.0, 65.0) * trend_factor), 2)

                # -------------------------------------------------------------
                # Ground-Truth Synthetic Anomaly Injections
                # -------------------------------------------------------------
                # Anomaly Scenario 1: CRITICAL Idle/Zombie GPU or High-End Compute Cluster
                if (day_idx in range(18, 24) or day_idx in range(64, 70)) and category in ["Compute", "AI and Machine Learning"] and dept["name"] == "AI/ML Research":
                    anomaly_flag = 1
                    anomaly_severity = "CRITICAL"
                    anomaly_type = "Idle/Zombie GPU Cluster"
                    billed_cost *= 3.8
                    consumed_qty *= 3.8
                    avg_cpu = float(np.random.uniform(2.1, 4.8))  # Underutilized
                    waste_cost = billed_cost * 0.82

                # Anomaly Scenario 2: CRITICAL Runaway Network Data Egress Surge
                elif (day_idx in [32, 33, 76, 77]) and category == "Networking":
                    anomaly_flag = 1
                    anomaly_severity = "CRITICAL"
                    anomaly_type = "Runaway Network Data Egress Surge"
                    billed_cost *= 4.6
                    consumed_qty *= 4.6
                    egress_gb *= 9.5
                    waste_cost = billed_cost * 0.74

                # Anomaly Scenario 3: HIGH Autoscaling Runaway Loop / Memory Leak
                elif (day_idx in [41, 42, 85, 86]) and category == "Serverless":
                    anomaly_flag = 1
                    anomaly_severity = "HIGH"
                    anomaly_type = "Autoscaling Runaway Loop"
                    billed_cost *= 3.2
                    consumed_qty *= 3.2
                    avg_cpu = float(np.random.uniform(88.0, 98.0))
                    waste_cost = billed_cost * 0.65

                # Anomaly Scenario 4: HIGH Cross-Region Replication Surge
                elif (day_idx in [52, 53]) and category == "Storage" and dept["name"] == "Data Platform":
                    anomaly_flag = 1
                    anomaly_severity = "HIGH"
                    anomaly_type = "Cross-Region Storage Replication Surge"
                    billed_cost *= 2.9
                    consumed_qty *= 2.9
                    storage_tb *= 2.4
                    waste_cost = billed_cost * 0.55

                # Anomaly Scenario 5: MEDIUM Stale Machine Images & Unattached Snapshots
                elif (day_idx % 22 == 0) and item["res_type"] == "Block Storage Snapshot":
                    anomaly_flag = 1
                    anomaly_severity = "MEDIUM"
                    anomaly_type = "Orphan Storage Volumes & Stale Snapshots"
                    billed_cost *= 2.1
                    consumed_qty *= 2.1
                    storage_tb *= 1.8
                    waste_cost = billed_cost * 0.70

                # Anomaly Scenario 6: MEDIUM Expired Reservation / On-Demand Fallback
                elif (day_idx in range(58, 62)) and category == "Database" and dept["name"] == "Core Engineering":
                    anomaly_flag = 1
                    anomaly_severity = "MEDIUM"
                    anomaly_type = "Expired Reservation Fallback"
                    billed_cost *= 1.65
                    waste_cost = billed_cost * 0.35

                # Pricing & Commitments
                if anomaly_flag == 1:
                    pricing_cat = "On-Demand"
                    commit_type = "None"
                    commit_cat = ""
                    commit_id = ""
                    commit_name = ""
                    commit_status = ""
                    effective_cost = billed_cost
                    list_cost = billed_cost * 1.05
                elif avg_cpu > 45.0 and not is_weekend:
                    pricing_cat = "CommitmentDiscount"
                    if prov == "AWS":
                        commit_type = "Savings Plan"
                        commit_id = "sp-9a8b7c6d-2025"
                        commit_name = "Compute Savings Plan 3-Year No Upfront"
                    elif prov == "Azure":
                        commit_type = "Reserved Instance"
                        commit_id = "res-az-prod-d16s"
                        commit_name = "Azure Reserved VM Instance 1-Year"
                    else:
                        commit_type = "Committed Use Discount"
                        commit_id = "cud-gcp-iowa-c2"
                        commit_name = "GCP Compute Engine 1-Year CUD"
                    commit_cat = "Usage"
                    commit_status = "Used"
                    effective_cost = billed_cost * 0.72  # 28% commitment discount
                    list_cost = billed_cost * 1.08
                else:
                    pricing_cat = "On-Demand"
                    commit_type = "None"
                    commit_cat = ""
                    commit_id = ""
                    commit_name = ""
                    commit_status = ""
                    effective_cost = billed_cost
                    list_cost = billed_cost * 1.04

                contracted_cost = round(list_cost * 0.95, 4)
                res_hash = uuid.uuid4().hex[:8]
                res_id = f"urn:{prov.lower()}:prod:{category.lower()}:{dept['name'].lower().replace(' ', '-').replace('/', '-')}:{res_hash}"
                res_name = f"{prov.lower()[:3]}-{srv_name.lower().replace('.', '-')[:12]}-{res_hash}"

                tags_str = f'{{"CostCenter":"{dept["code"]}","Department":"{dept["name"]}","Environment":"{dept["env"]}","Owner":"{dept["owner"]}"}}'

                records.append({
                    "ChargePeriodStart": day_str,
                    "ChargePeriodEnd": next_day_str,
                    "BillingPeriodStart": billing_period_start,
                    "BillingPeriodEnd": billing_period_end,
                    "ProviderName": prov,
                    "PublisherName": item["pub"],
                    "InvoiceIssuerName": item["issuer"],
                    "BillingAccountId": item["account_id"],
                    "BillingAccountName": item["account_name"],
                    "SubAccountId": f"sub-{dept['code'].lower()}-{prov.lower()[:3]}",
                    "SubAccountName": f"{dept['name'].lower().replace(' ', '-').replace('/', '-')}-{prov.lower()[:3]}-prod",
                    "ChargeCategory": "Usage",
                    "ChargeClass": "Original",
                    "ChargeDescription": f"{item['sku_desc']} Daily Allocated Telemetry",
                    "ChargeFrequency": "Usage-Based",
                    "BilledCost": round(billed_cost, 4),
                    "EffectiveCost": round(effective_cost, 4),
                    "ContractedCost": round(contracted_cost, 4),
                    "ListCost": round(list_cost, 4),
                    "BillingCurrency": "USD",
                    "PricingCurrency": "USD",
                    "PricingCategory": pricing_cat,
                    "PricingQuantity": round(consumed_qty, 2),
                    "PricingUnit": item["price_unit"],
                    "ConsumedQuantity": round(consumed_qty, 2),
                    "ConsumedUnit": item["unit"],
                    "ServiceName": srv_name,
                    "ServiceCategory": category,
                    "ResourceType": item["res_type"],
                    "ResourceId": res_id,
                    "ResourceName": res_name,
                    "SkuId": item["sku"],
                    "SkuPriceId": f"PRC-{item['sku']}",
                    "SkuDescription": item["sku_desc"],
                    "RegionId": item["region_id"],
                    "RegionName": item["region_name"],
                    "CommitmentDiscountCategory": commit_cat,
                    "CommitmentDiscountId": commit_id,
                    "CommitmentDiscountName": commit_name,
                    "CommitmentDiscountStatus": commit_status,
                    "CommitmentDiscountType": commit_type,
                    "Tags": tags_str,
                    "x_CostCenter": dept["name"],
                    "x_CostCenterCode": dept["code"],
                    "x_Environment": dept["env"],
                    "x_Owner": dept["owner"],
                    "x_AnomalyFlag": anomaly_flag,
                    "x_AnomalySeverity": anomaly_severity,
                    "x_AnomalyType": anomaly_type,
                    "x_EstWasteCostUSD": round(waste_cost, 2),
                    "x_AvgCpuUtilizationPct": round(avg_cpu, 1),
                    "x_DataEgressGB": round(egress_gb, 2),
                    "x_StorageAllocatedTB": round(storage_tb, 2)
                })

    df = pd.DataFrame(records)
    out_path = DATA_DIR / "benchmark_focus_1_0_multicloud.csv"
    df.to_csv(out_path, index=False)
    print(f"  [+] Saved {len(df):,} FOCUS 1.0 rows to {out_path}")
    print(f"      - Providers: {dict(df['ProviderName'].value_counts())}")
    print(f"      - Anomalies: {int(df['x_AnomalyFlag'].sum())} ({df['x_AnomalyFlag'].mean()*100:.1f}%)")
    print(f"      - Anomaly Severities: {dict(df['x_AnomalySeverity'].value_counts())}")
    return df


# ============================================================================
# 2. GENERATOR: Authentic GCP Cloud Billing BigQuery Detailed Export
# ============================================================================
def generate_benchmark_gcp_dataset(dates):
    np.random.seed(RANDOM_SEED + 10)
    print("\n[2/4] Generating GCP Cloud Billing BigQuery Detailed Export Dataset...")

    billing_account_id = "01A2B3-4C5D6E-7F8G9H"

    projects = [
        {"id": "abhi-core-services-prod", "name": "Abhi Core Enterprise Services", "team": "core-eng", "costcenter": "engineering"},
        {"id": "abhi-ai-platform-prod", "name": "Abhi AI & ML Platform", "team": "ai-research", "costcenter": "ai-research"},
        {"id": "abhi-data-lake-prod", "name": "Abhi BigQuery Analytics & Data Lake", "team": "data-platform", "costcenter": "data-platform"},
        {"id": "abhi-customer-portal", "name": "Abhi SaaS Customer Portal", "team": "frontend-web", "costcenter": "customer-portal"}
    ]

    skus = [
        # Compute Engine (E2, N2, C2, T2D, A2)
        {"srv_id": "6F81-5844-456A", "srv_desc": "Compute Engine", "sku_id": "24C2-A23F-89D1", "sku_desc": "E2 Instance Core running in Americas", "unit": "seconds", "rate": 0.0000085, "base_qty": 345600, "region": "us-central1", "zone": "us-central1-a"},
        {"srv_id": "6F81-5844-456A", "srv_desc": "Compute Engine", "sku_id": "9B3D-F412-A8E2", "sku_desc": "E2 Instance Ram running in Americas", "unit": "byte-seconds", "rate": 0.0000000000012, "base_qty": 5529600000000, "region": "us-central1", "zone": "us-central1-b"},
        {"srv_id": "6F81-5844-456A", "srv_desc": "Compute Engine", "sku_id": "31A7-68C5-D29E", "sku_desc": "N2 Instance Core running in Americas", "unit": "seconds", "rate": 0.0000108, "base_qty": 691200, "region": "us-central1", "zone": "us-central1-a"},
        {"srv_id": "6F81-5844-456A", "srv_desc": "Compute Engine", "sku_id": "C74E-1289-5FE3", "sku_desc": "C2 Compute-Optimized Core in Americas", "unit": "seconds", "rate": 0.0000125, "base_qty": 518400, "region": "us-central1", "zone": "us-central1-c"},
        {"srv_id": "6F81-5844-456A", "srv_desc": "Compute Engine", "sku_id": "78E1-D492-B310", "sku_desc": "T2D AMD Milan Core running in Americas", "unit": "seconds", "rate": 0.0000095, "base_qty": 432000, "region": "us-central1", "zone": "us-central1-a"},
        {"srv_id": "6F81-5844-456A", "srv_desc": "Compute Engine", "sku_id": "A100-80GB-GPU1", "sku_desc": "A2 HighGPU NVIDIA A100 GPU running in Americas", "unit": "seconds", "rate": 0.000815, "base_qty": 86400, "region": "us-central1", "zone": "us-central1-a"},

        # Cloud Storage
        {"srv_id": "95FF-2EF5-5EA1", "srv_desc": "Cloud Storage", "sku_id": "038B-6E3C-4C90", "sku_desc": "Standard Storage US Regional", "unit": "byte-seconds", "rate": 0.0000000000076, "base_qty": 864000000000000, "region": "us-central1", "zone": ""},
        {"srv_id": "95FF-2EF5-5EA1", "srv_desc": "Cloud Storage", "sku_id": "4E19-72DF-8A01", "sku_desc": "Nearline Storage US Multi-region", "unit": "byte-seconds", "rate": 0.0000000000038, "base_qty": 432000000000000, "region": "us", "zone": ""},
        {"srv_id": "95FF-2EF5-5EA1", "srv_desc": "Cloud Storage", "sku_id": "83CD-5B20-1F9A", "sku_desc": "Coldline Storage US Multi-region", "unit": "byte-seconds", "rate": 0.0000000000018, "base_qty": 216000000000000, "region": "us", "zone": ""},

        # Cloud SQL
        {"srv_id": "18C2-6831-2856", "srv_desc": "Cloud SQL", "sku_id": "6C49-163B-95AE", "sku_desc": "Cloud SQL for PostgreSQL vCPU", "unit": "seconds", "rate": 0.0000115, "base_qty": 691200, "region": "us-central1", "zone": "us-central1-a"},
        {"srv_id": "18C2-6831-2856", "srv_desc": "Cloud SQL", "sku_id": "D24A-89F1-2B44", "sku_desc": "Cloud SQL for MySQL vCPU", "unit": "seconds", "rate": 0.0000105, "base_qty": 345600, "region": "us-central1", "zone": "us-central1-b"},
        {"srv_id": "18C2-6831-2856", "srv_desc": "Cloud SQL", "sku_id": "97EF-4C21-6D11", "sku_desc": "Cloud SQL High Availability Storage", "unit": "byte-seconds", "rate": 0.0000000000065, "base_qty": 172800000000000, "region": "us-central1", "zone": ""},

        # BigQuery
        {"srv_id": "24E5-DAE4-C759", "srv_desc": "BigQuery", "sku_id": "A40E-272E-6D70", "sku_desc": "Analysis Active Queries Slots (TiB processed)", "unit": "bytes", "rate": 0.0000000000062, "base_qty": 15000000000000, "region": "us", "zone": ""},
        {"srv_id": "24E5-DAE4-C759", "srv_desc": "BigQuery", "sku_id": "45C1-3D8B-9E10", "sku_desc": "BigQuery Active Storage", "unit": "byte-seconds", "rate": 0.0000000000078, "base_qty": 900000000000000, "region": "us", "zone": ""},

        # Cloud Run
        {"srv_id": "A625-3C41-8971", "srv_desc": "Cloud Run", "sku_id": "67C8-D91E-45A0", "sku_desc": "Cloud Run CPU Allocation Time", "unit": "seconds", "rate": 0.000024, "base_qty": 250000, "region": "us-central1", "zone": ""},
        {"srv_id": "A625-3C41-8971", "srv_desc": "Cloud Run", "sku_id": "891A-2E44-CF67", "sku_desc": "Cloud Run Requests", "unit": "requests", "rate": 0.0000004, "base_qty": 12000000, "region": "us-central1", "zone": ""},

        # GKE
        {"srv_id": "B12E-9C34-58F0", "srv_desc": "Google Kubernetes Engine", "sku_id": "E721-39F2-C081", "sku_desc": "GKE Enterprise Cluster Management Fee", "unit": "seconds", "rate": 0.00002778, "base_qty": 86400, "region": "us-central1", "zone": ""},
        {"srv_id": "B12E-9C34-58F0", "srv_desc": "Google Kubernetes Engine", "sku_id": "F510-4821-B892", "sku_desc": "GKE Autopilot Pod vCPU Allocation", "unit": "seconds", "rate": 0.0000122, "base_qty": 1728000, "region": "us-central1", "zone": ""},

        # Egress
        {"srv_id": "6F81-5844-456A", "srv_desc": "Compute Engine", "sku_id": "D604-D73B-3032", "sku_desc": "Network Internet Egress from Iowa to Worldwide", "unit": "bytes", "rate": 0.00000000012, "base_qty": 850000000000, "region": "us-central1", "zone": ""},
        {"srv_id": "6F81-5844-456A", "srv_desc": "Compute Engine", "sku_id": "2710-85A4-9F31", "sku_desc": "Inter-region Network Egress to Europe", "unit": "bytes", "rate": 0.00000000002, "base_qty": 500000000000, "region": "us-central1", "zone": ""}
    ]

    records = []

    for day_idx, current_date in enumerate(dates):
        usage_start = current_date.strftime("%Y-%m-%d 00:00:00 UTC")
        usage_end = (current_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00 UTC")
        trend = 1.0 + (0.00085 * day_idx)

        for proj in projects:
            for s in skus:
                # Department project affinity: e.g. A2 GPU only in AI platform
                if "A100" in s["sku_id"] and proj["id"] != "abhi-ai-platform-prod":
                    continue
                if "BigQuery" in s["srv_desc"] and proj["id"] not in ["abhi-data-lake-prod", "abhi-core-services-prod"]:
                    continue

                qty_jitter = np.random.uniform(0.92, 1.08)
                usage_amount = round(s["base_qty"] * trend * qty_jitter, 2)
                raw_cost = usage_amount * s["rate"]

                # Anomalous spikes
                if day_idx in [15, 16, 55, 56] and "A100" in s["sku_id"]:
                    raw_cost *= 3.5
                    usage_amount *= 3.5
                elif day_idx in [30, 72] and "Egress" in s["sku_desc"]:
                    raw_cost *= 4.2
                    usage_amount *= 4.2

                # Credits (Sustained use discounts / Committed use discounts)
                credit_amount = 0.0
                credit_type = ""
                if "N2" in s["sku_desc"] or "E2" in s["sku_desc"] or "PostgreSQL" in s["sku_desc"]:
                    if np.random.rand() > 0.35:
                        credit_amount = round(-1.0 * (raw_cost * np.random.uniform(0.18, 0.30)), 4)
                        credit_type = "COMMITTED_USE_DISCOUNT" if "N2" in s["sku_desc"] else "SUSTAINED_USE_DISCOUNT"

                records.append({
                    "billing_account_id": billing_account_id,
                    "service.id": s["srv_id"],
                    "service.description": s["srv_desc"],
                    "sku.id": s["sku_id"],
                    "sku.description": s["sku_desc"],
                    "usage_start_time": usage_start,
                    "usage_end_time": usage_end,
                    "project.id": proj["id"],
                    "project.name": proj["name"],
                    "project.labels.key": "costcenter",
                    "project.labels.value": proj["costcenter"],
                    "location.region": s["region"],
                    "location.zone": s["zone"],
                    "cost": round(raw_cost, 4),
                    "currency": "USD",
                    "usage.amount": usage_amount,
                    "usage.unit": s["unit"],
                    "credits.amount": credit_amount,
                    "credits.type": credit_type
                })

    df = pd.DataFrame(records)
    out_path = DATA_DIR / "benchmark_gcp_billing_export.csv"
    df.to_csv(out_path, index=False)
    print(f"  [+] Saved {len(df):,} GCP BigQuery Billing rows to {out_path}")
    print(f"      - Projects: {list(df['project.id'].unique())}")
    print(f"      - Services: {list(df['service.description'].unique())}")
    return df


# ============================================================================
# 3. GENERATOR: Authentic Azure Cost Management and Billing Export
# ============================================================================
def generate_benchmark_azure_dataset(dates):
    np.random.seed(RANDOM_SEED + 20)
    print("\n[3/4] Generating Azure Cost Management & Billing Export Dataset...")

    sub_guid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    sub_name = "Abhi Azure Enterprise Production EA"

    resource_groups = [
        {"rg": "rg-abhi-compute-prod", "dept": "Core Engineering", "cost_center": "CC-103"},
        {"rg": "rg-abhi-ai-engine", "dept": "AI/ML Research", "cost_center": "CC-101"},
        {"rg": "rg-abhi-data-platform", "dept": "Data Platform", "cost_center": "CC-102"},
        {"rg": "rg-abhi-portal-services", "dept": "Customer Portal", "cost_center": "CC-104"}
    ]

    meters = [
        # Virtual Machines (B-series, D-series, E-series, F-series)
        {"category": "Virtual Machines", "sub_cat": "Standard_B2ms", "meter_id": "meter-b2ms-eastus", "name": "B2ms VM Hours", "res_type": "Microsoft.Compute/virtualMachines", "unit": "1 Hour", "rate": 0.0832, "base_qty": 48.0, "location": "eastus"},
        {"category": "Virtual Machines", "sub_cat": "Standard_D8s_v5", "meter_id": "meter-d8sv5-eastus", "name": "D8s v5 VM Hours", "res_type": "Microsoft.Compute/virtualMachines", "unit": "1 Hour", "rate": 0.384, "base_qty": 72.0, "location": "eastus"},
        {"category": "Virtual Machines", "sub_cat": "Standard_E16s_v5", "meter_id": "meter-e16sv5-eastus", "name": "E16s v5 Memory VM Hours", "res_type": "Microsoft.Compute/virtualMachines", "unit": "1 Hour", "rate": 1.056, "base_qty": 48.0, "location": "eastus"},
        {"category": "Virtual Machines", "sub_cat": "Standard_F8s_v2", "meter_id": "meter-f8sv2-eastus", "name": "F8s v2 Compute VM Hours", "res_type": "Microsoft.Compute/virtualMachines", "unit": "1 Hour", "rate": 0.338, "base_qty": 48.0, "location": "eastus"},

        # Managed Disks
        {"category": "Storage", "sub_cat": "Premium SSD Managed Disks", "meter_id": "meter-p20-disk", "name": "P20 LRS Disk Provisioned", "res_type": "Microsoft.Compute/disks", "unit": "1/Month", "rate": 73.22 / 30.0, "base_qty": 6.0, "location": "eastus"},
        {"category": "Storage", "sub_cat": "Standard SSD Managed Disks", "meter_id": "meter-e20-disk", "name": "E20 LRS Disk Provisioned", "res_type": "Microsoft.Compute/disks", "unit": "1/Month", "rate": 38.00 / 30.0, "base_qty": 10.0, "location": "eastus"},

        # Azure Blob Storage
        {"category": "Storage", "sub_cat": "General Block Blob", "meter_id": "meter-blob-hot-lrs", "name": "Hot LRS Data Stored", "res_type": "Microsoft.Storage/storageAccounts", "unit": "1 GB/Month", "rate": 0.018 / 30.0, "base_qty": 85000.0, "location": "eastus"},
        {"category": "Storage", "sub_cat": "General Block Blob", "meter_id": "meter-blob-cool-lrs", "name": "Cool LRS Data Stored", "res_type": "Microsoft.Storage/storageAccounts", "unit": "1 GB/Month", "rate": 0.010 / 30.0, "base_qty": 120000.0, "location": "eastus"},

        # Azure SQL Database
        {"category": "Azure SQL Database", "sub_cat": "General Purpose - Compute", "meter_id": "meter-sql-gp-gen5-8", "name": "General Purpose Compute Gen5 8 vCore", "res_type": "Microsoft.Sql/servers/databases", "unit": "1 vCore Hour", "rate": 0.292, "base_qty": 192.0, "location": "eastus"},
        {"category": "Azure SQL Database", "sub_cat": "Business Critical - Compute", "meter_id": "meter-sql-bc-gen5-16", "name": "Business Critical Compute Gen5 16 vCore", "res_type": "Microsoft.Sql/servers/databases", "unit": "1 vCore Hour", "rate": 0.730, "base_qty": 384.0, "location": "eastus2"},

        # Cosmos DB
        {"category": "Azure Cosmos DB", "sub_cat": "Provisioned Throughput", "meter_id": "meter-cosmos-autoscale-ru", "name": "Autoscale RU/s (100 RU/s)", "res_type": "Microsoft.DocumentDB/databaseAccounts", "unit": "100 RU/s Hour", "rate": 0.012, "base_qty": 4800.0, "location": "eastus"},

        # Azure App Service
        {"category": "Azure App Service", "sub_cat": "Premium v3 Plan", "meter_id": "meter-appservice-p2v3", "name": "P2v3 Premium Dedicated App Instance", "res_type": "Microsoft.Web/serverfarms", "unit": "1 Hour", "rate": 0.286, "base_qty": 72.0, "location": "eastus"},

        # Bandwidth / Egress
        {"category": "Bandwidth", "sub_cat": "Bandwidth Out", "meter_id": "meter-egress-zone1", "name": "Standard Data Transfer Out Zone 1", "res_type": "Microsoft.Network/virtualNetworks", "unit": "1 GB", "rate": 0.087, "base_qty": 950.0, "location": "eastus"}
    ]

    records = []

    for day_idx, current_date in enumerate(dates):
        date_str = current_date.strftime("%Y-%m-%d")
        trend = 1.0 + (0.00088 * day_idx)

        for rg in resource_groups:
            for m in meters:
                # Group affinity
                if "E16s" in m["sub_cat"] and rg["dept"] != "AI/ML Research":
                    continue
                if "Business Critical" in m["sub_cat"] and rg["dept"] not in ["Core Engineering", "Data Platform"]:
                    continue

                jitter = np.random.uniform(0.93, 1.07)
                qty = round(m["base_qty"] * trend * jitter, 2)
                cost = qty * m["rate"]

                # Anomalies
                if day_idx in [21, 22, 68, 69] and "E16s" in m["sub_cat"]:
                    cost *= 3.4
                    qty *= 3.4
                elif day_idx in [37, 78] and "Bandwidth" in m["category"]:
                    cost *= 4.5
                    qty *= 4.5

                # Pricing model
                if day_idx % 7 == 0 and "Virtual Machines" in m["category"]:
                    pricing_model = "Reservation"
                    res_id = "res-sub-d8s-3yr-001"
                    cost *= 0.70  # Reserved VM instance discount
                else:
                    pricing_model = "OnDemand"
                    res_id = ""

                res_hash = uuid.uuid4().hex[:8]
                full_resource_id = f"/subscriptions/{sub_guid}/resourceGroups/{rg['rg']}/providers/{m['res_type']}/{m['sub_cat'].lower()}-{res_hash}"

                records.append({
                    "SubscriptionGuid": sub_guid,
                    "SubscriptionName": sub_name,
                    "ResourceGroup": rg["rg"],
                    "ResourceLocation": m["location"],
                    "ConsumedService": m["category"],
                    "ResourceType": m["res_type"],
                    "ResourceId": full_resource_id,
                    "MeterCategory": m["category"],
                    "MeterSubCategory": m["sub_cat"],
                    "MeterId": m["meter_id"],
                    "MeterName": m["name"],
                    "MeterRegion": m["location"],
                    "PreTaxCost": round(cost, 4),
                    "Currency": "USD",
                    "UsageQuantity": qty,
                    "UnitOfMeasure": m["unit"],
                    "CostCenter": rg["cost_center"],
                    "Date": date_str,
                    "PricingModel": pricing_model,
                    "ReservationId": res_id
                })

    df = pd.DataFrame(records)
    out_path = DATA_DIR / "benchmark_azure_cost_export.csv"
    df.to_csv(out_path, index=False)
    print(f"  [+] Saved {len(df):,} Azure Cost Management rows to {out_path}")
    print(f"      - Resource Groups: {list(df['ResourceGroup'].unique())}")
    print(f"      - Meter Categories: {list(df['MeterCategory'].unique())}")
    return df


# ============================================================================
# 4. GENERATOR: Authentic AWS Cost and Usage Report (CUR)
# ============================================================================
def generate_benchmark_aws_cur_dataset(dates):
    np.random.seed(RANDOM_SEED + 30)
    print("\n[4/4] Generating AWS Cost & Usage Report (CUR) Dataset...")

    payer_id = "942182019482"
    linked_accounts = [
        {"id": "942182019482", "name": "abhi-aws-core-prod", "dept": "Core Engineering"},
        {"id": "942182019483", "name": "abhi-aws-ai-ml-prod", "dept": "AI/ML Research"},
        {"id": "942182019484", "name": "abhi-aws-data-lake-prod", "dept": "Data Platform"},
        {"id": "942182019485", "name": "abhi-aws-customer-portal", "dept": "Customer Portal"}
    ]

    items = [
        # EC2 (t4g, m6i, c6i, r6i, g5)
        {"code": "AmazonEC2", "srv": "Amazon Elastic Compute Cloud", "type": "BoxUsage:t4g.xlarge", "inst": "t4g.xlarge", "op": "RunInstances", "rate": 0.1344, "base_qty": 72.0, "az": "us-east-1a", "region": "us-east-1"},
        {"code": "AmazonEC2", "srv": "Amazon Elastic Compute Cloud", "type": "BoxUsage:m6i.2xlarge", "inst": "m6i.2xlarge", "op": "RunInstances", "rate": 0.384, "base_qty": 96.0, "az": "us-east-1b", "region": "us-east-1"},
        {"code": "AmazonEC2", "srv": "Amazon Elastic Compute Cloud", "type": "BoxUsage:c6i.4xlarge", "inst": "c6i.4xlarge", "op": "RunInstances", "rate": 0.680, "base_qty": 48.0, "az": "us-east-1a", "region": "us-east-1"},
        {"code": "AmazonEC2", "srv": "Amazon Elastic Compute Cloud", "type": "BoxUsage:r6i.4xlarge", "inst": "r6i.4xlarge", "op": "RunInstances", "rate": 1.008, "base_qty": 48.0, "az": "us-east-1c", "region": "us-east-1"},
        {"code": "AmazonEC2", "srv": "Amazon Elastic Compute Cloud", "type": "BoxUsage:g5.2xlarge", "inst": "g5.2xlarge", "op": "RunInstances", "rate": 1.212, "base_qty": 48.0, "az": "us-east-1a", "region": "us-east-1"},

        # EBS
        {"code": "AmazonEC2", "srv": "Amazon Elastic Compute Cloud", "type": "EBS:VolumeUsage.gp3", "inst": "", "op": "CreateVolume-gp3", "rate": 0.08 / 30.0, "base_qty": 18000.0, "az": "us-east-1a", "region": "us-east-1"},
        {"code": "AmazonEC2", "srv": "Amazon Elastic Compute Cloud", "type": "EBS:VolumeUsage.io2", "inst": "", "op": "CreateVolume-io2", "rate": 0.125 / 30.0, "base_qty": 6500.0, "az": "us-east-1b", "region": "us-east-1"},

        # S3
        {"code": "AmazonS3", "srv": "Amazon Simple Storage Service", "type": "TimedStorage-ByteHrs", "inst": "", "op": "StandardStorage", "rate": 0.023 / 720.0, "base_qty": 2800000.0, "az": "", "region": "us-east-1"},
        {"code": "AmazonS3", "srv": "Amazon Simple Storage Service", "type": "GlacierByteHrs", "inst": "", "op": "GlacierStorage", "rate": 0.004 / 720.0, "base_qty": 4500000.0, "az": "", "region": "us-east-1"},

        # RDS
        {"code": "AmazonRDS", "srv": "Amazon Relational Database Service", "type": "InstanceUsage:db.m6i.xlarge", "inst": "db.m6i.xlarge", "op": "CreateDBInstance", "rate": 0.350, "base_qty": 48.0, "az": "us-east-1a", "region": "us-east-1"},
        {"code": "AmazonRDS", "srv": "Amazon Relational Database Service", "type": "InstanceUsage:db.r6i.2xlarge", "inst": "db.r6i.2xlarge", "op": "CreateDBInstance:0002", "rate": 0.700, "base_qty": 48.0, "az": "us-east-1b", "region": "us-east-1"},

        # DynamoDB
        {"code": "AmazonDynamoDB", "srv": "Amazon DynamoDB", "type": "PayPerRequestThroughput", "inst": "", "op": "PayPerRequest", "rate": 0.00000125, "base_qty": 8500000.0, "az": "", "region": "us-east-1"},

        # Lambda
        {"code": "AWSLambda", "srv": "AWS Lambda", "type": "AWS-Lambda-Duration-GB-Second", "inst": "", "op": "Invoke", "rate": 0.0000166667, "base_qty": 2800000.0, "az": "", "region": "us-east-1"},

        # NAT Gateway
        {"code": "AmazonEC2", "srv": "Amazon Elastic Compute Cloud", "type": "NatGateway-Hours", "inst": "", "op": "NatGateway", "rate": 0.045, "base_qty": 72.0, "az": "us-east-1a", "region": "us-east-1"},

        # CloudFront
        {"code": "AmazonCloudFront", "srv": "Amazon CloudFront", "type": "DataTransfer-Out-Bytes", "inst": "", "op": "Global-Out", "rate": 0.085 / 1073741824.0, "base_qty": 850000000000.0, "az": "", "region": "us-east-1"},

        # Data Transfer
        {"code": "AWSDataTransfer", "srv": "AWS Data Transfer", "type": "AWS-Out-Bytes", "inst": "", "op": "DataTransfer-Out", "rate": 0.09 / 1073741824.0, "base_qty": 650000000000.0, "az": "", "region": "us-east-1"}
    ]

    records = []

    for day_idx, current_date in enumerate(dates):
        start_str = current_date.strftime("%Y-%m-%dT00:00:00Z")
        end_str = (current_date + datetime.timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
        interval = f"{start_str}/{end_str}"
        period_start = current_date.replace(day=1).strftime("%Y-%m-%dT00:00:00Z")
        trend = 1.0 + (0.0009 * day_idx)

        for acct in linked_accounts:
            for item in items:
                # Account affinity: g5 GPU only in AI/ML
                if "g5.2xlarge" in item["inst"] and acct["dept"] != "AI/ML Research":
                    continue
                if "r6i" in item["inst"] and acct["dept"] not in ["Core Engineering", "Data Platform"]:
                    continue

                jitter = np.random.uniform(0.92, 1.08)
                usage_amt = round(item["base_qty"] * trend * jitter, 4)
                unblended_cost = usage_amt * item["rate"]

                # Anomalies
                if day_idx in [26, 27, 70, 71] and "g5.2xlarge" in item["inst"]:
                    unblended_cost *= 3.6
                    usage_amt *= 3.6
                elif day_idx in [44, 82] and ("CloudFront" in item["code"] or "DataTransfer" in item["code"]):
                    unblended_cost *= 4.8
                    usage_amt *= 4.8

                blended_cost = unblended_cost * np.random.uniform(0.95, 0.99)
                pricing_term = "Reserved" if (day_idx % 5 == 0 and item["inst"]) else "OnDemand"

                line_item_id = f"aws-cur-{day_idx:03d}-{uuid.uuid4().hex[:12]}"

                records.append({
                    "identity/LineItemId": line_item_id,
                    "identity/TimeInterval": interval,
                    "bill/BillingPeriodStartDate": period_start,
                    "bill/PayerAccountId": payer_id,
                    "lineItem/UsageAccountId": acct["id"],
                    "lineItem/ProductCode": item["code"],
                    "lineItem/UsageType": item["type"],
                    "lineItem/Operation": item["op"],
                    "lineItem/AvailabilityZone": item["az"],
                    "lineItem/UsageStartDate": start_str,
                    "lineItem/UsageEndDate": end_str,
                    "lineItem/UsageAmount": usage_amt,
                    "lineItem/UnblendedCost": round(unblended_cost, 4),
                    "lineItem/BlendedCost": round(blended_cost, 4),
                    "lineItem/CurrencyCode": "USD",
                    "pricing/term": pricing_term,
                    "product/servicename": item["srv"],
                    "product/instanceType": item["inst"],
                    "product/region": item["region"]
                })

    df = pd.DataFrame(records)
    out_path = DATA_DIR / "benchmark_aws_cur_export.csv"
    df.to_csv(out_path, index=False)
    print(f"  [+] Saved {len(df):,} AWS CUR rows to {out_path}")
    print(f"      - Product Codes: {list(df['lineItem/ProductCode'].unique())}")
    print(f"      - Linked Accounts: {list(df['lineItem/UsageAccountId'].unique())}")
    return df


# ============================================================================
# MAIN ORCHESTRATION & VALIDATION
# ============================================================================
def main():
    print("=" * 80)
    print("  ABHI CLOUD TECH - FINOPS INTELLIGENCE BENCHMARK DATASET GENERATION")
    print(f"  Start Date: {START_DATE_STR} | Horizon: {DAYS_COUNT} Days | Output Dir: {DATA_DIR}")
    print("=" * 80)

    dates = get_date_range()

    df_focus = generate_benchmark_focus_dataset(dates)
    df_gcp = generate_benchmark_gcp_dataset(dates)
    df_azure = generate_benchmark_azure_dataset(dates)
    df_aws = generate_benchmark_aws_cur_dataset(dates)

    print("\n" + "=" * 80)
    print("  BENCHMARK DATASETS GENERATION COMPLETE - FINAL SUMMARY")
    print("=" * 80)
    summary_data = [
        {"Dataset": "benchmark_focus_1_0_multicloud.csv", "Rows": len(df_focus), "Columns": len(df_focus.columns), "Total Spend (USD)": f"${df_focus['BilledCost'].sum():,.2f}", "Format": "FOCUS 1.0 (AWS/Azure/GCP)"},
        {"Dataset": "benchmark_gcp_billing_export.csv", "Rows": len(df_gcp), "Columns": len(df_gcp.columns), "Total Spend (USD)": f"${df_gcp['cost'].sum():,.2f}", "Format": "GCP BigQuery Detailed Export"},
        {"Dataset": "benchmark_azure_cost_export.csv", "Rows": len(df_azure), "Columns": len(df_azure.columns), "Total Spend (USD)": f"${df_azure['PreTaxCost'].sum():,.2f}", "Format": "Azure Cost Management Export"},
        {"Dataset": "benchmark_aws_cur_export.csv", "Rows": len(df_aws), "Columns": len(df_aws.columns), "Total Spend (USD)": f"${df_aws['lineItem/UnblendedCost'].sum():,.2f}", "Format": "AWS CUR 2.0 Export"}
    ]
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    print("=" * 80)


if __name__ == "__main__":
    main()
