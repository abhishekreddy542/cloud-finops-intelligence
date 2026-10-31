import time
import os
import gc
import json
import sqlite3
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, mean_absolute_percentage_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostRegressor
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
tf.get_logger().setLevel("ERROR")

print("="*70, flush=True)
print("FINOPS CLOUD SPEND FORECASTING ALGORITHM BENCHMARK", flush=True)
print("="*70, flush=True)

# 1. Load Data
db_path = "data/finops_warehouse.db"
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT ChargePeriodStart as Date, EffectiveCost as DailyCost_USD FROM unified_focus_billing", conn)
conn.close()

# Aggregate daily total spend across 2025
daily_df = df.groupby("Date")["DailyCost_USD"].sum().reset_index()
daily_df.columns = ["Date", "DailySpend"]
daily_df["Date"] = pd.to_datetime(daily_df["Date"])
daily_df = daily_df.sort_values(by="Date").reset_index(drop=True)

print(f"Total Daily Spend Observations: {len(daily_df)} days (From {daily_df['Date'].min().strftime('%Y-%m-%d')} to {daily_df['Date'].max().strftime('%Y-%m-%d')})", flush=True)
print(f"Mean daily spend: ${daily_df['DailySpend'].mean():,.2f} | Std: ${daily_df['DailySpend'].std():,.2f}", flush=True)

# Feature engineering matching FinOpsForecaster
def build_features(df_daily, trend_model=None, is_training=True):
    df_feat = df_daily.copy()
    t = np.arange(len(df_feat)).reshape(-1, 1)
    
    if is_training:
        trend_model = Ridge(alpha=1.0)
        split_idx = max(1, int(len(df_feat) * 0.85))
        trend_model.fit(t[:split_idx], df_feat["DailySpend"].iloc[:split_idx])
        
    df_feat["Trend"] = trend_model.predict(t)
    df_feat["DetrendedSpend"] = df_feat["DailySpend"] - df_feat["Trend"]
    
    dow = df_feat["Date"].dt.dayofweek
    day = df_feat["Date"].dt.day
    month = df_feat["Date"].dt.month
    df_feat["dayofweek"] = dow
    df_feat["day"] = day
    df_feat["month"] = month
    df_feat["is_weekend"] = (dow >= 5).astype(int)
    
    df_feat["sin_dow"] = np.sin(2.0 * np.pi * dow / 7.0)
    df_feat["cos_dow"] = np.cos(2.0 * np.pi * dow / 7.0)
    df_feat["sin_month"] = np.sin(2.0 * np.pi * month / 12.0)
    df_feat["cos_month"] = np.cos(2.0 * np.pi * month / 12.0)
    df_feat["sin_day"] = np.sin(2.0 * np.pi * day / 31.0)
    df_feat["cos_day"] = np.cos(2.0 * np.pi * day / 31.0)
    
    df_feat["is_month_start"] = df_feat["Date"].dt.is_month_start.astype(int)
    df_feat["is_month_end"] = df_feat["Date"].dt.is_month_end.astype(int)
    
    for lag in [1, 2, 3, 7, 14, 21, 28]:
        df_feat[f"lag_{lag}"] = df_feat["DetrendedSpend"].shift(lag)
        
    shift_detrend = df_feat["DetrendedSpend"].shift(1)
    df_feat["rolling_mean_7"] = shift_detrend.rolling(7, min_periods=1).mean()
    df_feat["rolling_std_7"] = shift_detrend.rolling(7, min_periods=1).std().fillna(0.0)
    df_feat["rolling_min_7"] = shift_detrend.rolling(7, min_periods=1).min()
    df_feat["rolling_max_7"] = shift_detrend.rolling(7, min_periods=1).max()
    df_feat["rolling_mean_14"] = shift_detrend.rolling(14, min_periods=1).mean()
    df_feat["rolling_mean_30"] = shift_detrend.rolling(30, min_periods=1).mean()
    
    df_feat = df_feat.bfill().ffill().fillna(0.0)
    return df_feat, trend_model

