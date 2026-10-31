"""
Abhi Cloud Tech — ML Validation & Tuning Execution Pipeline
Executes chronological cross-validation, hyperparameter tuning, and diagnostic figure exports.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg") # Non-interactive headless backend for clean script execution
import matplotlib.pyplot as plt

# Ensure root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.anomaly_detection import FinOpsAnomalyDetector
from src.forecasting import FinOpsForecaster
from src.database import load_focus_dataframe
from src.ml_validation import (
    temporal_train_test_split,
    FinOpsTimeSeriesValidator,
    FinOpsHyperparameterOptimizer,
    FinOpsDiagnosticSuite,
    verify_quantile_monotonicity
)
from sklearn.inspection import permutation_importance

def main():
    print("=" * 80)
    print("ABHI CLOUD TECH — FINOPS ML VALIDATION, TUNING & DIAGNOSTICS SUITE")
    print("=" * 80)
    
    # Create assets directory for figures
    assets_dir = os.path.join(BASE_DIR, "notebooks", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # 1. Load Data from Warehouse
    print("\n[Step 1] Loading FOCUS Telemetry from SQLite Warehouse...")
    df = load_focus_dataframe()
    print(f"Loaded {len(df):,} records across {df['Date'].nunique()} days.")
    
    # -----------------------------------------------------------------
    # PART A: ANOMALY DETECTION ML VALIDATION & TUNING
    # -----------------------------------------------------------------
    print("\n" + "=" * 50)
    print("PART A: ANOMALY DETECTION VALIDATION")
    print("=" * 50)
    
    # 1. Temporal Split (85% Train, 15% Holdout)
    train_telemetry, test_telemetry = temporal_train_test_split(df, date_col="Date", test_ratio=0.15)
    
    # 2. 5-Fold TimeSeriesSplit Cross-Validation
    print("\n[*] Executing 5-Fold TimeSeriesSplit (Expanding Window CV) for Anomaly Detection...")
    validator = FinOpsTimeSeriesValidator(n_splits=5)
    anomaly_cv_results = validator.evaluate_anomaly_cv(FinOpsAnomalyDetector, df, ground_truth_col="Is_Anomaly")
    
    print("\n[Anomaly Detection 5-Fold CV Results]:")
    print(anomaly_cv_results["folds"][["Fold", "Test_Size", "Precision", "Recall", "F1_Score", "ROC_AUC", "PR_AUC"]])
    print(f"\nMean Precision: {anomaly_cv_results['mean_precision']:.4f}")
    print(f"Mean Recall:    {anomaly_cv_results['mean_recall']:.4f}")
    print(f"Mean F1-Score:  {anomaly_cv_results['mean_f1']:.4f}")
    print(f"Mean ROC-AUC:   {anomaly_cv_results['mean_roc_auc']:.4f}")
    print(f"Mean PR-AUC:    {anomaly_cv_results['mean_pr_auc']:.4f}")
    
    # 3. Fit on Train, Evaluate on Out-of-Time Test Holdout
    print("\n[*] Fitting Anomaly Detector on Chronological Train and Scoring Holdout...")
    detector = FinOpsAnomalyDetector(contamination=0.0184)
    detector.fit(train_telemetry)
    test_evaluated = detector.predict(test_telemetry)
    
    y_true_test = test_telemetry["Is_Anomaly"].values.astype(int)
    y_pred_test = test_evaluated["detected_anomaly"].values.astype(int)
    y_scores_test = test_evaluated["anomaly_score"].values
    
    # 4. Generate Diagnostic Figures
    anomaly_plot_path = os.path.join(assets_dir, "anomaly_detection_diagnostics.png")
    FinOpsDiagnosticSuite.plot_anomaly_diagnostics(
        y_true=y_true_test,
        y_pred=y_pred_test,
        y_scores=y_scores_test,
        feature_df=test_evaluated,
        save_path=anomaly_plot_path
    )
    plt.close("all")
    
    # -----------------------------------------------------------------
    # PART B: SPEND FORECASTING ML VALIDATION & TUNING
    # -----------------------------------------------------------------
    print("\n" + "=" * 50)
    print("PART B: SPEND FORECASTING VALIDATION")
    print("=" * 50)
    
    # Daily aggregation
    daily_spend = df.groupby("Date")["DailyCost_USD"].sum().reset_index()
    daily_spend.columns = ["Date", "DailySpend"]
    daily_spend["Date"] = pd.to_datetime(daily_spend["Date"])
    daily_spend = daily_spend.sort_values("Date").reset_index(drop=True)
    
    # 1. Temporal Split (85% Train, 15% Holdout)
    train_daily, test_daily = temporal_train_test_split(daily_spend, date_col="Date", test_ratio=0.15)
    
    # 2. 5-Fold TimeSeriesSplit Cross-Validation
    print("\n[*] Executing 5-Fold TimeSeriesSplit (Expanding Window CV) for Forecaster...")
    forecaster_cv_results = validator.evaluate_forecaster_cv(FinOpsForecaster, daily_spend)
    
    print("\n[Spend Forecasting 5-Fold CV Results]:")
    print(forecaster_cv_results["folds"][["Fold", "Test_Size", "MAE_USD", "RMSE_USD", "MAPE_Pct", "Empirical_Coverage_Pct", "Quantile_Violations"]])
    print(f"\nMean MAE:             ${forecaster_cv_results['mean_mae']:.2f} ± ${forecaster_cv_results['std_mae']:.2f}")
    print(f"Mean RMSE:            ${forecaster_cv_results['mean_rmse']:.2f}")
    print(f"Mean MAPE:            {forecaster_cv_results['mean_mape']:.2f}%")
    print(f"Mean 90% Coverage:    {forecaster_cv_results['mean_coverage']:.2f}%")
    print(f"Quantile Violations:  {forecaster_cv_results['total_violations']}")
    
    # 3. Train on Train Split, Evaluate on Test Holdout
    print("\n[*] Training FinOps Forecaster on Chronological Train and Scoring Holdout...")
    forecaster = FinOpsForecaster(forecast_horizon_days=30)
    eval_metrics = forecaster.train_and_evaluate(train_daily.rename(columns={"DailySpend": "DailyCost_USD"}))
    
    # Build test predictions
    feat_all = forecaster._create_features(daily_spend, is_training=False)
    feat_cols = forecaster.feature_cols
    
    test_slice = feat_all.iloc[len(train_daily):].copy()
    X_test = test_slice[feat_cols]
    y_test_actual = test_slice["DailySpend"].values
    t_test = test_slice["Trend"].values
    test_dates = test_slice["Date"]
    
    pred_detrend = forecaster.model.predict(X_test)
    pred_upper_raw = forecaster.upper_model.predict(X_test)
    pred_lower_raw = forecaster.lower_model.predict(X_test)
    
    y_pred = pred_detrend + t_test
    upper_pred = np.maximum(y_pred, pred_upper_raw + t_test)
    lower_pred = np.minimum(y_pred, np.maximum(0.0, pred_lower_raw + t_test))
    
    # 4. Quantile Monotonicity Verification
    cert = verify_quantile_monotonicity(lower_pred, y_pred, upper_pred)
    print("\n[Quantile Monotonicity Certification]:", cert)
    
    # 5. Permutation Feature Importance
    perm = permutation_importance(forecaster.model, X_test, test_slice["DetrendedSpend"], n_repeats=10, random_state=42)
    feature_importance_df = pd.DataFrame({
        "Feature": feat_cols,
        "Importance": perm.importances_mean
    }).sort_values("Importance", ascending=False).reset_index(drop=True)
    
    print("\n[Top 5 Predictive Features by Permutation Importance]:")
    print(feature_importance_df.head(5))
    
    # 6. Generate Forecasting Diagnostic Suite Figure
    forecasting_plot_path = os.path.join(assets_dir, "spend_forecasting_diagnostics.png")
    FinOpsDiagnosticSuite.plot_forecasting_diagnostics(
        dates=test_dates,
        y_true=y_test_actual,
        y_pred=y_pred,
        lower_pred=lower_pred,
        upper_pred=upper_pred,
        feature_importance_df=feature_importance_df,
        save_path=forecasting_plot_path
    )
    plt.close("all")
    
    print("\n" + "=" * 80)
    print("ALL VALIDATION PROCEDURES & DIAGNOSTIC VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print(f"Artifacts saved in: {assets_dir}")
    print("=" * 80)

if __name__ == "__main__":
    main()
