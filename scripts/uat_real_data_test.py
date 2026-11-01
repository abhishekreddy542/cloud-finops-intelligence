#!/usr/bin/env python3
"""
=========================================================================
Abhi Cloud Tech — Enterprise FinOps Intelligence Platform
=========================================================================
Script:     UAT Real-World Data Validation Pipeline
Purpose:    User Acceptance Testing with realistic vendor-format billing
            data from AWS CUR, Azure Cost Management, and GCP BigQuery
            billing exports.
Author:     Abhishek — Lead Architect, Abhi Cloud Tech
=========================================================================

This script:
  1. Generates realistic billing CSVs matching exact vendor schemas
  2. Maps each vendor format → FOCUS 1.0 standard columns
  3. Loads pre-trained ML models (anomaly detector + forecaster)
  4. Runs inference on external data
  5. Validates results and reports any issues
  6. Attempts to download Microsoft FinOps Toolkit dataset if available
=========================================================================
"""

import os
import sys
import io
import json
import random
import hashlib
import traceback
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Force UTF-8 stdout on Windows to avoid charmap encoding errors
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

UAT_DIR = PROJECT_ROOT / "data" / "uat"
UAT_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR = PROJECT_ROOT / "models"

# =========================================================================
# SECTION 1: REALISTIC VENDOR-FORMAT BILLING DATA GENERATORS
# =========================================================================

