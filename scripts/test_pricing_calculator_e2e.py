"""
Abhi Cloud Tech — Comprehensive Hyperscaler Pricing Calculator Verification
Covers:
- Google Cloud Platform (GCP) Compute Engine & Persistent Disk
- Amazon Web Services (AWS) EC2 & EBS Storage
- Microsoft Azure Virtual Machines, Managed Disks, Blob Storage, SQL DB, Cosmos DB & Networking
- Preset Standard Instance SKUs vs Custom Machine Types
- Multi-region tariffs and 1:1 Cross-Cloud Parity & Arbitrage
- Full Azure Machine Preset, Disk Tier, Savings Plan & Database Feature Verification
"""

import sys
import io
import requests

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_calculator_e2e():
    print("=" * 80)
    print("  HYPERSCALER CLOUD PRICING CALCULATOR END-TO-END VERIFICATION")
    print("  GCP, AWS & Microsoft Azure Comprehensive FinOps Intelligence Platform")
    print("=" * 80)

    s = requests.Session()
    
    # 1. Authenticate
    login_res = s.post(f"{BASE_URL}/api/auth/login", json={"user_id": "abhishek", "password": "password123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] User Authentication successful (SuperAdmin)")

    # 2. Verify Catalog Coverage for all 3 hyperscalers
    cat_res = s.get(f"{BASE_URL}/api/calculator/catalog", headers=headers)
    assert cat_res.status_code == 200
    cat = cat_res.json()
    assert "GCP" in cat and "AWS" in cat and "Azure" in cat
    az_cat = cat["Azure"]
    print(f"[PASS] GET /api/calculator/catalog returned all 3 hyperscalers (GCP, AWS, Azure)")

    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # SUITE AWS-A: Comprehensive Amazon Web Services (AWS) Machine Presets Audit
    # -------------------------------------------------------------------------
    aws_cat = cat["AWS"]
    aws_skus = {p["sku"]: p for p in aws_cat["machine_presets"]}

    # AWS-A1. Burstable / Micro (t4g & t3)
    required_burstable = [
        "t4g.nano", "t4g.micro", "t4g.small", "t4g.medium", "t4g.large", "t4g.xlarge",
        "t3.medium", "t3.xlarge"
    ]
    for sku in required_burstable:
        assert sku in aws_skus, f"Missing AWS Burstable machine preset: {sku}"
    print(f"[PASS] AWS Burstable / Micro Presets Verified: {', '.join(required_burstable)}")

    # AWS-A2. General Purpose (m6i, m6g, m7g)
    required_aws_gp = [
        "m6i.large", "m6i.xlarge", "m6i.2xlarge", "m6i.4xlarge", "m6i.8xlarge",
        "m6g.xlarge", "m7g.xlarge"
    ]
    for sku in required_aws_gp:
        assert sku in aws_skus, f"Missing AWS General Purpose machine preset: {sku}"
    print(f"[PASS] AWS General Purpose Presets Verified: {', '.join(required_aws_gp)}")

    # AWS-A3. Compute Optimized (c6i, c7g)
    required_aws_comp = [
        "c6i.large", "c6i.xlarge", "c6i.2xlarge", "c6i.4xlarge", "c7g.xlarge"
    ]
    for sku in required_aws_comp:
        assert sku in aws_skus, f"Missing AWS Compute Optimized machine preset: {sku}"
    print(f"[PASS] AWS Compute Optimized Presets Verified: {', '.join(required_aws_comp)}")

    # AWS-A4. Memory Optimized (r6i)
    required_aws_mem = [
        "r6i.large", "r6i.xlarge", "r6i.2xlarge", "r6i.4xlarge"
    ]
    for sku in required_aws_mem:
        assert sku in aws_skus, f"Missing AWS Memory Optimized machine preset: {sku}"
    print(f"[PASS] AWS Memory Optimized Presets Verified: {', '.join(required_aws_mem)}")

    # AWS-A5. GPU / Accelerated (g5, p4d)
    required_aws_gpu = [
        "g5.xlarge", "g5.2xlarge", "p4d.24xlarge"
    ]
    for sku in required_aws_gpu:
        assert sku in aws_skus, f"Missing AWS GPU/Accelerated machine preset: {sku}"
    print(f"[PASS] AWS GPU / Accelerated Presets Verified: {', '.join(required_aws_gpu)}")

    # -------------------------------------------------------------------------
    # SUITE AWS-B: AWS EBS & S3 Object Storage Tiers Verification
    # -------------------------------------------------------------------------
    aws_disks = aws_cat["storage_disk_types"]
    required_aws_storage = [
        ("gp3", 0.080),
        ("gp2", 0.100),
        ("io2", 0.125),
        ("st1", 0.045),
        ("sc1", 0.025),
        ("s3-standard", 0.023),
        ("s3-intelligent", 0.021),
        ("s3-glacier-flexible", 0.0036),
        ("s3-glacier-deep-archive", 0.00099)
    ]
    for disk_key, expected_rate in required_aws_storage:
        assert disk_key in aws_disks, f"Missing AWS storage tier: {disk_key}"
        assert abs(aws_disks[disk_key]["rate_per_gb_month"] - expected_rate) < 0.0001
    print(f"[PASS] AWS Storage Verified: gp3 ($0.08/GB), gp2, io2, st1, sc1 & S3 Tiers (Standard, Intelligent, Glacier, Deep Archive)")

    # -------------------------------------------------------------------------
    # SUITE AWS-C: AWS Commitment & Savings Plans Verification
    # -------------------------------------------------------------------------
    aws_commitments = aws_cat["commitment_discounts"]
    required_aws_commitments = [
        ("on_demand", 0.0),
        ("1yr_savings_plan", 28.0),
        ("3yr_savings_plan", 45.0),
        ("1yr_ri", 37.0),
        ("3yr_ri", 60.0),
        ("spot", 72.0)
    ]
    for comm_key, expected_discount in required_aws_commitments:
        assert comm_key in aws_commitments, f"Missing AWS commitment model: {comm_key}"
        assert aws_commitments[comm_key]["discount_pct"] == expected_discount
    print(f"[PASS] AWS Commitment Models Verified: On-Demand, 1-Yr/3-Yr Savings Plans (28%/45%), 1-Yr/3-Yr RIs (37%/60%) & Spot (72%)")

    # -------------------------------------------------------------------------
    # SUITE AWS-D: AWS Database, Storage & Networking Calculation APIs
    # -------------------------------------------------------------------------
    # AWS-D1: RDS Multi-AZ HA
    rds_res = s.post(f"{BASE_URL}/api/calculator/aws/database", json={
        "engine": "rds",
        "service_key": "rds_m6i_large_multiaz",
        "multi_az": True
    }, headers=headers)
    assert rds_res.status_code == 200
    rds_data = rds_res.json()
    assert rds_data["monthly_cost_usd"] == 259.88
    print(f"[PASS] AWS RDS Multi-AZ HA Test: {rds_data['name']} = ${rds_data['monthly_cost_usd']}/mo (${rds_data['hourly_usd']}/hr)")

    # AWS-D2: Aurora PostgreSQL Multi-AZ Enterprise
    aurora_res = s.post(f"{BASE_URL}/api/calculator/aws/database", json={
        "engine": "rds",
        "service_key": "aurora_postgresql",
        "multi_az": True
    }, headers=headers)
    assert aurora_res.status_code == 200
    aurora_data = aurora_res.json()
    assert aurora_data["monthly_cost_usd"] == 211.70
    print(f"[PASS] AWS Aurora PostgreSQL Test: {aurora_data['name']} = ${aurora_data['monthly_cost_usd']}/mo")

    # AWS-D3: DynamoDB Provisioned Capacity
    dynamo_prov = s.post(f"{BASE_URL}/api/calculator/aws/database", json={
        "engine": "dynamodb",
        "capacity_mode": "provisioned",
        "wcu": 100.0,
        "rcu": 200.0,
        "storage_gb": 50.0
    }, headers=headers)
    assert dynamo_prov.status_code == 200
    d_data = dynamo_prov.json()
    assert d_data["monthly_cost_usd"] > 0
    print(f"[PASS] AWS DynamoDB Provisioned Test: 100 WCU, 200 RCU, 50GB = ${d_data['monthly_cost_usd']}/mo")

    # AWS-D4: DynamoDB On-Demand Capacity
    dynamo_ondemand = s.post(f"{BASE_URL}/api/calculator/aws/database", json={
        "engine": "dynamodb",
        "capacity_mode": "on_demand",
        "million_writes": 20.0,
        "million_reads": 100.0,
        "storage_gb": 100.0
    }, headers=headers)
    assert dynamo_ondemand.status_code == 200
    d_od_data = dynamo_ondemand.json()
    assert d_od_data["monthly_cost_usd"] == 75.00
    print(f"[PASS] AWS DynamoDB On-Demand Test: 20M writes, 100M reads, 100GB = ${d_od_data['monthly_cost_usd']}/mo")

    # AWS-D5: AWS Internet Egress (First 100GB Free, $0.09/GB thereafter)
    egress_aws = s.post(f"{BASE_URL}/api/calculator/aws/networking", json={
        "egress_gb": 500.0
    }, headers=headers)
    assert egress_aws.status_code == 200
    eg_data = egress_aws.json()
    assert eg_data["free_gb"] == 100.0
    assert eg_data["billable_gb"] == 400.0
    assert eg_data["monthly_cost_usd"] == 36.00
    print(f"[PASS] AWS Internet Egress: 500 GB (100GB Free + 400GB @ $0.09/GB) = ${eg_data['monthly_cost_usd']}/mo")

    # AWS-D6: AWS EBS gp3 Volume with Provisioned IOPS & Throughput
    ebs_res = s.post(f"{BASE_URL}/api/calculator/aws/storage", json={
        "service": "ebs",
        "volume_type": "gp3",
        "size_gb": 200.0,
        "provisioned_iops": 5000,
        "throughput_mbps": 250
    }, headers=headers)
    assert ebs_res.status_code == 200
    ebs_data = ebs_res.json()
    assert ebs_data["monthly_cost_usd"] == 31.00
    print(f"[PASS] AWS EBS gp3 Test: 200GB + 5,000 IOPS + 250 MB/s = ${ebs_data['monthly_cost_usd']}/mo")

    # AWS-D7: AWS S3 Glacier Deep Archive
    s3_res = s.post(f"{BASE_URL}/api/calculator/aws/storage", json={
        "service": "s3",
        "tier": "s3-glacier-deep-archive",
        "size_gb": 10000.0
    }, headers=headers)
    assert s3_res.status_code == 200
    s3_data = s3_res.json()
    assert s3_data["monthly_cost_usd"] == 9.90
    print(f"[PASS] AWS S3 Glacier Deep Archive: 10,000 GB = ${s3_data['monthly_cost_usd']}/mo")

        # SUITE A: Comprehensive Microsoft Azure Machine Presets Audit
    # -------------------------------------------------------------------------
    az_skus = {p["sku"]: p for p in az_cat["machine_presets"]}
    
    # A1. General Purpose
    required_gp = [
        "Standard_B2s", "Standard_B4ms", 
        "Standard_D2s_v5", "Standard_D4s_v5", "Standard_D8s_v5", "Standard_D16s_v5", "Standard_D32s_v5"
    ]
    for sku in required_gp:
        assert sku in az_skus, f"Missing Azure GP machine preset: {sku}"
    print(f"[PASS] Azure GP Presets Verified: {', '.join(required_gp)}")

    # A2. Memory Optimized
    required_mem = ["Standard_E2s_v5", "Standard_E4s_v5", "Standard_E8s_v5", "Standard_E16s_v5"]
    for sku in required_mem:
        assert sku in az_skus, f"Missing Azure Memory Optimized machine preset: {sku}"
    print(f"[PASS] Azure Memory Optimized Presets Verified: {', '.join(required_mem)}")

    # A3. Compute Optimized
    required_comp = ["Standard_F4s_v2", "Standard_F8s_v2", "Standard_F16s_v2"]
    for sku in required_comp:
        assert sku in az_skus, f"Missing Azure Compute Optimized machine preset: {sku}"
    print(f"[PASS] Azure Compute Optimized Presets Verified: {', '.join(required_comp)}")

    # A4. GPU / AI Acceleration
    required_gpu = ["Standard_NC4as_T4_v3", "Standard_NC8as_T4_v3"]
    for sku in required_gpu:
        assert sku in az_skus, f"Missing Azure GPU/AI machine preset: {sku}"
    print(f"[PASS] Azure GPU/AI Acceleration Presets Verified: {', '.join(required_gpu)}")

    # -------------------------------------------------------------------------
    # SUITE B: Comprehensive Storage & Disks Verification
    # -------------------------------------------------------------------------
    az_disks = az_cat["storage_disk_types"]
    required_disks = [
        ("Standard_LRS", 0.040),
        ("StandardSSD_LRS", 0.075),
        ("Premium_LRS", 0.135),
        ("PremiumV2_LRS", 0.115),
        ("UltraSSD_LRS", 0.220),
        ("blob-hot", 0.018),
        ("blob-cool", 0.010),
        ("blob-cold", 0.0036),
        ("blob-archive", 0.00099)
    ]
    for disk_key, expected_rate in required_disks:
        assert disk_key in az_disks, f"Missing disk tier: {disk_key}"
        assert abs(az_disks[disk_key]["rate_per_gb_month"] - expected_rate) < 0.0001
    print(f"[PASS] Azure Disks & Storage Tiers Verified: HDD, SSD, Premium, Premium v2, Ultra & Blob Tiers (Hot/Cool/Cold/Archive)")

    # -------------------------------------------------------------------------
    # SUITE C: Commitment & Savings Plans Verification
    # -------------------------------------------------------------------------
    az_commitments = az_cat["commitment_discounts"]
    required_commitments = [
        ("on_demand", 0.0),
        ("1yr_savings_plan", 38.0),
        ("3yr_savings_plan", 56.0),
        ("1yr_ri", 42.0),
        ("3yr_ri", 62.0),
        ("spot", 80.0)
    ]
    for comm_key, expected_discount in required_commitments:
        assert comm_key in az_commitments, f"Missing commitment model: {comm_key}"
        assert az_commitments[comm_key]["discount_pct"] == expected_discount
    print(f"[PASS] Azure Commitment Models Verified: Pay-as-you-go, 1-Yr/3-Yr Savings Plans, 1-Yr/3-Yr RIs & Spot (80%)")

    # -------------------------------------------------------------------------
    # SUITE D: Baseline Hyperscaler Estimation Tests (GCP, AWS & Azure)
    # -------------------------------------------------------------------------
    # 3. Google Cloud Pricing: e2-standard-4 (4 vCPU, 16 GB RAM) + 100 GB pd-balanced in us-central1
    gcp_res = s.post(f"{BASE_URL}/api/calculator/estimate", json={
        "cloud_provider": "GCP",
        "region": "us-central1",
        "provisioning_mode": "preset",
        "machine_sku": "e2-standard-4",
        "storage_type": "pd-balanced",
        "storage_gb": 100.0,
        "instance_count": 1,
        "operating_hours_per_day": 24,
        "commitment": "on_demand"
    }, headers=headers)
    assert gcp_res.status_code == 200
    gcp_data = gcp_res.json()
    sel = gcp_data["selected_cloud"]
    assert sel["monthly_cost_usd"] == 107.85
    assert sel["breakdown"]["compute_monthly_usd"] == 97.85
    assert sel["breakdown"]["storage_monthly_usd"] == 10.00
    print(f"[PASS] GCP Preset Test: {sel['machine_sku']} in {sel['region_name']} = ${sel['monthly_cost_usd']}/mo (${sel['hourly_cost_usd']}/hr)")

    # 4. Google Cloud Custom Machine Type: 6 vCPU, 24 GB RAM + 250 GB pd-ssd + 1-Year CUD
    gcp_custom = s.post(f"{BASE_URL}/api/calculator/estimate", json={
        "cloud_provider": "GCP",
        "region": "us-central1",
        "provisioning_mode": "custom",
        "custom_vcpu": 6.0,
        "custom_ram_gb": 24.0,
        "storage_type": "pd-ssd",
        "storage_gb": 250.0,
        "commitment": "1yr_commitment"
    }, headers=headers)
    assert gcp_custom.status_code == 200
    c_sel = gcp_custom.json()["selected_cloud"]
    assert c_sel["monthly_cost_usd"] > 0
    assert c_sel["commitment_discount_pct"] == 37.0
    print(f"[PASS] GCP Custom VM: {c_sel['machine_sku']} with 1-Yr CUD = ${c_sel['monthly_cost_usd']}/mo (Saved ${c_sel['discount_savings_monthly_usd']}/mo)")

    # 5. AWS EC2 Pricing: m6i.xlarge + gp3 in us-east-1
    aws_res = s.post(f"{BASE_URL}/api/calculator/estimate", json={
        "cloud_provider": "AWS",
        "region": "us-east-1",
        "provisioning_mode": "preset",
        "machine_sku": "m6i.xlarge",
        "storage_type": "gp3",
        "storage_gb": 100.0,
        "commitment": "1yr_commitment"
    }, headers=headers)
    assert aws_res.status_code == 200
    aws_sel = aws_res.json()["selected_cloud"]
    assert aws_sel["monthly_cost_usd"] > 0
    print(f"[PASS] AWS EC2 Test: {aws_sel['machine_sku']} in {aws_sel['region_name']} = ${aws_sel['monthly_cost_usd']}/mo")

    # 6. Azure VM Pricing: Standard_D4s_v5 + Premium SSD + Azure Hybrid Benefit Windows
    azure_res = s.post(f"{BASE_URL}/api/calculator/estimate", json={
        "cloud_provider": "Azure",
        "region": "eastus",
        "provisioning_mode": "preset",
        "machine_sku": "Standard_D4s_v5",
        "storage_type": "Premium_LRS",
        "storage_gb": 128.0,
        "os_type": "windows",
        "azure_hybrid_benefit": True
    }, headers=headers)
    assert azure_res.status_code == 200
    az_sel = azure_res.json()["selected_cloud"]
    assert az_sel["provider_key"] == "Azure"
    assert az_sel["machine_sku"] == "Standard_D4s_v5"
    assert az_sel["monthly_cost_usd"] > 0
    assert az_sel["commitment_discount_pct"] >= 48.0 # AHB 48% discount applied
    print(f"[PASS] Azure VM Test: {az_sel['machine_sku']} (AHB Windows) = ${az_sel['monthly_cost_usd']}/mo")

    # 7. Azure Spot VM Test with 80% discount
    az_spot_res = s.post(f"{BASE_URL}/api/calculator/estimate", json={
        "cloud_provider": "Azure",
        "region": "eastus",
        "provisioning_mode": "preset",
        "machine_sku": "Standard_D8s_v5",
        "storage_type": "PremiumV2_LRS",
        "storage_gb": 200.0,
        "commitment": "spot"
    }, headers=headers)
    assert az_spot_res.status_code == 200
    az_spot_sel = az_spot_res.json()["selected_cloud"]
    assert az_spot_sel["commitment_discount_pct"] == 80.0
    print(f"[PASS] Azure Spot Test: {az_spot_sel['machine_sku']} with Spot (80% off) = ${az_spot_sel['monthly_cost_usd']}/mo (Saved ${az_spot_sel['discount_savings_monthly_usd']}/mo)")

    # 8. Azure Hybrid Benefit Linux (AHBL) Test
    az_ahbl_res = s.post(f"{BASE_URL}/api/calculator/estimate", json={
        "cloud_provider": "Azure",
        "region": "eastus",
        "provisioning_mode": "preset",
        "machine_sku": "Standard_E8s_v5",
        "storage_type": "Premium_LRS",
        "storage_gb": 256.0,
        "os_type": "linux",
        "azure_hybrid_benefit_linux": True
    }, headers=headers)
    assert az_ahbl_res.status_code == 200
    az_ahbl_sel = az_ahbl_res.json()["selected_cloud"]
    assert az_ahbl_sel["commitment_discount_pct"] == 18.0
    print(f"[PASS] Azure Hybrid Benefit Linux (AHBL): {az_ahbl_sel['machine_sku']} = ${az_ahbl_sel['monthly_cost_usd']}/mo (18% discount)")

    # -------------------------------------------------------------------------
    # SUITE E: Database & Networking Tests
    # -------------------------------------------------------------------------
    # E1. Azure SQL Database (vCore Gen5 Model)
    sql_res = s.post(f"{BASE_URL}/api/calculator/azure/database", json={
        "engine": "sql_vcore",
        "model": "vCore",
        "vcore_count": 4.0,
        "storage_gb": 250.0,
        "commitment": "1yr_ri",
        "azure_hybrid_benefit": True
    }, headers=headers)
    assert sql_res.status_code == 200
    sql_data = sql_res.json()
    assert sql_data["vcore_count"] == 4.0
    assert sql_data["monthly_cost_usd"] > 0
    print(f"[PASS] Azure SQL Database (vCore Gen5): 4 vCore + 250GB storage (1-Yr RI + AHB) = ${sql_data['monthly_cost_usd']}/mo")

    # E2. Azure SQL Database (DTU Model)
    dtu_res = s.post(f"{BASE_URL}/api/calculator/azure/database", json={
        "engine": "sql_dtu",
        "model": "DTU",
        "dtu_count": 200.0,
        "storage_gb": 100.0,
        "commitment": "1yr_ri"
    }, headers=headers)
    assert dtu_res.status_code == 200
    dtu_data = dtu_res.json()
    assert dtu_data["dtu_count"] == 200.0
    print(f"[PASS] Azure SQL Database (DTU Model): 200 DTU + 100GB storage = ${dtu_data['monthly_cost_usd']}/mo")

    # E3. Azure Cosmos DB (Provisioned RU/s)
    cosmos_res = s.post(f"{BASE_URL}/api/calculator/azure/database", json={
        "engine": "cosmos_ru",
        "capacity_mode": "provisioned",
        "provisioned_ru": 1000.0,
        "storage_gb": 100.0
    }, headers=headers)
    assert cosmos_res.status_code == 200
    cosmos_data = cosmos_res.json()
    assert cosmos_data["provisioned_ru_per_sec"] == 1000.0
    print(f"[PASS] Azure Cosmos DB (Provisioned): 1,000 RU/s + 100GB = ${cosmos_data['monthly_cost_usd']}/mo")

    # E4. Azure Cosmos DB (Serverless)
    cosmos_srv_res = s.post(f"{BASE_URL}/api/calculator/azure/database", json={
        "engine": "cosmos_serverless",
        "capacity_mode": "serverless",
        "serverless_million_ru": 25.0,
        "storage_gb": 50.0
    }, headers=headers)
    assert cosmos_srv_res.status_code == 200
    cosmos_srv_data = cosmos_srv_res.json()
    assert cosmos_srv_data["million_ru_month"] == 25.0
    print(f"[PASS] Azure Cosmos DB (Serverless): 25M RU/mo + 50GB = ${cosmos_srv_data['monthly_cost_usd']}/mo")

    # E5. Azure Egress Networking (First 100GB Free)
    egress_res = s.post(f"{BASE_URL}/api/calculator/azure/networking", json={
        "egress_gb": 500.0,
        "egress_type": "internet"
    }, headers=headers)
    assert egress_res.status_code == 200
    egress_data = egress_res.json()
    assert egress_data["free_gb"] == 100.0
    assert egress_data["billable_gb"] == 400.0
    expected_egress_cost = round(400.0 * 0.087, 2)
    assert egress_data["monthly_cost_usd"] == expected_egress_cost
    print(f"[PASS] Azure Internet Egress: 500 GB (100GB Free + 400GB billable @ $0.087/GB) = ${egress_data['monthly_cost_usd']}/mo")

    # -------------------------------------------------------------------------
    # SUITE F: 1:1 Cross-Cloud Parity & Arbitrage
    # -------------------------------------------------------------------------
    parity = gcp_res.json()["cross_cloud_parity"]
    assert "AWS" in parity and "Azure" in parity and "GCP" in parity
    print(f"[PASS] 1:1 Cross-Cloud Parity: GCP=${parity['GCP']['monthly_cost_usd']}/mo | AWS=${parity['AWS']['monthly_cost_usd']}/mo | Azure=${parity['Azure']['monthly_cost_usd']}/mo")

    # -------------------------------------------------------------------------
    # SUITE G: Backward-compatible /api/simulate for Azure Workloads
    # -------------------------------------------------------------------------
    sim_az_res = s.post(f"{BASE_URL}/api/simulate", json={
        "cloud_provider": "Azure",
        "machine_family": "Standard_Dsv5",
        "region": "eastus",
        "vcpu_count": 8,
        "ram_gb": 32,
        "downsize_pct": 50.0
    }, headers=headers)
    assert sim_az_res.status_code == 200
    sim_az = sim_az_res.json()
    assert sim_az["cloud_provider"] == "Azure"
    assert sim_az["instance_sku"] == "Standard_D8s_v5"
    assert sim_az["monthly_cost_usd"] > 0
    assert sim_az["potential_monthly_savings_usd"] == round(sim_az["monthly_cost_usd"] * 0.5, 2)
    print(f"[PASS] POST /api/simulate Azure Workload: {sim_az['instance_sku']} = ${sim_az['monthly_cost_usd']}/mo (Right-sizing 50% = -${sim_az['potential_monthly_savings_usd']}/mo)")

    # AWS backward compatibility check
    sim_res = s.post(f"{BASE_URL}/api/simulate", json={
        "cloud_provider": "AWS",
        "machine_family": "m6i",
        "region": "us-east-1",
        "vcpu_count": 16,
        "ram_gb": 64
    }, headers=headers)
    assert sim_res.status_code == 200
    print(f"[PASS] POST /api/simulate AWS backward compatibility: Monthly=${sim_res.json()['monthly_cost_usd']}")

    print("\n" + "=" * 80)
    print("  ALL HYPERSCALER PRICING CALCULATOR SUITES PASSED (100% GREEN)")
    print("  MICROSOFT AZURE COMPREHENSIVELY COVERED & AUDITED")
    print("=" * 80)

if __name__ == "__main__":
    test_calculator_e2e()
