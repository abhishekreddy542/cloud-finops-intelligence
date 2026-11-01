import os
import sys
import io
import json
import requests
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"

def test_full_application_functionality():
    print("=" * 75)
    print("  COMPREHENSIVE BUTTON & API FUNCTIONALITY TEST SUITE")
    print("  Abhi Cloud Tech — Enterprise FinOps Control Plane")
    print("=" * 75)

    s = requests.Session()
    total_tests = 0
    passed_tests = 0

    def check(title, status_ok, details=""):
        nonlocal total_tests, passed_tests
        total_tests += 1
        if status_ok:
            passed_tests += 1
            print(f"  [✓ PASS] {title:<48} {details}")
        else:
            print(f"  [✗ FAIL] {title:<48} {details}")

    # 1. AUTHENTICATION
    print("\n--- 1. Authentication & Session Security ---")
    login_res = s.post(f"{BASE_URL}/api/auth/login", json={"user_id": "abhishek", "password": "password123"})
    check("POST /api/auth/login (Valid User)", login_res.status_code == 200, f"Status: {login_res.status_code}")
    token = login_res.json().get("token", "")
    headers = {"Authorization": f"Bearer {token}"}

    sess_res = s.get(f"{BASE_URL}/api/auth/session", headers=headers)
    check("GET /api/auth/session (Session Token)", sess_res.status_code == 200, f"Role: {sess_res.json().get('user', {}).get('role_badge')}")

    # 2. EXECUTIVE COMMAND & KPIS
    print("\n--- 2. Executive Command & Overview KPIs ---")
    kpi_res = s.get(f"{BASE_URL}/api/kpis", headers=headers)
    check("GET /api/kpis (All Providers)", kpi_res.status_code == 200, f"Total Spend: ${kpi_res.json().get('total_spend_ytd', 0):,.2f}")
    kpi_data = kpi_res.json()
    check("KPI Waste Calculation Valid", kpi_data.get("anomalous_waste_usd", 0) > 0, f"Waste: ${kpi_data.get('anomalous_waste_usd', 0):,.2f}")
    check("KPI Maturity Stage Valid", kpi_data.get("finops_maturity_score", 0) > 0, f"Score: {kpi_data.get('finops_maturity_score')}/100")

    # 3. SPEND TRENDS & ANOMALIES
    print("\n--- 3. Spend Trends & Multi-Cloud Trajectory ---")
    trends_res = s.get(f"{BASE_URL}/api/trends", headers=headers)
    check("GET /api/trends (Trajectory & Donut)", trends_res.status_code == 200, f"History: {len(trends_res.json().get('dates', []))} days")
    trends_data = trends_res.json()
    pb_list = trends_data.get("provider_breakdown", [])
    pb_providers = [p.get("CloudProvider") if isinstance(p, dict) else p for p in pb_list]
    check("Provider Breakdown Present", "AWS" in pb_providers, f"Providers: {pb_providers}")

    # 4. DEPARTMENT ANALYTICS
    print("\n--- 4. Cost Analytics & Department Breakdown ---")
    dept_res = s.get(f"{BASE_URL}/api/departments", headers=headers)
    check("GET /api/departments (Cost Centers)", dept_res.status_code == 200, f"Depts: {len(dept_res.json().get('department_spend', []))}")

    # 5. ANOMALY DETECTION RADAR & FILTERS
    print("\n--- 5. Anomaly Detection Radar & Severity Filtering ---")
    anom_all = s.get(f"{BASE_URL}/api/anomalies?severity=ALL", headers=headers)
    check("GET /api/anomalies (Severity ALL)", anom_all.status_code == 200, f"Count: {len(anom_all.json())}")
    
    anom_crit = s.get(f"{BASE_URL}/api/anomalies?severity=CRITICAL", headers=headers)
    check("GET /api/anomalies (Severity CRITICAL)", anom_crit.status_code == 200, f"Critical: {len(anom_crit.json())}")

    anom_aws = s.get(f"{BASE_URL}/api/anomalies?providers=AWS&severity=ALL", headers=headers)
    check("GET /api/anomalies (Platform AWS filter)", anom_aws.status_code == 200, f"AWS Anomalies: {len(anom_aws.json())}")

    # 6. SPEND FORECASTING SCENARIO LEVERS
    print("\n--- 6. Budget Forecaster & Scenario Levers ---")
    fore_30 = s.post(f"{BASE_URL}/api/forecast", headers=headers, json={"horizon_days": 30, "workload_growth_pct": 0.0, "finops_savings_pct": 0.0})
    check("POST /api/forecast (30d Baseline)", fore_30.status_code == 200, f"Forecast Days: {len(fore_30.json().get('forecast', []))}")

    fore_growth = s.post(f"{BASE_URL}/api/forecast", headers=headers, json={"horizon_days": 60, "workload_growth_pct": 25.0, "finops_savings_pct": 15.0})
    check("POST /api/forecast (Growth +25%, Savings -15%)", fore_growth.status_code == 200, f"Projected Spend: ${fore_growth.json().get('projected_total_usd', 0):,.2f}")

    # 7. RIGHTSIZING & WORKLOAD SIMULATION (CRITICAL TEST!)
    print("\n--- 7. Rightsizing Engine & Workload Unit Economics ---")
    # Test AWS simulation
    sim_aws = s.post(f"{BASE_URL}/api/simulate", headers=headers, json={
        "cloud_provider": "AWS",
        "machine_family": "m6i",
        "region": "us-east-1",
        "vcpu_count": 32,
        "ram_gb": 128,
        "daily_hours": 24,
        "downsize_pct": 50.0
    })
    check("POST /api/simulate (AWS m6i.8xlarge)", sim_aws.status_code == 200, f"Monthly: ${sim_aws.json().get('monthly_cost_usd', 0):,.2f} | Savings: ${sim_aws.json().get('potential_monthly_savings_usd', 0):,.2f}")
    aws_res_json = sim_aws.json()
    check("AWS Instance SKU Resolved", aws_res_json.get("instance_sku") == "m6i.8xlarge", f"SKU: {aws_res_json.get('instance_sku')}")
    check("AWS Projected ROI Calculated", aws_res_json.get("potential_annual_savings_usd", 0) > 0, f"Annual ROI: ${aws_res_json.get('potential_annual_savings_usd', 0):,.2f}")

    # Test Azure simulation
    sim_azure = s.post(f"{BASE_URL}/api/simulate", headers=headers, json={
        "cloud_provider": "Azure",
        "machine_family": "Standard_Dsv5",
        "region": "eastus",
        "vcpu_count": 16,
        "ram_gb": 64,
        "daily_hours": 18,
        "downsize_pct": 40.0
    })
    check("POST /api/simulate (Azure Standard_D16s_v5)", sim_azure.status_code == 200, f"Monthly: ${sim_azure.json().get('monthly_cost_usd', 0):,.2f} | Savings: ${sim_azure.json().get('potential_monthly_savings_usd', 0):,.2f}")

    # Test GCP simulation
    sim_gcp = s.post(f"{BASE_URL}/api/simulate", headers=headers, json={
        "cloud_provider": "GCP",
        "machine_family": "n2",
        "region": "us-central1",
        "vcpu_count": 8,
        "ram_gb": 32,
        "daily_hours": 24,
        "downsize_pct": 50.0
    })
    check("POST /api/simulate (GCP n2-standard-8)", sim_gcp.status_code == 200, f"Monthly: ${sim_gcp.json().get('monthly_cost_usd', 0):,.2f} | Savings: ${sim_gcp.json().get('potential_monthly_savings_usd', 0):,.2f}")

    # Test Optimizer recommendations
    opt_res = s.get(f"{BASE_URL}/api/optimizer", headers=headers)
    check("GET /api/optimizer (Action Matrix Table)", opt_res.status_code == 200, f"Actions: {len(opt_res.json().get('action_matrix', []))}")
    opt_data = opt_res.json()
    check("Optimization Pillars Portfolio Generated", "Right_Sizing_Savings_USD" in opt_data.get("portfolio", {}) or "rightsizings" in opt_data.get("portfolio", {}), f"Pillars: {list(opt_data.get('portfolio', {}).keys())}")

    # 8. DATA INGESTION & DATASET REVERT
    print("\n--- 8. Data Ingestion, Reset & Cloud Connectors ---")
    st_res = s.get(f"{BASE_URL}/api/dataset/status", headers=headers)
    check("GET /api/dataset/status (Source Info)", st_res.status_code == 200, f"Source: {st_res.json().get('source_info', {}).get('name')}")

    # Test 1-click sample loading
    sample_gcp = s.post(f"{BASE_URL}/api/dataset/sample/gcp", headers=headers)
    check("POST /api/dataset/sample/gcp (Ingest GCP)", sample_gcp.status_code == 200, f"Rows: {sample_gcp.json().get('records_processed', 0):,}")

    # Test Revert to Warehouse
    reset_res = s.post(f"{BASE_URL}/api/dataset/reset", headers=headers)
    check("POST /api/dataset/reset (Revert to 32k)", reset_res.status_code == 200, f"Restored: {reset_res.json().get('records', 0):,} records")

    # Verify status after revert
    st_after = s.get(f"{BASE_URL}/api/dataset/status", headers=headers).json()
    check("Status Confirms Production Warehouse", st_after.get("is_custom_dataset") is False, f"Records: {st_after.get('source_info', {}).get('records'):,}")

    # Test Cloud Connector configuration
    conn_res = s.post(f"{BASE_URL}/api/connectors/cloud", headers=headers, json={
        "connector_type": "Azure",
        "config": {"storage_account": "enterprisecost2025", "container": "finops-exports"}
    })
    check("POST /api/connectors/cloud (Azure Connector)", conn_res.status_code == 200, f"Status: {conn_res.json().get('connector', {}).get('status')}")

    # 9. SUMMARY VERDICT
    print("\n" + "=" * 75)
    print(f"  TOTAL FUNCTIONALITY TESTS: {total_tests}")
    print(f"  PASSED:                     {passed_tests} / {total_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"  FAILED:                     {total_tests - passed_tests} / {total_tests}")
    print("=" * 75)

    return total_tests - passed_tests

if __name__ == "__main__":
    fails = test_full_application_functionality()
    sys.exit(fails)
