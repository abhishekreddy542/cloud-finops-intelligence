import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, mean_absolute_percentage_error
from datetime import timedelta

class FinOpsForecaster:
    """
    Production Time-Series Forecaster for Cloud Spend & Capacity Demand.
    Features:
      - Calendar & Cyclical Seasonality
      - Lag & Moving Window Volatility Indicators
      - Multi-Quantile Loss Ensembles (5th and 95th Risk Bounds)
      - Non-crossing Quantile Guarantees
      - Interactive Scenario Stress-Testing
    """
    def __init__(self, forecast_horizon_days=30):
        self.forecast_horizon_days = forecast_horizon_days
        self.model = HistGradientBoostingRegressor(
            loss="squared_error",
            max_iter=300, 
            learning_rate=0.04, 
            max_depth=6, 
            min_samples_leaf=10,
            random_state=42
        )
        self.upper_model = HistGradientBoostingRegressor(
            loss="quantile", quantile=0.95, max_iter=300, learning_rate=0.04, max_depth=6, min_samples_leaf=10, random_state=42
        )
        self.lower_model = HistGradientBoostingRegressor(
            loss="quantile", quantile=0.05, max_iter=300, learning_rate=0.04, max_depth=6, min_samples_leaf=10, random_state=42
        )
        self.metrics = {}
        
    def _create_features(self, df_daily: pd.DataFrame) -> pd.DataFrame:
        df = df_daily.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date").reset_index(drop=True)
        
        # Calendar & cyclical features
        df["dayofweek"] = df["Date"].dt.dayofweek
        df["day"] = df["Date"].dt.day
        df["month"] = df["Date"].dt.month
        df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
        df["trend"] = np.arange(len(df))
        
        # Historical lag features (strictly backward-looking to avoid leakage)
        for lag in [1, 2, 3, 7, 14, 21, 28]:
            df[f"lag_{lag}"] = df["DailySpend"].shift(lag)
            
        # Moving window aggregations
        df["rolling_mean_7"] = df["DailySpend"].shift(1).rolling(7).mean()
        df["rolling_std_7"] = df["DailySpend"].shift(1).rolling(7).std()
        df["rolling_mean_14"] = df["DailySpend"].shift(1).rolling(14).mean()
        df["rolling_mean_30"] = df["DailySpend"].shift(1).rolling(30).mean()
        
        return df

    def train_and_evaluate(self, df: pd.DataFrame):
        # Aggregate daily total spend across selected scope
        daily_spend = df.groupby("Date")["DailyCost_USD"].sum().reset_index()
        daily_spend.columns = ["Date", "DailySpend"]
        
        feat_df = self._create_features(daily_spend).dropna()
        
        feature_cols = [c for c in feat_df.columns if c not in ["Date", "DailySpend"]]
        
        # Temporal train/test split (85% train, 15% out-of-time test)
        split_idx = int(len(feat_df) * 0.85)
        train_df = feat_df.iloc[:split_idx]
        test_df = feat_df.iloc[split_idx:]
        
        X_train, y_train = train_df[feature_cols], train_df["DailySpend"]
        X_test, y_test = test_df[feature_cols], test_df["DailySpend"]
        
        # Fit models
        self.model.fit(X_train, y_train)
        self.upper_model.fit(X_train, y_train)
        self.lower_model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100
        
        self.metrics = {
            "MAE_USD": round(mae, 2),
            "RMSE_USD": round(rmse, 2),
            "MAPE_Pct": round(mape, 2),
            "Test_Sample_Count": len(test_df),
            "Mean_Daily_Spend_USD": round(float(y_test.mean()), 2)
        }
        self.last_daily_df = daily_spend
        self.feature_cols = feature_cols
        return self.metrics

    def generate_future_forecast(self, days_ahead=60, workload_growth_pct=0.0, finops_savings_pct=0.0) -> pd.DataFrame:
        """
        Recursively forecasts cloud spend into the future with scenario levers.
        Guarantees non-crossing quantile bounds (Lower <= Median <= Upper).
        """
        history_df = self.last_daily_df.copy()
        history_df["Date"] = pd.to_datetime(history_df["Date"])
        last_date = history_df["Date"].max()
        
        forecast_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
        forecast_records = []
        
        working_series = list(history_df["DailySpend"].values)
        dates_all = list(history_df["Date"].values)
        
        scenario_factor = (1.0 + workload_growth_pct / 100.0) * (1.0 - finops_savings_pct / 100.0)
        
        for future_date in forecast_dates:
            t = len(dates_all)
            dow = pd.Timestamp(future_date).dayofweek
            day = pd.Timestamp(future_date).day
            month = pd.Timestamp(future_date).month
            is_weekend = 1 if dow >= 5 else 0
            
            feat = {
                "dayofweek": dow,
                "day": day,
                "month": month,
                "is_weekend": is_weekend,
                "trend": t,
                "lag_1": working_series[-1],
                "lag_2": working_series[-2],
                "lag_3": working_series[-3],
                "lag_7": working_series[-7],
                "lag_14": working_series[-14],
                "lag_21": working_series[-21],
                "lag_28": working_series[-28],
                "rolling_mean_7": float(np.mean(working_series[-7:])),
                "rolling_std_7": float(np.std(working_series[-7:])),
                "rolling_mean_14": float(np.mean(working_series[-14:])),
                "rolling_mean_30": float(np.mean(working_series[-30:]))
            }
            
            x_row = pd.DataFrame([feat])[self.feature_cols]
            pred_base = float(self.model.predict(x_row)[0])
            pred_upper = float(self.upper_model.predict(x_row)[0])
            pred_lower = float(self.lower_model.predict(x_row)[0])
            
            # Apply scenario factor
            adj_base = pred_base * scenario_factor
            adj_upper = max(adj_base, pred_upper * scenario_factor)
            adj_lower = min(adj_base, max(0.0, pred_lower * scenario_factor))
            
            forecast_records.append({
                "Date": future_date.strftime("%Y-%m-%d"),
                "Forecasted_Spend_USD": round(adj_base, 2),
                "Upper_Bound_95_USD": round(adj_upper, 2),
                "Lower_Bound_95_USD": round(adj_lower, 2),
                "Is_Forecast": 1
            })
            
            working_series.append(adj_base)
            dates_all.append(future_date)
            
        return pd.DataFrame(forecast_records)

if __name__ == "__main__":
    import os
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "cloud_enterprise_billing_telemetry.csv")
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        forecaster = FinOpsForecaster()
        metrics = forecaster.train_and_evaluate(df)
        print("Model Performance Metrics:", metrics)
        future_df = forecaster.generate_future_forecast(days_ahead=30, workload_growth_pct=10)
        print(future_df.head())