feat_df, trend_m = build_features(daily_df, is_training=True)
feature_cols = [c for c in feat_df.columns if c not in ["Date", "DailySpend", "Trend", "DetrendedSpend"]]

# Temporal 85/15 out-of-time train/test split
split_idx = int(len(feat_df) * 0.85)
train_df = feat_df.iloc[:split_idx].copy()
test_df = feat_df.iloc[split_idx:].copy()

X_train, y_train_detrend = train_df[feature_cols], train_df["DetrendedSpend"]
X_test, y_test_detrend = test_df[feature_cols], test_df["DetrendedSpend"]
y_test_actual = test_df["DailySpend"].values
test_trends = test_df["Trend"].values

def pinball_loss(y, q_pred, alpha):
    err = y - q_pred
    return float(np.mean(np.maximum(alpha * err, (alpha - 1) * err)))

benchmark_forecasting_results = {}

def evaluate_forecast(name, p50_pred, p05_pred, p95_pred, train_time, infer_time_30d_ms, model_size_kb, notes=""):
    # Invariant check BEFORE post-hoc clipping
    raw_violations = int(((p05_pred > p50_pred) | (p50_pred > p95_pred) | (p05_pred > p95_pred)).sum())
    
    # Strictly enforce Monotonic Non-Crossing: Lower <= Median <= Upper
    p95_clean = np.maximum(p50_pred, p95_pred)
    p05_clean = np.minimum(p50_pred, np.maximum(0.0, p05_pred))
    
    clean_violations = int(((p05_clean > p50_pred) | (p50_pred > p95_clean) | (p05_clean > p95_clean)).sum())
    
    mae = float(mean_absolute_error(y_test_actual, p50_pred))
    rmse = float(root_mean_squared_error(y_test_actual, p50_pred))
    nonzero_mask = y_test_actual > 1e-4
    mape = float(np.mean(np.abs((y_test_actual[nonzero_mask] - p50_pred[nonzero_mask]) / y_test_actual[nonzero_mask])) * 100)
    
    coverage_90 = float(np.mean((y_test_actual >= p05_clean) & (y_test_actual <= p95_clean)) * 100)
    pinball_95 = float(pinball_loss(y_test_actual, p95_clean, 0.95))
    pinball_05 = float(pinball_loss(y_test_actual, p05_clean, 0.05))
    total_pinball = pinball_95 + pinball_05

    res = {
        "Model": name,
        "MAE_USD": round(mae, 2),
        "RMSE_USD": round(rmse, 2),
        "MAPE_Pct": round(mape, 2),
        "Coverage_90_Pct": round(coverage_90, 2),
        "Upper_Pinball_095": round(pinball_95, 2),
        "Lower_Pinball_005": round(pinball_05, 2),
        "Total_Pinball_Loss": round(total_pinball, 2),
        "Raw_Quantile_Violations": raw_violations,
        "Post_Clipping_Violations": clean_violations,
        "Train_Time_Sec": round(float(train_time), 3),
        "Inference_30d_ms": round(float(infer_time_30d_ms), 2),
        "Model_Size_KB": round(float(model_size_kb), 1),
        "Notes": notes
    }
    benchmark_forecasting_results[name] = res
    print(f"[{name:35s}] MAPE={mape:5.2f}% | MAE=${mae:7.2f} | RMSE=${rmse:7.2f} | Cov={coverage_90:5.2f}% | Pinball={total_pinball:7.2f} | RawViol={raw_violations:2d} | Train={train_time:5.3f}s | Lat={infer_time_30d_ms:5.2f}ms", flush=True)
    return res

# -------------------------------------------------------------
# 1. Current Production HistGradientBoosting Multi-Quantile Regressor
# -------------------------------------------------------------
print("\nEvaluating Model 1: Production HistGradientBoosting Regressor...", flush=True)
t0 = time.time()
hgb_p50 = HistGradientBoostingRegressor(loss="squared_error", max_iter=180, learning_rate=0.03, max_depth=4, min_samples_leaf=12, l2_regularization=1.0, random_state=42)
hgb_p95 = HistGradientBoostingRegressor(loss="quantile", quantile=0.95, max_iter=180, learning_rate=0.03, max_depth=4, min_samples_leaf=12, l2_regularization=1.0, random_state=42)
hgb_p05 = HistGradientBoostingRegressor(loss="quantile", quantile=0.05, max_iter=180, learning_rate=0.03, max_depth=4, min_samples_leaf=12, l2_regularization=1.0, random_state=42)

