import pandas as pd

df_csv = pd.read_csv("data/cloud_enterprise_billing_telemetry.csv", nrows=5)
print("Columns in cloud_enterprise_billing_telemetry.csv:")
print(list(df_csv.columns))
print("Sample row:")
print(df_csv.iloc[0].to_dict())

df_csv_latest = pd.read_csv("data/cloud_enterprise_billing_telemetry_latest.csv", nrows=5)
print("\nColumns in cloud_enterprise_billing_telemetry_latest.csv:")
print(list(df_csv_latest.columns))
