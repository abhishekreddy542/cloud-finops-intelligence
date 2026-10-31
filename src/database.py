import os
import sqlite3
import hashlib
import secrets
import pandas as pd
from typing import Optional, List
from sqlalchemy import create_engine, text, Engine

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "finops_warehouse.db")
DB_PATH = os.path.abspath(DB_PATH)

_cached_engine: Optional[Engine] = None

FOCUS_COLUMNS = [
    "RecordId", "Date", "CloudProvider", "Department", "ServiceName",
    "ServiceCategory", "Service", "RegionId", "RegionName", "ResourceId",
    "ResourceName", "SkuDescription", "ConsumedQuantity", "ConsumedUnit",
    "DailyCost_USD", "EffectiveCost", "ListCost", "PricingCategory",
    "TagEnvironment", "Avg_CPU_Utilization_Pct", "MaxCpuUtilizationPct",
    "vCPU_Hours", "Memory_GB_Hours", "Storage_TB", "Data_Egress_GB",
    "Is_Anomaly", "Anomaly_Type", "Est_Waste_Cost_USD"
]

def get_engine(db_path: Optional[str] = None) -> Engine:
    """
    Returns a managed SQLAlchemy Engine singleton to prevent connection leaks
    and file locking on SQLite databases.
    """
    global _cached_engine
    target_path = os.path.abspath(db_path or DB_PATH)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    if db_path is not None:
        # Separate engine instance for isolated test databases
        return create_engine(f"sqlite:///{target_path}", pool_pre_ping=True)
        
    if _cached_engine is None:
        _cached_engine = create_engine(f"sqlite:///{target_path}", pool_pre_ping=True)
    return _cached_engine

def close_engine():
    """Explicitly closes and disposes cached engine pool to prevent connection leaks."""
    global _cached_engine
    if _cached_engine is not None:
        _cached_engine.dispose()
        _cached_engine = None

