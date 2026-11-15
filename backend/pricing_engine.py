"""
Abhi Cloud Tech — Multi-Cloud Pricing Calculator & Arbitrage Engine
Faithfully implements the specifications and capabilities of:
1. Google Cloud Pricing Calculator (https://cloud.google.com/products/calculator)
2. AWS Pricing Calculator (https://calculator.aws/#/addService)
3. Microsoft Azure Pricing Calculator (https://azure.microsoft.com/en-in/pricing/calculator/)
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# --------------------------------------------------------------------------
# Provider Normalization Helper
# --------------------------------------------------------------------------
def normalize_provider_key(key: Optional[str]) -> str:
    """Normalizes any casing or variant of cloud provider to canonical key."""
    if not key:
        return "GCP"
    k = key.strip().upper()
    if k in ("AZURE", "MS_AZURE", "MICROSOFT_AZURE", "MICROSOFT AZURE"):
        return "Azure"
    if k in ("AWS", "AMAZON", "AMAZON WEB SERVICES"):
        return "AWS"
    if k in ("GCP", "GOOGLE", "GOOGLE CLOUD PLATFORM"):
        return "GCP"
    return "GCP"


# --------------------------------------------------------------------------
# Official Hyperscaler Cloud Catalog: Regions, Machine Presets, Disks & Commitments
# --------------------------------------------------------------------------
CLOUD_CATALOG: Dict[str, Dict[str, Any]] = {
    "GCP": {
        "provider_key": "GCP",
        "name": "Google Cloud Platform (GCP)",
        "brand_color": "#10B981",
        "official_url": "https://cloud.google.com/products/calculator",
        "regions": {
            "us-central1": {"name": "us-central1 (Iowa - Google Low-Carbon DC)", "multiplier": 1.00},
            "us-east4": {"name": "us-east4 (N. Virginia - Ashburn Corridor)", "multiplier": 1.09},
            "us-west1": {"name": "us-west1 (Oregon - Dalles Hydro)", "multiplier": 1.00},
            "europe-west3": {"name": "europe-west3 (Frankfurt, Germany)", "multiplier": 1.22},
            "europe-west1": {"name": "europe-west1 (St. Ghislain, Belgium)", "multiplier": 1.15},
            "asia-south1": {"name": "asia-south1 (Mumbai, India)", "multiplier": 1.11},
            "asia-southeast1": {"name": "asia-southeast1 (Jurong West, Singapore)", "multiplier": 1.14}
        },
        "machine_presets": [
            # Cost-optimized / Shared-core (E2 family)
            {"sku": "e2-micro", "family": "e2", "name": "e2-micro (2 shared vCPU, 1 GB RAM)", "vcpu": 0.25, "ram_gb": 1.0, "base_monthly_usd": 6.11},
            {"sku": "e2-small", "family": "e2", "name": "e2-small (2 shared vCPU, 2 GB RAM)", "vcpu": 0.5, "ram_gb": 2.0, "base_monthly_usd": 12.23},
            {"sku": "e2-medium", "family": "e2", "name": "e2-medium (2 shared vCPU, 4 GB RAM)", "vcpu": 1.0, "ram_gb": 4.0, "base_monthly_usd": 24.46},
            {"sku": "e2-standard-2", "family": "e2", "name": "e2-standard-2 (2 vCPU, 8 GB RAM)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 48.92},
            {"sku": "e2-standard-4", "family": "e2", "name": "e2-standard-4 (4 vCPU, 16 GB RAM)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 97.85},
            {"sku": "e2-standard-8", "family": "e2", "name": "e2-standard-8 (8 vCPU, 32 GB RAM)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 195.69},
            {"sku": "e2-standard-16", "family": "e2", "name": "e2-standard-16 (16 vCPU, 64 GB RAM)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 391.38},
            # General Purpose Intel (N2 family - Intel Cascade/Ice Lake)
            {"sku": "n2-standard-2", "family": "n2", "name": "n2-standard-2 (2 vCPU, 8 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 71.49},
            {"sku": "n2-standard-4", "family": "n2", "name": "n2-standard-4 (4 vCPU, 16 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 142.98},
            {"sku": "n2-standard-8", "family": "n2", "name": "n2-standard-8 (8 vCPU, 32 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 285.96},
            {"sku": "n2-standard-16", "family": "n2", "name": "n2-standard-16 (16 vCPU, 64 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 571.91},
            {"sku": "n2-standard-32", "family": "n2", "name": "n2-standard-32 (32 vCPU, 128 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 32.0, "ram_gb": 128.0, "base_monthly_usd": 1143.83},
            # General Purpose AMD (N2D family - AMD EPYC Milan - 13% savings)
            {"sku": "n2d-standard-4", "family": "n2d", "name": "n2d-standard-4 (4 vCPU, 16 GB RAM - AMD EPYC Milan)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 124.39},
            {"sku": "n2d-standard-8", "family": "n2d", "name": "n2d-standard-8 (8 vCPU, 32 GB RAM - AMD EPYC Milan)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 248.78},
            # Scale-Out / AMD (T2D family - AMD Tau Milan)
            {"sku": "t2d-standard-2", "family": "t2d", "name": "t2d-standard-2 (2 vCPU, 8 GB RAM - AMD Tau Milan)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 59.28},
            {"sku": "t2d-standard-4", "family": "t2d", "name": "t2d-standard-4 (4 vCPU, 16 GB RAM - AMD Tau Milan)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 118.55},
            {"sku": "t2d-standard-8", "family": "t2d", "name": "t2d-standard-8 (8 vCPU, 32 GB RAM - AMD Tau Milan)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 237.10},
            {"sku": "t2d-standard-16", "family": "t2d", "name": "t2d-standard-16 (16 vCPU, 64 GB RAM - AMD Tau Milan)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 474.20},
            # Compute-Optimized (C2 & C3 families)
            {"sku": "c2-standard-4", "family": "c2", "name": "c2-standard-4 (4 vCPU, 16 GB RAM - Compute Intensive)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 152.42},
            {"sku": "c2-standard-8", "family": "c2", "name": "c2-standard-8 (8 vCPU, 32 GB RAM - Compute Intensive)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 304.85},
            {"sku": "c2-standard-16", "family": "c2", "name": "c2-standard-16 (16 vCPU, 64 GB RAM - Compute Intensive)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 609.70},
            {"sku": "c3-standard-4", "family": "c3", "name": "c3-standard-4 (4 vCPU, 16 GB RAM - Intel Xeon Sapphire Rapids + IPU)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 155.05},
            # Memory-Optimized (M1 & M2 families - SAP HANA certified)
            {"sku": "m1-ultramem-40", "family": "m1", "name": "m1-ultramem-40 (40 vCPU, 961 GB RAM - Memory-Optimized SAP HANA)", "vcpu": 40.0, "ram_gb": 961.0, "base_monthly_usd": 3650.00},
            {"sku": "m2-ultramem-208", "family": "m2", "name": "m2-ultramem-208 (208 vCPU, 5888 GB RAM - Ultra-High Memory SAP HANA)", "vcpu": 208.0, "ram_gb": 5888.0, "base_monthly_usd": 24498.80},
            # Accelerator / AI (A2 & G2 families)
            {"sku": "a2-highgpu-1g", "family": "a2", "name": "a2-highgpu-1g (12 vCPU, 85 GB RAM, 1x NVIDIA A100 40GB)", "vcpu": 12.0, "ram_gb": 85.0, "base_monthly_usd": 2682.75},
            {"sku": "g2-standard-4", "family": "g2", "name": "g2-standard-4 (4 vCPU, 16 GB RAM, 1x NVIDIA L4 24GB Tensor Core)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 512.46}
        ],
        "custom_rates": {
            "vcpu_hourly": 0.0336,
            "ram_hourly": 0.0045
        },
        "storage_disk_types": {
            "pd-standard": {"name": "Standard Persistent Disk (pd-standard)", "rate_per_gb_month": 0.040, "note": "HDD storage for large sequential batch data"},
            "pd-balanced": {"name": "Balanced Persistent Disk (pd-balanced)", "rate_per_gb_month": 0.100, "note": "Cost-effective SSD for general-purpose compute"},
            "pd-ssd": {"name": "SSD Persistent Disk (pd-ssd)", "rate_per_gb_month": 0.170, "note": "High-IOPS performance SSD for database and low latency"},
            "pd-extreme": {"name": "Extreme Persistent Disk (pd-extreme)", "rate_per_gb_month": 0.250, "note": "Ultra-performance for high-end SAP and transactional RDBMS"},
            "hyperdisk-balanced": {"name": "Hyperdisk Balanced (hyperdisk-balanced)", "rate_per_gb_month": 0.090, "note": "Next-gen block storage with dynamically scalable IOPS & throughput"},
            "hyperdisk-throughput": {"name": "Hyperdisk Throughput (hyperdisk-throughput)", "rate_per_gb_month": 0.045, "note": "Cost-effective scale-out analytics and sequential streaming workloads"},
            "hyperdisk-extreme": {"name": "Hyperdisk Extreme (hyperdisk-extreme)", "rate_per_gb_month": 0.300, "note": "Highest maximum IOPS (up to 500k) for mission-critical databases"},
            "gcs-standard": {"name": "Cloud Storage Standard (gcs-standard)", "rate_per_gb_month": 0.020, "note": "Hot active data, web content and multi-cloud analytics"},
            "gcs-nearline": {"name": "Cloud Storage Nearline (gcs-nearline)", "rate_per_gb_month": 0.010, "note": "Fast, durable storage for data accessed less than once a month"},
            "gcs-coldline": {"name": "Cloud Storage Coldline (gcs-coldline)", "rate_per_gb_month": 0.004, "note": "Low-cost disaster recovery and archival accessed at most once a quarter"},
            "gcs-archive": {"name": "Cloud Storage Archive (gcs-archive)", "rate_per_gb_month": 0.0012, "note": "Lowest cost digital preservation and compliance regulatory vault"}
        },
        "commitment_discounts": {
            "on_demand": {"name": "On-Demand (Pay-As-You-Go - 0% discount)", "discount_pct": 0.0},
            "1yr_commitment": {"name": "1-Year Committed Use Discount (CUD - 37% off)", "discount_pct": 37.0},
            "3yr_commitment": {"name": "3-Year Committed Use Discount (CUD - 55% off)", "discount_pct": 55.0},
            "spot": {"name": "Spot / Preemptible VMs (60-91% off, avg 70%)", "discount_pct": 70.0}
        },
        "database_services": {
            "cloud_sql_mysql": {
                "name": "Cloud SQL for MySQL (Enterprise)",
                "engine": "MySQL 8.0",
                "presets": [
                    {"sku": "db-custom-2-7680", "name": "db-custom-2-7680 (2 vCPU, 7.5 GB RAM)", "vcpu": 2.0, "ram_gb": 7.5, "base_monthly_usd": 98.55},
                    {"sku": "db-custom-4-15360", "name": "db-custom-4-15360 (4 vCPU, 15 GB RAM)", "vcpu": 4.0, "ram_gb": 15.0, "base_monthly_usd": 197.10},
                    {"sku": "db-custom-8-30720", "name": "db-custom-8-30720 (8 vCPU, 30 GB RAM)", "vcpu": 8.0, "ram_gb": 30.0, "base_monthly_usd": 394.20}
                ],
                "storage_rate_per_gb_month": 0.170,
                "ha_multiplier": 2.0,
                "cud_1yr_discount_pct": 25.0,
                "cud_3yr_discount_pct": 52.0
            },
            "cloud_sql_postgres": {
                "name": "Cloud SQL for PostgreSQL (Enterprise)",
                "engine": "PostgreSQL 16",
                "presets": [
                    {"sku": "db-custom-2-7680", "name": "db-custom-2-7680 (2 vCPU, 7.5 GB RAM)", "vcpu": 2.0, "ram_gb": 7.5, "base_monthly_usd": 98.55},
                    {"sku": "db-custom-4-15360", "name": "db-custom-4-15360 (4 vCPU, 15 GB RAM)", "vcpu": 4.0, "ram_gb": 15.0, "base_monthly_usd": 197.10},
                    {"sku": "db-custom-8-30720", "name": "db-custom-8-30720 (8 vCPU, 30 GB RAM)", "vcpu": 8.0, "ram_gb": 30.0, "base_monthly_usd": 394.20}
                ],
                "storage_rate_per_gb_month": 0.170,
                "ha_multiplier": 2.0,
                "cud_1yr_discount_pct": 25.0,
                "cud_3yr_discount_pct": 52.0
            },
            "cloud_sql_enterprise_plus": {
                "name": "Cloud SQL Enterprise Plus (MySQL/PostgreSQL - 99.99% SLA)",
                "engine": "Enterprise Plus",
                "presets": [
                    {"sku": "db-enterprise-plus-2-16", "name": "db-enterprise-plus-2-16 (2 vCPU, 16 GB RAM)", "vcpu": 2.0, "ram_gb": 16.0, "base_monthly_usd": 164.25},
                    {"sku": "db-enterprise-plus-4-32", "name": "db-enterprise-plus-4-32 (4 vCPU, 32 GB RAM)", "vcpu": 4.0, "ram_gb": 32.0, "base_monthly_usd": 328.50},
                    {"sku": "db-enterprise-plus-8-64", "name": "db-enterprise-plus-8-64 (8 vCPU, 64 GB RAM)", "vcpu": 8.0, "ram_gb": 64.0, "base_monthly_usd": 657.00}
                ],
                "storage_rate_per_gb_month": 0.300,
                "ha_multiplier": 2.0,
                "cud_1yr_discount_pct": 25.0,
                "cud_3yr_discount_pct": 52.0
            }
        },
        "analytics_services": {
            "bigquery": {
                "name": "Google BigQuery Serverless Data Warehouse",
                "analysis_on_demand_per_tb": 6.25,
                "free_tier_analysis_tb": 1.0,
                "editions": {
                    "standard": {
                        "name": "BigQuery Standard Edition",
                        "rate_per_slot_hour": 0.040,
                        "base_monthly_per_100_slots": 2920.00
                    },
                    "enterprise": {
                        "name": "BigQuery Enterprise Edition",
                        "rate_per_slot_hour": 0.060,
                        "base_monthly_per_100_slots": 4380.00,
                        "cud_1yr_discount_pct": 20.0,
                        "cud_3yr_discount_pct": 40.0
                    },
                    "enterprise_plus": {
                        "name": "BigQuery Enterprise Plus Edition",
                        "rate_per_slot_hour": 0.100,
                        "base_monthly_per_100_slots": 7300.00,
                        "cud_1yr_discount_pct": 25.0,
                        "cud_3yr_discount_pct": 45.0
                    }
                },
                "storage": {
                    "active_storage_per_gb_month": 0.020,
                    "long_term_storage_per_gb_month": 0.010,
                    "free_tier_storage_gb": 10.0
                }
            }
        },
        "networking_services": {
            "name": "Google Cloud Global Network & Interconnect",
            "premium_tier": {
                "name": "Premium Tier (High-performance global private fiber backbone)",
                "tiers": [
                    {"max_gb": 10000.0, "rate_per_gb": 0.120, "label": "0 - 10 TB ($0.12/GB)"},
                    {"max_gb": 50000.0, "rate_per_gb": 0.110, "label": "10 TB - 50 TB ($0.11/GB)"},
                    {"max_gb": None, "rate_per_gb": 0.080, "label": "Over 50 TB ($0.08/GB)"}
                ]
            },
            "standard_tier": {
                "name": "Standard Tier (Public ISP transit routing)",
                "rate_per_gb": 0.085
            },
            "inter_region_egress": {
                "name": "Inter-Region Egress (Within North America)",
                "rate_per_gb": 0.010
            },
            "inter_continent_egress": {
                "name": "Inter-Continent Egress (Cross-continent to EMEA/APAC)",
                "rate_per_gb": 0.080
            },
            "ingress": {
                "name": "Internet & Inter-region Ingress (Always Free)",
                "rate_per_gb": 0.000
            }
        }
    },
    "AWS": {
        "provider_key": "AWS",
        "name": "Amazon Web Services (AWS)",
        "brand_color": "#FF9900",
        "official_url": "https://calculator.aws/#/addService",
        "regions": {
            "us-east-1": {"name": "us-east-1 (US East - N. Virginia)", "multiplier": 1.00},
            "us-west-2": {"name": "us-west-2 (US West - Oregon)", "multiplier": 1.00},
            "eu-central-1": {"name": "eu-central-1 (Europe - Frankfurt)", "multiplier": 1.18},
            "eu-west-1": {"name": "eu-west-1 (Europe - Ireland)", "multiplier": 1.10},
            "ap-south-1": {"name": "ap-south-1 (Asia Pacific - Mumbai)", "multiplier": 1.09},
            "ap-southeast-1": {"name": "ap-southeast-1 (Asia Pacific - Singapore)", "multiplier": 1.14},
            "sa-east-1": {"name": "sa-east-1 (South America - São Paulo)", "multiplier": 1.34}
        },
        "machine_presets": [
            # --- General Purpose (Intel Ice Lake, Graviton2/3 ARM) ---
            {"sku": "m6i.large", "family": "m6i", "category": "General Purpose", "name": "m6i.large (2 vCPU, 8 GB RAM - Intel Ice Lake)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 70.08},
            {"sku": "m6i.xlarge", "family": "m6i", "category": "General Purpose", "name": "m6i.xlarge (4 vCPU, 16 GB RAM - Intel Ice Lake)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 140.16},
            {"sku": "m6i.2xlarge", "family": "m6i", "category": "General Purpose", "name": "m6i.2xlarge (8 vCPU, 32 GB RAM - Intel Ice Lake)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 280.32},
            {"sku": "m6i.4xlarge", "family": "m6i", "category": "General Purpose", "name": "m6i.4xlarge (16 vCPU, 64 GB RAM - Intel Ice Lake)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 560.64},
            {"sku": "m6i.8xlarge", "family": "m6i", "category": "General Purpose", "name": "m6i.8xlarge (32 vCPU, 128 GB RAM - Intel Ice Lake)", "vcpu": 32.0, "ram_gb": 128.0, "base_monthly_usd": 1121.28},
            {"sku": "m6g.xlarge", "family": "m6g", "category": "General Purpose", "name": "m6g.xlarge (4 vCPU, 16 GB RAM - Graviton2 ARM - 20% off)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 112.13},
            {"sku": "m7g.xlarge", "family": "m7g", "category": "General Purpose", "name": "m7g.xlarge (4 vCPU, 16 GB RAM - Graviton3 ARM)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 119.14},
            # --- Burstable / Micro (Graviton2 & Intel Xeon) ---
            {"sku": "t4g.nano", "family": "t4g", "category": "Burstable / Micro", "name": "t4g.nano (2 vCPU burst, 0.5 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 0.5, "base_monthly_usd": 3.07},
            {"sku": "t4g.micro", "family": "t4g", "category": "Burstable / Micro", "name": "t4g.micro (2 vCPU burst, 1 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 1.0, "base_monthly_usd": 6.13},
            {"sku": "t4g.small", "family": "t4g", "category": "Burstable / Micro", "name": "t4g.small (2 vCPU burst, 2 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 2.0, "base_monthly_usd": 12.26},
            {"sku": "t4g.medium", "family": "t4g", "category": "Burstable / Micro", "name": "t4g.medium (2 vCPU burst, 4 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 4.0, "base_monthly_usd": 24.53},
            {"sku": "t4g.large", "family": "t4g", "category": "Burstable / Micro", "name": "t4g.large (2 vCPU burst, 8 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 49.06},
            {"sku": "t4g.xlarge", "family": "t4g", "category": "Burstable / Micro", "name": "t4g.xlarge (4 vCPU burst, 16 GB RAM - Graviton2)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 98.11},
            {"sku": "t3.medium", "family": "t3", "category": "Burstable / Micro", "name": "t3.medium (2 vCPU burst, 4 GB RAM - Intel Xeon)", "vcpu": 2.0, "ram_gb": 4.0, "base_monthly_usd": 30.37},
            {"sku": "t3.xlarge", "family": "t3", "category": "Burstable / Micro", "name": "t3.xlarge (4 vCPU burst, 16 GB RAM - Intel Xeon)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 121.47},
            # --- Compute Optimized (Intel Ice Lake & Graviton3) ---
            {"sku": "c6i.large", "family": "c6i", "category": "Compute Optimized", "name": "c6i.large (2 vCPU, 4 GB RAM - Intel Ice Lake)", "vcpu": 2.0, "ram_gb": 4.0, "base_monthly_usd": 62.05},
            {"sku": "c6i.xlarge", "family": "c6i", "category": "Compute Optimized", "name": "c6i.xlarge (4 vCPU, 8 GB RAM - Compute Optimized)", "vcpu": 4.0, "ram_gb": 8.0, "base_monthly_usd": 124.10},
            {"sku": "c6i.2xlarge", "family": "c6i", "category": "Compute Optimized", "name": "c6i.2xlarge (8 vCPU, 16 GB RAM - Compute Optimized)", "vcpu": 8.0, "ram_gb": 16.0, "base_monthly_usd": 248.20},
            {"sku": "c6i.4xlarge", "family": "c6i", "category": "Compute Optimized", "name": "c6i.4xlarge (16 vCPU, 32 GB RAM - Compute Optimized)", "vcpu": 16.0, "ram_gb": 32.0, "base_monthly_usd": 496.40},
            {"sku": "c7g.xlarge", "family": "c7g", "category": "Compute Optimized", "name": "c7g.xlarge (4 vCPU, 8 GB RAM - Graviton3 ARM)", "vcpu": 4.0, "ram_gb": 8.0, "base_monthly_usd": 105.49},
            # --- Memory Optimized (Intel Ice Lake 8:1 RAM-to-vCPU) ---
            {"sku": "r6i.large", "family": "r6i", "category": "Memory Optimized", "name": "r6i.large (2 vCPU, 16 GB RAM - Memory Optimized 8:1)", "vcpu": 2.0, "ram_gb": 16.0, "base_monthly_usd": 91.98},
            {"sku": "r6i.xlarge", "family": "r6i", "category": "Memory Optimized", "name": "r6i.xlarge (4 vCPU, 32 GB RAM - Memory Optimized 8:1)", "vcpu": 4.0, "ram_gb": 32.0, "base_monthly_usd": 183.96},
            {"sku": "r6i.2xlarge", "family": "r6i", "category": "Memory Optimized", "name": "r6i.2xlarge (8 vCPU, 64 GB RAM - Memory Optimized 8:1)", "vcpu": 8.0, "ram_gb": 64.0, "base_monthly_usd": 367.92},
            {"sku": "r6i.4xlarge", "family": "r6i", "category": "Memory Optimized", "name": "r6i.4xlarge (16 vCPU, 128 GB RAM - Memory Optimized 8:1)", "vcpu": 16.0, "ram_gb": 128.0, "base_monthly_usd": 735.84},
            # --- GPU / Accelerated Computing ---
            {"sku": "g5.xlarge", "family": "g5", "category": "GPU / Accelerated", "name": "g5.xlarge (4 vCPU, 16 GB RAM, 1x NVIDIA A10G 24GB)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 734.38},
            {"sku": "g5.2xlarge", "family": "g5", "category": "GPU / Accelerated", "name": "g5.2xlarge (8 vCPU, 32 GB RAM, 1x NVIDIA A10G 24GB)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 884.76},
            {"sku": "p4d.24xlarge", "family": "p4d", "category": "GPU / Accelerated", "name": "p4d.24xlarge (96 vCPU, 1152 GB RAM, 8x NVIDIA A100 40GB)", "vcpu": 96.0, "ram_gb": 1152.0, "base_monthly_usd": 23923.99}
        ],
        "custom_rates": {
            "vcpu_hourly": 0.0480,
            "ram_hourly": 0.0060
        },
        "storage_disk_types": {
            "gp3": {"name": "General Purpose SSD (gp3 - $0.08/GB-mo base + 3,000 IOPS baseline)", "rate_per_gb_month": 0.080, "note": "Latest generation general purpose SSD ($0.08/GB-mo base + baseline 3,000 IOPS & 125 MB/s)"},
            "gp2": {"name": "General Purpose SSD legacy (gp2 - $0.10/GB-mo)", "rate_per_gb_month": 0.100, "note": "Legacy standard SSD with burstable baseline ($0.10/GB-mo)"},
            "io2": {"name": "Provisioned IOPS SSD (io2 Block Express - $0.125/GB-mo base)", "rate_per_gb_month": 0.125, "note": "Sub-millisecond latency for mission-critical databases ($0.125/GB-mo base + provisioned IOPS)"},
            "st1": {"name": "Throughput Optimized HDD (st1 - $0.045/GB-mo)", "rate_per_gb_month": 0.045, "note": "Low-cost HDD for big data, data warehousing and log processing ($0.045/GB-mo)"},
            "sc1": {"name": "Cold HDD (sc1 - $0.025/GB-mo)", "rate_per_gb_month": 0.025, "note": "Lowest cost magnetic storage for infrequently accessed sequential workloads ($0.025/GB-mo)"},
            "s3-standard": {"name": "Amazon S3 Standard Object Storage ($0.023/GB-mo)", "rate_per_gb_month": 0.023, "note": "High-durability object storage for frequently accessed multi-tenant assets"},
            "s3-intelligent": {"name": "Amazon S3 Intelligent-Tiering ($0.021/GB-mo)", "rate_per_gb_month": 0.021, "note": "Automated cost optimization across frequent and infrequent access tiers"},
            "s3-glacier-flexible": {"name": "Amazon S3 Glacier Flexible Retrieval ($0.0036/GB-mo)", "rate_per_gb_month": 0.0036, "note": "Low-cost cold archive storage with flexible retrieval in minutes to hours"},
            "s3-glacier-deep-archive": {"name": "Amazon S3 Glacier Deep Archive ($0.00099/GB-mo)", "rate_per_gb_month": 0.00099, "note": "Lowest-cost cloud object storage for compliance long-term data retention"}
        },
        "commitment_discounts": {
            "on_demand": {"name": "On-Demand (Pay-As-You-Go - 0% discount)", "discount_pct": 0.0},
            "1yr_savings_plan": {"name": "1-Year Compute Savings Plan (28% discount)", "discount_pct": 28.0},
            "1yr_commitment": {"name": "1-Year Compute Savings Plan (28% discount)", "discount_pct": 28.0},
            "3yr_savings_plan": {"name": "3-Year Compute Savings Plan (45% discount)", "discount_pct": 45.0},
            "3yr_commitment": {"name": "3-Year Compute Savings Plan (45% discount)", "discount_pct": 45.0},
            "1yr_ri": {"name": "1-Year Standard EC2 Reserved Instance (37% discount)", "discount_pct": 37.0},
            "3yr_ri": {"name": "3-Year Standard EC2 Reserved Instance (60% discount)", "discount_pct": 60.0},
            "spot": {"name": "EC2 Spot Instances (70-90% discount, avg 72%)", "discount_pct": 72.0}
        },
        "database_services": {
            "rds_m6i_large_single": {
                "name": "RDS PostgreSQL/MySQL (db.m6i.large - Single-AZ)",
                "engine": "PostgreSQL / MySQL",
                "vcpu": 2.0,
                "ram_gb": 8.0,
                "multi_az": False,
                "hourly_usd": 0.178,
                "monthly_usd": 129.94,
                "note": "Standard enterprise general-purpose relational database"
            },
            "rds_m6i_large_multiaz": {
                "name": "RDS PostgreSQL/MySQL (db.m6i.large - Multi-AZ HA)",
                "engine": "PostgreSQL / MySQL",
                "vcpu": 2.0,
                "ram_gb": 8.0,
                "multi_az": True,
                "hourly_usd": 0.356,
                "monthly_usd": 259.88,
                "note": "Production synchronous multi-AZ standby replication for zero data loss"
            },
            "aurora_mysql": {
                "name": "Amazon Aurora MySQL (Multi-AZ Enterprise)",
                "engine": "Amazon Aurora MySQL",
                "vcpu": 2.0,
                "ram_gb": 8.0,
                "multi_az": True,
                "hourly_usd": 0.290,
                "monthly_usd": 211.70,
                "note": "High-throughput cloud-native MySQL with 6-way storage replication"
            },
            "aurora_postgresql": {
                "name": "Amazon Aurora PostgreSQL (Multi-AZ Enterprise)",
                "engine": "Amazon Aurora PostgreSQL",
                "vcpu": 2.0,
                "ram_gb": 8.0,
                "multi_az": True,
                "hourly_usd": 0.290,
                "monthly_usd": 211.70,
                "note": "High-throughput cloud-native PostgreSQL with 6-way storage replication"
            },
            "dynamodb_on_demand": {
                "name": "Amazon DynamoDB (On-Demand Capacity)",
                "wcu_per_million": 1.25,
                "rcu_per_million": 0.25,
                "storage_rate_per_gb_month": 0.25,
                "note": "Pay-per-request pricing: $1.25 per million write units, $0.25 per million read units"
            },
            "dynamodb_provisioned": {
                "name": "Amazon DynamoDB (Provisioned Capacity)",
                "wcu_hourly": 0.00065,
                "rcu_hourly": 0.00013,
                "storage_rate_per_gb_month": 0.25,
                "note": "Dedicated provisioned throughput: $0.00065/WCU-hour, $0.00013/RCU-hour"
            }
        },
        "networking_services": {
            "internet_egress": {
                "name": "AWS Data Transfer / Internet Outbound Egress",
                "free_tier_gb": 100.0,
                "rate_per_gb": 0.090,
                "note": "First 100 GB/month data transfer out to the Internet is free; $0.09/GB outbound thereafter"
            },
            "inter_region_egress": {
                "name": "AWS Inter-Region Data Transfer",
                "rate_per_gb": 0.020,
                "note": "Traffic between AWS regions (e.g., us-east-1 to us-west-2)"
            }
        }
    },
    "Azure": {
        "provider_key": "Azure",
        "name": "Microsoft Azure",
        "brand_color": "#0284C7",
        "official_url": "https://azure.microsoft.com/en-in/pricing/calculator/",
        "regions": {
            "eastus": {"name": "eastus (East US - Virginia)", "multiplier": 1.00},
            "westus2": {"name": "westus2 (West US 2 - Washington)", "multiplier": 1.00},
            "westeurope": {"name": "westeurope (West Europe - Netherlands)", "multiplier": 1.17},
            "northeurope": {"name": "northeurope (North Europe - Ireland)", "multiplier": 1.15},
            "centralindia": {"name": "centralindia (Central India - Pune)", "multiplier": 1.10},
            "southeastasia": {"name": "southeastasia (Southeast Asia - Singapore)", "multiplier": 1.13},
            "centralus": {"name": "centralus (Central US - Iowa)", "multiplier": 1.00},
            "uksouth": {"name": "uksouth (UK South - London)", "multiplier": 1.16}
        },
        "machine_presets": [
            # --- General Purpose Burstable (B-series) ---
            {"sku": "Standard_B1s", "family": "Standard_B", "name": "Standard_B1s (1 vCPU, 1 GB RAM - Burstable)", "vcpu": 1.0, "ram_gb": 1.0, "base_monthly_usd": 7.59},
            {"sku": "Standard_B2s", "family": "Standard_B", "name": "Standard_B2s (2 vCPU, 4 GB RAM - Burstable)", "vcpu": 2.0, "ram_gb": 4.0, "base_monthly_usd": 30.37},
            {"sku": "Standard_B4ms", "family": "Standard_B", "name": "Standard_B4ms (4 vCPU, 16 GB RAM - Burstable)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 121.47},
            # --- General Purpose (Dv5-series - Intel Xeon Platinum 8370C Ice Lake) ---
            {"sku": "Standard_D2s_v5", "family": "Standard_Dsv5", "name": "Standard_D2s_v5 (2 vCPU, 8 GB RAM - Intel Ice Lake)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 70.08},
            {"sku": "Standard_D4s_v5", "family": "Standard_Dsv5", "name": "Standard_D4s_v5 (4 vCPU, 16 GB RAM - Intel Ice Lake)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 140.16},
            {"sku": "Standard_D8s_v5", "family": "Standard_Dsv5", "name": "Standard_D8s_v5 (8 vCPU, 32 GB RAM - Intel Ice Lake)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 280.32},
            {"sku": "Standard_D16s_v5", "family": "Standard_Dsv5", "name": "Standard_D16s_v5 (16 vCPU, 64 GB RAM - Intel Ice Lake)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 560.64},
            {"sku": "Standard_D32s_v5", "family": "Standard_Dsv5", "name": "Standard_D32s_v5 (32 vCPU, 128 GB RAM - Intel Ice Lake)", "vcpu": 32.0, "ram_gb": 128.0, "base_monthly_usd": 1121.28},
            # --- General Purpose AMD (Dasv5-series - AMD EPYC 7763 Milan) ---
            {"sku": "Standard_D4as_v5", "family": "Standard_Dasv5", "name": "Standard_D4as_v5 (4 vCPU, 16 GB RAM - AMD Milan - 12% off)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 123.37},
            {"sku": "Standard_D8as_v5", "family": "Standard_Dasv5", "name": "Standard_D8as_v5 (8 vCPU, 32 GB RAM - AMD Milan - 12% off)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 246.74},
            # --- Memory Optimized (Ev5-series - Intel Xeon Ice Lake 8:1 RAM-to-vCPU) ---
            {"sku": "Standard_E2s_v5", "family": "Standard_Esv5", "name": "Standard_E2s_v5 (2 vCPU, 16 GB RAM - Memory Optimized)", "vcpu": 2.0, "ram_gb": 16.0, "base_monthly_usd": 91.98},
            {"sku": "Standard_E4s_v5", "family": "Standard_Esv5", "name": "Standard_E4s_v5 (4 vCPU, 32 GB RAM - Memory Optimized)", "vcpu": 4.0, "ram_gb": 32.0, "base_monthly_usd": 183.96},
            {"sku": "Standard_E8s_v5", "family": "Standard_Esv5", "name": "Standard_E8s_v5 (8 vCPU, 64 GB RAM - Memory Optimized)", "vcpu": 8.0, "ram_gb": 64.0, "base_monthly_usd": 367.92},
            {"sku": "Standard_E16s_v5", "family": "Standard_Esv5", "name": "Standard_E16s_v5 (16 vCPU, 128 GB RAM - Memory Optimized)", "vcpu": 16.0, "ram_gb": 128.0, "base_monthly_usd": 735.84},
            # --- Compute Optimized (Fsv2-series - Intel Xeon Platinum 8168 3.7GHz Turbo) ---
            {"sku": "Standard_F4s_v2", "family": "Standard_Fsv2", "name": "Standard_F4s_v2 (4 vCPU, 8 GB RAM - Compute Intensive)", "vcpu": 4.0, "ram_gb": 8.0, "base_monthly_usd": 123.00},
            {"sku": "Standard_F8s_v2", "family": "Standard_Fsv2", "name": "Standard_F8s_v2 (8 vCPU, 16 GB RAM - Compute Intensive)", "vcpu": 8.0, "ram_gb": 16.0, "base_monthly_usd": 246.01},
            {"sku": "Standard_F16s_v2", "family": "Standard_Fsv2", "name": "Standard_F16s_v2 (16 vCPU, 32 GB RAM - Compute Intensive)", "vcpu": 16.0, "ram_gb": 32.0, "base_monthly_usd": 492.02},
            # --- GPU / AI Acceleration (NCas_T4_v3 - NVIDIA Tesla T4 16GB) ---
            {"sku": "Standard_NC4as_T4_v3", "family": "Standard_NCas_T4", "name": "Standard_NC4as_T4_v3 (4 vCPU, 28 GB RAM, 1x NVIDIA T4 GPU)", "vcpu": 4.0, "ram_gb": 28.0, "base_monthly_usd": 383.98},
            {"sku": "Standard_NC8as_T4_v3", "family": "Standard_NCas_T4", "name": "Standard_NC8as_T4_v3 (8 vCPU, 56 GB RAM, 1x NVIDIA T4 GPU)", "vcpu": 8.0, "ram_gb": 56.0, "base_monthly_usd": 543.12}
        ],
        "custom_rates": {
            "vcpu_hourly": 0.0475,
            "ram_hourly": 0.0059
        },
        "storage_disk_types": {
            "Standard_LRS": {"name": "Standard HDD Managed Disk (Standard_LRS)", "rate_per_gb_month": 0.040, "note": "Low cost backup and non-critical dev/test"},
            "standard-hdd": {"name": "Standard HDD Managed Disk (Standard_LRS)", "rate_per_gb_month": 0.040, "note": "Low cost backup and non-critical dev/test"},
            "StandardSSD_LRS": {"name": "Standard SSD Managed Disk (StandardSSD_LRS)", "rate_per_gb_month": 0.075, "note": "Cost-effective solid state drive for web servers and light workloads"},
            "standard-ssd": {"name": "Standard SSD Managed Disk (StandardSSD_LRS)", "rate_per_gb_month": 0.075, "note": "Cost-effective solid state drive for web servers and light workloads"},
            "Premium_LRS": {"name": "Premium SSD Managed Disk (Premium_LRS - P1-P80)", "rate_per_gb_month": 0.135, "note": "High performance SSD for production I/O-intensive workloads"},
            "premium-ssd": {"name": "Premium SSD Managed Disk (Premium_LRS - P1-P80)", "rate_per_gb_month": 0.135, "note": "High performance SSD for production I/O-intensive workloads"},
            "PremiumV2_LRS": {"name": "Premium SSD v2 Managed Disk (PremiumV2_LRS)", "rate_per_gb_month": 0.115, "note": "Next-gen sub-millisecond disk with independently scalable IOPS/throughput"},
            "premium-ssd-v2": {"name": "Premium SSD v2 Managed Disk (PremiumV2_LRS)", "rate_per_gb_month": 0.115, "note": "Next-gen sub-millisecond disk with independently scalable IOPS/throughput"},
            "UltraSSD_LRS": {"name": "Ultra Disk Managed Storage (UltraSSD_LRS)", "rate_per_gb_month": 0.220, "note": "Sub-millisecond latency for SAP HANA and top-tier SQL workloads"},
            "ultra-disk": {"name": "Ultra Disk Managed Storage (UltraSSD_LRS)", "rate_per_gb_month": 0.220, "note": "Sub-millisecond latency for SAP HANA and top-tier SQL workloads"},
            "blob-hot": {"name": "Azure Blob Storage (Hot Tier)", "rate_per_gb_month": 0.018, "note": "Optimized for frequently accessed unstructured object data"},
            "blob-cool": {"name": "Azure Blob Storage (Cool Tier)", "rate_per_gb_month": 0.010, "note": "Infrequently accessed data stored for at least 30 days"},
            "blob-cold": {"name": "Azure Blob Storage (Cold Tier)", "rate_per_gb_month": 0.0036, "note": "Rarely accessed data stored for at least 90 days"},
            "blob-archive": {"name": "Azure Blob Storage (Archive Tier)", "rate_per_gb_month": 0.00099, "note": "Long-term archive stored for at least 180 days with flexible retrieval"}
        },
        "commitment_discounts": {
            "on_demand": {"name": "Pay-as-you-go (0% discount)", "discount_pct": 0.0},
            "1yr_savings_plan": {"name": "1-Year Savings Plan (38% discount)", "discount_pct": 38.0},
            "3yr_savings_plan": {"name": "3-Year Savings Plan (56% discount)", "discount_pct": 56.0},
            "1yr_ri": {"name": "1-Year Reserved Instance (42% discount)", "discount_pct": 42.0},
            "3yr_ri": {"name": "3-Year Reserved Instance (62% discount)", "discount_pct": 62.0},
            "1yr_commitment": {"name": "1-Year Reserved Instance (42% discount)", "discount_pct": 42.0},
            "3yr_commitment": {"name": "3-Year Reserved Instance (62% discount)", "discount_pct": 62.0},
            "spot": {"name": "Spot Instances (80% discount)", "discount_pct": 80.0}
        },
        "database_services": {
            "azure_sql_vcore": {
                "name": "Azure SQL Database (vCore Gen5 Model)",
                "compute_rate_per_vcore_hour": 0.252,
                "storage_rate_per_gb_month": 0.115,
                "ahb_discount_pct": 48.0,
                "note": "Independent compute and storage scaling for enterprise mission-critical workloads"
            },
            "azure_sql_dtu": {
                "name": "Azure SQL Database (Standard DTU Model)",
                "rate_per_dtu_month": 0.020,
                "storage_rate_per_gb_month": 0.100,
                "note": "Preconfigured database throughput units (S0-S12) for predictable web workloads"
            },
            "cosmos_db_ru": {
                "name": "Azure Cosmos DB (Provisioned RU/s)",
                "rate_per_100_ru_hour": 0.008,
                "storage_rate_per_gb_month": 0.250,
                "note": "Guaranteed low latency with provisioned Request Units per second"
            },
            "cosmos_db_serverless": {
                "name": "Azure Cosmos DB (Serverless)",
                "rate_per_million_ru": 0.250,
                "storage_rate_per_gb_month": 0.250,
                "note": "Pay-per-request model for spiky, intermittent traffic workloads"
            }
        },
        "networking_services": {
            "internet_egress": {
                "name": "Azure Internet Egress Bandwidth",
                "free_tier_gb": 100.0,
                "tiers": [
                    {"max_gb": 100.0, "rate_per_gb": 0.000, "label": "First 100 GB / month (Free)"},
                    {"max_gb": 10000.0, "rate_per_gb": 0.087, "label": "100 GB - 10 TB ($0.087/GB)"},
                    {"max_gb": 50000.0, "rate_per_gb": 0.083, "label": "10 TB - 50 TB ($0.083/GB)"},
                    {"max_gb": 150000.0, "rate_per_gb": 0.070, "label": "50 TB - 150 TB ($0.070/GB)"},
                    {"max_gb": None, "rate_per_gb": 0.050, "label": "Over 150 TB ($0.050/GB)"}
                ]
            },
            "inter_region_egress": {
                "name": "Azure Inter-Region Egress Bandwidth",
                "rate_per_gb": 0.020,
                "note": "Traffic between Azure regions within North America / Europe"
            }
        }
    }
}

# Compatibility aliases
REAL_CLOUD_CATALOG = CLOUD_CATALOG
HYPERSCALER_PRICING_CATALOG = CLOUD_CATALOG
HYPERSCALER_CATALOG = CLOUD_CATALOG

# --------------------------------------------------------------------------
# Request & Calculation Models
# --------------------------------------------------------------------------
class CloudCalculatorRequest(BaseModel):
    cloud_provider: str = Field(default="GCP", description="Selected Cloud: GCP, AWS, or Azure")
    region: str = Field(default="us-central1", description="Region key")
    provisioning_mode: str = Field(default="preset", description="preset (predetermined machine type) or custom")
    machine_sku: Optional[str] = Field(default="e2-standard-4", description="Predetermined machine SKU")
    custom_vcpu: float = Field(default=4.0, ge=0.25, le=512.0, description="Custom vCPU count")
    custom_ram_gb: float = Field(default=16.0, ge=0.5, le=4096.0, description="Custom RAM in GB")
    storage_type: str = Field(default="pd-balanced", description="Storage disk type")
    storage_gb: float = Field(default=100.0, ge=0.0, le=500000.0, description="Boot disk / storage size in GB")
    instance_count: int = Field(default=1, ge=1, le=1000, description="Number of VM instances")
    operating_hours_per_day: int = Field(default=24, ge=1, le=24, description="Operating hours per day (1-24)")
    commitment: str = Field(default="on_demand", description="on_demand, 1yr_savings_plan, 3yr_savings_plan, 1yr_ri, 3yr_ri, 1yr_commitment, 3yr_commitment, spot")
    os_type: str = Field(default="linux", description="linux or windows")
    azure_hybrid_benefit: bool = Field(default=False, description="Azure Hybrid Benefit Windows (AHB: 48% off VM license / BYOL)")
    azure_hybrid_benefit_linux: bool = Field(default=False, description="Azure Hybrid Benefit Linux (AHBL: RHEL/SLES license savings)")
    downsize_pct: float = Field(default=50.0, ge=0.0, le=100.0, description="Rightsizing downsize potential percentage")
    egress_gb: float = Field(default=0.0, ge=0.0, le=1000000.0, description="Monthly network egress in GB (first 100GB free on Azure)")


# --------------------------------------------------------------------------
# Granular Calculation Functions
# --------------------------------------------------------------------------
def calculate_aws_egress_cost(egress_gb: float) -> Dict[str, Any]:
    """Calculates AWS Internet Data Transfer / Egress cost (first 100GB/month free, $0.09/GB outbound thereafter)."""
    if egress_gb <= 0:
        return {"egress_gb": 0.0, "free_gb": 0.0, "billable_gb": 0.0, "monthly_cost_usd": 0.0, "rate_desc": "First 100 GB free, $0.09/GB thereafter"}
    
    free_gb = min(100.0, egress_gb)
    billable_gb = max(0.0, egress_gb - 100.0)
    monthly_cost = round(billable_gb * 0.090, 2)
    return {
        "egress_gb": egress_gb,
        "free_gb": free_gb,
        "billable_gb": billable_gb,
        "monthly_cost_usd": monthly_cost,
        "rate_desc": "First 100 GB/mo free, then $0.090/GB outbound"
    }


def calculate_aws_ebs_cost(volume_type: str = "gp3", size_gb: float = 100.0, provisioned_iops: int = 3000, throughput_mbps: int = 125, region_multiplier: float = 1.0) -> Dict[str, Any]:
    """Calculates AWS EBS volume storage costs including gp3 provisioned IOPS/throughput and io2."""
    vol = volume_type.lower()
    base_rates = {
        "gp3": 0.080,
        "gp2": 0.100,
        "io2": 0.125,
        "st1": 0.045,
        "sc1": 0.025
    }
    rate = base_rates.get(vol, 0.080)
    capacity_cost = (size_gb * rate) * region_multiplier
    iops_cost = 0.0
    throughput_cost = 0.0

    if vol == "gp3":
        if provisioned_iops > 3000:
            iops_cost = (provisioned_iops - 3000) * 0.005 * region_multiplier
        if throughput_mbps > 125:
            throughput_cost = (throughput_mbps - 125) * 0.040 * region_multiplier
    elif vol == "io2":
        iops_cost = provisioned_iops * 0.065 * region_multiplier

    total = round(capacity_cost + iops_cost + throughput_cost, 2)
    return {
        "volume_type": volume_type,
        "size_gb": size_gb,
        "capacity_cost_usd": round(capacity_cost, 2),
        "iops_cost_usd": round(iops_cost, 2),
        "throughput_cost_usd": round(throughput_cost, 2),
        "monthly_cost_usd": total,
        "annual_cost_usd": round(total * 12.0, 2)
    }


def calculate_aws_s3_cost(tier: str = "s3-standard", size_gb: float = 1000.0, region_multiplier: float = 1.0) -> Dict[str, Any]:
    """Calculates AWS S3 Object Storage costs across Standard, Intelligent-Tiering, Glacier Flexible, and Glacier Deep Archive."""
    tier_rates = {
        "s3-standard": 0.023,
        "s3-intelligent": 0.021,
        "s3-glacier-flexible": 0.0036,
        "s3-glacier-deep-archive": 0.00099
    }
    rate = tier_rates.get(tier.lower(), 0.023)
    monthly = round((size_gb * rate) * region_multiplier, 2)
    return {
        "tier": tier,
        "size_gb": size_gb,
        "rate_per_gb_month": rate,
        "monthly_cost_usd": monthly,
        "annual_cost_usd": round(monthly * 12.0, 2)
    }


def calculate_aws_rds_cost(service_key: str = "rds_m6i_large_multiaz", multi_az: bool = True, hours_per_month: int = 730, region_multiplier: float = 1.0) -> Dict[str, Any]:
    """Calculates AWS RDS (Aurora PostgreSQL/MySQL, db.m6i.large, Multi-AZ) costs."""
    aws_dbs = CLOUD_CATALOG["AWS"]["database_services"]
    spec = aws_dbs.get(service_key) or aws_dbs.get("rds_m6i_large_multiaz")
    hourly = spec["hourly_usd"] * region_multiplier
    monthly = round(hourly * hours_per_month, 2)
    return {
        "service_key": service_key,
        "name": spec["name"],
        "engine": spec["engine"],
        "vcpu": spec["vcpu"],
        "ram_gb": spec["ram_gb"],
        "multi_az": spec["multi_az"],
        "hourly_usd": round(hourly, 4),
        "monthly_cost_usd": monthly,
        "annual_cost_usd": round(monthly * 12.0, 2)
    }


def calculate_aws_dynamodb_cost(capacity_mode: str = "provisioned", wcu: float = 100.0, rcu: float = 200.0, storage_gb: float = 50.0, million_writes: float = 10.0, million_reads: float = 50.0, region_multiplier: float = 1.0) -> Dict[str, Any]:
    """Calculates Amazon DynamoDB costs for On-Demand WCU/RCU or Provisioned capacity."""
    aws_dbs = CLOUD_CATALOG["AWS"]["database_services"]
    if capacity_mode.lower() == "on_demand":
        spec = aws_dbs["dynamodb_on_demand"]
        write_cost = (million_writes * spec["wcu_per_million"]) * region_multiplier
        read_cost = (million_reads * spec["rcu_per_million"]) * region_multiplier
        storage_cost = (storage_gb * spec["storage_rate_per_gb_month"]) * region_multiplier
        total = round(write_cost + read_cost + storage_cost, 2)
        return {
            "capacity_mode": "On-Demand",
            "million_writes": million_writes,
            "million_reads": million_reads,
            "storage_gb": storage_gb,
            "write_cost_usd": round(write_cost, 2),
            "read_cost_usd": round(read_cost, 2),
            "storage_cost_usd": round(storage_cost, 2),
            "monthly_cost_usd": total,
            "annual_cost_usd": round(total * 12.0, 2)
        }
    else:
        spec = aws_dbs["dynamodb_provisioned"]
        wcu_monthly = (wcu * spec["wcu_hourly"] * 730.0) * region_multiplier
        rcu_monthly = (rcu * spec["rcu_hourly"] * 730.0) * region_multiplier
        storage_cost = (storage_gb * spec["storage_rate_per_gb_month"]) * region_multiplier
        total = round(wcu_monthly + rcu_monthly + storage_cost, 2)
        return {
            "capacity_mode": "Provisioned",
            "wcu": wcu,
            "rcu": rcu,
            "storage_gb": storage_gb,
            "wcu_monthly_usd": round(wcu_monthly, 2),
            "rcu_monthly_usd": round(rcu_monthly, 2),
            "storage_cost_usd": round(storage_cost, 2),
            "monthly_cost_usd": total,
            "annual_cost_usd": round(total * 12.0, 2)
        }


def calculate_azure_egress_cost(egress_gb: float, egress_type: str = "internet") -> Dict[str, Any]:
    """Calculates Azure network egress according to tiered rates (first 100GB free for internet)."""
    if egress_gb <= 0:
        return {"egress_gb": 0.0, "free_gb": 0.0, "billable_gb": 0.0, "monthly_cost_usd": 0.0}

    if egress_type == "inter_region":
        cost = egress_gb * 0.020
        return {
            "egress_gb": egress_gb,
            "free_gb": 0.0,
            "billable_gb": egress_gb,
            "monthly_cost_usd": round(cost, 2),
            "rate_desc": "$0.020/GB inter-region data transfer"
        }

    # Internet Egress with first 100 GB/month free
    free_gb = min(100.0, egress_gb)
    billable_gb = max(0.0, egress_gb - 100.0)
    cost = 0.0
    remaining = billable_gb

    # Tier 1: 100 GB - 10,000 GB (9,900 GB span) @ $0.087
    t1_cap = 9900.0
    t1_chunk = min(remaining, t1_cap)
    cost += t1_chunk * 0.087
    remaining -= t1_chunk

    # Tier 2: 10 TB - 50 TB (40,000 GB span) @ $0.083
    if remaining > 0:
        t2_cap = 40000.0
        t2_chunk = min(remaining, t2_cap)
        cost += t2_chunk * 0.083
        remaining -= t2_chunk

    # Tier 3: 50 TB - 150 TB (100,000 GB span) @ $0.070
    if remaining > 0:
        t3_cap = 100000.0
        t3_chunk = min(remaining, t3_cap)
        cost += t3_chunk * 0.070
        remaining -= t3_chunk

    # Tier 4: Over 150 TB @ $0.050
    if remaining > 0:
        cost += remaining * 0.050

    return {
        "egress_gb": egress_gb,
        "free_gb": free_gb,
        "billable_gb": billable_gb,
        "monthly_cost_usd": round(cost, 2),
        "rate_desc": "First 100 GB free, then $0.087/GB tiered down to $0.050/GB"
    }


def calculate_azure_sql_database_cost(
    model: str = "vCore",
    vcore_count: float = 2.0,
    dtu_count: float = 100.0,
    storage_gb: float = 100.0,
    commitment: str = "on_demand",
    ahb: bool = False,
    region_multiplier: float = 1.0
) -> Dict[str, Any]:
    """Calculates Azure SQL Database costs for vCore Gen5 or DTU models with AHB and RI support."""
    az = CLOUD_CATALOG["Azure"]["database_services"]
    if model.lower() in ("dtu", "standard_dtu"):
        dtu_spec = az["azure_sql_dtu"]
        compute_cost = (dtu_count * dtu_spec["rate_per_dtu_month"]) * region_multiplier
        storage_cost = (storage_gb * dtu_spec["storage_rate_per_gb_month"]) * region_multiplier
        base_monthly = compute_cost + storage_cost
        disc_pct = 0.0
        if commitment in ("1yr_ri", "1yr_commitment", "1yr_savings_plan"):
            disc_pct = 35.0
        elif commitment in ("3yr_ri", "3yr_commitment", "3yr_savings_plan"):
            disc_pct = 50.0
        discounted = (compute_cost * (1.0 - disc_pct / 100.0)) + storage_cost
        return {
            "service": "Azure SQL Database (DTU)",
            "model": "Standard DTU",
            "dtu_count": dtu_count,
            "storage_gb": storage_gb,
            "compute_monthly_usd": round(compute_cost, 2),
            "storage_monthly_usd": round(storage_cost, 2),
            "monthly_cost_usd": round(discounted, 2),
            "annual_cost_usd": round(discounted * 12.0, 2),
            "discount_pct": disc_pct
        }
    else:
        vcore_spec = az["azure_sql_vcore"]
        base_compute = (vcore_count * vcore_spec["compute_rate_per_vcore_hour"] * 730.0) * region_multiplier
        storage_cost = (storage_gb * vcore_spec["storage_rate_per_gb_month"]) * region_multiplier
        
        # Commitment discount
        ri_disc = 0.0
        if commitment in ("1yr_ri", "1yr_commitment"):
            ri_disc = 42.0
        elif commitment in ("3yr_ri", "3yr_commitment"):
            ri_disc = 62.0
        elif commitment == "1yr_savings_plan":
            ri_disc = 38.0
        elif commitment == "3yr_savings_plan":
            ri_disc = 56.0

        # Azure Hybrid Benefit (AHB for SQL Server: 48% off compute licensing)
        ahb_disc = 48.0 if ahb else 0.0
        effective_disc = min(85.0, ri_disc + ahb_disc)

        discounted_compute = base_compute * (1.0 - effective_disc / 100.0)
        total_monthly = discounted_compute + storage_cost

        return {
            "service": "Azure SQL Database (vCore)",
            "model": "General Purpose vCore Gen5",
            "vcore_count": vcore_count,
            "storage_gb": storage_gb,
            "compute_monthly_usd": round(discounted_compute, 2),
            "storage_monthly_usd": round(storage_cost, 2),
            "monthly_cost_usd": round(total_monthly, 2),
            "annual_cost_usd": round(total_monthly * 12.0, 2),
            "discount_pct": effective_disc,
            "azure_hybrid_benefit_applied": ahb
        }


def calculate_azure_cosmos_db_cost(
    capacity_mode: str = "provisioned",
    provisioned_ru: float = 400.0,
    serverless_million_ru: float = 10.0,
    storage_gb: float = 50.0,
    region_multiplier: float = 1.0
) -> Dict[str, Any]:
    """Calculates Azure Cosmos DB costs for provisioned RU/s or serverless requests."""
    az = CLOUD_CATALOG["Azure"]["database_services"]
    if capacity_mode.lower() == "serverless":
        spec = az["cosmos_db_serverless"]
        request_cost = (serverless_million_ru * spec["rate_per_million_ru"]) * region_multiplier
        storage_cost = (storage_gb * spec["storage_rate_per_gb_month"]) * region_multiplier
        total = request_cost + storage_cost
        return {
            "service": "Azure Cosmos DB (Serverless)",
            "capacity_mode": "Serverless",
            "million_ru_month": serverless_million_ru,
            "storage_gb": storage_gb,
            "request_monthly_usd": round(request_cost, 2),
            "storage_monthly_usd": round(storage_cost, 2),
            "monthly_cost_usd": round(total, 2),
            "annual_cost_usd": round(total * 12.0, 2)
        }
    else:
        spec = az["cosmos_db_ru"]
        throughput_units = max(1.0, provisioned_ru / 100.0)
        compute_cost = (throughput_units * spec["rate_per_100_ru_hour"] * 730.0) * region_multiplier
        storage_cost = (storage_gb * spec["storage_rate_per_gb_month"]) * region_multiplier
        total = compute_cost + storage_cost
        return {
            "service": "Azure Cosmos DB (Provisioned)",
            "capacity_mode": "Provisioned RU/s",
            "provisioned_ru_per_sec": provisioned_ru,
            "storage_gb": storage_gb,
            "throughput_monthly_usd": round(compute_cost, 2),
            "storage_monthly_usd": round(storage_cost, 2),
            "monthly_cost_usd": round(total, 2),
            "annual_cost_usd": round(total * 12.0, 2)
        }


def calculate_gcp_network_egress_cost(
    egress_gb: float = 1000.0,
    tier: str = "premium",
    destination: str = "internet"
) -> Dict[str, Any]:
    """
    Calculates GCP Network Egress costs for Premium Tier (Google Private Backbone)
    vs Standard Tier (Public ISP Peering) and Inter-region.
    """
    if egress_gb <= 0:
        return {"egress_gb": 0.0, "monthly_cost_usd": 0.0, "tier": tier, "rate_desc": "No egress"}

    if tier.lower() == "standard":
        cost = egress_gb * 0.085
        return {
            "egress_gb": egress_gb,
            "monthly_cost_usd": round(cost, 2),
            "tier": "Standard Tier (Public Transit ISP Peering)",
            "rate_desc": "$0.085/GB across all destinations"
        }
    elif destination == "inter_region":
        cost = egress_gb * 0.010
        return {
            "egress_gb": egress_gb,
            "monthly_cost_usd": round(cost, 2),
            "tier": "Inter-Region (North America)",
            "rate_desc": "$0.010/GB inter-region data transfer"
        }
    elif destination == "inter_continent":
        cost = egress_gb * 0.080
        return {
            "egress_gb": egress_gb,
            "monthly_cost_usd": round(cost, 2),
            "tier": "Inter-Continent (NA to EMEA/APAC)",
            "rate_desc": "$0.080/GB inter-continent data transfer"
        }
    else:
        # Premium Tier: Tiered pricing
        cost = 0.0
        remaining = egress_gb
        # 0 - 10 TB (10,000 GB) @ $0.12/GB
        t1 = min(remaining, 10000.0)
        cost += t1 * 0.120
        remaining -= t1
        # 10 TB - 50 TB (40,000 GB) @ $0.11/GB
        if remaining > 0:
            t2 = min(remaining, 40000.0)
            cost += t2 * 0.110
            remaining -= t2
        # Over 50 TB @ $0.08/GB
        if remaining > 0:
            cost += remaining * 0.080

        return {
            "egress_gb": egress_gb,
            "monthly_cost_usd": round(cost, 2),
            "tier": "Premium Tier (Google Global Private Fiber Backbone)",
            "rate_desc": "$0.12/GB (first 10TB), $0.11/GB (next 40TB), $0.08/GB (>50TB)"
        }


def calculate_gcp_cloud_sql_cost(
    engine: str = "mysql",
    sku: str = "db-custom-4-15360",
    storage_gb: float = 100.0,
    high_availability: bool = False,
    commitment: str = "on_demand",
    region_multiplier: float = 1.0
) -> Dict[str, Any]:
    """
    Calculates Google Cloud SQL costs for MySQL, PostgreSQL, or Enterprise Plus
    with optional High Availability (regional standby) and 1-Yr / 3-Yr CUD.
    """
    gcp_db = CLOUD_CATALOG["GCP"]["database_services"]
    if "enterprise_plus" in engine.lower():
        spec = gcp_db["cloud_sql_enterprise_plus"]
    elif "postgres" in engine.lower():
        spec = gcp_db["cloud_sql_postgres"]
    else:
        spec = gcp_db["cloud_sql_mysql"]

    preset = next((p for p in spec["presets"] if p["sku"] == sku), spec["presets"][1])
    ha_factor = spec["ha_multiplier"] if high_availability else 1.0

    base_compute_monthly = preset["base_monthly_usd"] * region_multiplier * ha_factor
    storage_monthly = storage_gb * spec["storage_rate_per_gb_month"] * region_multiplier * ha_factor

    disc_pct = 0.0
    if commitment in ("1yr_commitment", "1yr_cud", "1yr_ri"):
        disc_pct = spec.get("cud_1yr_discount_pct", 25.0)
    elif commitment in ("3yr_commitment", "3yr_cud", "3yr_ri"):
        disc_pct = spec.get("cud_3yr_discount_pct", 52.0)

    discounted_compute = base_compute_monthly * (1.0 - (disc_pct / 100.0))
    total_monthly = discounted_compute + storage_monthly

    return {
        "service": spec["name"],
        "engine": spec["engine"],
        "sku": preset["sku"],
        "name": preset["name"],
        "vcpu": preset["vcpu"],
        "ram_gb": preset["ram_gb"],
        "storage_gb": storage_gb,
        "high_availability": high_availability,
        "commitment": commitment,
        "discount_pct": disc_pct,
        "compute_monthly_usd": round(discounted_compute, 2),
        "storage_monthly_usd": round(storage_monthly, 2),
        "monthly_cost_usd": round(total_monthly, 2),
        "annual_cost_usd": round(total_monthly * 12.0, 2)
    }


def calculate_gcp_bigquery_cost(
    pricing_model: str = "on_demand",
    edition: str = "enterprise",
    query_tb_per_month: float = 10.0,
    slots_reserved: int = 100,
    active_storage_gb: float = 500.0,
    long_term_storage_gb: float = 2000.0,
    commitment: str = "on_demand"
) -> Dict[str, Any]:
    """
    Calculates Google BigQuery analytics spend for On-Demand ($6.25/TB analysis,
    1TB free tier) or Edition slot commitments (Standard, Enterprise, Enterprise Plus)
    plus active and long-term storage.
    """
    bq = CLOUD_CATALOG["GCP"]["analytics_services"]["bigquery"]
    storage_spec = bq["storage"]

    billable_active_gb = max(0.0, active_storage_gb - storage_spec["free_tier_storage_gb"])
    storage_cost = (billable_active_gb * storage_spec["active_storage_per_gb_month"]) + \
                   (long_term_storage_gb * storage_spec["long_term_storage_per_gb_month"])

    if pricing_model.lower() == "edition":
        ed_spec = bq["editions"].get(edition.lower(), bq["editions"]["enterprise"])
        base_slot_cost = slots_reserved * ed_spec["rate_per_slot_hour"] * 730.0
        disc_pct = 0.0
        if commitment in ("1yr_commitment", "1yr_cud", "1yr_ri"):
            disc_pct = ed_spec.get("cud_1yr_discount_pct", 20.0)
        elif commitment in ("3yr_commitment", "3yr_cud", "3yr_ri"):
            disc_pct = ed_spec.get("cud_3yr_discount_pct", 40.0)
        compute_cost = base_slot_cost * (1.0 - (disc_pct / 100.0))
        model_desc = f"{ed_spec['name']} ({slots_reserved} dedicated slots)"
    else:
        billable_tb = max(0.0, query_tb_per_month - bq["free_tier_analysis_tb"])
        compute_cost = billable_tb * bq["analysis_on_demand_per_tb"]
        disc_pct = 0.0
        model_desc = f"On-Demand Analysis ({query_tb_per_month} TB scanned, 1 TB free tier)"

    total_monthly = compute_cost + storage_cost
    return {
        "service": bq["name"],
        "pricing_model": pricing_model,
        "model_description": model_desc,
        "query_compute_monthly_usd": round(compute_cost, 2),
        "storage_monthly_usd": round(storage_cost, 2),
        "monthly_cost_usd": round(total_monthly, 2),
        "annual_cost_usd": round(total_monthly * 12.0, 2),
        "discount_pct": disc_pct
    }


# --------------------------------------------------------------------------
# Main Workload Estimation Engine
# --------------------------------------------------------------------------
def calculate_cloud_workload_estimate(req: CloudCalculatorRequest) -> Dict[str, Any]:
    """
    Computes exact granular monthly and hourly costs for the user's selected cloud,
    region, machine preset or custom vCPU/RAM, and boot disk type.
    Also calculates 1:1 parity equivalents across the other two cloud providers.
    """
    prov_key = normalize_provider_key(req.cloud_provider)
    prov = CLOUD_CATALOG[prov_key]

    # 1. Resolve Region
    regions = prov["regions"]
    reg_key = req.region if req.region in regions else list(regions.keys())[0]
    reg_info = regions[reg_key]
    reg_multiplier = reg_info["multiplier"]

    # 2. Resolve Machine Hardware (vCPU, RAM, SKU Name)
    if req.provisioning_mode == "preset":
        preset_match = next((p for p in prov["machine_presets"] if p["sku"] == req.machine_sku), None)
        if not preset_match:
            # Fallback to sensible default in this provider's presets
            preset_match = prov["machine_presets"][4] if len(prov["machine_presets"]) > 4 else prov["machine_presets"][0]
        vcpu = preset_match["vcpu"]
        ram_gb = preset_match["ram_gb"]
        sku_display = preset_match["sku"]
        sku_full_name = preset_match["name"]
        raw_base_monthly = preset_match["base_monthly_usd"]
    else:
        vcpu = req.custom_vcpu
        ram_gb = req.custom_ram_gb
        sku_display = f"Custom ({vcpu} vCPU, {ram_gb} GB RAM)"
        sku_full_name = f"Custom Configured Compute Engine ({vcpu} vCPU, {ram_gb} GB RAM)"
        rates = prov["custom_rates"]
        hourly_custom = (vcpu * rates["vcpu_hourly"]) + (ram_gb * rates["ram_hourly"])
        raw_base_monthly = hourly_custom * 730.0

    # 3. Resolve Storage Disk
    disks = prov["storage_disk_types"]
    disk_key = req.storage_type if req.storage_type in disks else list(disks.keys())[0]
    disk_info = disks[disk_key]
    disk_rate = disk_info["rate_per_gb_month"]
    monthly_storage_per_instance = req.storage_gb * disk_rate * reg_multiplier

    # 4. Resolve Commitment Discount
    discounts = prov["commitment_discounts"]
    disc_info = discounts.get(req.commitment, discounts["on_demand"])
    base_disc_pct = disc_info["discount_pct"]

    # Azure Hybrid Benefit (AHB Windows: 48% off VM license; AHBL Linux: 18% off)
    ahb_disc = 0.0
    if prov_key == "Azure":
        if req.os_type.lower() == "windows" and req.azure_hybrid_benefit:
            ahb_disc = 48.0
        elif (req.os_type.lower() in ["linux", "rhel", "sles"]) and (req.azure_hybrid_benefit_linux or req.azure_hybrid_benefit):
            ahb_disc = 18.0

    effective_disc_pct = min(90.0, base_disc_pct + ahb_disc)

    # OS Licensing
    # Windows VM standard surcharge is ~48% on Azure unless AHB is enabled (paying Linux base rate)
    if req.os_type.lower() == "windows":
        os_multiplier = 1.0 if (prov_key == "Azure" and req.azure_hybrid_benefit) else 1.48
    else:
        os_multiplier = 1.0

    # Hours calculation
    hours_ratio = req.operating_hours_per_day / 24.0

    # Compute Cost calculation
    compute_base_monthly = raw_base_monthly * reg_multiplier * os_multiplier * hours_ratio
    discount_factor = max(0.0, 1.0 - (effective_disc_pct / 100.0))
    discounted_compute_monthly = compute_base_monthly * discount_factor

    # Egress Cost calculation (if requested)
    if prov_key == "Azure":
        egress_summary = calculate_azure_egress_cost(req.egress_gb, "internet")
    elif prov_key == "GCP":
        egress_summary = calculate_gcp_network_egress_cost(req.egress_gb, "premium")
    elif prov_key == "AWS":
        egress_summary = calculate_aws_egress_cost(req.egress_gb) if "calculate_aws_egress_cost" in globals() else {"monthly_cost_usd": round(req.egress_gb * 0.09, 2), "free_gb": 0.0, "billable_gb": req.egress_gb}
    else:
        egress_summary = {
            "monthly_cost_usd": round(max(0.0, req.egress_gb * 0.085), 2),
            "free_gb": 0.0,
            "billable_gb": req.egress_gb
        }
    monthly_egress = egress_summary["monthly_cost_usd"]

    # Total per instance & across fleet
    unit_monthly = discounted_compute_monthly + monthly_storage_per_instance
    total_monthly = (unit_monthly * req.instance_count) + monthly_egress
    total_hourly = total_monthly / (730.0 * hours_ratio) if (730.0 * hours_ratio) > 0 else 0.0
    total_annual = total_monthly * 12.0

    # Undiscounted baseline for savings transparency
    # Baseline assumes full retail on-demand compute without AHB/commitments
    retail_os_mult = 1.48 if req.os_type.lower() == "windows" else 1.0
    retail_compute_monthly = raw_base_monthly * reg_multiplier * retail_os_mult * hours_ratio
    undiscounted_monthly = ((retail_compute_monthly + monthly_storage_per_instance) * req.instance_count) + monthly_egress
    discount_savings_monthly = max(0.0, undiscounted_monthly - total_monthly)

    # Rightsizing Before vs After potential
    downsized_monthly = total_monthly * (1.0 - (req.downsize_pct / 100.0))
    monthly_rightsizing_recovery = total_monthly - downsized_monthly

    # 5. Cross-Cloud 1:1 Parity Benchmark on the OTHER two clouds
    cross_cloud_parity = {}
    for other_key in ["GCP", "AWS", "Azure"]:
        other_prov = CLOUD_CATALOG[other_key]
        other_reg_key = list(other_prov["regions"].keys())[0]
        other_reg_mult = other_prov["regions"][other_reg_key]["multiplier"]

        # Find closest preset equivalent matching vCPU and RAM (prioritizing general-purpose baseline)
        matching_preset = min(
            other_prov["machine_presets"],
            key=lambda p: (
                abs(p["vcpu"] - vcpu) + abs(p["ram_gb"] - ram_gb),
                0 if p.get("family") in ["m6i", "Standard_Dsv5", "e2", "n2"] else 1
            )
        )

        # Apply proportional commitment discount on other clouds
        other_disc_pct = base_disc_pct
        if req.commitment == "spot":
            other_disc_pct = 70.0
        elif req.commitment in ("3yr_ri", "3yr_savings_plan", "3yr_commitment"):
            other_disc_pct = 55.0
        elif req.commitment in ("1yr_ri", "1yr_savings_plan", "1yr_commitment"):
            other_disc_pct = 35.0

        other_os_mult = 1.45 if (req.os_type.lower() == "windows" and other_key != "Azure") else 1.0
        other_compute_base = matching_preset["base_monthly_usd"] * other_reg_mult * other_os_mult * hours_ratio
        other_disc_factor = (1.0 - (other_disc_pct / 100.0))
        other_discounted_compute = other_compute_base * other_disc_factor

        # Equivalent disk matching
        if "ssd" in disk_key.lower():
            other_disk_key = next((k for k in other_prov["storage_disk_types"] if "ssd" in k.lower() or "gp3" in k.lower() or "balanced" in k.lower()), list(other_prov["storage_disk_types"].keys())[0])
        elif "ultra" in disk_key.lower() or "extreme" in disk_key.lower():
            other_disk_key = next((k for k in other_prov["storage_disk_types"] if "ultra" in k.lower() or "extreme" in k.lower() or "io2" in k.lower()), list(other_prov["storage_disk_types"].keys())[0])
        else:
            other_disk_key = list(other_prov["storage_disk_types"].keys())[0]

        other_disk_rate = other_prov["storage_disk_types"][other_disk_key]["rate_per_gb_month"]
        other_storage_cost = req.storage_gb * other_disk_rate * other_reg_mult

        other_total = (other_discounted_compute + other_storage_cost) * req.instance_count

        cross_cloud_parity[other_key] = {
            "provider_key": other_key,
            "provider_name": other_prov["name"],
            "brand_color": other_prov["brand_color"],
            "equivalent_sku": matching_preset["sku"],
            "equivalent_sku_name": matching_preset["name"],
            "equivalent_disk": other_prov["storage_disk_types"][other_disk_key]["name"],
            "monthly_cost_usd": round(other_total, 2),
            "annual_cost_usd": round(other_total * 12.0, 2),
            "delta_vs_current_usd": round(other_total - total_monthly, 2)
        }

    # Determine cross-cloud winner and intelligent arbitrage recommendation
    all_three = list(cross_cloud_parity.values())
    cheapest = min(all_three, key=lambda x: x["monthly_cost_usd"])
    is_current_optimal = (cheapest["provider_key"] == prov_key)

    if is_current_optimal:
        other_two = [x for x in all_three if x["provider_key"] != prov_key]
        next_cheapest = min(other_two, key=lambda x: x["monthly_cost_usd"])
        cheaper_by_monthly = max(0.0, round(next_cheapest["monthly_cost_usd"] - total_monthly, 2))
        cheaper_by_annual = round(cheaper_by_monthly * 12.0, 2)
        arbitrage_message = (
            f"Optimal Placement: {prov['name']} is already your lowest-cost cloud provider for this workload. "
            f"It is ${cheaper_by_monthly:,.2f}/month (${cheaper_by_annual:,.2f}/year) cheaper than {next_cheapest['provider_name']}."
        )
        savings_monthly = 0.0
        savings_annual = 0.0
    else:
        savings_monthly = max(0.0, round(total_monthly - cheapest["monthly_cost_usd"], 2))
        savings_annual = round(savings_monthly * 12.0, 2)
        savings_pct = round((savings_monthly / total_monthly) * 100, 1) if total_monthly > 0 else 0.0
        arbitrage_message = (
            f"FinOps Arbitrage Alert: Migrating this workload to {cheapest['provider_name']} instead of {prov['name']} "
            f"saves ${savings_monthly:,.2f}/month (${savings_annual:,.2f}/year) — a {savings_pct}% cost reduction."
        )

    return {
        "status": "success",
        "selected_cloud": {
            "provider_key": prov_key,
            "provider_name": prov["name"],
            "brand_color": prov["brand_color"],
            "region_key": reg_key,
            "region_name": reg_info["name"],
            "provisioning_mode": req.provisioning_mode,
            "machine_sku": sku_display,
            "machine_name": sku_full_name,
            "vcpu": vcpu,
            "ram_gb": ram_gb,
            "storage_type_key": disk_key,
            "storage_type_name": disk_info["name"],
            "storage_gb": req.storage_gb,
            "instance_count": req.instance_count,
            "operating_hours_per_day": req.operating_hours_per_day,
            "commitment_model": disc_info["name"],
            "commitment_discount_pct": effective_disc_pct,
            "monthly_cost_usd": round(total_monthly, 2),
            "hourly_cost_usd": round(total_hourly, 4),
            "annual_cost_usd": round(total_annual, 2),
            "undiscounted_monthly_cost_usd": round(undiscounted_monthly, 2),
            "discount_savings_monthly_usd": round(discount_savings_monthly, 2),
            "rightsized_monthly_cost_usd": round(downsized_monthly, 2),
            "rightsized_monthly_savings_usd": round(monthly_rightsizing_recovery, 2),
            "rightsized_annual_savings_usd": round(monthly_rightsizing_recovery * 12.0, 2),
            "breakdown": {
                "compute_monthly_usd": round(discounted_compute_monthly * req.instance_count, 2),
                "storage_monthly_usd": round(monthly_storage_per_instance * req.instance_count, 2),
                "egress_monthly_usd": round(monthly_egress, 2)
            }
        },
        "cross_cloud_parity": cross_cloud_parity,
        "arbitrage_summary": {
            "is_current_optimal": is_current_optimal,
            "recommended_provider": cheapest["provider_key"],
            "recommended_provider_name": cheapest["provider_name"],
            "recommended_monthly_cost_usd": cheapest["monthly_cost_usd"],
            "savings_vs_current_usd": savings_monthly,
            "savings_vs_current_annual_usd": savings_annual,
            "recommendation_message": arbitrage_message
        }
    }
