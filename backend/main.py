import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.services import finops_service

app = FastAPI(
    title="Abhi Cloud Tech | FinOps ML API",
    description="Enterprise Machine Learning REST API for Multi-Cloud Cost Optimization & Anomaly Detection",
    version="2.0.0"
)

# -------------------------------------------------------------
# Request Models
# -------------------------------------------------------------
class ForecastRequest(BaseModel):
    horizon_days: int = 60
    workload_growth_pct: float = 15.0
    finops_savings_pct: float = 10.0

class SimulateRequest(BaseModel):
    vcpu_count: int = 32
    ram_gb: int = 128
    daily_hours: int = 24
    downsize_pct: float = 50.0

# -------------------------------------------------------------
# API Routes
# -------------------------------------------------------------
@app.get("/api/meta/filters")
def get_filter_options():
    df = finops_service.analyzed_df
    return {
        "providers": sorted(list(df["CloudProvider"].unique())),
        "departments": sorted(list(df["Department"].unique())),
        "total_records": len(df),
        "date_min": str(df["Date"].min()),
        "date_max": str(df["Date"].max())
    }

@app.get("/api/kpis")
def get_kpi_metrics(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None)
):
    return finops_service.get_overview_kpis(providers, departments)

@app.get("/api/trends")
def get_spend_trends(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None)
):
    return finops_service.get_spend_trends(providers, departments)

@app.get("/api/departments")
def get_department_analytics(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None)
):
    return finops_service.get_department_analytics(providers, departments)

@app.get("/api/anomalies")
def get_anomalies(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None),
    severity: Optional[str] = "ALL"
):
    return finops_service.get_anomalies(providers, departments, severity)

@app.post("/api/forecast")
def generate_forecast(req: ForecastRequest):
    return finops_service.get_forecast(
        horizon_days=req.horizon_days,
        workload_growth=req.workload_growth_pct,
        finops_savings=req.finops_savings_pct
    )

@app.get("/api/optimizer")
def get_optimization(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None)
):
    return finops_service.get_optimization_portfolio(providers, departments)

@app.post("/api/simulate")
def simulate_workload(req: SimulateRequest):
    hourly_rate = (req.vcpu_count * 0.048) + (req.ram_gb * 0.006)
    daily_cost = hourly_rate * req.daily_hours
    monthly_cost = daily_cost * 30
    monthly_savings = monthly_cost * (req.downsize_pct / 100.0)
    
    return {
        "hourly_cost_usd": round(hourly_rate, 3),
        "daily_cost_usd": round(daily_cost, 2),
        "monthly_cost_usd": round(monthly_cost, 2),
        "potential_monthly_savings_usd": round(monthly_savings, 2),
        "potential_annual_savings_usd": round(monthly_savings * 12, 2)
    }

# -------------------------------------------------------------
# Static Frontend Serving
# -------------------------------------------------------------
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
static_dir = os.path.join(frontend_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Abhi Cloud Tech FinOps ML API is live. Frontend index.html not yet found."}