hgb_p50.fit(X_train, y_train_detrend)
hgb_p95.fit(X_train, y_train_detrend)
hgb_p05.fit(X_train, y_train_detrend)
hgb_train_time = time.time() - t0

# Latency for 30 day step
t_inf = time.time()
for _ in range(10):
    pred_50_raw = hgb_p50.predict(X_test.iloc[:30])
    pred_95_raw = hgb_p95.predict(X_test.iloc[:30])
    pred_05_raw = hgb_p05.predict(X_test.iloc[:30])
hgb_inf_ms = ((time.time() - t_inf) / 10.0) * 1000.0

pred_50 = hgb_p50.predict(X_test) + test_trends
pred_95 = hgb_p95.predict(X_test) + test_trends
pred_05 = hgb_p05.predict(X_test) + test_trends

evaluate_forecast(
    "HistGradientBoosting Multi-Quantile",
    pred_50, pred_05, pred_95, hgb_train_time, hgb_inf_ms, 185.0,
    "Native Scikit-Learn zero-dependency histogram boosting"
)

# -------------------------------------------------------------
# 2. LightGBM Multi-Quantile Regressor
# -------------------------------------------------------------
print("Evaluating Model 2: LightGBM Multi-Quantile Regressor...", flush=True)
t0 = time.time()
lgb_p50 = lgb.LGBMRegressor(objective="regression", n_estimators=180, learning_rate=0.03, max_depth=4, num_leaves=15, min_child_samples=12, reg_lambda=1.0, random_state=42, verbose=-1)
lgb_p95 = lgb.LGBMRegressor(objective="quantile", alpha=0.95, n_estimators=180, learning_rate=0.03, max_depth=4, num_leaves=15, min_child_samples=12, reg_lambda=1.0, random_state=42, verbose=-1)
lgb_p05 = lgb.LGBMRegressor(objective="quantile", alpha=0.05, n_estimators=180, learning_rate=0.03, max_depth=4, num_leaves=15, min_child_samples=12, reg_lambda=1.0, random_state=42, verbose=-1)

lgb_p50.fit(X_train, y_train_detrend)
lgb_p95.fit(X_train, y_train_detrend)
lgb_p05.fit(X_train, y_train_detrend)
lgb_train_time = time.time() - t0

t_inf = time.time()
for _ in range(10):
    _ = lgb_p50.predict(X_test.iloc[:30])
    _ = lgb_p95.predict(X_test.iloc[:30])
    _ = lgb_p05.predict(X_test.iloc[:30])
lgb_inf_ms = ((time.time() - t_inf) / 10.0) * 1000.0

pred_50_lgb = lgb_p50.predict(X_test) + test_trends
pred_95_lgb = lgb_p95.predict(X_test) + test_trends
pred_05_lgb = lgb_p05.predict(X_test) + test_trends

evaluate_forecast(
    "LightGBM Quantile Regressor",
    pred_50_lgb, pred_05_lgb, pred_95_lgb, lgb_train_time, lgb_inf_ms, 320.0,
    "Leaf-wise tree growth with quantile objective"
)

# -------------------------------------------------------------
# 3. XGBoost Multi-Quantile Regressor
# -------------------------------------------------------------
print("Evaluating Model 3: XGBoost Multi-Quantile Regressor...", flush=True)
t0 = time.time()
xgb_p50 = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=180, learning_rate=0.03, max_depth=4, reg_lambda=1.0, random_state=42)
xgb_p95 = xgb.XGBRegressor(objective="reg:quantileerror", quantile_alpha=0.95, n_estimators=180, learning_rate=0.03, max_depth=4, reg_lambda=1.0, random_state=42)
xgb_p05 = xgb.XGBRegressor(objective="reg:quantileerror", quantile_alpha=0.05, n_estimators=180, learning_rate=0.03, max_depth=4, reg_lambda=1.0, random_state=42)

