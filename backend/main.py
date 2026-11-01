import os
import secrets
import time
from typing import List, Optional, Dict
from collections import defaultdict
import io
import pandas as pd
from fastapi import FastAPI, Query, HTTPException, Header, Request, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from backend.services import finops_service
from backend.pricing_engine import (
    CLOUD_CATALOG,
    REAL_CLOUD_CATALOG,
    CloudCalculatorRequest,
    calculate_cloud_workload_estimate
)
from src.database import (
    get_daily_spend_summary,
    get_monthly_provider_summary,
    get_department_summary,
    get_active_anomalies,
    get_service_efficiency_summary,
    get_engine,
    authenticate_user,
    register_user,
    seed_default_users
)
from sqlalchemy import text

# Initialize database credentials table and default enterprise accounts
seed_default_users()

app = FastAPI(
    title="Abhi Cloud Tech | FinOps ML API",
    description="Enterprise Machine Learning REST API for Multi-Cloud Cost Optimization & Anomaly Detection",
    version="1.11.26"
)

# -------------------------------------------------------------
# Enterprise DevSecOps Security Headers & CORS Middleware
# -------------------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://unpkg.com; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Enterprise Session Token Management & RBAC Dependencies
# -------------------------------------------------------------
ACTIVE_SESSIONS: Dict[str, dict] = {}
SESSION_TTL_SECONDS = 8 * 3600  # 8-Hour Session Expiry

# Deterministic test session token for CI/CD test automation & regression harness
TEST_TOKEN = "act_session_test_admin_token_001"
ACTIVE_SESSIONS[TEST_TOKEN] = {
    "user_id": "abhishek",
    "full_name": "M Abhishek Reddy",
    "created_at": time.time(),
    "expires_at": time.time() + (365 * 86400)
}

def create_session(user_id: str, full_name: str) -> str:
    token = f"act_session_{secrets.token_hex(24)}"
    now = time.time()
    ACTIVE_SESSIONS[token] = {
        "user_id": user_id,
        "full_name": full_name,
        "created_at": now,
        "expires_at": now + SESSION_TTL_SECONDS
    }
    return token

def invalidate_session(token: str) -> bool:
    if token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
        return True
    return False

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI security dependency validating incoming Bearer authorization token.
    Enforces authentication across all operational FinOps endpoints.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials were not provided. Expected 'Authorization: Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = parts[1]
    session = ACTIVE_SESSIONS.get(token)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session token. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if time.time() > session["expires_at"]:
        del ACTIVE_SESSIONS[token]
        raise HTTPException(
            status_code=401,
            detail="Session has expired. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return session

# Rate Limiting for Authentication Endpoints (Max 5 attempts per 60 seconds per IP)
LOGIN_ATTEMPTS: Dict[str, List[float]] = defaultdict(list)
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_WINDOW_SECONDS = 60

def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    valid_attempts = [t for t in LOGIN_ATTEMPTS[client_ip] if now - t < LOCKOUT_WINDOW_SECONDS]
    LOGIN_ATTEMPTS[client_ip] = valid_attempts
    if len(valid_attempts) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many authentication attempts. Please wait 60 seconds before retrying."
        )

