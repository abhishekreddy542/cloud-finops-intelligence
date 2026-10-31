import sys
import sqlite3
import pandas as pd

print("Python version:", sys.version)

packages = ["sklearn", "scipy", "statsmodels", "lightgbm", "xgboost", "catboost", "prophet", "torch", "tensorflow", "fastapi"]
for p in packages:
    try:
        mod = __import__(p)
        ver = getattr(mod, "__version__", "installed")
        print(f"  [AVAILABLE] {p}: {ver}")
    except ImportError as e:
        print(f"  [NOT INSTALLED] {p}: {e}")

conn = sqlite3.connect("data/finops_warehouse.db")
cur = conn.cursor()
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("\nTables in data/finops_warehouse.db:")
for t in tables:
    t_name = t[0]
    count = cur.execute(f"SELECT count(*) FROM {t_name}").fetchone()[0]
    print(f" - {t_name}: {count} records")
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({t_name})").fetchall()]
    print(f"    Columns ({len(cols)}): {cols}")

conn.close()
