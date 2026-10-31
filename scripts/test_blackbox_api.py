import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import time
import json
import traceback
from fastapi.testclient import TestClient
from backend.main import app, TEST_TOKEN

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {TEST_TOKEN}"}

def run_tests():
    results = []
    
    def test_case(category, test_id, description, method, url, json_body=None, expected_status=200, headers=AUTH_HEADERS, custom_assert=None):
        t0 = time.perf_counter()
        try:
            if method == "GET":
                resp = client.get(url, headers=headers)
            elif method == "POST":
                resp = client.post(url, json=json_body, headers=headers)
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            
            passed = resp.status_code == expected_status
            if passed and custom_assert:
                passed = bool(custom_assert(resp))
                
            data = None
            try:
                data = resp.json()
            except Exception:
                data = resp.text
                
            results.append({
                "category": category,
                "id": test_id,
                "description": description,
                "method": method,
                "url": url,
                "status_code": resp.status_code,
                "expected_status": expected_status,
                "passed": passed,
                "elapsed_ms": elapsed_ms,
                "response_preview": str(data)[:200]
            })
            print(f"[{'PASS' if passed else 'FAIL'}] {test_id}: {description} (HTTP {resp.status_code}, {elapsed_ms}ms)")
            return resp, data
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            results.append({
                "category": category,
                "id": test_id,
                "description": description,
                "method": method,
                "url": url,
                "status_code": "ERROR",
                "expected_status": expected_status,
                "passed": False,
                "elapsed_ms": elapsed_ms,
                "response_preview": f"Exception: {str(e)}"
            })
            print(f"[FAIL] {test_id}: {description} - Exception: {e}")
            return None, None

    print("=================================================================")
    print(" 1. DEVSECOPS SECURITY & AUTHENTICATION ENFORCEMENT VERIFICATION")
    print("=================================================================")
    # Unauthenticated attempts to protected endpoints must be rejected with HTTP 401
    test_case("Security", "TC-SEC-01", "Unauthenticated access to /api/kpis (expects 401)", "GET", "/api/kpis",
              headers=None, expected_status=401)
    test_case("Security", "TC-SEC-02", "Invalid bearer token to /api/kpis (expects 401)", "GET", "/api/kpis",
              headers={"Authorization": "Bearer invalid_malicious_token_123"}, expected_status=401)
    test_case("Security", "TC-SEC-03", "Malformed Authorization header (expects 401)", "GET", "/api/kpis",
              headers={"Authorization": "Basic not_a_bearer_token"}, expected_status=401)
    test_case("Security", "TC-SEC-04", "Unauthenticated access to /api/warehouse/health (expects 401)", "GET", "/api/warehouse/health",
              headers=None, expected_status=401)
    test_case("Security", "TC-SEC-05", "Unauthenticated access to /api/auth/session (expects 401)", "GET", "/api/auth/session",
              headers=None, expected_status=401)
    test_case("Security", "TC-SEC-06", "Authenticated access to /api/kpis with valid Bearer token", "GET", "/api/kpis",
              headers=AUTH_HEADERS, expected_status=200)
    test_case("Security", "TC-SEC-07", "Verify HTTP Security Headers (X-Frame-Options, CSP, nosniff)", "GET", "/",
              headers=None, expected_status=200,
              custom_assert=lambda r: "x-frame-options" in r.headers and "x-content-type-options" in r.headers and "content-security-policy" in r.headers)

    print("\n=================================================================")
    print(" 2. AUTHENTICATION & USER MANAGEMENT FLOWS")
    print("=================================================================")
    test_case("Auth", "TC-AUTH-01", "Get authenticated enterprise IAM session", "GET", "/api/auth/session",
              headers=AUTH_HEADERS, expected_status=200)
    test_case("Auth", "TC-AUTH-02", "Login with valid credentials (abhishek:password123)", "POST", "/api/auth/login",
              {"user_id": "abhishek", "password": "password123"}, headers=None, expected_status=200)
    test_case("Auth", "TC-AUTH-03", "Login with invalid password (expects 401)", "POST", "/api/auth/login",
              {"user_id": "abhishek", "password": "wrong_password"}, headers=None, expected_status=401)
    test_case("Auth", "TC-AUTH-04", "Signup with new compliant credentials (>=8 char pwd)", "POST", "/api/auth/signup",
              {"user_id": f"analyst_{int(time.time())}", "password": "SecurePassword2026!", "full_name": "Cloud Cost Analyst"},
              headers=None, expected_status=200)
    test_case("Auth", "TC-AUTH-05", "Signup with short password < 8 chars (expects 422)", "POST", "/api/auth/signup",
              {"user_id": f"short_{int(time.time())}", "password": "1234", "full_name": "Short Pwd"},
              headers=None, expected_status=422)
    test_case("Auth", "TC-AUTH-06", "Signup with existing user ID (expects 400)", "POST", "/api/auth/signup",
              {"user_id": "abhishek", "password": "SecurePassword2026!"}, headers=None, expected_status=400)

    # Login with admin to get an ephemeral session token to test logout without invalidating global test token
    ephemeral_login = client.post("/api/auth/login", json={"user_id": "admin", "password": "admin123"})
    ephemeral_token = ephemeral_login.json().get("token")
    test_case("Auth", "TC-AUTH-07", "Logout active session (ephemeral token)", "POST", "/api/auth/logout",
              headers={"Authorization": f"Bearer {ephemeral_token}"}, expected_status=200)

    print("\n=================================================================")
    print(" 3. BASELINE VALID OPERATIONAL ENDPOINTS")
    print("=================================================================")
    test_case("Meta", "TC-META-01", "Get filter metadata", "GET", "/api/meta/filters")
    test_case("Meta", "TC-META-02", "Get cloud catalog (public metadata)", "GET", "/api/meta/catalog", headers=None)
    test_case("Core", "TC-KPI-01", "Get default KPIs", "GET", "/api/kpis")
    test_case("Core", "TC-TRND-01", "Get default Trends", "GET", "/api/trends")
    test_case("Core", "TC-DEPT-01", "Get default Department analytics", "GET", "/api/departments")
    test_case("Core", "TC-ANOM-01", "Get default Anomalies", "GET", "/api/anomalies")
    test_case("Core", "TC-ANOM-02", "Get Critical Anomalies", "GET", "/api/anomalies?severity=CRITICAL")
    test_case("Core", "TC-ANOM-03", "Get High Anomalies", "GET", "/api/anomalies?severity=HIGH")
    test_case("Core", "TC-ANOM-04", "Get Medium Anomalies", "GET", "/api/anomalies?severity=MEDIUM")
    test_case("Core", "TC-FCST-01", "Generate default forecast (60d)", "POST", "/api/forecast", 
              {"horizon_days": 60, "workload_growth_pct": 15.0, "finops_savings_pct": 10.0})
    test_case("Core", "TC-OPT-01", "Get default Optimizer recommendations", "GET", "/api/optimizer")
    test_case("Core", "TC-SIM-01", "Simulate AWS us-east-1 workload", "POST", "/api/simulate",
              {"cloud_provider": "AWS", "region": "us-east-1", "vcpu_count": 32, "ram_gb": 128, "daily_hours": 24, "downsize_pct": 50.0})
    test_case("Core", "TC-SIM-02", "Simulate Azure eastus workload", "POST", "/api/simulate",
              {"cloud_provider": "Azure", "region": "eastus", "vcpu_count": 16, "ram_gb": 64, "daily_hours": 24, "downsize_pct": 30.0})
    test_case("Core", "TC-SIM-03", "Simulate GCP europe-west3 workload", "POST", "/api/simulate",
              {"cloud_provider": "GCP", "region": "europe-west3", "vcpu_count": 64, "ram_gb": 256, "daily_hours": 12, "downsize_pct": 50.0})
    test_case("Core", "TC-SIM-04", "Simulate AWS with m6g Graviton2 ARM family", "POST", "/api/simulate",
              {"cloud_provider": "AWS", "machine_family": "m6g", "region": "us-east-1", "vcpu_count": 32, "ram_gb": 128, "daily_hours": 24, "downsize_pct": 50.0})
    test_case("Core", "TC-SIM-05", "Simulate GCP with e2 Cost-Optimized machine type", "POST", "/api/simulate",
              {"cloud_provider": "GCP", "machine_family": "e2", "region": "us-central1", "vcpu_count": 32, "ram_gb": 128, "daily_hours": 24, "downsize_pct": 50.0})
    test_case("Core", "TC-SIM-06", "Simulate Azure with Standard_B burstable family", "POST", "/api/simulate",
              {"cloud_provider": "Azure", "machine_family": "Standard_B", "region": "eastus", "vcpu_count": 16, "ram_gb": 64, "daily_hours": 24, "downsize_pct": 50.0})

    print("\n=================================================================")
    print(" 4. FILTER COMBINATIONS & QUERY ARGS TESTING")
    print("=================================================================")
    test_case("Filtering", "TC-FILT-01", "KPIs with single provider (AWS)", "GET", "/api/kpis?providers=AWS")
    test_case("Filtering", "TC-FILT-02", "KPIs with multi-provider (AWS & Azure)", "GET", "/api/kpis?providers=AWS&providers=Azure")
    test_case("Filtering", "TC-FILT-03", "KPIs with single department", "GET", "/api/kpis?departments=Platform%20Engineering")
    test_case("Filtering", "TC-FILT-04", "Trends with multi-provider & multi-department", "GET", 
              "/api/trends?providers=AWS&providers=GCP&departments=Platform%20Engineering&departments=Data%20Science%20%26%20AI")
    test_case("Filtering", "TC-FILT-05", "Optimizer with provider filter", "GET", "/api/optimizer?providers=Azure")

    print("\n=================================================================")
    print(" 5. INVALID INPUTS, OUT-OF-RANGE & EDGE CASES")
    print("=================================================================")
    test_case("Edge", "TC-EDGE-01", "KPIs with non-existent provider (empty dataset)", "GET", "/api/kpis?providers=NonExistentCloud")
    test_case("Edge", "TC-EDGE-02", "Trends with non-existent department", "GET", "/api/trends?departments=NonExistentDept")
    test_case("Edge", "TC-EDGE-03", "Anomalies with invalid severity", "GET", "/api/anomalies?severity=NON_EXISTENT_SEVERITY")
    test_case("Validation", "TC-EDGE-04", "Forecast with zero horizon days (expects 422)", "POST", "/api/forecast", 
              {"horizon_days": 0, "workload_growth_pct": 10.0, "finops_savings_pct": 5.0}, expected_status=422)
    test_case("Validation", "TC-EDGE-05", "Forecast with negative horizon days (expects 422)", "POST", "/api/forecast", 
              {"horizon_days": -10, "workload_growth_pct": 10.0, "finops_savings_pct": 5.0}, expected_status=422)
    test_case("Validation", "TC-EDGE-06", "Forecast with >180 horizon days (DoS protection expects 422)", "POST", "/api/forecast", 
              {"horizon_days": 500, "workload_growth_pct": 10.0, "finops_savings_pct": 5.0}, expected_status=422)
    test_case("Boundary", "TC-EDGE-07", "Forecast with boundary horizon 1 day (expects 200)", "POST", "/api/forecast", 
              {"horizon_days": 1, "workload_growth_pct": 10.0, "finops_savings_pct": 5.0}, expected_status=200)
    test_case("Edge", "TC-EDGE-08", "Forecast with empty JSON body (uses defaults)", "POST", "/api/forecast", {}, expected_status=200)
    test_case("Validation", "TC-VAL-01", "Forecast with invalid data type for horizon_days (string)", "POST", "/api/forecast", 
              {"horizon_days": "not-a-number"}, expected_status=422)
    test_case("Edge", "TC-SIM-EDGE-01", "Simulate with unknown cloud provider (fallback logic)", "POST", "/api/simulate",
              {"cloud_provider": "Alibaba", "region": "cn-hangzhou", "vcpu_count": 16, "ram_gb": 64, "daily_hours": 24, "downsize_pct": 50.0})
    test_case("Edge", "TC-SIM-EDGE-02", "Simulate with unknown region in AWS (fallback logic)", "POST", "/api/simulate",
              {"cloud_provider": "AWS", "region": "mars-colony-1", "vcpu_count": 8, "ram_gb": 32, "daily_hours": 24, "downsize_pct": 50.0})
    test_case("Edge", "TC-SIM-EDGE-03", "Simulate with 0 daily hours", "POST", "/api/simulate",
              {"cloud_provider": "AWS", "region": "us-east-1", "vcpu_count": 16, "ram_gb": 64, "daily_hours": 0, "downsize_pct": 50.0})
    test_case("Edge", "TC-SIM-EDGE-04", "Simulate with 100% downsize", "POST", "/api/simulate",
              {"cloud_provider": "Azure", "region": "eastus", "vcpu_count": 32, "ram_gb": 128, "daily_hours": 24, "downsize_pct": 100.0})
    test_case("Validation", "TC-VAL-02", "Simulate with invalid type for vcpu_count", "POST", "/api/simulate",
              {"vcpu_count": "many_cores"}, expected_status=422)
    test_case("Validation", "TC-VAL-03", "Simulate with 0 vcpu_count (out of bounds < 1)", "POST", "/api/simulate",
              {"vcpu_count": 0}, expected_status=422)
    test_case("Validation", "TC-VAL-04", "Simulate with daily_hours > 24 (out of bounds)", "POST", "/api/simulate",
              {"daily_hours": 25}, expected_status=422)
    test_case("Validation", "TC-VAL-05", "Simulate with downsize_pct > 100 (out of bounds)", "POST", "/api/simulate",
              {"downsize_pct": 150.0}, expected_status=422)
    test_case("Edge", "TC-SIM-EDGE-05", "Simulate with empty payload (defaults)", "POST", "/api/simulate", {}, expected_status=200)

    print("\n=================================================================")
    print(" 6. FOCUS 1.0 SQL DATA WAREHOUSE ENDPOINTS")
    print("=================================================================")
    test_case("Warehouse", "TC-WH-01", "Get FOCUS daily summary", "GET", "/api/warehouse/daily-summary")
    test_case("Warehouse", "TC-WH-02", "Get provider monthly summary", "GET", "/api/warehouse/provider-monthly")
    test_case("Warehouse", "TC-WH-03", "Get department summary", "GET", "/api/warehouse/department-summary")
    test_case("Warehouse", "TC-WH-04", "Get active anomalies from warehouse view", "GET", "/api/warehouse/active-anomalies")
    test_case("Warehouse", "TC-WH-05", "Get service efficiency matrix", "GET", "/api/warehouse/service-efficiency")
    test_case("Warehouse", "TC-WH-06", "Get warehouse health telemetry", "GET", "/api/warehouse/health")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    print("\n=================================================================")
    print(f" TOTAL TESTS: {total} | PASSED: {passed} | FAILED: {failed}")
    print("=================================================================")
    
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blackbox_test_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_tests()