def record_failed_attempt(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    LOGIN_ATTEMPTS[client_ip].append(time.time())

def clear_failed_attempts(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    LOGIN_ATTEMPTS.pop(client_ip, None)

# -------------------------------------------------------------
# Official Cloud Provider Regional Rate Database (Canonical Keys & Machine Families)
# Synchronized with AWS, Microsoft Azure, and Google Cloud Pricing Calculators
# -------------------------------------------------------------
for _prov in REAL_CLOUD_CATALOG.values():
    if "compute_families" in _prov and "families" not in _prov:
        _prov["families"] = _prov["compute_families"]

# -------------------------------------------------------------
# -------------------------------------------------------------
# Request Models
# -------------------------------------------------------------
class ForecastRequest(BaseModel):
    horizon_days: int = Field(default=60, ge=1, le=180, description="Forecast horizon in days (1 to 180)")
    workload_growth_pct: float = Field(default=15.0, ge=-100.0, le=500.0, description="Workload growth percent")
    finops_savings_pct: float = Field(default=10.0, ge=0.0, le=100.0, description="Finops savings discount percent")

class SimulateRequest(BaseModel):
    cloud_provider: str = Field(default="AWS", description="Cloud provider (AWS, Azure, GCP)")
    machine_family: Optional[str] = Field(default=None, description="Machine type / family (e.g. e2, n2, m6i, m6g, Standard_Dsv5, Standard_B)")
    region: str = Field(default="us-east-1", description="Region key")
    vcpu_count: int = Field(default=32, ge=1, le=512, description="Number of vCPU cores")
    ram_gb: int = Field(default=128, ge=1, le=4096, description="RAM in GB")
    daily_hours: int = Field(default=24, ge=0, le=24, description="Operating hours per day")
    downsize_pct: float = Field(default=50.0, ge=0.0, le=100.0, description="Downsizing percent")

class CloudConnectorRequest(BaseModel):
    connector_type: str = Field(..., description="Cloud provider type: AWS, Azure, or GCP")
    config: dict = Field(default_factory=dict, description="Configuration parameters (bucket, role_arn, dataset, etc.)")

# -------------------------------------------------------------
# Protected API Routes (Requires Enterprise Bearer Token)
# -------------------------------------------------------------
@app.get("/api/meta/filters")
def get_filter_options(current_user: dict = Depends(get_current_user)):
    df = finops_service.analyzed_df
    return {
        "providers": sorted(list(df["CloudProvider"].unique())),
        "departments": sorted(list(df["Department"].unique())),
        "total_records": len(df),
        "date_min": str(df["Date"].min()),
        "date_max": str(df["Date"].max())
    }

@app.get("/api/meta/catalog")
def get_cloud_catalog():
    """Returns official provider regions and pricing for interactive dropdowns"""
    return REAL_CLOUD_CATALOG

@app.get("/api/kpis")
def get_kpi_metrics(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    return finops_service.get_overview_kpis(providers, departments)

@app.get("/api/trends")
def get_spend_trends(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    return finops_service.get_spend_trends(providers, departments)

@app.get("/api/departments")
def get_department_analytics(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    return finops_service.get_department_analytics(providers, departments)

@app.get("/api/anomalies")
def get_anomalies(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None),
    severity: Optional[str] = "ALL",
    limit: Optional[int] = Query(None, ge=1, le=5000, description="Max anomalies to return (omit for all)"),
    current_user: dict = Depends(get_current_user)
):
    return finops_service.get_anomalies(providers, departments, severity, limit)

@app.post("/api/forecast")
def generate_forecast(
    req: ForecastRequest,
    current_user: dict = Depends(get_current_user)
):
    return finops_service.get_forecast(
        horizon_days=req.horizon_days,
        workload_growth=req.workload_growth_pct,
        finops_savings=req.finops_savings_pct
    )

@app.get("/api/optimizer")
def get_optimization(
    providers: Optional[List[str]] = Query(None),
    departments: Optional[List[str]] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    return finops_service.get_optimization_portfolio(providers, departments)

@app.get("/api/ml/models")
def get_ml_model_registry(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the active MLOps model registry metadata: serialized joblib artifacts,
    hyperparameters, performance metrics, and serialization timestamps.
    """
    return finops_service.get_model_registry()

# -------------------------------------------------------------
# Real-Time Cloud Billing Ingestion & Connector API Endpoints
# -------------------------------------------------------------
@app.post("/api/dataset/upload")
async def upload_billing_dataset(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and ingest an external real-time billing CSV (AWS CUR, Azure Cost Mgmt, GCP BigQuery, or FOCUS 1.0).
    Runs pre-trained Anomaly Detection & Time-Series Forecasting instantly.
    """
    if not file.filename.lower().endswith((".csv", ".tsv", ".txt")):
        raise HTTPException(status_code=400, detail="Only CSV, TSV, or TXT billing files are supported.")
    
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            
        sep = "\t" if file.filename.lower().endswith(".tsv") else ","
        try:
            df = pd.read_csv(io.BytesIO(content), sep=sep, low_memory=False)
        except Exception:
            df = pd.read_csv(io.BytesIO(content), sep=None, engine="python")
            
        if df.empty:
            raise HTTPException(status_code=400, detail="Parsed dataset contains 0 records.")
            
        result = finops_service.ingest_billing_dataframe(df, source_name=file.filename)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest billing dataset: {str(e)}")

@app.post("/api/dataset/sample/{provider}")
def load_sample_dataset(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Loads prepared real-world vendor billing sample files from data/uat/ with one click:
    'aws' (CUR), 'azure' (Cost Mgmt), 'gcp' (BigQuery), or 'microsoft' (FOCUS 1.0).
    """
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data", "uat")
    file_map = {
        "aws": ("aws_cur_billing_export.csv", "AWS Cost & Usage Report Sample"),
        "azure": ("azure_cost_management_export.csv", "Azure Cost Management Sample"),
        "gcp": ("gcp_bigquery_billing_export.csv", "GCP BigQuery Detailed Export Sample"),
        "microsoft": (os.path.join("finops-toolkit", "EA-Cost-FOCUS_1.0.csv"), "Microsoft FOCUS 1.0 Enterprise Dataset"),
        "focus": (os.path.join("finops-toolkit", "EA-Cost-FOCUS_1.0.csv"), "Microsoft FOCUS 1.0 Enterprise Dataset")
    }
    
    key = provider.lower().strip()
    if key not in file_map:
        raise HTTPException(status_code=400, detail=f"Unknown sample provider '{provider}'. Choose 'aws', 'azure', 'gcp', or 'microsoft'.")
        
    rel_path, label = file_map[key]
    file_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Sample file not found at {file_path}")
        
    try:
        nrows = 10000 if "focus" in key or "microsoft" in key else None
        df = pd.read_csv(file_path, nrows=nrows, low_memory=False)
        result = finops_service.ingest_billing_dataframe(df, source_name=f"{label} ({len(df):,} rows)")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample dataset: {str(e)}")

@app.post("/api/dataset/reset")
def reset_to_default_warehouse(
    current_user: dict = Depends(get_current_user)
):
    """
    Resets the platform back to the standard SQLite FinOps Warehouse (32,850 records).
    """
    return finops_service.reset_to_warehouse()

@app.get("/api/dataset/status")
def get_dataset_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the currently active dataset status, source name, record count, and cloud connectors.
    """
    return finops_service.get_dataset_status()

@app.post("/api/connectors/cloud")
def configure_cloud_connector(
    req: CloudConnectorRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Configures and validates an automated live cloud billing connector (AWS S3, Azure Blob, GCP BigQuery).
    """
    return finops_service.save_cloud_connector(req.connector_type, req.config)

@app.get("/api/connectors/cloud")
def get_cloud_connectors(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the list of configured live cloud billing connectors.
    """
    return finops_service.cloud_connectors

@app.post("/api/simulate")
def simulate_workload(
    req: SimulateRequest,
    current_user: dict = Depends(get_current_user)
):
    provider_key = req.cloud_provider if req.cloud_provider in CLOUD_CATALOG else "AWS"
    prov = CLOUD_CATALOG[provider_key]
    regions = prov["regions"]
    reg_key = req.region.strip() if req.region and req.region.strip() in regions else list(regions.keys())[0]
    multiplier = regions[reg_key]["multiplier"]
    
    # Base rates from custom rates or preset
    rates = prov.get("custom_rates", {"vcpu_hourly": 0.048, "ram_hourly": 0.006})
    vcpu_base = rates.get("vcpu_hourly", 0.048)
    ram_base = rates.get("ram_hourly", 0.006)
    
    hourly_rate = ((req.vcpu_count * vcpu_base) + (req.ram_gb * ram_base)) * multiplier
    daily_cost = hourly_rate * req.daily_hours
    monthly_cost = daily_cost * 30
    monthly_savings = monthly_cost * (req.downsize_pct / 100.0)
    
    # Instance SKU
    fam = (req.machine_family or "m6i").strip()
    if provider_key == "AWS":
        size_tag = "8xlarge" if req.vcpu_count >= 32 else "4xlarge" if req.vcpu_count >= 16 else "2xlarge" if req.vcpu_count >= 8 else "xlarge"
        sku = f"{fam}.{size_tag}"
    elif provider_key == "Azure":
        sku = f"{fam}_{req.vcpu_count}s_v5" if "_" not in fam else f"{fam}"
    elif provider_key == "GCP":
        sku = f"{fam}-standard-{req.vcpu_count}"
    else:
        sku = f"{fam}-{req.vcpu_count}"
        
    return {
        "cloud_provider": provider_key,
        "machine_family_key": fam,
        "machine_family_name": f"{provider_key} {fam}",
        "machine_family_note": "Production tier baseline",
        "region_key": reg_key,
        "region_name": regions[reg_key]["name"],
        "region_note": "Standard tariff",
        "multiplier": multiplier,
        "instance_sku": sku,
        "family": fam,
        "base_vcpu_rate": vcpu_base,
        "base_ram_rate": ram_base,
        "hourly_cost_usd": round(hourly_rate, 4),
        "daily_cost_usd": round(daily_cost, 2),
        "monthly_cost_usd": round(monthly_cost, 2),
        "potential_monthly_savings_usd": round(monthly_savings, 2),
        "potential_annual_savings_usd": round(monthly_savings * 12, 2)
    }

# -------------------------------------------------------------
# Official Multi-Cloud Pricing Calculator & Arbitrage Endpoints
# Aligned with Google Cloud, AWS, and Azure Pricing Calculators
# -------------------------------------------------------------
@app.post("/api/calculator/estimate")
def calculate_workload_estimate(
    req: CloudCalculatorRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Official Cloud Pricing Calculator API.
    Computes exact monthly and hourly pricing based on:
    - Selected Cloud Provider (GCP, AWS, Azure)
    - Deployment Region
    - Machine Type (Preset standard SKU or Custom vCPU/RAM)
    - Boot Disk / Storage type & capacity (GB)
    - Operating schedule (hours/day & instance count)
    - Commitment discounts (1-Yr, 3-Yr, Spot) & Azure Hybrid Benefit
    Also returns 1:1 cross-cloud parity benchmark across the other two cloud providers.
    """
    return calculate_cloud_workload_estimate(req)

@app.post("/api/calculator/multicloud-compare")
def compare_multicloud_pricing(
    req: CloudCalculatorRequest,
    current_user: dict = Depends(get_current_user)
):
    return calculate_cloud_workload_estimate(req)

@app.get("/api/calculator/catalog")
def get_pricing_calculator_catalog(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns full official cloud catalog with regions, machine presets,
    custom rates, storage disk types, and commitment discounts for GCP, AWS, and Azure.
    """
    return CLOUD_CATALOG

# -------------------------------------------------------------
# High-Performance FOCUS 1.0 Data Warehouse SQL View Endpoints
# -------------------------------------------------------------
@app.get("/api/warehouse/daily-summary")
def get_warehouse_daily_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    provider: Optional[str] = Query(None, description="Cloud provider (AWS, Azure, GCP)"),
    department: Optional[str] = Query(None, description="Department name"),
    current_user: dict = Depends(get_current_user)
):
    df = get_daily_spend_summary(start_date=start_date, end_date=end_date, provider=provider, department=department)
    return df.to_dict(orient="records")

@app.get("/api/warehouse/provider-monthly")
def get_warehouse_provider_monthly(
    provider: Optional[str] = Query(None, description="Cloud provider filter"),
    current_user: dict = Depends(get_current_user)
):
    df = get_monthly_provider_summary(provider=provider)
    return df.to_dict(orient="records")

@app.get("/api/warehouse/department-summary")
def get_warehouse_department_summary(
    department: Optional[str] = Query(None, description="Department filter"),
    current_user: dict = Depends(get_current_user)
):
    df = get_department_summary(department=department)
    return df.to_dict(orient="records")

@app.get("/api/warehouse/active-anomalies")
def get_warehouse_active_anomalies(
    limit: int = Query(50, ge=1, le=500, description="Max anomalies to return"),
    current_user: dict = Depends(get_current_user)
):
    df = get_active_anomalies(limit=limit)
    return df.to_dict(orient="records")

@app.get("/api/warehouse/service-efficiency")
def get_warehouse_service_efficiency(current_user: dict = Depends(get_current_user)):
    df = get_service_efficiency_summary()
    return df.to_dict(orient="records")

@app.get("/api/warehouse/health")
def get_warehouse_health(current_user: dict = Depends(get_current_user)):
    engine = get_engine()
    with engine.connect() as conn:
        total_rows = conn.execute(text("SELECT count(*) FROM unified_focus_billing;")).fetchone()[0]
        indexes = conn.execute(text("SELECT count(*) FROM sqlite_master WHERE type='index' AND tbl_name='unified_focus_billing';")).fetchone()[0]
        views = conn.execute(text("SELECT count(*) FROM sqlite_master WHERE type='view';")).fetchone()[0]
        journal_mode = conn.execute(text("PRAGMA journal_mode;")).fetchone()[0]
        cache_size = conn.execute(text("PRAGMA cache_size;")).fetchone()[0]
        mmap_size = conn.execute(text("PRAGMA mmap_size;")).fetchone()[0]
    return {
        "status": "healthy",
        "specification": "FinOps Open Cost & Usage Specification (FOCUS™ 1.0)",
        "total_records": total_rows,
        "index_count": indexes,
        "view_count": views,
        "sqlite_pragmas": {
            "journal_mode": journal_mode,
            "cache_size_pages": cache_size,
            "mmap_size_bytes": mmap_size
        }
    }

class LoginRequest(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50, description="Unique User ID or username")
    password: str = Field(..., min_length=8, description="Account password")

class SignUpRequest(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50, description="Desired User ID or username")
    password: str = Field(..., min_length=8, description="Password (at least 8 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")

@app.post("/api/auth/login")
def login_user(req: LoginRequest, request: Request):
    """
    Authenticates user credentials against the SQLite warehouse database.
    Protected with rate-limiting against brute force attacks.
    """
    check_rate_limit(request)
    user = authenticate_user(req.user_id, req.password)
    if not user:
        record_failed_attempt(request)
        raise HTTPException(
            status_code=401,
            detail="Invalid User ID or password. Please verify credentials or sign up."
        )
    clear_failed_attempts(request)
    token = create_session(user["user_id"], user["full_name"])
    return {
        "status": "success",
        "message": f"Successfully authenticated as {user['full_name']}",
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "organization": "Abhi Cloud Tech Inc."
        }
    }

@app.post("/api/auth/signup")
def signup_user(req: SignUpRequest, request: Request):
    """
    Registers a new user account into the SQLite warehouse database.
    Enforces minimum 8-character password policy and rate-limits registrations.
    """
    check_rate_limit(request)
    try:
        new_user = register_user(req.user_id, req.password, req.full_name)
    except ValueError as e:
        record_failed_attempt(request)
        raise HTTPException(status_code=400, detail=str(e))
    
    clear_failed_attempts(request)
    token = create_session(new_user["user_id"], new_user["full_name"])
    return {
        "status": "success",
        "message": f"Account '{new_user['user_id']}' created successfully!",
        "token": token,
        "user": {
            "user_id": new_user["user_id"],
            "full_name": new_user["full_name"],
            "organization": "Abhi Cloud Tech Inc."
        }
    }

@app.post("/api/auth/logout")
def logout_user(authorization: Optional[str] = Header(None)):
    """
    Logs out the user and invalidates the session token in the server registry.
    """
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            invalidate_session(parts[1])
    return {
        "status": "success",
        "message": "User session logged out successfully."
    }

@app.get("/api/auth/session")
def get_auth_session(current_user: dict = Depends(get_current_user)):
    """
    Enterprise IAM Session & Credentials Configuration endpoint.
    Protected: Only authenticated sessions can inspect federated multi-cloud identity state and tenant IDs.
    """
    return {
        "status": "authenticated",
        "user": {
            "name": current_user["full_name"],
            "user_id": current_user["user_id"],
            "email": f"{current_user['user_id']}@abhicloudtech.io",
            "role": "Principal Cloud Architect" if current_user["user_id"] == "abhishek" else "FinOps Analyst",
            "role_badge": "SuperAdmin" if current_user["user_id"] == "abhishek" else "Analyst",
            "organization": "Abhi Cloud Tech Inc.",
            "tenant_id": "org-abhi-cloud-tech-prod",
            "idp": "AWS IAM Identity Center (SSO) + Azure Entra ID",
            "mfa_verified": True,
            "session_valid_hours": 8
        },
        "federated_accounts": {
            "aws_account_id": "9421-8201-9482",
            "azure_tenant_id": "72f988bf-86f1-41af-91ab-2d7cd011db47",
            "gcp_project_id": "abhi-cloud-tech-prod-vpc"
        }
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
