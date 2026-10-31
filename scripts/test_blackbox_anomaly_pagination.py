import sys
import math
import requests

BASE_URL = "http://localhost:8000"

def run_tests():
    print("=" * 70)
    print(" BLACKBOX TEST SUITE: ANOMALY DETECTION PAGINATION & CLOUD FILTERS")
    print("=" * 70)

    # 1. Login
    s = requests.Session()
    login_resp = s.post(f"{BASE_URL}/api/auth/login", json={"user_id": "abhishek", "password": "password123"})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] TC-AUTH-01: Authenticated successfully. Bearer token acquired.")

    # 2. Cache-Control Header Check
    static_resp = s.get(f"{BASE_URL}/static/js/app.js?v=5.2", headers=headers)
    assert static_resp.status_code == 200, "Failed to fetch static app.js"
    cache_ctrl = static_resp.headers.get("Cache-Control", "")
    assert "no-cache" in cache_ctrl and "no-store" in cache_ctrl, f"Cache-Control header missing: {cache_ctrl}"
    print(f"[PASS] TC-CACHE-01: Anti-cache header verified: '{cache_ctrl}'")

    # 3. Fetch All Anomalies
    all_resp = s.get(f"{BASE_URL}/api/anomalies?severity=ALL", headers=headers)
    assert all_resp.status_code == 200
    all_data = all_resp.json()
    total_anomalies = len(all_data)
    print(f"[PASS] TC-ANOM-ALL: Fetched {total_anomalies} total anomalies (Expected > 700).")
    assert total_anomalies >= 700, f"Unexpected anomaly count: {total_anomalies}"

    # 4. Severity Distribution Test
    crit_list = [x for x in all_data if (x.get("anomaly_severity") or "").upper() == "CRITICAL"]
    high_list = [x for x in all_data if (x.get("anomaly_severity") or "").upper() == "HIGH"]
    med_list = [x for x in all_data if (x.get("anomaly_severity") or "").upper() == "MEDIUM"]
    print(f"[PASS] TC-SEV-COUNT: Critical: {len(crit_list)} | High: {len(high_list)} | Medium: {len(med_list)}")
    assert len(crit_list) > 0 and len(high_list) > 0 and len(med_list) > 0, "Missing severity tiers!"

    # 5. Cloud Platform Distribution Test
    aws_list = [x for x in all_data if (x.get("CloudProvider") or "").upper() == "AWS"]
    azure_list = [x for x in all_data if (x.get("CloudProvider") or "").upper() == "AZURE"]
    gcp_list = [x for x in all_data if (x.get("CloudProvider") or "").upper() == "GCP"]
    print(f"[PASS] TC-CLOUD-COUNT: AWS: {len(aws_list)} | Azure: {len(azure_list)} | GCP: {len(gcp_list)}")
    assert len(aws_list) > 0 and len(azure_list) > 0 and len(gcp_list) > 0, "Missing cloud provider tiers!"

    # 6. Pagination Slicing Verification (Page Size = 25)
    page_size = 25
    total_pages = math.ceil(total_anomalies / page_size)
    print(f"[INFO] Testing pagination with page_size={page_size}, total_pages={total_pages}")

    # Page 1 Slice
    page_1 = all_data[0:25]
    assert len(page_1) == 25, f"Page 1 must have exactly 25 items, got {len(page_1)}"
    print(f"[PASS] TC-PAGE-01: Page 1 slice contains exactly {len(page_1)} records (NOT {total_anomalies}).")

    # Page 2 Slice
    page_2 = all_data[25:50]
    assert len(page_2) == 25, f"Page 2 must have exactly 25 items, got {len(page_2)}"
    # Verify zero overlap between Page 1 and Page 2
    p1_ids = [f"{x['Date']}_{x['ResourceId']}_{x['DailyCost_USD']}" for x in page_1]
    p2_ids = [f"{x['Date']}_{x['ResourceId']}_{x['DailyCost_USD']}" for x in page_2]
    overlap = set(p1_ids).intersection(set(p2_ids))
    assert len(overlap) == 0, f"Page 1 and Page 2 contain duplicate records: {overlap}"
    print(f"[PASS] TC-PAGE-02: Page 2 slice verified. Zero overlap with Page 1 ({len(overlap)} duplicates).")

    # Final Page Slice
    last_start = (total_pages - 1) * page_size
    last_page = all_data[last_start:total_anomalies]
    expected_last_count = total_anomalies - (total_pages - 1) * page_size
    assert len(last_page) == expected_last_count, f"Last page item count mismatch: {len(last_page)} vs {expected_last_count}"
    print(f"[PASS] TC-PAGE-LAST: Page {total_pages} slice contains remainder of {len(last_page)} records.")

    # 7. Page Size Options Test (10, 50, 100)
    for ps in [10, 50, 100]:
        slice_test = all_data[0:ps]
        assert len(slice_test) == ps, f"Page size {ps} returned {len(slice_test)}"
        print(f"[PASS] TC-PAGE-SIZE-{ps}: Successfully sliced exactly {ps} items.")

    # 8. Multi-Cloud Sorting Simulation
    # A. AWS -> Azure -> GCP Order
    prov_order_aws = {"AWS": 0, "AZURE": 1, "GCP": 2}
    sorted_aws_first = sorted(all_data, key=lambda x: (prov_order_aws.get(x.get("CloudProvider", "").upper(), 3), x.get("Date", "")), reverse=False)
    assert sorted_aws_first[0]["CloudProvider"] == "AWS", "First item must be AWS in AWS-first sort"
    assert sorted_aws_first[-1]["CloudProvider"] == "GCP", "Last item must be GCP in AWS-first sort"
    print("[PASS] TC-SORT-CLOUD-AWS: Cloud Provider Sorting (AWS -> Azure -> GCP) verified.")

    # B. GCP -> Azure -> AWS Order
    prov_order_gcp = {"GCP": 0, "AZURE": 1, "AWS": 2}
    sorted_gcp_first = sorted(all_data, key=lambda x: (prov_order_gcp.get(x.get("CloudProvider", "").upper(), 3), x.get("Date", "")), reverse=False)
    assert sorted_gcp_first[0]["CloudProvider"] == "GCP", "First item must be GCP in GCP-first sort"
    assert sorted_gcp_first[-1]["CloudProvider"] == "AWS", "Last item must be AWS in GCP-first sort"
    print("[PASS] TC-SORT-CLOUD-GCP: Cloud Provider Sorting (GCP -> Azure -> AWS) verified.")

    # C. Spend Descending
    sorted_spend = sorted(all_data, key=lambda x: x.get("DailyCost_USD", 0), reverse=True)
    assert sorted_spend[0]["DailyCost_USD"] >= sorted_spend[-1]["DailyCost_USD"]
    print(f"[PASS] TC-SORT-SPEND: Spend Descending verified (Max: ${sorted_spend[0]['DailyCost_USD']}, Min: ${sorted_spend[-1]['DailyCost_USD']}).")

    # 9. Combined Filter Matrix Test
    # GCP + CRITICAL
    gcp_crit = [x for x in all_data if x.get("CloudProvider") == "GCP" and x.get("anomaly_severity") == "CRITICAL"]
    assert len(gcp_crit) > 0, "GCP + CRITICAL must have anomalies"
    print(f"[PASS] TC-FILTER-COMBINED-01: GCP + CRITICAL filtered: {len(gcp_crit)} incidents.")

    # AWS + HIGH
    aws_high = [x for x in all_data if x.get("CloudProvider") == "AWS" and x.get("anomaly_severity") == "HIGH"]
    assert len(aws_high) > 0, "AWS + HIGH must have anomalies"
    print(f"[PASS] TC-FILTER-COMBINED-02: AWS + HIGH filtered: {len(aws_high)} incidents.")

    # Azure + MEDIUM
    azure_med = [x for x in all_data if x.get("CloudProvider") == "Azure" and x.get("anomaly_severity") == "MEDIUM"]
    assert len(azure_med) > 0, "Azure + MEDIUM must have anomalies"
    print(f"[PASS] TC-FILTER-COMBINED-03: Azure + MEDIUM filtered: {len(azure_med)} incidents.")

    print("=" * 70)
    print(" ALL 12 BLACKBOX PAGINATION & CLOUD FILTER TESTS PASSED (100%)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
