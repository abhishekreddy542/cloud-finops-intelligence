import os
import secrets
import time
from typing import List, Optional, Dict
from collections import defaultdict
from fastapi import FastAPI, Query, HTTPException, Header, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field
from backend.services import finops_service
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
    version="2.0.0"
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
# -------------------------------------------------------------
REAL_CLOUD_CATALOG: Dict[str, Dict] = {
    "AWS": {
        "families": {
            "m6i": {
                "name": "General Purpose Intel Ice Lake (m6i)",
                "vcpu_rate": 0.0480,
                "ram_rate": 0.0060,
                "sku_prefix": "m6i",
                "note": "Standard enterprise general-purpose baseline"
            },
            "m6g": {
                "name": "AWS Graviton2 ARM (m6g - 20% Cost Advantage)",
                "vcpu_rate": 0.0384,
                "ram_rate": 0.0048,
                "sku_prefix": "m6g",
                "note": "Custom AWS ARM silicon with superior price/performance"
            },
            "c6i": {
                "name": "Compute Optimized Intel (c6i)",
                "vcpu_rate": 0.0425,
                "ram_rate": 0.0053,
                "sku_prefix": "c6i",
                "note": "Optimized for compute-bound batch & high single-thread loads"
            },
            "r6i": {
                "name": "Memory Optimized Intel (r6i)",
                "vcpu_rate": 0.0504,
                "ram_rate": 0.0063,
                "sku_prefix": "r6i",
                "note": "Designed for in-memory databases, Redis & Spark caches"
            }
        },
        "regions": {
            "us-east-1": {"name": "us-east-1 (US East - N. Virginia)", "multiplier": 1.00, "note": "Global Baseline"},
            "us-west-2": {"name": "us-west-2 (US West - Oregon)", "multiplier": 1.00, "note": "US West Hydro Baseline"},
            "eu-central-1": {"name": "eu-central-1 (Europe - Frankfurt)", "multiplier": 1.18, "note": "Frankfurt Energy & Carbon Tax (+18%)"},
            "eu-west-1": {"name": "eu-west-1 (Europe - Ireland)", "multiplier": 1.10, "note": "Ireland Dublin Campus (+10%)"},
            "ap-south-1": {"name": "ap-south-1 (Asia Pacific - Mumbai)", "multiplier": 1.09, "note": "India Domestic Gateway (+9%)"},
            "ap-southeast-1": {"name": "ap-southeast-1 (Asia Pacific - Singapore)", "multiplier": 1.14, "note": "APAC Regional Interconnect (+14%)"},
            "sa-east-1": {"name": "sa-east-1 (South America - São Paulo)", "multiplier": 1.34, "note": "LATAM Import Tariffs (+34%)"}
        }
    },
    "Azure": {
        "families": {
            "Standard_Dsv5": {
                "name": "General Purpose Intel Ice Lake (Standard Dsv5)",
                "vcpu_rate": 0.0475,
                "ram_rate": 0.0059,
                "sku_prefix": "Standard_D",
                "note": "Balanced Azure compute baseline"
            },
            "Standard_B": {
                "name": "Burstable Economy (Standard B-Series - 25% Cheaper)",
                "vcpu_rate": 0.0356,
                "ram_rate": 0.0044,
                "sku_prefix": "Standard_B",
                "note": "Burstable CPU for dev/test and variable non-steady loads"
            },
            "Standard_Dasv5": {
                "name": "AMD EPYC Balanced (Standard Dasv5 - 12% Cheaper)",
                "vcpu_rate": 0.0418,
                "ram_rate": 0.0052,
                "sku_prefix": "Standard_D",
                "note": "High-efficiency AMD Milan processor architecture"
            },
            "Standard_Esv5": {
                "name": "Memory Optimized (Standard Esv5)",
                "vcpu_rate": 0.0510,
                "ram_rate": 0.0062,
                "sku_prefix": "Standard_E",
                "note": "Large memory footprint for analytics and enterprise ERP"
            }
        },
        "regions": {
            "eastus": {"name": "eastus (East US - Virginia)", "multiplier": 1.00, "note": "Azure East Baseline"},
            "westus2": {"name": "westus2 (West US 2 - Washington)", "multiplier": 1.00, "note": "Azure West Baseline"},
            "westeurope": {"name": "westeurope (West Europe - Netherlands)", "multiplier": 1.17, "note": "Amsterdam Interconnect (+17%)"},
            "northeurope": {"name": "northeurope (North Europe - Ireland)", "multiplier": 1.15, "note": "Dublin Campus (+15%)"},
            "centralindia": {"name": "centralindia (Central India - Pune)", "multiplier": 1.10, "note": "Pune Enterprise DC (+10%)"},
            "southeastasia": {"name": "southeastasia (Southeast Asia - Singapore)", "multiplier": 1.13, "note": "Singapore Regional (+13%)"}
        }
    },
    "GCP": {
        "families": {
            "e2": {
                "name": "e2-standard (Cost-Optimized / Dynamic Resource Allocation - 28% Cheaper)",
                "vcpu_rate": 0.0336,
                "ram_rate": 0.0045,
                "sku_prefix": "e2-standard",
                "note": "Shared-core dynamic scheduling; best for microservices & batch"
            },
            "n2": {
                "name": "n2-standard (Balanced Performance Intel Cascade Lake)",
                "vcpu_rate": 0.0465,
                "ram_rate": 0.0057,
                "sku_prefix": "n2-standard",
                "note": "Standard Google Compute Engine baseline with guaranteed QoS"
            },
            "t2d": {
                "name": "t2d-standard (AMD EPYC Milan - 17% Cheaper)",
                "vcpu_rate": 0.0384,
                "ram_rate": 0.0048,
                "sku_prefix": "t2d-standard",
                "note": "Cost-effective scale-out containers and web services"
            },
            "c2": {
                "name": "c2-standard (Compute-Intensive High Clock)",
                "vcpu_rate": 0.0522,
                "ram_rate": 0.0064,
                "sku_prefix": "c2-standard",
                "note": "High-frequency compute for numerical modeling & gaming"
            }
        },
        "regions": {
            "us-central1": {"name": "us-central1 (US Central - Iowa)", "multiplier": 1.00, "note": "Google Low-Carbon Baseline"},
            "us-east4": {"name": "us-east4 (US East - Northern Virginia)", "multiplier": 1.09, "note": "Ashburn Tech Corridor (+9%)"},
            "europe-west3": {"name": "europe-west3 (Europe - Frankfurt)", "multiplier": 1.22, "note": "Frankfurt Colocation (+22%)"},
            "europe-west1": {"name": "europe-west1 (Europe - Belgium)", "multiplier": 1.15, "note": "St. Ghislain Hyperscale (+15%)"},
            "asia-south1": {"name": "asia-south1 (Asia South - Mumbai)", "multiplier": 1.11, "note": "Mumbai Metro (+11%)"},
            "asia-southeast1": {"name": "asia-southeast1 (Asia Southeast - Singapore)", "multiplier": 1.14, "note": "Jurong West Center (+14%)"}
        }
    }
}

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

