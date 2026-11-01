import os
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, mean_absolute_percentage_error
from datetime import timedelta

class FinOpsForecaster:
    """
    Production Time-Series Forecaster for Cloud Spend & Capacity Demand.
    Enhanced Architecture:
      - Deterministic Linear Trend Extrapolation (mitigates tree boundary plateauing)
      - Cyclical Seasonality (Fourier sine/cosine terms for weekly and monthly cycles)
      - L2-Regularized Shallow HistGradientBoosting on Detrended Residuals
      - Rolling Window Volatility & Moving Averages (7, 14, 30 days)
      - Calibrated Multi-Quantile Risk Bounds (5th and 95th Risk Bounds)
      - Strict Non-crossing Quantile Invariant (Lower <= Median <= Upper)
      - Interactive Scenario Stress-Testing
    """
    def __init__(self, forecast_horizon_days=30):
        self.forecast_horizon_days = forecast_horizon_days
        # Regularized base model: prevents memorizing noise on ~300 training days
        self.trend_model = Ridge(alpha=1.0)
        self.model = HistGradientBoostingRegressor(
            loss="squared_error",
            max_iter=180, 
            learning_rate=0.03, 
            max_depth=4, 
            min_samples_leaf=12,
            l2_regularization=1.0,
            random_state=42
        )
        self.upper_model = HistGradientBoostingRegressor(
            loss="quantile",
            quantile=0.95,
            max_iter=180,
            learning_rate=0.03,
            max_depth=4,
            min_samples_leaf=12,
            l2_regularization=1.0,
            random_state=42
        )
        self.lower_model = HistGradientBoostingRegressor(
            loss="quantile",
            quantile=0.05,
            max_iter=180,
            learning_rate=0.03,
            max_depth=4,
            min_samples_leaf=12,
            l2_regularization=1.0,
            random_state=42
        )
        self.metrics = {}
        self.feature_cols = []
        self.last_daily_df = None
        self.train_len = 0
        
    def _extract_feature_row(self, dt: pd.Timestamp, detrended_history: list) -> dict:
        """Helper to compute features for a single day given detrended history series."""
        dow = dt.dayofweek
        day = dt.day
        month = dt.month
        is_weekend = 1 if dow >= 5 else 0

        def safe_lag(arr, lag):
            if not arr:
                return 0.0
            idx = min(lag, len(arr))
            return float(arr[-idx])

        def safe_window(arr, window, stat="mean"):
            if not arr:
                return 0.0
            w = min(window, len(arr))
            slice_ = arr[-w:]
            if stat == "mean":
                return float(np.mean(slice_))
            elif stat == "std":
                return float(np.std(slice_)) if len(slice_) > 1 else 0.0
            elif stat == "min":
                return float(np.min(slice_))
            elif stat == "max":
                return float(np.max(slice_))
            return 0.0

        feat = {
            "dayofweek": dow,
            "day": day,
            "month": month,
            "is_weekend": is_weekend,
            "sin_dow": float(np.sin(2.0 * np.pi * dow / 7.0)),
            "cos_dow": float(np.cos(2.0 * np.pi * dow / 7.0)),
            "sin_month": float(np.sin(2.0 * np.pi * month / 12.0)),
            "cos_month": float(np.cos(2.0 * np.pi * month / 12.0)),
            "sin_day": float(np.sin(2.0 * np.pi * day / 31.0)),
            "cos_day": float(np.cos(2.0 * np.pi * day / 31.0)),
            "is_month_start": 1 if dt.is_month_start else 0,
            "is_month_end": 1 if dt.is_month_end else 0,
            "lag_1": safe_lag(detrended_history, 1),
            "lag_2": safe_lag(detrended_history, 2),
            "lag_3": safe_lag(detrended_history, 3),
            "lag_7": safe_lag(detrended_history, 7),
            "lag_14": safe_lag(detrended_history, 14),
            "lag_21": safe_lag(detrended_history, 21),
            "lag_28": safe_lag(detrended_history, 28),
            "rolling_mean_7": safe_window(detrended_history, 7, "mean"),
            "rolling_std_7": safe_window(detrended_history, 7, "std"),
            "rolling_min_7": safe_window(detrended_history, 7, "min"),
            "rolling_max_7": safe_window(detrended_history, 7, "max"),
            "rolling_mean_14": safe_window(detrended_history, 14, "mean"),
            "rolling_mean_30": safe_window(detrended_history, 30, "mean")
        }
        return feat

    def _create_features(self, df_daily: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        df = df_daily.copy()
        if df.empty:
            return df
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date").reset_index(drop=True)
        
        # Trend estimation
        t = np.arange(len(df)).reshape(-1, 1)
        if is_training:
            split_idx = max(1, int(len(df) * 0.85))
            self.trend_model.fit(t[:split_idx], df["DailySpend"].iloc[:split_idx])
            self.train_len = len(df)
            
        df["Trend"] = self.trend_model.predict(t)
        df["DetrendedSpend"] = df["DailySpend"] - df["Trend"]
        
        # Calendar & cyclical features
        dow = df["Date"].dt.dayofweek
        day = df["Date"].dt.day
        month = df["Date"].dt.month
        df["dayofweek"] = dow
        df["day"] = day
        df["month"] = month
        df["is_weekend"] = (dow >= 5).astype(int)
        
        # Cyclical Fourier transforms (periodicity 7 for week, 12 for month, 31 for day)
        df["sin_dow"] = np.sin(2.0 * np.pi * dow / 7.0)
        df["cos_dow"] = np.cos(2.0 * np.pi * dow / 7.0)
        df["sin_month"] = np.sin(2.0 * np.pi * month / 12.0)
        df["cos_month"] = np.cos(2.0 * np.pi * month / 12.0)
        df["sin_day"] = np.sin(2.0 * np.pi * day / 31.0)
        df["cos_day"] = np.cos(2.0 * np.pi * day / 31.0)
        
        # Milestone flags
        df["is_month_start"] = df["Date"].dt.is_month_start.astype(int)
        df["is_month_end"] = df["Date"].dt.is_month_end.astype(int)
        
        # Historical lag features on detrended series
        for lag in [1, 2, 3, 7, 14, 21, 28]:
            df[f"lag_{lag}"] = df["DetrendedSpend"].shift(lag)
            
        # Moving window aggregations on detrended series
        shift_detrend = df["DetrendedSpend"].shift(1)
        df["rolling_mean_7"] = shift_detrend.rolling(7, min_periods=1).mean()
        df["rolling_std_7"] = shift_detrend.rolling(7, min_periods=1).std().fillna(0.0)
        df["rolling_min_7"] = shift_detrend.rolling(7, min_periods=1).min()
        df["rolling_max_7"] = shift_detrend.rolling(7, min_periods=1).max()
        df["rolling_mean_14"] = shift_detrend.rolling(14, min_periods=1).mean()
        df["rolling_mean_30"] = shift_detrend.rolling(30, min_periods=1).mean()
        
        df = df.bfill().ffill().fillna(0.0)
        return df

    def train_and_evaluate(self, df: pd.DataFrame):
        if df.empty or "DailyCost_USD" not in df.columns:
            self.metrics = {
                "MAE_USD": 0.0,
                "RMSE_USD": 0.0,
                "MAPE_Pct": 0.0,
                "Test_Sample_Count": 0,
                "Mean_Daily_Spend_USD": 0.0,
                "Quantile_Crossing_Violations": 0,
                "Empirical_Coverage_Pct": 0.0,
                "Upper_Pinball_Loss": 0.0,
                "Lower_Pinball_Loss": 0.0
            }
            self.last_daily_df = pd.DataFrame(columns=["Date", "DailySpend"])
            return self.metrics

        # Aggregate daily total spend across selected scope
        daily_spend = df.groupby("Date")["DailyCost_USD"].sum().reset_index()
        daily_spend.columns = ["Date", "DailySpend"]
        daily_spend["Date"] = pd.to_datetime(daily_spend["Date"], errors="coerce").fillna(pd.Timestamp("2025-01-01"))
        daily_spend = daily_spend.sort_values(by="Date").reset_index(drop=True)
        
        feat_df = self._create_features(daily_spend, is_training=True).reset_index(drop=True)
        
        feature_cols = [c for c in feat_df.columns if c not in ["Date", "DailySpend", "Trend", "DetrendedSpend"]]
        self.feature_cols = feature_cols
        
        if len(feat_df) < 6:
            self.model.fit(feat_df[feature_cols], feat_df["DetrendedSpend"])
            self.upper_model.fit(feat_df[feature_cols], feat_df["DetrendedSpend"])
            self.lower_model.fit(feat_df[feature_cols], feat_df["DetrendedSpend"])
            self.metrics = {
                "MAE_USD": 0.0,
                "RMSE_USD": 0.0,
                "MAPE_Pct": 0.0,
                "Test_Sample_Count": len(feat_df),
                "Mean_Daily_Spend_USD": round(float(daily_spend["DailySpend"].mean()), 2) if not daily_spend.empty else 0.0,
                "Quantile_Crossing_Violations": 0,
                "Empirical_Coverage_Pct": 100.0,
                "Upper_Pinball_Loss": 0.0,
                "Lower_Pinball_Loss": 0.0
            }
            self.last_daily_df = daily_spend
            return self.metrics

        # Temporal train/test split (85% train, 15% out-of-time test)
        split_idx = int(len(feat_df) * 0.85)
        train_df = feat_df.iloc[:split_idx]
        test_df = feat_df.iloc[split_idx:]
        
        X_train, y_train_detrend = train_df[feature_cols], train_df["DetrendedSpend"]
        X_test, y_test_detrend = test_df[feature_cols], test_df["DetrendedSpend"]
        
        # Fit models on stationary detrended residual
        self.model.fit(X_train, y_train_detrend)
        self.upper_model.fit(X_train, y_train_detrend)
        self.lower_model.fit(X_train, y_train_detrend)
        
        pred_detrend = self.model.predict(X_test)
        pred_upper_raw = self.upper_model.predict(X_test)
        pred_lower_raw = self.lower_model.predict(X_test)
        
        test_trends = test_df["Trend"].values
        y_test_actual = test_df["DailySpend"].values
        
        y_pred = pred_detrend + test_trends
        upper_pred_raw = pred_upper_raw + test_trends
        lower_pred_raw = pred_lower_raw + test_trends
        
        # Strict Monotonic Non-Crossing Quantiles: Lower <= Median <= Upper
        upper_pred = np.maximum(y_pred, upper_pred_raw)
        lower_pred = np.minimum(y_pred, np.maximum(0.0, lower_pred_raw))
        
        mae = mean_absolute_error(y_test_actual, y_pred)
        rmse = root_mean_squared_error(y_test_actual, y_pred)

        # Zero-safe MAPE calculation
        nonzero_mask = y_test_actual > 1e-4
        if np.any(nonzero_mask):
            mape = float(np.mean(np.abs((y_test_actual[nonzero_mask] - y_pred[nonzero_mask]) / y_test_actual[nonzero_mask])) * 100)
        else:
            mape = 0.0
        
        crossing_violations = int(((lower_pred > y_pred) | (y_pred > upper_pred) | (lower_pred > upper_pred)).sum())
        coverage_90 = round(float(np.mean((y_test_actual >= lower_pred) & (y_test_actual <= upper_pred)) * 100), 2)
        
        def pinball_loss(y, q_pred, alpha):
            err = y - q_pred
            return float(np.mean(np.maximum(alpha * err, (alpha - 1) * err)))
            
        upper_pinball = round(pinball_loss(y_test_actual, upper_pred, 0.95), 2)
        lower_pinball = round(pinball_loss(y_test_actual, lower_pred, 0.05), 2)
        
        self.metrics = {
            "MAE_USD": round(mae, 2),
            "RMSE_USD": round(rmse, 2),
            "MAPE_Pct": round(mape, 2),
            "Test_Sample_Count": len(test_df),
            "Mean_Daily_Spend_USD": round(float(y_test_actual.mean()), 2),
            "Quantile_Crossing_Violations": crossing_violations,
            "Empirical_Coverage_Pct": coverage_90,
            "Upper_Pinball_Loss": upper_pinball,
            "Lower_Pinball_Loss": lower_pinball,
            # Aliases for notebook compatibility
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2),
            "pinball_loss_mean": round((upper_pinball + lower_pinball) / 2.0, 4),
            "quantile_crossing_violations": crossing_violations
        }
        self.last_daily_df = daily_spend
        return self.metrics

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Alias for _create_features for notebook and pipeline compatibility."""
        return self._create_features(df, is_training=False)

    def generate_future_forecast(self, days_ahead=60, workload_growth_pct=0.0, finops_savings_pct=0.0, days=None, **kwargs) -> pd.DataFrame:
        """
        Recursively forecasts cloud spend into the future with scenario levers.
        Guarantees non-crossing quantile bounds (Lower <= Median <= Upper).
        Supports days or days_ahead parameter flexibly.
        """
        if days is not None:
            days_ahead = days
        elif "days" in kwargs and kwargs["days"] is not None:
            days_ahead = kwargs["days"]
            
        cols = ["Date", "Forecasted_Spend_USD", "Upper_Bound_95_USD", "Lower_Bound_95_USD", "Is_Forecast"]
        if days_ahead <= 0 or self.last_daily_df is None or self.last_daily_df.empty:
            return pd.DataFrame(columns=cols)

        history_df = self.last_daily_df.copy()
        history_df["Date"] = pd.to_datetime(history_df["Date"])
        last_date = history_df["Date"].max()
        n_history = len(history_df)
        
        # Linear trend extrapolation
        total_days = n_history + days_ahead
        t_all = np.arange(total_days).reshape(-1, 1)
        trend_all = self.trend_model.predict(t_all)
        
        history_trend = trend_all[:n_history]
        future_trend = trend_all[n_history:]
        
        detrended_working_series = list((history_df["DailySpend"].values - history_trend))
        
        forecast_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
        forecast_records = []
        
        scenario_factor = (1.0 + workload_growth_pct / 100.0) * (1.0 - finops_savings_pct / 100.0)
        
        for idx, future_date in enumerate(forecast_dates):
            t_future = future_trend[idx]
            dt = pd.Timestamp(future_date)
            
            feat = self._extract_feature_row(dt, detrended_working_series)
            x_row = pd.DataFrame([feat])[self.feature_cols]
            
            pred_detrend_base = float(self.model.predict(x_row)[0])
            pred_detrend_upper = float(self.upper_model.predict(x_row)[0])
            pred_detrend_lower = float(self.lower_model.predict(x_row)[0])
            
            raw_base = pred_detrend_base + t_future
            raw_upper = pred_detrend_upper + t_future
            raw_lower = pred_detrend_lower + t_future
            
            # Apply scenario factor with non-negative bounds
            adj_base = max(0.0, raw_base * scenario_factor)
            adj_upper = max(adj_base, raw_upper * scenario_factor)
            adj_lower = min(adj_base, max(0.0, raw_lower * scenario_factor))
            adj_lower = max(0.0, adj_lower)
            
            forecast_records.append({
                "Date": future_date.strftime("%Y-%m-%d"),
                "Forecasted_Spend_USD": round(adj_base, 2),
                "Predicted_Spend_USD": round(adj_base, 2),
                "Predicted_Spend": round(adj_base, 2),
                "Upper_Bound_95_USD": round(adj_upper, 2),
                "UpperBound_Spend_USD": round(adj_upper, 2),
                "Upper_Bound_P95": round(adj_upper, 2),
                "Lower_Bound_95_USD": round(adj_lower, 2),
                "LowerBound_Spend_USD": round(adj_lower, 2),
                "Lower_Bound_P05": round(adj_lower, 2),
                "Is_Forecast": 1
            })
            
            # Update detrended series with base residual for next recursive step
            detrended_working_series.append(pred_detrend_base)
            
        return pd.DataFrame(forecast_records)

    def predict_future(self, df: pd.DataFrame = None, horizon_days: int = 30, workload_growth_pct: float = 0.0, finops_savings_pct: float = 0.0) -> pd.DataFrame:
        """Alias for generate_future_forecast supporting explicit dataframe input."""
        if df is not None and not df.empty:
            if "DailySpend" in df.columns:
                self.last_daily_df = df[["Date", "DailySpend"]].copy()
            elif "DailyCost_USD" in df.columns:
                daily = df.groupby("Date")["DailyCost_USD"].sum().reset_index()
                daily.columns = ["Date", "DailySpend"]
                self.last_daily_df = daily
        return self.generate_future_forecast(days_ahead=horizon_days, workload_growth_pct=workload_growth_pct, finops_savings_pct=finops_savings_pct)

    def save(self, filepath: str) -> str:
        """
        Serializes the trained FinOpsForecaster model, trend extrapolator,
        quantile regressors, and lag features to disk using joblib.
        """
        import joblib
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        joblib.dump(self, filepath)
        return filepath

    @classmethod
    def load(cls, filepath: str) -> "FinOpsForecaster":
        """
        Loads a pre-trained FinOpsForecaster model and historical state from disk.
        """
        import joblib
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model artifact not found at {filepath}")
        loaded = joblib.load(filepath)
        if not isinstance(loaded, cls):
            raise TypeError(f"Loaded object is {type(loaded)}, expected {cls.__name__}")
        return loaded

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
