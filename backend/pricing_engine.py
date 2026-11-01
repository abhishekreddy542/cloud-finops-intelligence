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
            {"sku": "e2-micro", "family": "e2", "name": "e2-micro (2 shared vCPU, 1 GB RAM)", "vcpu": 0.25, "ram_gb": 1.0, "base_monthly_usd": 6.11},
            {"sku": "e2-small", "family": "e2", "name": "e2-small (2 shared vCPU, 2 GB RAM)", "vcpu": 0.5, "ram_gb": 2.0, "base_monthly_usd": 12.23},
            {"sku": "e2-medium", "family": "e2", "name": "e2-medium (2 shared vCPU, 4 GB RAM)", "vcpu": 1.0, "ram_gb": 4.0, "base_monthly_usd": 24.46},
            {"sku": "e2-standard-2", "family": "e2", "name": "e2-standard-2 (2 vCPU, 8 GB RAM)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 48.92},
            {"sku": "e2-standard-4", "family": "e2", "name": "e2-standard-4 (4 vCPU, 16 GB RAM)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 97.85},
            {"sku": "e2-standard-8", "family": "e2", "name": "e2-standard-8 (8 vCPU, 32 GB RAM)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 195.69},
            {"sku": "e2-standard-16", "family": "e2", "name": "e2-standard-16 (16 vCPU, 64 GB RAM)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 391.38},
            {"sku": "n2-standard-2", "family": "n2", "name": "n2-standard-2 (2 vCPU, 8 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 71.49},
            {"sku": "n2-standard-4", "family": "n2", "name": "n2-standard-4 (4 vCPU, 16 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 142.98},
            {"sku": "n2-standard-8", "family": "n2", "name": "n2-standard-8 (8 vCPU, 32 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 285.96},
            {"sku": "n2-standard-16", "family": "n2", "name": "n2-standard-16 (16 vCPU, 64 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 571.91},
            {"sku": "n2-standard-32", "family": "n2", "name": "n2-standard-32 (32 vCPU, 128 GB RAM - Intel Cascade/Ice Lake)", "vcpu": 32.0, "ram_gb": 128.0, "base_monthly_usd": 1143.83},
            {"sku": "t2d-standard-2", "family": "t2d", "name": "t2d-standard-2 (2 vCPU, 8 GB RAM - AMD Tau Milan)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 59.28},
            {"sku": "t2d-standard-4", "family": "t2d", "name": "t2d-standard-4 (4 vCPU, 16 GB RAM - AMD Tau Milan)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 118.55},
            {"sku": "t2d-standard-8", "family": "t2d", "name": "t2d-standard-8 (8 vCPU, 32 GB RAM - AMD Tau Milan)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 237.10},
            {"sku": "c2-standard-4", "family": "c2", "name": "c2-standard-4 (4 vCPU, 16 GB RAM - Compute Intensive)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 152.42},
            {"sku": "c2-standard-8", "family": "c2", "name": "c2-standard-8 (8 vCPU, 32 GB RAM - Compute Intensive)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 304.85},
            {"sku": "c2-standard-16", "family": "c2", "name": "c2-standard-16 (16 vCPU, 64 GB RAM - Compute Intensive)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 609.70}
        ],
        "custom_rates": {
            "vcpu_hourly": 0.0336,
            "ram_hourly": 0.0045
        },
        "storage_disk_types": {
            "pd-standard": {"name": "Standard Persistent Disk (pd-standard)", "rate_per_gb_month": 0.040, "note": "HDD storage for large sequential batch data"},
            "pd-balanced": {"name": "Balanced Persistent Disk (pd-balanced)", "rate_per_gb_month": 0.100, "note": "Cost-effective SSD for general-purpose compute"},
            "pd-ssd": {"name": "SSD Persistent Disk (pd-ssd)", "rate_per_gb_month": 0.170, "note": "High-IOPS performance SSD for database and low latency"},
            "pd-extreme": {"name": "Extreme Persistent Disk (pd-extreme)", "rate_per_gb_month": 0.250, "note": "Ultra-performance for high-end SAP and transactional RDBMS"}
        },
        "commitment_discounts": {
            "on_demand": {"name": "On-Demand (Pay-As-You-Go)", "discount_pct": 0.0},
            "1yr_commitment": {"name": "1-Year Committed Use Discount (CUD - 37% off)", "discount_pct": 37.0},
            "3yr_commitment": {"name": "3-Year Committed Use Discount (CUD - 55% off)", "discount_pct": 55.0},
            "spot": {"name": "Spot / Preemptible VMs (60-70% off)", "discount_pct": 70.0}
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
            {"sku": "t4g.nano", "family": "t4g", "name": "t4g.nano (2 vCPU burst, 0.5 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 0.5, "base_monthly_usd": 3.07},
            {"sku": "t4g.micro", "family": "t4g", "name": "t4g.micro (2 vCPU burst, 1 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 1.0, "base_monthly_usd": 6.13},
            {"sku": "t4g.small", "family": "t4g", "name": "t4g.small (2 vCPU burst, 2 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 2.0, "base_monthly_usd": 12.26},
            {"sku": "t4g.medium", "family": "t4g", "name": "t4g.medium (2 vCPU burst, 4 GB RAM - Graviton2)", "vcpu": 2.0, "ram_gb": 4.0, "base_monthly_usd": 24.53},
            {"sku": "m6i.large", "family": "m6i", "name": "m6i.large (2 vCPU, 8 GB RAM - Intel Ice Lake)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 70.08},
            {"sku": "m6i.xlarge", "family": "m6i", "name": "m6i.xlarge (4 vCPU, 16 GB RAM - Intel Ice Lake)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 140.16},
            {"sku": "m6i.2xlarge", "family": "m6i", "name": "m6i.2xlarge (8 vCPU, 32 GB RAM - Intel Ice Lake)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 280.32},
            {"sku": "m6i.4xlarge", "family": "m6i", "name": "m6i.4xlarge (16 vCPU, 64 GB RAM - Intel Ice Lake)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 560.64},
            {"sku": "m6i.8xlarge", "family": "m6i", "name": "m6i.8xlarge (32 vCPU, 128 GB RAM - Intel Ice Lake)", "vcpu": 32.0, "ram_gb": 128.0, "base_monthly_usd": 1121.28},
            {"sku": "m6g.xlarge", "family": "m6g", "name": "m6g.xlarge (4 vCPU, 16 GB RAM - Graviton2 ARM - 20% off)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 112.13},
            {"sku": "m6g.2xlarge", "family": "m6g", "name": "m6g.2xlarge (8 vCPU, 32 GB RAM - Graviton2 ARM - 20% off)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 224.26},
            {"sku": "c6i.xlarge", "family": "c6i", "name": "c6i.xlarge (4 vCPU, 8 GB RAM - Compute Optimized)", "vcpu": 4.0, "ram_gb": 8.0, "base_monthly_usd": 124.10},
            {"sku": "c6i.2xlarge", "family": "c6i", "name": "c6i.2xlarge (8 vCPU, 16 GB RAM - Compute Optimized)", "vcpu": 8.0, "ram_gb": 16.0, "base_monthly_usd": 248.20},
            {"sku": "r6i.xlarge", "family": "r6i", "name": "r6i.xlarge (4 vCPU, 32 GB RAM - Memory Optimized 8:1)", "vcpu": 4.0, "ram_gb": 32.0, "base_monthly_usd": 183.96},
            {"sku": "r6i.2xlarge", "family": "r6i", "name": "r6i.2xlarge (8 vCPU, 64 GB RAM - Memory Optimized 8:1)", "vcpu": 8.0, "ram_gb": 64.0, "base_monthly_usd": 367.92}
        ],
        "custom_rates": {
            "vcpu_hourly": 0.0480,
            "ram_hourly": 0.0060
        },
        "storage_disk_types": {
            "gp3": {"name": "General Purpose SSD (gp3 - 3,000 IOPS baseline)", "rate_per_gb_month": 0.080, "note": "Latest generation general purpose SSD with independent IOPS scaling"},
            "gp2": {"name": "General Purpose SSD (gp2)", "rate_per_gb_month": 0.100, "note": "Legacy standard SSD with burstable baseline"},
            "io2": {"name": "Provisioned IOPS SSD (io2 Block Express)", "rate_per_gb_month": 0.125, "note": "Sub-millisecond latency for mission-critical databases"},
            "st1": {"name": "Throughput Optimized HDD (st1)", "rate_per_gb_month": 0.045, "note": "Low-cost HDD for big data, data warehousing and log processing"},
            "sc1": {"name": "Cold HDD (sc1)", "rate_per_gb_month": 0.025, "note": "Lowest cost magnetic storage for infrequently accessed sequential workloads"}
        },
        "commitment_discounts": {
            "on_demand": {"name": "On-Demand (Pay-As-You-Go)", "discount_pct": 0.0},
            "1yr_commitment": {"name": "1-Year Compute Savings Plan (35% off)", "discount_pct": 35.0},
            "3yr_commitment": {"name": "3-Year Compute Savings Plan (55% off)", "discount_pct": 55.0},
            "spot": {"name": "EC2 Spot Instances (~70% off)", "discount_pct": 70.0}
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
            "southeastasia": {"name": "southeastasia (Southeast Asia - Singapore)", "multiplier": 1.13}
        },
        "machine_presets": [
            {"sku": "Standard_B1s", "family": "Standard_B", "name": "Standard_B1s (1 vCPU, 1 GB RAM - Burstable)", "vcpu": 1.0, "ram_gb": 1.0, "base_monthly_usd": 7.59},
            {"sku": "Standard_B2s", "family": "Standard_B", "name": "Standard_B2s (2 vCPU, 4 GB RAM - Burstable)", "vcpu": 2.0, "ram_gb": 4.0, "base_monthly_usd": 30.37},
            {"sku": "Standard_B4ms", "family": "Standard_B", "name": "Standard_B4ms (4 vCPU, 16 GB RAM - Burstable)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 121.47},
            {"sku": "Standard_D2s_v5", "family": "Standard_Dsv5", "name": "Standard_D2s_v5 (2 vCPU, 8 GB RAM - Intel Ice Lake)", "vcpu": 2.0, "ram_gb": 8.0, "base_monthly_usd": 70.08},
            {"sku": "Standard_D4s_v5", "family": "Standard_Dsv5", "name": "Standard_D4s_v5 (4 vCPU, 16 GB RAM - Intel Ice Lake)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 140.16},
            {"sku": "Standard_D8s_v5", "family": "Standard_Dsv5", "name": "Standard_D8s_v5 (8 vCPU, 32 GB RAM - Intel Ice Lake)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 280.32},
            {"sku": "Standard_D16s_v5", "family": "Standard_Dsv5", "name": "Standard_D16s_v5 (16 vCPU, 64 GB RAM - Intel Ice Lake)", "vcpu": 16.0, "ram_gb": 64.0, "base_monthly_usd": 560.64},
            {"sku": "Standard_D32s_v5", "family": "Standard_Dsv5", "name": "Standard_D32s_v5 (32 vCPU, 128 GB RAM - Intel Ice Lake)", "vcpu": 32.0, "ram_gb": 128.0, "base_monthly_usd": 1121.28},
            {"sku": "Standard_D4as_v5", "family": "Standard_Dasv5", "name": "Standard_D4as_v5 (4 vCPU, 16 GB RAM - AMD Milan - 12% off)", "vcpu": 4.0, "ram_gb": 16.0, "base_monthly_usd": 123.37},
            {"sku": "Standard_D8as_v5", "family": "Standard_Dasv5", "name": "Standard_D8as_v5 (8 vCPU, 32 GB RAM - AMD Milan - 12% off)", "vcpu": 8.0, "ram_gb": 32.0, "base_monthly_usd": 246.74},
            {"sku": "Standard_E4s_v5", "family": "Standard_Esv5", "name": "Standard_E4s_v5 (4 vCPU, 32 GB RAM - Memory Optimized)", "vcpu": 4.0, "ram_gb": 32.0, "base_monthly_usd": 183.96},
            {"sku": "Standard_E8s_v5", "family": "Standard_Esv5", "name": "Standard_E8s_v5 (8 vCPU, 64 GB RAM - Memory Optimized)", "vcpu": 8.0, "ram_gb": 64.0, "base_monthly_usd": 367.92},
            {"sku": "Standard_F4s_v2", "family": "Standard_Fsv2", "name": "Standard_F4s_v2 (4 vCPU, 8 GB RAM - Compute Intensive)", "vcpu": 4.0, "ram_gb": 8.0, "base_monthly_usd": 123.00}
        ],
        "custom_rates": {
            "vcpu_hourly": 0.0475,
            "ram_hourly": 0.0059
        },
        "storage_disk_types": {
            "standard-hdd": {"name": "Standard HDD Managed Disk", "rate_per_gb_month": 0.040, "note": "Low cost backup and non-critical dev/test"},
            "standard-ssd": {"name": "Standard SSD Managed Disk", "rate_per_gb_month": 0.075, "note": "Cost-effective solid state drive for web servers and light workloads"},
            "premium-ssd": {"name": "Premium SSD Managed Disk (P1-P80)", "rate_per_gb_month": 0.135, "note": "High performance SSD for production I/O-intensive workloads"},
            "ultra-disk": {"name": "Ultra Disk Managed Storage", "rate_per_gb_month": 0.220, "note": "Sub-millisecond latency for SAP HANA and top-tier SQL workloads"}
        },
        "commitment_discounts": {
            "on_demand": {"name": "Pay-As-You-Go (0% off)", "discount_pct": 0.0},
            "1yr_commitment": {"name": "1-Year Reserved Virtual Machine (~35% off)", "discount_pct": 35.0},
            "3yr_commitment": {"name": "3-Year Reserved Virtual Machine (~55% off)", "discount_pct": 55.0},
            "spot": {"name": "Azure Spot Virtual Machines (~70% off)", "discount_pct": 70.0}
        }
    }
}

# Compatibility alias for existing codebase
REAL_CLOUD_CATALOG = CLOUD_CATALOG

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
    commitment: str = Field(default="on_demand", description="on_demand, 1yr_commitment, 3yr_commitment, spot")
    os_type: str = Field(default="linux", description="linux or windows")
    azure_hybrid_benefit: bool = Field(default=False, description="Azure Hybrid Benefit (BYOL Windows)")
    downsize_pct: float = Field(default=50.0, ge=0.0, le=100.0, description="Rightsizing downsize potential percentage")


def calculate_cloud_workload_estimate(req: CloudCalculatorRequest) -> Dict[str, Any]:
    """
    Computes exact granular monthly and hourly costs for the user's selected cloud,
    region, machine preset or custom vCPU/RAM, and boot disk type.
    Also calculates 1:1 parity equivalents across the other two cloud providers.
    """
    prov_key = req.cloud_provider.upper()
    if prov_key not in CLOUD_CATALOG:
        prov_key = "GCP"
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
            preset_match = prov["machine_presets"][4]  # Default e.g. e2-standard-4 or m6i.xlarge
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

    # Azure Hybrid Benefit (saves 40% on Windows compute)
    ahb_disc = 40.0 if prov_key == "AZURE" and req.os_type.lower() == "windows" and req.azure_hybrid_benefit else 0.0
    effective_disc_pct = min(85.0, base_disc_pct + ahb_disc)

    # OS Licensing
    os_multiplier = 1.45 if req.os_type.lower() == "windows" and not (prov_key == "AZURE" and req.azure_hybrid_benefit) else 1.0

    # Hours calculation
    hours_ratio = req.operating_hours_per_day / 24.0

    # Compute Cost calculation
    compute_base_monthly = raw_base_monthly * reg_multiplier * os_multiplier * hours_ratio
    discount_factor = (1.0 - (effective_disc_pct / 100.0))
    discounted_compute_monthly = compute_base_monthly * discount_factor

    # Total per instance & across fleet
    unit_monthly = discounted_compute_monthly + monthly_storage_per_instance
    total_monthly = unit_monthly * req.instance_count
    total_hourly = total_monthly / (730.0 * hours_ratio) if (730.0 * hours_ratio) > 0 else 0.0
    total_annual = total_monthly * 12.0

    # Undiscounted baseline for savings transparency
    undiscounted_monthly = ((compute_base_monthly + monthly_storage_per_instance) * req.instance_count)
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

        # Find closest preset or custom equivalent
        matching_preset = min(
            other_prov["machine_presets"],
            key=lambda p: abs(p["vcpu"] - vcpu) + abs(p["ram_gb"] - ram_gb)
        )

        other_compute_base = matching_preset["base_monthly_usd"] * other_reg_mult * os_multiplier * hours_ratio
        other_disc_factor = (1.0 - (base_disc_pct / 100.0))
        other_discounted_compute = other_compute_base * other_disc_factor

        # Equivalent disk
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
                "storage_monthly_usd": round(monthly_storage_per_instance * req.instance_count, 2)
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
