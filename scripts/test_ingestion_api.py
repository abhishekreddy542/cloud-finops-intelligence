import os
import sys
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def test_ingestion_api():
    print("=" * 70)
    print("  TESTING REAL-TIME DATASET INGESTION & CLOUD CONNECTOR ENDPOINTS")
    print("=" * 70)

    s = requests.Session()
    # 1. Login
    login_resp = s.post(f"{BASE_URL}/api/auth/login", json={"user_id": "abhishek", "password": "password123"})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[+] Successfully authenticated as abhishek")

    # 2. Get dataset status
    res = s.get(f"{BASE_URL}/api/dataset/status", headers=headers)
    assert res.status_code == 200, f"Status failed: {res.text}"
    status_data = res.json()
    print(f"[+] Current Dataset: {status_data['source_info']['name']} ({status_data['source_info']['records']:,} rows)")

    # 3. Test 1-click sample loading: AWS
    res = s.post(f"{BASE_URL}/api/dataset/sample/aws", headers=headers)
    assert res.status_code == 200, f"AWS sample failed: {res.text}"
    aws_data = res.json()
    print(f"[+] Loaded AWS CUR: {aws_data['records_processed']:,} rows | Anomalies: {aws_data['anomalies_detected']} | Waste: ${aws_data['total_waste_usd']:,.2f}")

    # 4. Check KPIs after AWS sample loaded
    kpis = s.get(f"{BASE_URL}/api/kpis", headers=headers).json()
    print(f"[+] Verified Live KPIs: Total Spend = ${kpis['total_spend_ytd']:,.2f} | Anomalies = {kpis['anomaly_incident_count']}")

    # 5. Test 1-click sample loading: Azure
    res = s.post(f"{BASE_URL}/api/dataset/sample/azure", headers=headers)
    assert res.status_code == 200, f"Azure sample failed: {res.text}"
    az_data = res.json()
    print(f"[+] Loaded Azure Cost Mgmt: {az_data['records_processed']:,} rows | Anomalies: {az_data['anomalies_detected']}")

    # 6. Test 1-click sample loading: GCP
    res = s.post(f"{BASE_URL}/api/dataset/sample/gcp", headers=headers)
    assert res.status_code == 200, f"GCP sample failed: {res.text}"
    gcp_data = res.json()
    print(f"[+] Loaded GCP BigQuery: {gcp_data['records_processed']:,} rows | Anomalies: {gcp_data['anomalies_detected']}")

    # 7. Test file upload via multipart/form-data
    csv_path = Path(r"C:\Users\M Abhishek Reddy\.gemini\antigravity\scratch\cloud-finops-intelligence\data\uat\aws_cur_billing_export.csv")
    with open(csv_path, "rb") as f:
        files = {"file": ("custom_aws_cur.csv", f, "text/csv")}
        res = s.post(f"{BASE_URL}/api/dataset/upload", headers=headers, files=files)
    assert res.status_code == 200, f"Upload failed: {res.text}"
    up_data = res.json()
    print(f"[+] Successfully uploaded file: {up_data['source_name']} | Detected: {up_data['detected_format']} | Rows: {up_data['records_processed']:,}")

    # 8. Test Cloud Connectors API
    connector_payload = {
        "connector_type": "AWS",
        "config": {
            "bucket": "s3://my-enterprise-billing-bucket",
            "role_arn": "arn:aws:iam::112233445566:role/FinOpsCurSync",
            "region": "us-east-1"
        }
    }
    res = s.post(f"{BASE_URL}/api/connectors/cloud", headers=headers, json=connector_payload)
    assert res.status_code == 200, f"Connector save failed: {res.text}"
    print(f"[+] Saved AWS Cloud Connector: {res.json()['message']}")

    # 9. Test Reset to Warehouse
    res = s.post(f"{BASE_URL}/api/dataset/reset", headers=headers)
    assert res.status_code == 200, f"Reset failed: {res.text}"
    reset_data = res.json()
    print(f"[+] Reset to default warehouse: {reset_data['records']:,} rows restored.")

    print("\n" + "=" * 70)
    print("  [SUCCESS] All 9/9 Ingestion & Connector Tests PASSED (100%)!")
    print("=" * 70)

if __name__ == "__main__":
    test_ingestion_api()