@app.post("/api/simulate")
def simulate_workload(
    req: SimulateRequest,
    current_user: dict = Depends(get_current_user)
):
    provider_key = req.cloud_provider if req.cloud_provider in REAL_CLOUD_CATALOG else "AWS"
    provider_data = REAL_CLOUD_CATALOG[provider_key]
    families = provider_data.get("families", {})
    regions = provider_data["regions"]
    
    # 1. Select Machine Family
    fam_key = (req.machine_family or "").strip()
    fam_spec = None
    if fam_key in families:
        fam_spec = families[fam_key]
    else:
        for k, v in families.items():
            if k.lower() in fam_key.lower() or fam_key.lower() in k.lower():
                fam_spec = v
                fam_key = k
                break
        if not fam_spec:
            fam_key = list(families.keys())[0]
            fam_spec = families[fam_key]

    # 2. Select Region (exact match or fallback)
    reg_key = req.region.strip()
    reg_spec = None
    if reg_key in regions:
        reg_spec = regions[reg_key]
    else:
        for k, v in regions.items():
            if k in reg_key or reg_key.startswith(k):
                reg_spec = v
                reg_key = k
                break
        if not reg_spec:
            reg_key = list(regions.keys())[0]
            reg_spec = regions[reg_key]
            
    multiplier = reg_spec["multiplier"]
    region_display_name = reg_spec["name"]
    region_note = reg_spec["note"]
    
    # Machine family base rates
    vcpu_base = fam_spec["vcpu_rate"]
    ram_base = fam_spec["ram_rate"]
    
    hourly_rate = ((req.vcpu_count * vcpu_base) + (req.ram_gb * ram_base)) * multiplier
    daily_cost = hourly_rate * req.daily_hours
    monthly_cost = daily_cost * 30
    monthly_savings = monthly_cost * (req.downsize_pct / 100.0)
    
    # Equivalent Instance SKU Name
    sku_prefix = fam_spec.get("sku_prefix", fam_key)
    if provider_key == "AWS":
        size_tag = "8xlarge" if req.vcpu_count >= 32 else "4xlarge" if req.vcpu_count >= 16 else "2xlarge" if req.vcpu_count >= 8 else "xlarge"
        sku = f"{sku_prefix}.{size_tag}"
    elif provider_key == "Azure":
        if "Standard_B" in fam_key:
            sku = f"Standard_B{req.vcpu_count}ms"
        elif "Standard_Das" in fam_key:
            sku = f"Standard_D{req.vcpu_count}as_v5"
        elif "Standard_E" in fam_key:
            sku = f"Standard_E{req.vcpu_count}s_v5"
        else:
            sku = f"Standard_D{req.vcpu_count}s_v5"
    elif provider_key == "GCP":
        sku = f"{sku_prefix}-{req.vcpu_count}"
        
    return {
        "cloud_provider": provider_key,
        "machine_family_key": fam_key,
        "machine_family_name": fam_spec["name"],
        "machine_family_note": fam_spec["note"],
        "region_key": reg_key,
        "region_name": region_display_name,
        "region_note": region_note,
        "multiplier": multiplier,
        "instance_sku": sku,
        "family": fam_spec["name"],
        "base_vcpu_rate": vcpu_base,
        "base_ram_rate": ram_base,
        "hourly_cost_usd": round(hourly_rate, 4),
        "daily_cost_usd": round(daily_cost, 2),
        "monthly_cost_usd": round(monthly_cost, 2),
        "potential_monthly_savings_usd": round(monthly_savings, 2),
        "potential_annual_savings_usd": round(monthly_savings * 12, 2)
    }

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
