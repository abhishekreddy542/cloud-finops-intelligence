import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect("data/finops_warehouse.db")
df = pd.read_sql_query("SELECT * FROM unified_focus_billing", conn)
conn.close()

print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print("\nIsAnomaly value counts:")
print(df["IsAnomaly"].value_counts(dropna=False))

print("\nAnomalyType value counts:")
print(df["AnomalyType"].value_counts(dropna=False))

print("\nEstWasteCostUSD summary for anomalies:")
print(df[df["IsAnomaly"] == 1]["EstWasteCostUSD"].describe())

print("\nDate range (ChargePeriodStart):")
print(df["ChargePeriodStart"].min(), "to", df["ChargePeriodStart"].max())

# Aggregated daily spend
daily = df.groupby("ChargePeriodStart")["EffectiveCost"].sum().reset_index()
print("\nDaily spend stats:")
print(daily["EffectiveCost"].describe())
print(f"Total days: {len(daily)}")