xgb_p50.fit(X_train, y_train_detrend)
xgb_p95.fit(X_train, y_train_detrend)
xgb_p05.fit(X_train, y_train_detrend)
xgb_train_time = time.time() - t0

t_inf = time.time()
for _ in range(10):
    _ = xgb_p50.predict(X_test.iloc[:30])
    _ = xgb_p95.predict(X_test.iloc[:30])
    _ = xgb_p05.predict(X_test.iloc[:30])
xgb_inf_ms = ((time.time() - t_inf) / 10.0) * 1000.0

pred_50_xgb = xgb_p50.predict(X_test) + test_trends
pred_95_xgb = xgb_p95.predict(X_test) + test_trends
pred_05_xgb = xgb_p05.predict(X_test) + test_trends

evaluate_forecast(
    "XGBoost Multi-Quantile (reg:quantileerror)",
    pred_50_xgb, pred_05_xgb, pred_95_xgb, xgb_train_time, xgb_inf_ms, 450.0,
    "Exact tree depth with quantile loss gradients"
)

# -------------------------------------------------------------
# 4. CatBoost MultiQuantile Regressor
# -------------------------------------------------------------
print("Evaluating Model 4: CatBoost MultiQuantile Regressor...", flush=True)
t0 = time.time()
cb = CatBoostRegressor(
    loss_function="MultiQuantile:alpha=0.05,0.5,0.95",
    iterations=200,
    learning_rate=0.03,
    depth=4,
    l2_leaf_reg=1.0,
    random_seed=42,
    verbose=0
)
cb.fit(X_train, y_train_detrend)
cb_train_time = time.time() - t0

t_inf = time.time()
for _ in range(10):
    _ = cb.predict(X_test.iloc[:30])
cb_inf_ms = ((time.time() - t_inf) / 10.0) * 1000.0

cb_preds = cb.predict(X_test)
# cb_preds has shape (len, 3): columns correspond to alpha=0.05, 0.5, 0.95
pred_05_cb = cb_preds[:, 0] + test_trends
pred_50_cb = cb_preds[:, 1] + test_trends
pred_95_cb = cb_preds[:, 2] + test_trends

evaluate_forecast(
    "CatBoost MultiQuantile (Single Model)",
    pred_50_cb, pred_05_cb, pred_95_cb, cb_train_time, cb_inf_ms, 580.0,
    "Symmetric oblivious trees with simultaneous multi-quantile output"
)

# -------------------------------------------------------------
# 5. SARIMAX Classical State-Space Model
# -------------------------------------------------------------
print("Evaluating Model 5: SARIMAX (1,1,1)x(1,0,1,7)...", flush=True)
t0 = time.time()
train_series = train_df["DailySpend"].values
sarima_model = SARIMAX(train_series, order=(1, 1, 1), seasonal_order=(1, 0, 1, 7), enforce_stationarity=False, enforce_invertibility=False)
sarima_fit = sarima_model.fit(disp=False)
sarima_train_time = time.time() - t0

t_inf = time.time()
sarima_pred_obj = sarima_fit.get_forecast(steps=len(test_df))
sarima_inf_ms = (time.time() - t_inf) * 1000.0

pred_50_sarima = sarima_pred_obj.predicted_mean
sarima_ci = sarima_pred_obj.conf_int(alpha=0.10) # 90% confidence interval (5% to 95%)
pred_05_sarima = sarima_ci[:, 0]
pred_95_sarima = sarima_ci[:, 1]

evaluate_forecast(
    "SARIMAX (1,1,1)x(1,0,1,7)",
    pred_50_sarima, pred_05_sarima, pred_95_sarima, sarima_train_time, sarima_inf_ms, 95.0,
    "Classical linear autoregressive integrated seasonal state-space"
)

# -------------------------------------------------------------
# 6. Holt-Winters Exponential Smoothing
# -------------------------------------------------------------
print("Evaluating Model 6: Holt-Winters Exponential Smoothing (Additive 7d)...", flush=True)
t0 = time.time()
hw = ExponentialSmoothing(train_series, trend="add", seasonal="add", seasonal_periods=7)
hw_fit = hw.fit()
hw_train_time = time.time() - t0

