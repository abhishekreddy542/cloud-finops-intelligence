"""
Abhi Cloud Tech — Interactive FinOps Database Shell
Allows manual inspection, SQL execution, and querying against finops_warehouse.db.
"""

import os
import sys
import sqlite3
import pandas as pd

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "finops_warehouse.db"))

PRESET_QUERIES = {
    "1": ("View All Registered Users", "SELECT id, user_id, full_name, created_at FROM users;"),
    "2": ("Multi-Cloud Total Spend by Provider", """
        SELECT ProviderName AS CloudProvider,
               count(*) AS RecordCount,
               round(sum(BilledCost), 2) AS TotalSpend_USD,
               round(avg(AvgCpuUtilizationPct), 1) AS AvgCPU_Pct
        FROM unified_focus_billing
        GROUP BY ProviderName
        ORDER BY TotalSpend_USD DESC;
    """),
    "3": ("Top 10 Costliest Resources Across Clouds", """
        SELECT ChargePeriodStart AS Date, ProviderName, TagCostCenter AS Department,
               ServiceName, ResourceId, round(BilledCost, 2) AS DailyCost_USD
        FROM unified_focus_billing
        ORDER BY BilledCost DESC
        LIMIT 10;
    """),
    "4": ("Critical Cost Anomalies (> $500 Surge)", """
        SELECT ChargePeriodStart AS Date, ProviderName, TagCostCenter, ServiceName,
               round(BilledCost, 2) AS Spend_USD, round(EstWasteCostUSD, 2) AS Surge_USD,
               AnomalyType, AvgCpuUtilizationPct
        FROM unified_focus_billing
        WHERE IsAnomaly = 1
        ORDER BY EstWasteCostUSD DESC
        LIMIT 10;
    """),
    "5": ("Department Cost Breakdown", """
        SELECT TagCostCenter AS Department,
               round(sum(BilledCost), 2) AS TotalSpend_USD,
               round(sum(CASE WHEN ProviderName='AWS' THEN BilledCost ELSE 0 END), 2) AS AWS_Spend,
               round(sum(CASE WHEN ProviderName='Azure' THEN BilledCost ELSE 0 END), 2) AS Azure_Spend,
               round(sum(CASE WHEN ProviderName='Google Cloud' THEN BilledCost ELSE 0 END), 2) AS GCP_Spend
        FROM unified_focus_billing
        GROUP BY TagCostCenter
        ORDER BY TotalSpend_USD DESC;
    """),
    "6": ("List All Database Tables and Views", """
        SELECT type, name FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY type, name;
    """)
}

def execute_query(conn, sql: str):
    sql_clean = sql.strip()
    if not sql_clean:
        return
    try:
        # Check if query returns rows
        first_word = sql_clean.split()[0].upper()
        if first_word in ("SELECT", "PRAGMA", "EXPLAIN", "WITH"):
            df = pd.read_sql_query(sql_clean, conn)
            if df.empty:
                print("\n[i] Query returned 0 rows.\n")
            else:
                pd.set_option('display.max_columns', 15)
                pd.set_option('display.width', 120)
                pd.set_option('display.max_colwidth', 40)
                print(f"\n--- Query Result ({len(df)} rows) ---")
                print(df.to_string(index=False))
                print("-" * 60 + "\n")
        else:
            cur = conn.cursor()
            cur.execute(sql_clean)
            conn.commit()
            print(f"\n[+] Statement executed successfully. Rows affected: {cur.rowcount}\n")
    except Exception as e:
        print(f"\n[!] SQL Error: {e}\n")

def interactive_shell():
    if not os.path.exists(DB_PATH):
        print(f"[!] Database not found at: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    print("=" * 70)
    print("  ABHI CLOUD TECH — FINOPS DATABASE MANUAL SHELL")
    print(f"  Connected to: {DB_PATH}")
    print("=" * 70)
    print("\nPreset Quick Queries:")
    for k, (desc, _) in PRESET_QUERIES.items():
        print(f"  [{k}] {desc}")
    print("  [exit / quit] Exit Shell")
    print("\nOr simply type any custom SQL query and press Enter (e.g. SELECT * FROM users;)")
    print("-" * 70)

    while True:
        try:
            user_input = input("FinOps-SQL> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Disconnecting from database. Goodbye!")
                break
            
            # Check if preset number selected
            if user_input in PRESET_QUERIES:
                desc, sql = PRESET_QUERIES[user_input]
                print(f"\n[*] Executing Preset [{user_input}]: {desc}")
                print(f"    SQL: {sql.strip()}")
                execute_query(conn, sql)
            else:
                execute_query(conn, user_input)
        except (KeyboardInterrupt, EOFError):
            print("\nDisconnecting. Goodbye!")
            break

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command-line mode: python scripts/db_shell.py "SELECT ..."
        query = " ".join(sys.argv[1:])
        conn = sqlite3.connect(DB_PATH)
        execute_query(conn, query)
        conn.close()
    else:
        # Interactive mode
        interactive_shell()