def generate_aws_cur_csv(output_path: str, num_rows: int = 5000) -> str:
    """
    Generate a CSV that mirrors the AWS Cost & Usage Report (CUR) format.
    
    Real CUR columns include:
      identity/LineItemId, identity/TimeInterval,
      bill/InvoiceId, bill/BillingEntity, bill/BillingPeriodStartDate,
      lineItem/UsageAccountId, lineItem/LineItemType,
      lineItem/UsageStartDate, lineItem/UsageEndDate,
      lineItem/ProductCode, lineItem/UsageType, lineItem/Operation,
      lineItem/UsageAmount, lineItem/NormalizedUsageAmount,
      lineItem/CurrencyCode, lineItem/UnblendedRate, lineItem/UnblendedCost,
      lineItem/BlendedRate, lineItem/BlendedCost,
      product/instanceType, product/region, product/operatingSystem,
      resourceTags/user:Environment, resourceTags/user:CostCenter
    """
    random.seed(42)
    np.random.seed(42)
    
    services = [
        ("AmazonEC2", "RunInstances", "m5.xlarge", "Compute"),
        ("AmazonEC2", "RunInstances", "c5.2xlarge", "Compute"),
        ("AmazonEC2", "RunInstances", "r5.4xlarge", "Compute"),
        ("AmazonEC2", "RunInstances", "t3.medium", "Compute"),
        ("AmazonS3", "PutObject", None, "Storage"),
        ("AmazonS3", "GetObject", None, "Storage"),
        ("AmazonRDS", "CreateDBInstance", "db.r5.large", "Database"),
        ("AmazonRDS", "CreateDBInstance", "db.m5.xlarge", "Database"),
        ("AWSLambda", "Invoke", None, "Compute"),
        ("AmazonEKS", "RunPod", "m5.2xlarge", "Containers"),
        ("AmazonCloudFront", "EdgeTransfer", None, "Network"),
        ("AmazonDynamoDB", "ReadCapacity", None, "Database"),
        ("ElasticLoadBalancing", "LoadBalancerUsage", None, "Network"),
        ("AWSDataTransfer", "DataTransfer-Out-Bytes", None, "Network"),
        ("AmazonEBS", "VolumeUsage.gp3", None, "Storage"),
        ("AmazonECR", "ContainerStorage", None, "Containers"),
        ("AmazonSageMaker", "TrainingJob", "ml.p3.2xlarge", "AI/ML"),
    ]
    
    regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1", "eu-central-1"]
    accounts = ["123456789012", "234567890123", "345678901234"]
    cost_centers = ["Engineering", "Data-Science", "Finance", "AI/ML Research", "DevOps", "Marketing"]
    environments = ["Production", "Staging", "Development", "Research-Lab"]
    
    start_date = datetime(2025, 1, 1)
    rows = []
    
    for i in range(num_rows):
        day_offset = random.randint(0, 364)
        usage_date = start_date + timedelta(days=day_offset)
        svc = random.choice(services)
        product_code, operation, instance_type, category = svc
        region = random.choice(regions)
        account = random.choice(accounts)
        cost_center = random.choice(cost_centers)
        env = random.choice(environments)
        
        # Realistic cost distribution
        base_cost = {
            "AmazonEC2": random.uniform(50, 800),
            "AmazonS3": random.uniform(5, 150),
            "AmazonRDS": random.uniform(30, 500),
            "AWSLambda": random.uniform(0.5, 50),
            "AmazonEKS": random.uniform(80, 600),
            "AmazonCloudFront": random.uniform(10, 200),
            "AmazonDynamoDB": random.uniform(5, 100),
            "ElasticLoadBalancing": random.uniform(15, 80),
            "AWSDataTransfer": random.uniform(20, 300),
            "AmazonEBS": random.uniform(10, 120),
            "AmazonECR": random.uniform(2, 30),
            "AmazonSageMaker": random.uniform(100, 1500),
        }.get(product_code, random.uniform(10, 200))
        
        # Inject anomalies (~3% of rows)
        if random.random() < 0.03:
            base_cost *= random.uniform(3.0, 8.0)
        
        usage_hours = random.uniform(1, 744)
        unblended_rate = round(base_cost / max(usage_hours, 1), 6)
        
        row = {
            "identity/LineItemId": hashlib.md5(f"{i}-{day_offset}".encode()).hexdigest()[:24],
            "identity/TimeInterval": f"{usage_date.strftime('%Y-%m-%dT00:00:00Z')}/{(usage_date + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z')}",
            "bill/InvoiceId": f"INV-{usage_date.strftime('%Y%m')}",
            "bill/BillingEntity": "AWS",
            "bill/BillingPeriodStartDate": usage_date.replace(day=1).strftime("%Y-%m-%dT00:00:00Z"),
            "bill/BillingPeriodEndDate": (usage_date.replace(day=28) + timedelta(days=4)).replace(day=1).strftime("%Y-%m-%dT00:00:00Z"),
            "bill/PayerAccountId": "111111111111",
            "lineItem/UsageAccountId": account,
            "lineItem/LineItemType": "Usage",
            "lineItem/UsageStartDate": usage_date.strftime("%Y-%m-%dT00:00:00Z"),
            "lineItem/UsageEndDate": (usage_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z"),
            "lineItem/ProductCode": product_code,
            "lineItem/UsageType": f"{region}-BoxUsage:{instance_type}" if instance_type else f"{region}-{operation}",
            "lineItem/Operation": operation,
            "lineItem/UsageAmount": round(usage_hours, 4),
            "lineItem/NormalizedUsageAmount": round(usage_hours * random.uniform(0.8, 1.2), 4),
            "lineItem/CurrencyCode": "USD",
            "lineItem/UnblendedRate": round(unblended_rate, 8),
            "lineItem/UnblendedCost": round(base_cost, 6),
            "lineItem/BlendedRate": round(unblended_rate * 0.95, 8),
            "lineItem/BlendedCost": round(base_cost * 0.95, 6),
            "product/instanceType": instance_type if instance_type else "",
            "product/region": region,
            "product/operatingSystem": random.choice(["Linux", "Windows", "RHEL", ""]),
            "product/servicename": product_code,
            "resourceTags/user:Environment": env,
            "resourceTags/user:CostCenter": cost_center,
            "resourceTags/user:Team": random.choice(["Platform", "Data", "Backend", "ML", "Infra"]),
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"  [+] AWS CUR CSV generated: {num_rows} rows → {output_path}")
    return output_path


def generate_azure_cost_mgmt_csv(output_path: str, num_rows: int = 5000) -> str:
    """
    Generate a CSV that mirrors Azure Cost Management export format.
    
    Real Azure export columns:
      InvoiceSectionName, AccountName, AccountOwnerId,
      SubscriptionId, SubscriptionName, ResourceGroup,
      ResourceLocation, Date, ProductName, MeterCategory,
      MeterSubCategory, MeterId, MeterName, MeterRegion,
      UnitOfMeasure, Quantity, EffectivePrice, CostInBillingCurrency,
      IsAzureCreditEligible, PayGPrice, Frequency,
      ResourceType, ChargeType, PublisherType,
      Tags (JSON)
    """
    random.seed(43)
    np.random.seed(43)
    
    services = [
        ("Microsoft.Compute", "Virtual Machines", "Standard_D4s_v3", "Compute"),
        ("Microsoft.Compute", "Virtual Machines", "Standard_E8s_v3", "Compute"),
        ("Microsoft.Compute", "Virtual Machines", "Standard_B2ms", "Compute"),
        ("Microsoft.Storage", "Storage", "Standard_LRS", "Storage"),
        ("Microsoft.Storage", "Blob Storage", "Hot_LRS", "Storage"),
        ("Microsoft.Sql", "SQL Database", "Standard_S1", "Database"),
        ("Microsoft.Sql", "SQL Database", "Premium_P1", "Database"),
        ("Microsoft.ContainerService", "Azure Kubernetes Service", "Standard_D8s_v3", "Containers"),
        ("Microsoft.Network", "Virtual Network", None, "Network"),
        ("Microsoft.Network", "Load Balancer", "Standard", "Network"),
        ("Microsoft.Network", "Bandwidth", None, "Network"),
        ("Microsoft.CognitiveServices", "Azure OpenAI Service", None, "AI/ML"),
        ("Microsoft.Web", "App Service", "P1v3", "Compute"),
        ("Microsoft.DBforPostgreSQL", "Azure Database for PostgreSQL", "GP_Gen5_4", "Database"),
        ("Microsoft.Cache", "Azure Cache for Redis", "C1", "Database"),
    ]
    
    regions = ["eastus", "westus2", "northeurope", "southeastasia", "westeurope"]
    subscriptions = [
        ("sub-prod-001", "Production Workloads"),
        ("sub-dev-002", "Development & Testing"),
        ("sub-data-003", "Data Analytics Platform"),
    ]
    resource_groups = ["rg-web-prod", "rg-data-prod", "rg-ml-research", "rg-devops", "rg-shared-services", "rg-finance-analytics"]
    cost_centers = ["Engineering", "Data-Science", "Finance", "AI/ML Research", "DevOps", "Marketing"]
    
    start_date = datetime(2025, 1, 1)
    rows = []
    
    for i in range(num_rows):
        day_offset = random.randint(0, 364)
        usage_date = start_date + timedelta(days=day_offset)
        svc = random.choice(services)
        resource_type, meter_category, meter_sub, svc_category = svc
        region = random.choice(regions)
        sub_id, sub_name = random.choice(subscriptions)
        rg = random.choice(resource_groups)
        cost_center = random.choice(cost_centers)
        
        base_cost = {
            "Microsoft.Compute": random.uniform(40, 700),
            "Microsoft.Storage": random.uniform(5, 120),
            "Microsoft.Sql": random.uniform(30, 450),
            "Microsoft.ContainerService": random.uniform(60, 500),
            "Microsoft.Network": random.uniform(10, 200),
            "Microsoft.CognitiveServices": random.uniform(20, 800),
            "Microsoft.Web": random.uniform(20, 300),
            "Microsoft.DBforPostgreSQL": random.uniform(25, 350),
            "Microsoft.Cache": random.uniform(15, 150),
        }.get(resource_type, random.uniform(10, 200))
        
        # Inject anomalies
        if random.random() < 0.03:
            base_cost *= random.uniform(3.0, 8.0)
        
        quantity = random.uniform(1, 744)
        effective_price = round(base_cost / max(quantity, 1), 6)
        
        tags_dict = {
            "CostCenter": cost_center,
            "Environment": random.choice(["Production", "Staging", "Dev", "Research"]),
            "Owner": f"team-{random.choice(['platform', 'data', 'backend', 'ml'])}@abhicloudtech.com"
        }
        
        row = {
            "InvoiceSectionName": "Abhi Cloud Tech Enterprise",
            "AccountName": "abhi-azure-enterprise",
            "AccountOwnerId": "admin@abhicloudtech.com",
            "SubscriptionId": sub_id,
            "SubscriptionName": sub_name,
            "ResourceGroup": rg,
            "ResourceLocation": region,
            "Date": usage_date.strftime("%m/%d/%Y"),
            "ProductName": meter_category,
            "MeterCategory": meter_category,
            "MeterSubCategory": meter_sub if meter_sub else "",
            "MeterId": hashlib.md5(f"azure-{i}-{day_offset}".encode()).hexdigest(),
            "MeterName": f"{meter_sub or meter_category} - {region}",
            "MeterRegion": region,
            "UnitOfMeasure": random.choice(["1 Hour", "1 GB", "10,000 Transactions", "1 GB/Month"]),
            "Quantity": round(quantity, 4),
            "EffectivePrice": round(effective_price, 8),
            "CostInBillingCurrency": round(base_cost, 6),
            "IsAzureCreditEligible": random.choice(["True", "False"]),
            "PayGPrice": round(effective_price * 1.1, 8),
            "Frequency": "UsageBased",
            "ResourceType": resource_type,
            "ChargeType": "Usage",
            "PublisherType": "Azure",
            "Tags": json.dumps(tags_dict),
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"  [+] Azure Cost Management CSV generated: {num_rows} rows → {output_path}")
    return output_path


def generate_gcp_billing_csv(output_path: str, num_rows: int = 5000) -> str:
    """
    Generate a CSV that mirrors GCP BigQuery Billing Export format.
    
    Real GCP export columns:
      billing_account_id, project.id, project.name, project.number,
      service.id, service.description, sku.id, sku.description,
      usage_start_time, usage_end_time,
      location.location, location.country, location.region, location.zone,
      cost, currency, currency_conversion_rate,
      usage.amount, usage.unit, usage.amount_in_pricing_units,
      credits.amount, credits.name, credits.type,
      labels.key, labels.value,
      cost_type
    """
    random.seed(44)
    np.random.seed(44)
    
    services = [
        ("6F81-5844-456A", "Compute Engine", "D212-55B9-3E37", "N2 Instance Core running in Americas"),
        ("6F81-5844-456A", "Compute Engine", "A32B-CF88-1234", "E2 Instance Ram running in Americas"),
        ("95FF-2EF5-5EA1", "Cloud Storage", "B7B1-A3CC-5678", "Standard Storage US Multi-Region"),
        ("95FF-2EF5-5EA1", "Cloud Storage", "C3D4-E5F6-7890", "Nearline Storage US"),
        ("A1E8-BE35-7924", "BigQuery", "F678-9012-3456", "Analysis Slots"),
        ("A1E8-BE35-7924", "BigQuery", "G789-0123-4567", "Active Storage"),
        ("2062-016F-44A2", "Cloud SQL", "H890-1234-5678", "HA - PostgreSQL - vCPU"),
        ("2062-016F-44A2", "Cloud SQL", "I901-2345-6789", "HA - MySQL - RAM"),
        ("6F81-5844-456A", "Compute Engine", "J012-3456-7890", "GKE Autopilot Pod"),
        ("152E-C115-5142", "Cloud Run", "K123-4567-8901", "CPU Allocation Time"),
        ("CC63-D537-1FD5", "Cloud Networking", "L234-5678-9012", "External Egress to Americas"),
        ("CC63-D537-1FD5", "Cloud Networking", "M345-6789-0123", "Cloud Load Balancing - Forwarding Rule"),
        ("1111-2222-3333", "Vertex AI", "N456-7890-1234", "Training - GPU hours"),
        ("4444-5555-6666", "Cloud Functions", "O567-8901-2345", "CPU Time - Gen2"),
    ]
    
    regions = ["us-central1", "us-east1", "europe-west1", "asia-southeast1", "us-west1"]
    projects = [
        ("prj-prod-analytics", "Production Analytics", "123456789"),
        ("prj-ml-research", "ML Research Lab", "234567890"),
        ("prj-web-platform", "Web Platform", "345678901"),
    ]
    cost_centers = ["Engineering", "Data-Science", "Finance", "AI/ML Research", "DevOps", "Marketing"]
    
    start_date = datetime(2025, 1, 1)
    rows = []
    
    for i in range(num_rows):
        day_offset = random.randint(0, 364)
        usage_date = start_date + timedelta(days=day_offset)
        svc = random.choice(services)
        svc_id, svc_desc, sku_id, sku_desc = svc
        region = random.choice(regions)
        proj_id, proj_name, proj_num = random.choice(projects)
        cost_center = random.choice(cost_centers)
        
        base_cost = {
            "Compute Engine": random.uniform(30, 700),
            "Cloud Storage": random.uniform(3, 100),
            "BigQuery": random.uniform(10, 400),
            "Cloud SQL": random.uniform(25, 450),
            "Cloud Run": random.uniform(5, 80),
            "Cloud Networking": random.uniform(10, 250),
            "Vertex AI": random.uniform(50, 1200),
            "Cloud Functions": random.uniform(1, 30),
        }.get(svc_desc, random.uniform(10, 200))
        
        # Inject anomalies
        if random.random() < 0.03:
            base_cost *= random.uniform(3.0, 8.0)
        
        usage_amount = random.uniform(0.5, 5000)
        
        credits_amount = 0.0
        credits_name = ""
        credits_type = ""
        if random.random() < 0.1:
            credits_amount = -round(base_cost * random.uniform(0.05, 0.30), 4)
            credits_name = random.choice(["Sustained Use Discount", "Committed Use Discount", "Free Tier Credits"])
            credits_type = random.choice(["SUSTAINED_USAGE_DISCOUNT", "COMMITTED_USAGE_DISCOUNT", "PROMOTION"])
        
        row = {
            "billing_account_id": "01ABCD-234EFG-567HIJ",
            "project.id": proj_id,
            "project.name": proj_name,
            "project.number": proj_num,
            "service.id": svc_id,
            "service.description": svc_desc,
            "sku.id": sku_id,
            "sku.description": sku_desc,
            "usage_start_time": usage_date.strftime("%Y-%m-%dT00:00:00Z"),
            "usage_end_time": (usage_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z"),
            "location.location": region,
            "location.country": {"us-central1": "US", "us-east1": "US", "us-west1": "US", "europe-west1": "DE", "asia-southeast1": "SG"}.get(region, "US"),
            "location.region": region,
            "location.zone": f"{region}-a" if random.random() > 0.5 else "",
            "cost": round(base_cost, 6),
            "currency": "USD",
            "currency_conversion_rate": 1.0,
            "usage.amount": round(usage_amount, 6),
            "usage.unit": random.choice(["seconds", "byte-seconds", "requests", "gibibyte month"]),
            "usage.amount_in_pricing_units": round(usage_amount * random.uniform(0.001, 1.0), 6),
            "credits.amount": credits_amount,
            "credits.name": credits_name,
            "credits.type": credits_type,
            "labels.key": "cost_center",
            "labels.value": cost_center,
            "cost_type": "regular",
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"  [+] GCP BigQuery Billing CSV generated: {num_rows} rows → {output_path}")
    return output_path


# =========================================================================
# SECTION 2: VENDOR FORMAT → FOCUS 1.0 COLUMN MAPPERS
# =========================================================================

def map_aws_cur_to_focus(csv_path: str) -> pd.DataFrame:
    """
    Maps AWS CUR CSV → FOCUS 1.0 columns expected by our ML models.
    
    FOCUS Target Schema:
      Date, CloudProvider, Department, Service, DailyCost_USD,
      vCPU_Hours, Avg_CPU_Utilization_Pct, Data_Egress_GB, Storage_TB
    """
    print(f"\n  [AWS CUR → FOCUS 1.0] Mapping {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"    Raw shape: {df.shape}, Columns: {list(df.columns[:10])}...")
    
    # Parse date from the time interval field
    df["Date"] = pd.to_datetime(
        df["lineItem/UsageStartDate"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    
    df["CloudProvider"] = "AWS"
    df["Department"] = df["resourceTags/user:CostCenter"].fillna("Unknown")
    
    # Service: use productCode + instanceType for specificity
    df["Service"] = df.apply(
        lambda r: f"{r['lineItem/ProductCode']} ({r['product/instanceType']})" 
        if pd.notna(r.get("product/instanceType")) and r["product/instanceType"] != "" 
        else str(r["lineItem/ProductCode"]),
        axis=1
    )
    
    df["DailyCost_USD"] = pd.to_numeric(df["lineItem/UnblendedCost"], errors="coerce").fillna(0.0)
    df["vCPU_Hours"] = pd.to_numeric(df["lineItem/UsageAmount"], errors="coerce").fillna(0.0)
    
    # Synthesize utilization (not in CUR — real monitoring comes from CloudWatch)
    np.random.seed(100)
    df["Avg_CPU_Utilization_Pct"] = np.where(
        df["lineItem/ProductCode"].isin(["AmazonEC2", "AmazonEKS", "AmazonSageMaker"]),
        np.random.uniform(15, 85, len(df)),
        np.random.uniform(0, 20, len(df))
    )
    
    # Estimate egress from network services
    df["Data_Egress_GB"] = np.where(
        df["lineItem/ProductCode"].isin(["AWSDataTransfer", "AmazonCloudFront"]),
        df["vCPU_Hours"] * np.random.uniform(0.5, 2.0, len(df)),
        np.random.uniform(0, 50, len(df))
    )
    
    # Estimate storage from storage services
    df["Storage_TB"] = np.where(
        df["lineItem/ProductCode"].isin(["AmazonS3", "AmazonEBS"]),
        np.random.uniform(5, 100, len(df)),
        np.random.uniform(0, 10, len(df))
    )
    
    focus_cols = ["Date", "CloudProvider", "Department", "Service", "DailyCost_USD",
                  "vCPU_Hours", "Avg_CPU_Utilization_Pct", "Data_Egress_GB", "Storage_TB"]
    result = df[focus_cols].copy()
    
    print(f"    Mapped shape: {result.shape}")
    print(f"    Cost range: ${result['DailyCost_USD'].min():.2f} — ${result['DailyCost_USD'].max():.2f}")
    print(f"    Date range: {result['Date'].min()} → {result['Date'].max()}")
    print(f"    Unique services: {result['Service'].nunique()}")
    return result


def map_azure_cost_to_focus(csv_path: str) -> pd.DataFrame:
    """
    Maps Azure Cost Management export CSV → FOCUS 1.0 columns.
    """
    print(f"\n  [Azure Cost Mgmt → FOCUS 1.0] Mapping {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"    Raw shape: {df.shape}, Columns: {list(df.columns[:10])}...")
    
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["CloudProvider"] = "Azure"
    
    # Extract CostCenter from JSON tags
    def extract_cost_center(tags_str):
        try:
            tags = json.loads(tags_str) if isinstance(tags_str, str) else {}
            return tags.get("CostCenter", "Unknown")
        except (json.JSONDecodeError, TypeError):
            return "Unknown"
    
    df["Department"] = df["Tags"].apply(extract_cost_center)
    
    df["Service"] = df.apply(
        lambda r: f"{r['MeterCategory']} ({r['MeterSubCategory']})"
        if pd.notna(r.get("MeterSubCategory")) and r["MeterSubCategory"] != ""
        else str(r["MeterCategory"]),
        axis=1
    )
    
    df["DailyCost_USD"] = pd.to_numeric(df["CostInBillingCurrency"], errors="coerce").fillna(0.0)
    df["vCPU_Hours"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0.0)
    
    # Synthesize utilization and telemetry
    np.random.seed(101)
    is_compute = df["ResourceType"].str.contains("Compute|ContainerService", case=False, na=False)
    df["Avg_CPU_Utilization_Pct"] = np.where(is_compute, np.random.uniform(15, 85, len(df)), np.random.uniform(0, 20, len(df)))
    
    is_network = df["ResourceType"].str.contains("Network", case=False, na=False)
    df["Data_Egress_GB"] = np.where(is_network, df["vCPU_Hours"] * np.random.uniform(0.5, 2.0, len(df)), np.random.uniform(0, 50, len(df)))
    
    is_storage = df["ResourceType"].str.contains("Storage", case=False, na=False)
    df["Storage_TB"] = np.where(is_storage, np.random.uniform(5, 100, len(df)), np.random.uniform(0, 10, len(df)))
    
    focus_cols = ["Date", "CloudProvider", "Department", "Service", "DailyCost_USD",
                  "vCPU_Hours", "Avg_CPU_Utilization_Pct", "Data_Egress_GB", "Storage_TB"]
    result = df[focus_cols].copy()
    
    print(f"    Mapped shape: {result.shape}")
    print(f"    Cost range: ${result['DailyCost_USD'].min():.2f} — ${result['DailyCost_USD'].max():.2f}")
    print(f"    Date range: {result['Date'].min()} → {result['Date'].max()}")
    print(f"    Unique services: {result['Service'].nunique()}")
    return result


def map_gcp_billing_to_focus(csv_path: str) -> pd.DataFrame:
    """
    Maps GCP BigQuery Billing export CSV → FOCUS 1.0 columns.
    """
    print(f"\n  [GCP Billing → FOCUS 1.0] Mapping {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"    Raw shape: {df.shape}, Columns: {list(df.columns[:10])}...")
    
    df["Date"] = pd.to_datetime(df["usage_start_time"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["CloudProvider"] = "GCP"
    df["Department"] = df["labels.value"].fillna("Unknown")
    
    df["Service"] = df.apply(
        lambda r: f"{r['service.description']} ({r['sku.description'][:40]})",
        axis=1
    )
    
    # Net cost = cost + credits (credits are negative)
    df["DailyCost_USD"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0.0) + \
                          pd.to_numeric(df["credits.amount"], errors="coerce").fillna(0.0)
    df["DailyCost_USD"] = df["DailyCost_USD"].clip(lower=0)
    
    df["vCPU_Hours"] = pd.to_numeric(df["usage.amount"], errors="coerce").fillna(0.0)
    
    # Synthesize telemetry
    np.random.seed(102)
    is_compute = df["service.description"].str.contains("Compute|Cloud Run|Vertex", case=False, na=False)
    df["Avg_CPU_Utilization_Pct"] = np.where(is_compute, np.random.uniform(15, 85, len(df)), np.random.uniform(0, 20, len(df)))
    
    is_network = df["service.description"].str.contains("Network", case=False, na=False)
    df["Data_Egress_GB"] = np.where(is_network, df["vCPU_Hours"] * np.random.uniform(0.01, 0.5, len(df)), np.random.uniform(0, 50, len(df)))
    
    is_storage = df["service.description"].str.contains("Storage", case=False, na=False)
    df["Storage_TB"] = np.where(is_storage, np.random.uniform(5, 100, len(df)), np.random.uniform(0, 10, len(df)))
    
    focus_cols = ["Date", "CloudProvider", "Department", "Service", "DailyCost_USD",
                  "vCPU_Hours", "Avg_CPU_Utilization_Pct", "Data_Egress_GB", "Storage_TB"]
    result = df[focus_cols].copy()
    
    print(f"    Mapped shape: {result.shape}")
    print(f"    Cost range: ${result['DailyCost_USD'].min():.2f} — ${result['DailyCost_USD'].max():.2f}")
    print(f"    Date range: {result['Date'].min()} → {result['Date'].max()}")
    print(f"    Unique services: {result['Service'].nunique()}")
    return result


# =========================================================================
# SECTION 3: ML MODEL INFERENCE RUNNER
# =========================================================================

def run_anomaly_detection_uat(focus_df: pd.DataFrame, provider_label: str) -> dict:
    """
    Load pre-trained anomaly detector and run inference on external data.
    """
    from src.anomaly_detection import FinOpsAnomalyDetector
    
    detector_path = MODELS_DIR / "anomaly_detector_isolation_forest.joblib"
    result = {
        "provider": provider_label,
        "input_rows": len(focus_df),
        "status": "UNKNOWN",
        "anomalies_detected": 0,
        "severity_breakdown": {},
        "total_waste_usd": 0.0,
        "root_cause_breakdown": {},
        "errors": [],
    }
    
    try:
        # Load pre-trained model
        detector = FinOpsAnomalyDetector.load(str(detector_path))
        print(f"    [✓] Loaded pre-trained anomaly detector ({len(detector.model.estimators_)} trees)")
        
        # Run inference (predict only — no retraining)
        analyzed = detector.predict(focus_df)
        
        anomalies = analyzed[analyzed["Is_Anomaly"] == True]
        result["anomalies_detected"] = len(anomalies)
        result["severity_breakdown"] = anomalies["Anomaly_Severity"].value_counts().to_dict() if len(anomalies) > 0 else {}
        result["total_waste_usd"] = round(float(anomalies["Waste_Cost_USD"].sum()), 2) if len(anomalies) > 0 else 0.0
        result["root_cause_breakdown"] = anomalies["Diagnostic_Root_Cause"].value_counts().to_dict() if len(anomalies) > 0 else {}
        result["status"] = "PASS"
        
        print(f"    [✓] Anomaly detection completed: {len(anomalies)}/{len(focus_df)} anomalies")
        print(f"        Severity: {result['severity_breakdown']}")
        print(f"        Total waste: ${result['total_waste_usd']:,.2f}")
        
    except Exception as e:
        result["status"] = "FAIL"
        result["errors"].append(f"{type(e).__name__}: {str(e)}")
        traceback.print_exc()
        print(f"    [✗] Anomaly detection FAILED: {e}")
    
    return result


def run_forecasting_uat(focus_df: pd.DataFrame, provider_label: str) -> dict:
    """
    Load pre-trained forecaster and run inference on external data.
    """
    from src.forecasting import FinOpsForecaster
    
    forecaster_path = MODELS_DIR / "spend_forecaster_histgradient.joblib"
    result = {
        "provider": provider_label,
        "input_rows": len(focus_df),
        "status": "UNKNOWN",
        "forecast_days": 0,
        "metrics": {},
        "quantile_violations": 0,
        "forecast_sample": [],
        "errors": [],
    }
    
    try:
        # Load pre-trained model
        forecaster = FinOpsForecaster.load(str(forecaster_path))
        print(f"    [✓] Loaded pre-trained forecaster (horizon={forecaster.forecast_horizon_days}d)")
        
        # Run train_and_evaluate on external data to test compatibility
        metrics = forecaster.train_and_evaluate(focus_df)
        result["metrics"] = {k: round(v, 4) if isinstance(v, float) else v for k, v in metrics.items()}
        
        # Generate future forecast
        forecast_df = forecaster.generate_future_forecast()
        result["forecast_days"] = len(forecast_df)
        result["quantile_violations"] = int(metrics.get("Quantile_Crossing_Violations", 0))
        
        if len(forecast_df) > 0:
            result["forecast_sample"] = forecast_df.head(5).to_dict("records")
        
        result["status"] = "PASS"
        print(f"    [✓] Forecasting completed: {len(forecast_df)} future days")
        print(f"        MAPE: {metrics.get('MAPE_Pct', 'N/A')}%, RMSE: ${metrics.get('RMSE_USD', 'N/A')}")
        print(f"        Quantile violations: {result['quantile_violations']}")
        
    except Exception as e:
        result["status"] = "FAIL"
        result["errors"].append(f"{type(e).__name__}: {str(e)}")
        traceback.print_exc()
        print(f"    [✗] Forecasting FAILED: {e}")
    
    return result


# =========================================================================
# SECTION 4: COMBINED UAT TEST RUNNER
# =========================================================================

def run_combined_multi_cloud_uat(focus_dfs: list, labels: list) -> dict:
    """
    Combine all vendor FOCUS DataFrames into one multi-cloud dataset
    and run anomaly detection + forecasting on the unified view.
    """
    print("\n" + "="*70)
    print("  COMBINED MULTI-CLOUD UAT (All Providers Merged)")
    print("="*70)
    
    combined_df = pd.concat(focus_dfs, ignore_index=True)
    print(f"  Combined dataset: {len(combined_df)} rows, {combined_df['CloudProvider'].nunique()} providers")
    print(f"  Provider breakdown: {combined_df['CloudProvider'].value_counts().to_dict()}")
    
    anomaly_result = run_anomaly_detection_uat(combined_df, "Multi-Cloud Combined")
    forecast_result = run_forecasting_uat(combined_df, "Multi-Cloud Combined")
    
    return {
        "total_rows": len(combined_df),
        "anomaly_detection": anomaly_result,
        "forecasting": forecast_result,
    }


# =========================================================================
# SECTION 5: FINOPS TOOLKIT DATASET HANDLER (if downloaded)
# =========================================================================

def try_finops_toolkit_dataset() -> dict:
    """
    Attempt to extract and test the Microsoft FinOps Toolkit dataset.
    """
    zip_path = UAT_DIR / "finops-toolkit-dataset-examples.zip"
    result = {"status": "SKIPPED", "message": "", "files_found": []}
    
    if not zip_path.exists():
        result["message"] = "FinOps Toolkit ZIP not downloaded — skipping"
        print(f"\n  [!] {result['message']}")
        return result
    
    try:
        import zipfile
        extract_dir = UAT_DIR / "finops-toolkit"
        with zipfile.ZipFile(str(zip_path), 'r') as zf:
            zf.extractall(str(extract_dir))
            result["files_found"] = zf.namelist()
        
        print(f"\n  [✓] Extracted FinOps Toolkit: {len(result['files_found'])} files")
        for f in result['files_found'][:10]:
            print(f"      - {f}")
        
        # Look for CSV files
        csv_files = [f for f in result["files_found"] if f.endswith('.csv')]
        if csv_files:
            result["status"] = "EXTRACTED"
            result["message"] = f"Found {len(csv_files)} CSV files"
        else:
            result["status"] = "NO_CSV"
            result["message"] = f"Extracted {len(result['files_found'])} files but no CSVs found"
    except Exception as e:
        result["status"] = "ERROR"
        result["message"] = f"Extraction failed: {e}"
    
    return result


# =========================================================================
# SECTION 6: MAIN UAT ORCHESTRATOR
# =========================================================================

def main():
    print("=" * 70)
    print("  ABHI CLOUD TECH — FinOps Intelligence UAT Pipeline")
    print("  User Acceptance Testing with Real-World Vendor Billing Formats")
    print("=" * 70)
    print(f"  Timestamp:   {datetime.now().isoformat()}")
    print(f"  Project:     {PROJECT_ROOT}")
    print(f"  Models:      {MODELS_DIR}")
    print(f"  UAT Data:    {UAT_DIR}")
    
    # ── Step 1: Verify pre-trained models exist ──
    print("\n" + "─" * 70)
    print("  STEP 1: Pre-trained Model Artifact Verification")
    print("─" * 70)
    
    detector_exists = (MODELS_DIR / "anomaly_detector_isolation_forest.joblib").exists()
    forecaster_exists = (MODELS_DIR / "spend_forecaster_histgradient.joblib").exists()
    
    print(f"  Anomaly Detector:  {'✓ FOUND' if detector_exists else '✗ MISSING'}")
    print(f"  Spend Forecaster:  {'✓ FOUND' if forecaster_exists else '✗ MISSING'}")
    
    if not detector_exists or not forecaster_exists:
        print("\n  [CRITICAL] Pre-trained model artifacts not found!")
        print("  Run: python scripts/train_and_save_models.py")
        sys.exit(1)
    
    # ── Step 2: Generate vendor-format billing CSVs ──
    print("\n" + "─" * 70)
    print("  STEP 2: Generate Realistic Vendor-Format Billing CSVs")
    print("─" * 70)
    
    aws_csv = str(UAT_DIR / "aws_cur_billing_export.csv")
    azure_csv = str(UAT_DIR / "azure_cost_management_export.csv")
    gcp_csv = str(UAT_DIR / "gcp_bigquery_billing_export.csv")
    
    generate_aws_cur_csv(aws_csv, num_rows=5000)
    generate_azure_cost_mgmt_csv(azure_csv, num_rows=5000)
    generate_gcp_billing_csv(gcp_csv, num_rows=5000)
    
    # ── Step 3: Map vendor formats → FOCUS 1.0 ──
    print("\n" + "─" * 70)
    print("  STEP 3: Vendor Format → FOCUS 1.0 Column Mapping")
    print("─" * 70)
    
    aws_focus = map_aws_cur_to_focus(aws_csv)
    azure_focus = map_azure_cost_to_focus(azure_csv)
    gcp_focus = map_gcp_billing_to_focus(gcp_csv)
    
    # Save mapped FOCUS CSVs for inspection
    aws_focus.to_csv(str(UAT_DIR / "aws_focus_mapped.csv"), index=False)
    azure_focus.to_csv(str(UAT_DIR / "azure_focus_mapped.csv"), index=False)
    gcp_focus.to_csv(str(UAT_DIR / "gcp_focus_mapped.csv"), index=False)
    print("\n  [✓] FOCUS-mapped CSVs saved to data/uat/")
    
    # ── Step 4: Per-provider anomaly detection ──
    print("\n" + "─" * 70)
    print("  STEP 4: Per-Provider Anomaly Detection UAT")
    print("─" * 70)
    
    uat_results = {"timestamp": datetime.now().isoformat(), "providers": {}, "combined": {}}
    
    for label, focus_df in [("AWS", aws_focus), ("Azure", azure_focus), ("GCP", gcp_focus)]:
        print(f"\n  ── {label} ──")
        anomaly_res = run_anomaly_detection_uat(focus_df, label)
        uat_results["providers"][label] = {"anomaly_detection": anomaly_res}
    
    # ── Step 5: Per-provider forecasting ──
    print("\n" + "─" * 70)
    print("  STEP 5: Per-Provider Spend Forecasting UAT")
    print("─" * 70)
    
    for label, focus_df in [("AWS", aws_focus), ("Azure", azure_focus), ("GCP", gcp_focus)]:
        print(f"\n  ── {label} ──")
        forecast_res = run_forecasting_uat(focus_df, label)
        uat_results["providers"][label]["forecasting"] = forecast_res
    
    # ── Step 6: Combined multi-cloud UAT ──
    combined = run_combined_multi_cloud_uat(
        [aws_focus, azure_focus, gcp_focus],
        ["AWS", "Azure", "GCP"]
    )
    uat_results["combined"] = combined
    
    # ── Step 7: FinOps Toolkit (if available) ──
    print("\n" + "─" * 70)
    print("  STEP 7: Microsoft FinOps Toolkit Dataset (Optional)")
    print("─" * 70)
    toolkit_result = try_finops_toolkit_dataset()
    uat_results["finops_toolkit"] = toolkit_result
    
    # ── Step 8: UAT Summary Report ──
    print("\n" + "=" * 70)
    print("  UAT VALIDATION SUMMARY REPORT")
    print("=" * 70)
    
    total_pass = 0
    total_fail = 0
    total_tests = 0
    
    print(f"\n  {'Provider':<20} {'Anomaly Det.':<15} {'Forecasting':<15} {'Anomalies':<10} {'Waste USD':<15}")
    print(f"  {'─'*75}")
    
    for provider, results in uat_results["providers"].items():
        ad_status = results["anomaly_detection"]["status"]
        fc_status = results["forecasting"]["status"]
        anomalies = results["anomaly_detection"]["anomalies_detected"]
        waste = results["anomaly_detection"]["total_waste_usd"]
        
        total_tests += 2
        total_pass += (1 if ad_status == "PASS" else 0) + (1 if fc_status == "PASS" else 0)
        total_fail += (1 if ad_status == "FAIL" else 0) + (1 if fc_status == "FAIL" else 0)
        
        ad_icon = "✓ PASS" if ad_status == "PASS" else "✗ FAIL"
        fc_icon = "✓ PASS" if fc_status == "PASS" else "✗ FAIL"
        print(f"  {provider:<20} {ad_icon:<15} {fc_icon:<15} {anomalies:<10} ${waste:>12,.2f}")
    
    # Combined
    comb_ad = uat_results["combined"]["anomaly_detection"]["status"]
    comb_fc = uat_results["combined"]["forecasting"]["status"]
    comb_anomalies = uat_results["combined"]["anomaly_detection"]["anomalies_detected"]
    comb_waste = uat_results["combined"]["anomaly_detection"]["total_waste_usd"]
    total_tests += 2
    total_pass += (1 if comb_ad == "PASS" else 0) + (1 if comb_fc == "PASS" else 0)
    total_fail += (1 if comb_ad == "FAIL" else 0) + (1 if comb_fc == "FAIL" else 0)
    
    comb_ad_icon = "✓ PASS" if comb_ad == "PASS" else "✗ FAIL"
    comb_fc_icon = "✓ PASS" if comb_fc == "PASS" else "✗ FAIL"
    print(f"  {'Multi-Cloud':<20} {comb_ad_icon:<15} {comb_fc_icon:<15} {comb_anomalies:<10} ${comb_waste:>12,.2f}")
    
    print(f"\n  {'─'*75}")
    print(f"  TOTAL:  {total_pass}/{total_tests} PASSED  |  {total_fail}/{total_tests} FAILED")
    
    # Forecasting metrics summary
    print(f"\n  FORECASTING METRICS:")
    for provider, results in uat_results["providers"].items():
        m = results["forecasting"]["metrics"]
        mape = m.get("MAPE_Pct", "N/A")
        rmse = m.get("RMSE_USD", "N/A")
        qv = results["forecasting"]["quantile_violations"]
        print(f"    {provider:<20} MAPE: {mape}%  |  RMSE: ${rmse}  |  QV: {qv}")
    
    cm = uat_results["combined"]["forecasting"]["metrics"]
    print(f"    {'Multi-Cloud':<20} MAPE: {cm.get('MAPE_Pct', 'N/A')}%  |  RMSE: ${cm.get('RMSE_USD', 'N/A')}  |  QV: {uat_results['combined']['forecasting']['quantile_violations']}")
    
    # ── Error Log ──
    all_errors = []
    for provider, results in uat_results["providers"].items():
        for module in ["anomaly_detection", "forecasting"]:
            if results.get(module, {}).get("errors"):
                for err in results[module]["errors"]:
                    all_errors.append(f"  [{provider}/{module}] {err}")
    
    for module in ["anomaly_detection", "forecasting"]:
        if uat_results["combined"].get(module, {}).get("errors"):
            for err in uat_results["combined"][module]["errors"]:
                all_errors.append(f"  [Multi-Cloud/{module}] {err}")
    
    if all_errors:
        print(f"\n  ⚠ ERRORS REQUIRING BACKPROPAGATION:")
        for e in all_errors:
            print(f"    {e}")
    else:
        print(f"\n  ✓ NO ERRORS — All tests passed cleanly.")
    
    # Save full report JSON
    report_path = UAT_DIR / "uat_validation_report.json"
    with open(str(report_path), "w") as f:
        json.dump(uat_results, f, indent=2, default=str)
    print(f"\n  [✓] Full UAT report saved to: {report_path}")
    
    print(f"\n  FinOps Toolkit: {toolkit_result['status']} — {toolkit_result['message']}")
    
    # Final verdict
    print("\n" + "=" * 70)
    if total_fail == 0:
        print("  🎉 UAT VERDICT: ALL TESTS PASSED — System is production-ready.")
    else:
        print(f"  ⚠ UAT VERDICT: {total_fail} TEST(S) FAILED — Backpropagation required.")
    print("=" * 70)
    
    return total_fail


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