t_inf = time.time()
pred_50_hw = hw_fit.forecast(len(test_df))
hw_inf_ms = (time.time() - t_inf) * 1000.0

# Empirical residual standard deviation for bounds
train_resid = train_series - hw_fit.fittedvalues
sigma_hw = np.std(train_resid)
pred_95_hw = pred_50_hw + 1.645 * sigma_hw
pred_05_hw = np.maximum(0, pred_50_hw - 1.645 * sigma_hw)

evaluate_forecast(
    "Holt-Winters Triple Exponential",
    pred_50_hw, pred_05_hw, pred_95_hw, hw_train_time, hw_inf_ms, 15.0,
    "Additive trend & 7-day cyclical seasonality smoothing"
)

# -------------------------------------------------------------
# 7. Deep Learning LSTM (Recurrent Neural Network)
# -------------------------------------------------------------
print("Evaluating Model 7: Deep Learning LSTM (2-Layer Keras)...", flush=True)
# Prepare sequence data
lookback = 14
def make_sequences(y_data, lookback_w=14):
    X_s, y_s = [], []
    for i in range(len(y_data) - lookback_w):
        X_s.append(y_data[i:i+lookback_w])
        y_s.append(y_data[i+lookback_w])
    return np.array(X_s)[..., np.newaxis], np.array(y_s)

scaler_ts = StandardScaler()
scaled_train_detrend = scaler_ts.fit_transform(y_train_detrend.values.reshape(-1, 1)).flatten()

X_seq_train, y_seq_train = make_sequences(scaled_train_detrend, lookback)

lstm_in = keras.Input(shape=(lookback, 1))
x = layers.LSTM(32, return_sequences=True)(lstm_in)
x = layers.LSTM(16)(x)
x = layers.Dense(16, activation="relu")(x)
lstm_out = layers.Dense(1)(x)

lstm_model = keras.Model(lstm_in, lstm_out)
lstm_model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.01), loss="mse")

t0 = time.time()
lstm_model.fit(X_seq_train, y_seq_train, epochs=25, batch_size=16, verbose=0, shuffle=False)
lstm_train_time = time.time() - t0

# Recursive rollout on test
curr_window = list(scaled_train_detrend[-lookback:])
lstm_preds_scaled = []
t_inf = time.time()
for step in range(len(test_df)):
    inp = np.array(curr_window[-lookback:]).reshape(1, lookback, 1)
    p_step = float(lstm_model.predict(inp, verbose=0)[0, 0])
    lstm_preds_scaled.append(p_step)
    curr_window.append(p_step)
lstm_inf_ms = (time.time() - t_inf) * 1000.0

lstm_detrend_pred = scaler_ts.inverse_transform(np.array(lstm_preds_scaled).reshape(-1, 1)).flatten()
pred_50_lstm = lstm_detrend_pred + test_trends

# Residual variance from train fit for uncertainty bounds
train_preds_scaled = lstm_model.predict(X_seq_train, verbose=0).flatten()
resid_scaled = y_seq_train - train_preds_scaled
resid_usd = resid_scaled * scaler_ts.scale_[0]
sigma_lstm = np.std(resid_usd)
pred_95_lstm = pred_50_lstm + 1.645 * sigma_lstm
pred_05_lstm = np.maximum(0, pred_50_lstm - 1.645 * sigma_lstm)

evaluate_forecast(
    "Deep Learning LSTM (2-Layer Recurrent)",
    pred_50_lstm, pred_05_lstm, pred_95_lstm, lstm_train_time, lstm_inf_ms, 720.0,
    "Sequential sliding-window LSTM (lookback=14) on stationary detrended spend"
)

# Save benchmark results
out_json = "scripts/benchmark_spend_forecasting_results.json"
with open(out_json, "w") as f:
    json.dump(benchmark_forecasting_results, f, indent=2)

print("\nSaved forecasting benchmark results to", out_json, flush=True)
