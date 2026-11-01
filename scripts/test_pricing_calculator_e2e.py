"""
Abhi Cloud Tech — Comprehensive Hyperscaler Pricing Calculator Verification
Covers:
- Google Cloud Platform (GCP) Compute Engine & Persistent Disk
- Amazon Web Services (AWS) EC2 & EBS Storage
- Microsoft Azure Virtual Machines & Managed Disks
- Preset Standard Instance SKUs vs Custom Machine Types
- Multi-region tariffs and 1:1 Cross-Cloud Parity
"""

import sys
import io
import requests

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_calculator_e2e():
    print("=" * 75)
    print("  HYPERSCALER CLOUD PRICING CALCULATOR END-TO-END VERIFICATION")
    print("  GCP, AWS & Azure Interactive Pricing Engine")
    print("=" * 75)

    s = requests.Session()
    
    # 1. Authenticate
    login_res = s.post(f"{BASE_URL}/api/auth/login", json={"user_id": "abhishek", "password": "password123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] User Authentication successful (SuperAdmin)")

    # 2. Verify Catalog
    cat_res = s.get(f"{BASE_URL}/api/calculator/catalog", headers=headers)
    assert cat_res.status_code == 200
    cat = cat_res.json()
    assert "GCP" in cat and "AWS" in cat and "Azure" in cat
    print(f"[PASS] GET /api/calculator/catalog returned all 3 hyperscalers (GCP, AWS, Azure)")

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

    # 6. Azure VM Pricing: Standard_D4s_v5 + Premium SSD + Azure Hybrid Benefit
    azure_res = s.post(f"{BASE_URL}/api/calculator/estimate", json={
        "cloud_provider": "Azure",
        "region": "eastus",
        "provisioning_mode": "preset",
        "machine_sku": "Standard_D4s_v5",
        "storage_type": "premium-ssd",
        "storage_gb": 128.0,
        "os_type": "windows",
        "azure_hybrid_benefit": True
    }, headers=headers)
    assert azure_res.status_code == 200
    az_sel = azure_res.json()["selected_cloud"]
    assert az_sel["monthly_cost_usd"] > 0
    print(f"[PASS] Azure VM Test: {az_sel['machine_sku']} (AHB Windows) = ${az_sel['monthly_cost_usd']}/mo")

    # 7. Cross-Cloud 1:1 Parity Benchmark
    parity = gcp_res.json()["cross_cloud_parity"]
    assert "AWS" in parity and "Azure" in parity and "GCP" in parity
    print(f"[PASS] 1:1 Cross-Cloud Parity: GCP=${parity['GCP']['monthly_cost_usd']}/mo | AWS=${parity['AWS']['monthly_cost_usd']}/mo | Azure=${parity['Azure']['monthly_cost_usd']}/mo")

    # 8. Backward-compatible /api/simulate
    sim_res = s.post(f"{BASE_URL}/api/simulate", json={
        "cloud_provider": "AWS",
        "machine_family": "m6i",
        "region": "us-east-1",
        "vcpu_count": 16,
        "ram_gb": 64
    }, headers=headers)
    assert sim_res.status_code == 200
    print(f"[PASS] POST /api/simulate backward compatibility: Monthly=${sim_res.json()['monthly_cost_usd']}")

    print("\n" + "=" * 75)
    print("  ALL 8 HYPERSCALER PRICING CALCULATOR SUITES PASSED (100% GREEN)")
    print("=" * 75)

if __name__ == "__main__":
    test_calculator_e2e()
