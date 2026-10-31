import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.services import finops_service

def verify():
    print("=" * 60)
    print("Verifying FinOps Intelligence Pipeline against FOCUS 1.0 Data...")
    print("=" * 60)
    
    kpis = finops_service.get_overview_kpis()
    print("KPIs:", kpis)
    
    anomalies = finops_service.get_anomalies(severity="CRITICAL")
    print(f"Critical Anomalies detected: {len(anomalies)}")
    if anomalies:
        print("Sample critical anomaly:")
        print(anomalies[0])
        
    metrics = finops_service.forecast_metrics
    print("Forecast Metrics:", metrics)
    
    trends = finops_service.get_spend_trends()
    print(f"Daily trends data points: {len(trends['daily_trend'])}")
    print(f"Cloud provider distribution: {trends['provider_breakdown']}")
    
    opt = finops_service.get_optimization_portfolio()
    print("Optimization Portfolio:", opt["portfolio"])
    print(f"Action Matrix Recommendations: {len(opt['action_matrix'])}")
    
    print("=" * 60)
    print("SUCCESS: All pipeline components operational on FOCUS 1.0!")
    print("=" * 60)

if __name__ == "__main__":
    verify()