def initialize_database(db_path: Optional[str] = None):
    """
    Initializes the SQLite FinOps Data Warehouse with FOCUS 1.0 Specification schema:
    FinOps Open Cost and Usage Specification (supported by AWS, Azure, Google Cloud).
    Includes high-performance compound indexing for multi-cloud OLAP queries.
    """
    engine = get_engine(db_path)
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS unified_focus_billing (
            RecordId TEXT PRIMARY KEY,
            ChargePeriodStart TEXT NOT NULL,
            ChargePeriodEnd TEXT NOT NULL,
            ProviderName TEXT NOT NULL,           -- 'AWS', 'Azure', 'Google Cloud'
            BillingAccountId TEXT NOT NULL,
            SubAccountId TEXT NOT NULL,           -- AWS Account ID / Azure Sub ID / GCP Project ID
            SubAccountName TEXT NOT NULL,
            RegionId TEXT NOT NULL,               -- e.g. 'us-east-1', 'eastus', 'us-central1'
            RegionName TEXT NOT NULL,
            ServiceName TEXT NOT NULL,           -- e.g. 'AmazonEC2', 'Compute Engine', 'Microsoft.Compute'
            ServiceCategory TEXT NOT NULL,       -- 'Compute', 'Storage', 'Database', 'Network', 'Containers'
            ResourceId TEXT NOT NULL,             -- Full canonical ARN, Azure ID, or GCP URI
            ResourceName TEXT NOT NULL,           -- Hostname / Resource tag
            ResourceType TEXT NOT NULL,           -- Virtual Machine, Storage Bucket, Relational DB
            SkuId TEXT NOT NULL,                  -- Cloud SKU ID
            SkuDescription TEXT NOT NULL,         -- e.g. 'm6i.4xlarge On Demand', 'Standard D4s v5'
            ConsumedQuantity REAL NOT NULL,       -- Usage quantity (Hours, GB, TB)
            ConsumedUnit TEXT NOT NULL,           -- 'Hours', 'GB', 'TB'
            BilledCost REAL NOT NULL,             -- Billed cost in USD
            EffectiveCost REAL NOT NULL,          -- Amortized cost after commitments
            ListCost REAL NOT NULL,               -- Public on-demand rate
            PricingCategory TEXT NOT NULL,        -- 'On-Demand', 'CommitmentDiscount', 'Spot'
            ChargeCategory TEXT NOT NULL,         -- 'Usage', 'Purchase', 'Tax', 'Adjustment'
            TagCostCenter TEXT NOT NULL,          -- 'AI/ML Research', 'Data Platform', etc.
            TagEnvironment TEXT NOT NULL,         -- 'Production', 'Staging', 'Research'
            TagOwner TEXT NOT NULL,
            -- Telemetry metrics joined from CloudWatch / Azure Monitor / Google Cloud Operations
            AvgCpuUtilizationPct REAL NOT NULL,
            MaxCpuUtilizationPct REAL NOT NULL,
            MemoryAllocatedGB REAL NOT NULL,
            StorageAllocatedTB REAL NOT NULL,
            NetworkEgressGB REAL NOT NULL,
            IsAnomaly INTEGER DEFAULT 0,
            AnomalyType TEXT DEFAULT 'None',
            EstWasteCostUSD REAL DEFAULT 0.0
        );
        """))
        
        # Compound Indices for sub-second analytical slicing
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_focus_date ON unified_focus_billing(ChargePeriodStart);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_focus_provider ON unified_focus_billing(ProviderName);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_focus_category ON unified_focus_billing(ServiceCategory);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_focus_dept ON unified_focus_billing(TagCostCenter);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_focus_compound ON unified_focus_billing(ProviderName, TagCostCenter, ServiceCategory);"))

        # Create billing_records backwards-compatibility view
        conn.execute(text("""
        CREATE VIEW IF NOT EXISTS billing_records AS 
        SELECT 
            RecordId, 
            ChargePeriodStart as Date, 
            ProviderName as CloudProvider, 
            ProviderName as Provider, 
            TagCostCenter as Department, 
            ServiceName, 
            ServiceCategory, 
            ServiceName || ' (' || ServiceCategory || ')' as Service, 
            RegionId, 
            RegionName, 
            ResourceId, 
            ResourceName, 
            SkuDescription, 
            ConsumedQuantity, 
            ConsumedUnit, 
            BilledCost as DailyCost_USD, 
            EffectiveCost, 
            ListCost, 
            PricingCategory, 
            TagEnvironment, 
            AvgCpuUtilizationPct as Avg_CPU_Utilization_Pct, 
            MaxCpuUtilizationPct, 
            StorageAllocatedTB, 
            MemoryAllocatedGB, 
            NetworkEgressGB, 
            ConsumedQuantity as vCPU_Hours, 
            MemoryAllocatedGB as Memory_GB_Hours, 
            StorageAllocatedTB as Storage_TB, 
            NetworkEgressGB as Data_Egress_GB, 
            IsAnomaly as Is_Anomaly, 
            AnomalyType as Anomaly_Type, 
            EstWasteCostUSD as Est_Waste_Cost_USD, 
            EstWasteCostUSD as Waste_Cost_USD 
        FROM unified_focus_billing;
        """))
        conn.commit()
    init_users_table(db_path)
    seed_default_users(db_path)
    print(f"FinOps Data Warehouse initialized at: {db_path or DB_PATH}")

class FinOpsDatabase:
    """Wrapper class providing an object-oriented interface to the FinOps Data Warehouse."""
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = os.path.abspath(db_path or DB_PATH)
        self.engine = get_engine(self.db_path)
        initialize_database(self.db_path)

    def load_data(self, **kwargs) -> pd.DataFrame:
        return load_focus_dataframe(engine=self.engine, **kwargs)

    def get_connection(self):
        return sqlite3.connect(self.db_path)

def init_users_table(db_path: Optional[str] = None):
    """Initializes the users table for credentials storage in the SQLite warehouse."""
    engine = get_engine(db_path)
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_userid ON users(user_id);"))
        conn.commit()

def hash_password(password: str, salt: Optional[str] = None, iterations: int = 600000) -> tuple:
    """Enterprise PBKDF2-HMAC-SHA256 password hashing with individual salts (OWASP standard: 600,000 iterations)."""
    if not salt:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations).hex()
    return pwd_hash, salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """Verifies a plaintext password against the stored PBKDF2 hash using constant-time comparison."""
    # Verify with OWASP 600,000 iterations
    pwd_hash_600k, _ = hash_password(password, salt, iterations=600000)
    if secrets.compare_digest(pwd_hash_600k, password_hash):
        return True
    # Backwards compatibility check with 100,000 iterations
    pwd_hash_100k, _ = hash_password(password, salt, iterations=100000)
    return secrets.compare_digest(pwd_hash_100k, password_hash)

def register_user(user_id: str, password: str, full_name: Optional[str] = None, db_path: Optional[str] = None) -> dict:
    """
    Registers a new user into the database.
    Enforces uniqueness on user_id (case-insensitive), minimum 8-character password policy,
    and secure PBKDF2-600k password hashing.
    """
    clean_id = (user_id or "").strip()
    if not clean_id:
        raise ValueError("User ID cannot be empty.")
    if len(clean_id) < 3 or len(clean_id) > 50:
        raise ValueError("User ID must be between 3 and 50 characters.")
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    
    clean_name = (full_name or "").strip() or clean_id
    init_users_table(db_path)
    engine = get_engine(db_path)
    with engine.connect() as conn:
        existing = conn.execute(
            text("SELECT user_id FROM users WHERE lower(user_id) = lower(:uid)"),
            {"uid": clean_id}
        ).fetchone()
        if existing:
            raise ValueError(f"User ID '{clean_id}' already exists. Please choose a different User ID or sign in.")
        
        pwd_hash, salt = hash_password(password, iterations=600000)
        conn.execute(
            text("INSERT INTO users (user_id, full_name, password_hash, salt) VALUES (:uid, :name, :hash, :salt)"),
            {"uid": clean_id, "name": clean_name, "hash": pwd_hash, "salt": salt}
        )
        conn.commit()
    return {"user_id": clean_id, "full_name": clean_name}

def authenticate_user(user_id: str, password: str, db_path: Optional[str] = None) -> Optional[dict]:
    """
    Authenticates a user against the database credentials store.
    Returns user details dictionary on success, or None on failure.
    """
    clean_id = (user_id or "").strip()
    if not clean_id or not password:
        return None
    init_users_table(db_path)
    engine = get_engine(db_path)
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT user_id, full_name, password_hash, salt FROM users WHERE lower(user_id) = lower(:uid)"),
            {"uid": clean_id}
        ).fetchone()
        if not row:
            return None
        db_uid, db_name, db_hash, db_salt = row
        if verify_password(password, db_hash, db_salt):
            return {"user_id": db_uid, "full_name": db_name}
        return None

def seed_default_users(db_path: Optional[str] = None):
    """Seeds default enterprise accounts into the database if not already present."""
    init_users_table(db_path)
    defaults = [
        ("abhishek", "password123", "M Abhishek Reddy"),
        ("admin", "admin123", "FinOps Administrator")
    ]
    for uid, pwd, name in defaults:
        try:
            register_user(uid, pwd, name, db_path)
        except ValueError:
            pass # Already exists

def optimize_database(db_path: Optional[str] = None):
    """
    Runs SQLite PRAGMA analyze and optimize for maximum query execution performance.
    """
    engine = get_engine(db_path)
    with engine.connect() as conn:
        conn.execute(text("PRAGMA analyze;"))
        conn.execute(text("PRAGMA optimize;"))
        conn.commit()

def load_focus_dataframe(
    providers: Optional[List[str]] = None,
    departments: Optional[List[str]] = None,
    service_categories: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    engine: Optional[Engine] = None
) -> pd.DataFrame:
    """
    Reads normalized FOCUS 1.0 records from SQLite database with compound query filtering.
    Safe against SQL injection with strict parameter binding.
    """
    eng = engine or get_engine()
    
    # Check if table exists
    with eng.connect() as conn:
        check_table = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='unified_focus_billing';")
        ).fetchone()
        if not check_table:
            return pd.DataFrame(columns=FOCUS_COLUMNS)
            
    where_clauses = []
    params = {}
    
    if providers:
        placeholders = []
        for i, prov in enumerate(providers):
            key = f"prov_{i}"
            placeholders.append(f":{key}")
            params[key] = prov
        where_clauses.append(f"ProviderName IN ({', '.join(placeholders)})")
        
    if departments:
        placeholders = []
        for i, dept in enumerate(departments):
            key = f"dept_{i}"
            placeholders.append(f":{key}")
            params[key] = dept
        where_clauses.append(f"TagCostCenter IN ({', '.join(placeholders)})")
        
    if service_categories:
        placeholders = []
        for i, cat in enumerate(service_categories):
            key = f"cat_{i}"
            placeholders.append(f":{key}")
            params[key] = cat
        where_clauses.append(f"ServiceCategory IN ({', '.join(placeholders)})")
        
    if start_date:
        where_clauses.append("ChargePeriodStart >= :start_date")
        params["start_date"] = start_date
        
    if end_date:
        where_clauses.append("ChargePeriodStart <= :end_date")
        params["end_date"] = end_date
        
    if min_cost is not None:
        where_clauses.append("BilledCost >= :min_cost")
        params["min_cost"] = float(min_cost)
        
    if max_cost is not None:
        where_clauses.append("BilledCost <= :max_cost")
        params["max_cost"] = float(max_cost)
        
    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)
        
    query_str = f"""
    SELECT 
        RecordId,
        ChargePeriodStart as Date,
        ProviderName as CloudProvider,
        TagCostCenter as Department,
        ServiceName,
        ServiceCategory,
        ServiceName || ' (' || ServiceCategory || ')' as Service,
        RegionId,
        RegionName,
        ResourceId,
        ResourceName,
        SkuDescription,
        ConsumedQuantity,
        ConsumedUnit,
        BilledCost as DailyCost_USD,
        EffectiveCost,
        ListCost,
        PricingCategory,
        TagEnvironment,
        AvgCpuUtilizationPct as Avg_CPU_Utilization_Pct,
        MaxCpuUtilizationPct,
        ConsumedQuantity as vCPU_Hours,
        MemoryAllocatedGB as Memory_GB_Hours,
        StorageAllocatedTB as Storage_TB,
        NetworkEgressGB as Data_Egress_GB,
        IsAnomaly as Is_Anomaly,
        AnomalyType as Anomaly_Type,
        EstWasteCostUSD as Est_Waste_Cost_USD
    FROM unified_focus_billing
    {where_sql}
    ORDER BY ChargePeriodStart ASC
    """
    
    with eng.connect() as conn:
        df = pd.read_sql_query(text(query_str), conn, params=params)
        
    if df.empty:
        return pd.DataFrame(columns=FOCUS_COLUMNS)
    return df

def get_daily_spend_summary(start_date=None, end_date=None, provider=None, department=None) -> pd.DataFrame:
    eng = get_engine()
    where = ["1=1"]
    params = {}
    if start_date:
        where.append("ChargePeriodStart >= :start_date")
        params["start_date"] = start_date
    if end_date:
        where.append("ChargePeriodStart <= :end_date")
        params["end_date"] = end_date
    if provider:
        where.append("ProviderName = :provider")
        params["provider"] = provider
    if department:
        where.append("TagCostCenter = :department")
        params["department"] = department
        
    q = f"""
    SELECT ChargePeriodStart as Date, ProviderName as CloudProvider, TagCostCenter as Department,
           round(sum(BilledCost), 2) as TotalSpend_USD, round(avg(AvgCpuUtilizationPct), 1) as AvgCPU_Pct,
           count(*) as RecordCount, max(IsAnomaly) as HasAnomaly
    FROM unified_focus_billing
    WHERE {' AND '.join(where)}
    GROUP BY ChargePeriodStart, ProviderName, TagCostCenter
    ORDER BY ChargePeriodStart ASC
    """
    with eng.connect() as conn:
        return pd.read_sql_query(text(q), conn, params=params)

def get_monthly_provider_summary(provider=None) -> pd.DataFrame:
    eng = get_engine()
    where = ["1=1"]
    params = {}
    if provider:
        where.append("ProviderName = :provider")
        params["provider"] = provider
        
    q = f"""
    SELECT substr(ChargePeriodStart, 1, 7) as Month, ProviderName as CloudProvider,
           round(sum(BilledCost), 2) as MonthlySpend_USD, round(sum(EstWasteCostUSD), 2) as WasteCost_USD,
           count(*) as RecordCount
    FROM unified_focus_billing
    WHERE {' AND '.join(where)}
    GROUP BY substr(ChargePeriodStart, 1, 7), ProviderName
    ORDER BY Month ASC, ProviderName ASC
    """
    with eng.connect() as conn:
        return pd.read_sql_query(text(q), conn, params=params)

def get_department_summary(department=None) -> pd.DataFrame:
    eng = get_engine()
    where = ["1=1"]
    params = {}
    if department:
        where.append("TagCostCenter = :department")
        params["department"] = department
        
    q = f"""
    SELECT TagCostCenter as Department, ProviderName as CloudProvider,
           round(sum(BilledCost), 2) as TotalSpend_USD, round(avg(AvgCpuUtilizationPct), 1) as AvgCPU_Pct,
           round(sum(EstWasteCostUSD), 2) as WasteCost_USD
    FROM unified_focus_billing
    WHERE {' AND '.join(where)}
    GROUP BY TagCostCenter, ProviderName
    ORDER BY TotalSpend_USD DESC
    """
    with eng.connect() as conn:
        return pd.read_sql_query(text(q), conn, params=params)

def get_active_anomalies(limit: int = 50) -> pd.DataFrame:
    eng = get_engine()
    q = f"""
    SELECT ChargePeriodStart as Date, ProviderName as CloudProvider, TagCostCenter as Department,
           ServiceName as Service, RegionName, ResourceId, round(BilledCost, 2) as DailyCost_USD,
           round(EstWasteCostUSD, 2) as CostSpike_USD, AnomalyType, AvgCpuUtilizationPct
    FROM unified_focus_billing
    WHERE IsAnomaly = 1
    ORDER BY BilledCost DESC
    LIMIT {int(limit)}
    """
    with eng.connect() as conn:
        return pd.read_sql_query(text(q), conn)

def get_service_efficiency_summary() -> pd.DataFrame:
    eng = get_engine()
    q = """
    SELECT ServiceName, ServiceCategory, ProviderName as CloudProvider,
           round(sum(BilledCost), 2) as TotalSpend_USD, round(avg(AvgCpuUtilizationPct), 1) as AvgCPU_Pct,
           round(sum(EstWasteCostUSD), 2) as TotalWaste_USD, count(*) as UsageCount
    FROM unified_focus_billing
    GROUP BY ServiceName, ServiceCategory, ProviderName
    ORDER BY TotalSpend_USD DESC
    """
    with eng.connect() as conn:
        return pd.read_sql_query(text(q), conn)

if __name__ == "__main__":
    initialize_database()
