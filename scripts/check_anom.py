import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.services import finops_service

df = finops_service.analyzed_df
print("Total records:", len(df))
print("Anomalies detected (detected_anomaly==1):", (df["detected_anomaly"] == 1).sum())
anom = df[df["detected_anomaly"] == 1]
print("Severity value counts in analyzed_df:")
print(anom["anomaly_severity"].value_counts())

all_anoms = finops_service.get_anomalies(severity="ALL")
print(f"\nget_anomalies(severity='ALL') returns {len(all_anoms)} records")
severities_in_all = [x["anomaly_severity"] for x in all_anoms]
from collections import Counter
print("Severities in returned ALL list:", Counter(severities_in_all))

crit_anoms = finops_service.get_anomalies(severity="CRITICAL")
print(f"get_anomalies(severity='CRITICAL') returns {len(crit_anoms)} records")
high_anoms = finops_service.get_anomalies(severity="HIGH")
print(f"get_anomalies(severity='HIGH') returns {len(high_anoms)} records")
med_anoms = finops_service.get_anomalies(severity="MEDIUM")
print(f"get_anomalies(severity='MEDIUM') returns {len(med_anoms)} records")
