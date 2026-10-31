"""
Abhi Cloud Tech — Enterprise FinOps & Multi-Cloud Optimization Platform
Module: src/ml_validation.py
Lead Architect: Abhishek (FinOps ML Validation & Tuning Specialist)

Gold-Standard Data Science, Data Engineering, and ML Validation Framework:
1. Temporal Chronological Train-Test Holdout (Strict No-Lookahead Leakage)
2. 5-Fold TimeSeriesSplit (Expanding Window Cross-Validation) for Forecaster & Anomaly Detector
3. Systematic Hyperparameter Search (GridSearchCV / RandomizedSearchCV)
4. Comprehensive Diagnostic Visualizations & Statistical Metrics Suite:
   - Anomaly Detection: Confusion Matrix, Classification Report, ROC-AUC, PR-AUC, Anomaly Score Density, Feature Correlation Heatmap
   - Spend Forecasting: Actual vs Predicted with 90% Confidence Interval Fan Bands, Residual Diagnostics (Time Series, KDE, Q-Q Plot, ACF), Feature Importance, Quantile Monotonicity Invariant
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime

from sklearn.model_selection import TimeSeriesSplit, ParameterGrid
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc,
    precision_recall_curve, average_precision_score,
    precision_score, recall_score, f1_score, roc_auc_score,
    mean_absolute_error, root_mean_squared_error, mean_absolute_percentage_error
)
from sklearn.inspection import permutation_importance
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf

# =====================================================================
# 1. TEMPORAL DATA SPLITTING & TIME-SERIES CROSS-VALIDATION
# =====================================================================

def temporal_train_test_split(
    df: pd.DataFrame, 
    date_col: str = "Date", 
    test_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Chronological Train-Test Split (Temporal Out-of-Time Holdout).
    Strictly forbids random shuffling or stratified K-Fold to prevent future lookahead leakage.
    
    Parameters:
        df: Input DataFrame containing time-series telemetry.
        date_col: Name of the timestamp/date column.
        test_ratio: Fraction of the most recent time horizon allocated to the test set (default: 15%).
        
    Returns:
        (train_df, test_df) sorted chronologically.
    """
    if df.empty:
        return df.copy(), df.copy()
        
    df_sorted = df.copy()
    df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
    df_sorted = df_sorted.sort_values(by=date_col).reset_index(drop=True)
    
    n_samples = len(df_sorted)
    split_idx = int(n_samples * (1.0 - test_ratio))
    split_idx = max(1, min(split_idx, n_samples - 1))
    
    train_df = df_sorted.iloc[:split_idx].copy().reset_index(drop=True)
    test_df = df_sorted.iloc[split_idx:].copy().reset_index(drop=True)
    
    train_dates = (train_df[date_col].min().strftime('%Y-%m-%d'), train_df[date_col].max().strftime('%Y-%m-%d'))
    test_dates = (test_df[date_col].min().strftime('%Y-%m-%d'), test_df[date_col].max().strftime('%Y-%m-%d'))
    
    print(f"[Temporal Split] Total: {n_samples:,} rows | Train: {len(train_df):,} rows ({train_dates[0]} to {train_dates[1]}) | Test Holdout: {len(test_df):,} rows ({test_dates[0]} to {test_dates[1]})")
    return train_df, test_df


class FinOpsTimeSeriesValidator:
    """
    Production Time-Series Cross-Validator implementing 5-Fold Expanding Window
    evaluation without lookahead leakage.
    """
    def __init__(self, n_splits: int = 5):
        self.n_splits = n_splits
        self.tscv = TimeSeriesSplit(n_splits=n_splits)

    def evaluate_forecaster_cv(
        self, 
        forecaster_cls, 
        df_daily: pd.DataFrame, 
        **forecaster_kwargs
    ) -> Dict[str, Any]:
        """
        Runs 5-Fold Expanding Window Cross-Validation on the Daily Cloud Spend Forecaster.
        Evaluates MAE, RMSE, MAPE, 90% Empirical Coverage, Pinball Losses, and Quantile Crossing Violations.
        """
        df = df_daily.copy()
        if "Date" not in df.columns or ("DailySpend" not in df.columns and "DailyCost_USD" not in df.columns):
            raise ValueError("DataFrame must contain 'Date' and ('DailySpend' or 'DailyCost_USD')")
            
        if "DailySpend" not in df.columns:
            df = df.groupby("Date")["DailyCost_USD"].sum().reset_index()
            df.columns = ["Date", "DailySpend"]
            
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        
        fold_results = []
        
        for fold_idx, (train_idx, test_idx) in enumerate(self.tscv.split(df), 1):
            train_sub = df.iloc[train_idx].copy()
            test_sub = df.iloc[test_idx].copy()
            
            forecaster = forecaster_cls(**forecaster_kwargs)
            # Create feature representations
            forecaster.trend_model.fit(np.arange(len(train_sub)).reshape(-1, 1), train_sub["DailySpend"])
            forecaster.train_len = len(train_sub)
            
            # Use unified feature extractor
            feat_all = forecaster._create_features(pd.concat([train_sub, test_sub], ignore_index=True), is_training=False)
            feat_cols = [c for c in feat_all.columns if c not in ["Date", "DailySpend", "Trend", "DetrendedSpend"]]
            
            X_tr = feat_all.iloc[:len(train_sub)][feat_cols]
            y_tr_detrend = feat_all.iloc[:len(train_sub)]["DetrendedSpend"]
            
            X_te = feat_all.iloc[len(train_sub):][feat_cols]
            y_te_actual = feat_all.iloc[len(train_sub):]["DailySpend"].values
            te_trend = feat_all.iloc[len(train_sub):]["Trend"].values
            
            # Fit models on fold train
            forecaster.model.fit(X_tr, y_tr_detrend)
            forecaster.upper_model.fit(X_tr, y_tr_detrend)
            forecaster.lower_model.fit(X_tr, y_tr_detrend)
            
            pred_detrend = forecaster.model.predict(X_te)
            pred_upper_raw = forecaster.upper_model.predict(X_te)
            pred_lower_raw = forecaster.lower_model.predict(X_te)
            
            y_pred = pred_detrend + te_trend
            upper_pred = np.maximum(y_pred, pred_upper_raw + te_trend)
            lower_pred = np.minimum(y_pred, np.maximum(0.0, pred_lower_raw + te_trend))
            
            mae = float(mean_absolute_error(y_te_actual, y_pred))
            rmse = float(root_mean_squared_error(y_te_actual, y_pred))
            
            nonzero = y_te_actual > 1e-4
            mape = float(np.mean(np.abs((y_te_actual[nonzero] - y_pred[nonzero]) / y_te_actual[nonzero])) * 100) if np.any(nonzero) else 0.0
            
            coverage = float(np.mean((y_te_actual >= lower_pred) & (y_te_actual <= upper_pred)) * 100)
            violations = int(((lower_pred > y_pred) | (y_pred > upper_pred) | (lower_pred > upper_pred)).sum())
            
            # Pinball loss
            def pinball(y, q, alpha):
                err = y - q
                return float(np.mean(np.maximum(alpha * err, (alpha - 1) * err)))
                
            upper_pinball = pinball(y_te_actual, upper_pred, 0.95)
            lower_pinball = pinball(y_te_actual, lower_pred, 0.05)
            
            fold_results.append({
                "Fold": fold_idx,
                "Train_Size": len(train_sub),
                "Test_Size": len(test_sub),
                "Test_Start": test_sub["Date"].min().strftime("%Y-%m-%d"),
                "Test_End": test_sub["Date"].max().strftime("%Y-%m-%d"),
                "MAE_USD": round(mae, 2),
                "RMSE_USD": round(rmse, 2),
                "MAPE_Pct": round(mape, 2),
                "Empirical_Coverage_Pct": round(coverage, 2),
                "Upper_Pinball_Loss": round(upper_pinball, 2),
                "Lower_Pinball_Loss": round(lower_pinball, 2),
                "Quantile_Violations": violations
            })
            
        summary_df = pd.DataFrame(fold_results)
        return {
            "folds": summary_df,
            "mean_mae": round(summary_df["MAE_USD"].mean(), 2),
            "std_mae": round(summary_df["MAE_USD"].std(), 2),
            "mean_rmse": round(summary_df["RMSE_USD"].mean(), 2),
            "mean_mape": round(summary_df["MAPE_Pct"].mean(), 2),
            "mean_coverage": round(summary_df["Empirical_Coverage_Pct"].mean(), 2),
            "total_violations": int(summary_df["Quantile_Violations"].sum())
        }

    def evaluate_anomaly_cv(
        self, 
        detector_cls, 
        df_telemetry: pd.DataFrame, 
        ground_truth_col: str = "Is_Anomaly",
        **detector_kwargs
    ) -> Dict[str, Any]:
        """
        Runs 5-Fold Expanding Window Cross-Validation on the Anomaly Detector.
        Evaluates Precision, Recall, F1-Score, ROC-AUC, and Average Precision (PR-AUC) across folds.
        """
        df = df_telemetry.copy()
        date_col = "Date" if "Date" in df.columns else "ChargePeriodStart"
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col).reset_index(drop=True)
        
        # Ground truth resolution
        if ground_truth_col not in df.columns and "IsAnomaly" in df.columns:
            df[ground_truth_col] = df["IsAnomaly"].astype(int)
        elif ground_truth_col in df.columns:
            df[ground_truth_col] = df[ground_truth_col].astype(int)
        else:
            raise ValueError(f"Ground truth column '{ground_truth_col}' not found.")
            
        fold_results = []
        
        for fold_idx, (train_idx, test_idx) in enumerate(self.tscv.split(df), 1):
            train_sub = df.iloc[train_idx].copy()
            test_sub = df.iloc[test_idx].copy()
            
            detector = detector_cls(**detector_kwargs)
            # Fit on training fold
            detector.fit(train_sub)
            
            # Predict on out-of-time test fold (true out-of-sample inference without retraining)
            res_test = detector.predict(test_sub)
            
            y_true = test_sub[ground_truth_col].values
            y_pred = res_test["detected_anomaly"].values.astype(int)
            y_scores = res_test["anomaly_score"].values
            
            p = float(precision_score(y_true, y_pred, zero_division=0))
            r = float(recall_score(y_true, y_pred, zero_division=0))
            f1 = float(f1_score(y_true, y_pred, zero_division=0))
            
            # ROC AUC & PR AUC
            try:
                roc_val = float(roc_auc_score(y_true, y_scores))
            except Exception:
                roc_val = 0.5
                
            try:
                pr_auc_val = float(average_precision_score(y_true, y_scores))
            except Exception:
                pr_auc_val = 0.0
                
            cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()
            
            fold_results.append({
                "Fold": fold_idx,
                "Train_Size": len(train_sub),
                "Test_Size": len(test_sub),
                "Test_Start": test_sub[date_col].min().strftime("%Y-%m-%d"),
                "Test_End": test_sub[date_col].max().strftime("%Y-%m-%d"),
                "Precision": round(p, 4),
                "Recall": round(r, 4),
                "F1_Score": round(f1, 4),
                "ROC_AUC": round(roc_val, 4),
                "PR_AUC": round(pr_auc_val, 4),
                "TP": int(tp), "FP": int(fp), "FN": int(fn), "TN": int(tn)
            })
            
        summary_df = pd.DataFrame(fold_results)
        return {
            "folds": summary_df,
            "mean_precision": round(summary_df["Precision"].mean(), 4),
            "mean_recall": round(summary_df["Recall"].mean(), 4),
            "mean_f1": round(summary_df["F1_Score"].mean(), 4),
            "mean_roc_auc": round(summary_df["ROC_AUC"].mean(), 4),
            "mean_pr_auc": round(summary_df["PR_AUC"].mean(), 4)
        }


# =====================================================================
# 2. SYSTEMATIC HYPERPARAMETER OPTIMIZATION (GRID SEARCH)
# =====================================================================

class FinOpsHyperparameterOptimizer:
    """
    Systematic Hyperparameter Tuning for Cloud Spend Forecasting & Anomaly Detection
    using strictly temporal cross-validation.
    """
    
    @staticmethod
    def tune_forecaster(
        df_daily: pd.DataFrame, 
        forecaster_cls,
        param_grid: Optional[Dict[str, list]] = None,
        n_splits: int = 5
    ) -> Dict[str, Any]:
        """
        Optimizes HistGradientBoostingRegressor hyperparameters across learning rate,
        max depth, min samples leaf, and L2 regularization.
        """
        if param_grid is None:
            param_grid = {
                "learning_rate": [0.01, 0.03, 0.08],
                "max_depth": [3, 4, 6],
                "min_samples_leaf": [8, 12, 20],
                "l2_regularization": [0.1, 1.0, 5.0]
            }
            
        grid = list(ParameterGrid(param_grid))
        print(f"[*] Starting Forecaster Hyperparameter Grid Search ({len(grid)} candidate configurations)...")
        
        validator = FinOpsTimeSeriesValidator(n_splits=n_splits)
        best_mae = float("inf")
        best_params = None
        best_metrics = None
        search_history = []
        
        for idx, params in enumerate(grid, 1):
            try:
                forecaster_instance = forecaster_cls(forecast_horizon_days=30)
                # Overwrite model parameters
                for m in [forecaster_instance.model, forecaster_instance.upper_model, forecaster_instance.lower_model]:
                    for p_name, p_val in params.items():
                        setattr(m, p_name, p_val)
                        
                cv_res = validator.evaluate_forecaster_cv(lambda **kw: forecaster_instance, df_daily)
                mae = cv_res["mean_mae"]
                search_history.append({
                    **params,
                    "Mean_MAE": mae,
                    "Mean_RMSE": cv_res["mean_rmse"],
                    "Mean_MAPE": cv_res["mean_mape"],
                    "Coverage_Pct": cv_res["mean_coverage"],
                    "Violations": cv_res["total_violations"]
                })
                
                if mae < best_mae:
                    best_mae = mae
                    best_params = params
                    best_metrics = cv_res
            except Exception as e:
                continue
                
        results_df = pd.DataFrame(search_history).sort_values("Mean_MAE").reset_index(drop=True)
        print(f"[+] Optimization Complete. Best Parameters: {best_params} | Best MAE: ${best_mae:.2f}")
        return {
            "best_params": best_params,
            "best_mae": best_mae,
            "best_metrics": best_metrics,
            "results_df": results_df
        }

    @staticmethod
    def tune_anomaly_detector(
        df_telemetry: pd.DataFrame,
        detector_cls,
        param_grid: Optional[Dict[str, list]] = None,
        n_splits: int = 5
    ) -> Dict[str, Any]:
        """
        Optimizes Isolation Forest hyperparameters: contamination rate, n_estimators,
        and max_samples ratio.
        """
        if param_grid is None:
            param_grid = {
                "contamination": [0.010, 0.012, 0.015, 0.020],
                "n_estimators": [100, 180, 250],
                "max_samples": [0.8, 1.0]
            }
            
        grid = list(ParameterGrid(param_grid))
        print(f"[*] Starting Anomaly Detector Hyperparameter Search ({len(grid)} candidate configurations)...")
        
        validator = FinOpsTimeSeriesValidator(n_splits=n_splits)
        best_f1 = -1.0
        best_params = None
        best_metrics = None
        search_history = []
        
        for idx, params in enumerate(grid, 1):
            try:
                def make_detector(**kw):
                    det = detector_cls(contamination=params["contamination"])
                    det.model.set_params(
                        n_estimators=params["n_estimators"],
                        max_samples=params["max_samples"],
                        contamination=params["contamination"],
                        random_state=42
                    )
                    return det
                    
                cv_res = validator.evaluate_anomaly_cv(make_detector, df_telemetry)
                f1 = cv_res["mean_f1"]
                search_history.append({
                    **params,
                    "Mean_Precision": cv_res["mean_precision"],
                    "Mean_Recall": cv_res["mean_recall"],
                    "Mean_F1": f1,
                    "Mean_ROC_AUC": cv_res["mean_roc_auc"],
                    "Mean_PR_AUC": cv_res["mean_pr_auc"]
                })
                
                if f1 > best_f1:
                    best_f1 = f1
                    best_params = params
                    best_metrics = cv_res
            except Exception as e:
                continue
                
        results_df = pd.DataFrame(search_history).sort_values("Mean_F1", ascending=False).reset_index(drop=True)
        print(f"[+] Optimization Complete. Best Parameters: {best_params} | Best Mean F1: {best_f1:.4f}")
        return {
            "best_params": best_params,
            "best_f1": best_f1,
            "best_metrics": best_metrics,
            "results_df": results_df
        }


# =====================================================================
# 3. DIAGNOSTIC SUITES & STATISTICAL VISUALIZATIONS
# =====================================================================

class FinOpsDiagnosticSuite:
    """
    Renders and exports diagnostic visualization suites for executive reports
    and Jupyter Notebook presentations.
    """
    
    @staticmethod
    def plot_anomaly_diagnostics(
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        y_scores: np.ndarray,
        feature_df: Optional[pd.DataFrame] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Renders a 6-panel diagnostic dashboard for Anomaly Detection:
        1. Confusion Matrix with counts & normalized percentages
        2. Precision-Recall Curve with Average Precision (AP)
        3. Receiver Operating Characteristic (ROC) Curve with AUC
        4. Anomaly Score Density Distribution (Normal vs Anomalous)
        5. Telemetry Feature Correlation Heatmap (Seaborn)
        6. Anomaly Precision & Recall metrics summary bar
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 11))
        fig.suptitle("FinOps Anomaly Detection — Model Diagnostic Evaluation Suite", fontsize=16, fontweight="bold", y=0.98)
        
        # 1. Confusion Matrix Heatmap
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        annot = np.array([
            [f"{cm[0,0]:,}\n({cm_norm[0,0]:.1%})", f"{cm[0,1]:,}\n({cm_norm[0,1]:.1%})"],
            [f"{cm[1,0]:,}\n({cm_norm[1,0]:.1%})", f"{cm[1,1]:,}\n({cm_norm[1,1]:.1%})"]
        ])
        sns.heatmap(cm, annot=annot, fmt="", cmap="Blues", cbar=False, ax=axes[0, 0],
                    xticklabels=["Normal", "Anomaly"], yticklabels=["Normal", "Anomaly"], annot_kws={"size": 11, "weight": "bold"})
        axes[0, 0].set_title("Confusion Matrix (Holdout)", fontsize=12, fontweight="bold")
        axes[0, 0].set_ylabel("True Category")
        axes[0, 0].set_xlabel("Predicted Category")
        
        # 2. Precision-Recall Curve
        precisions, recalls, _ = precision_recall_curve(y_true, y_scores)
        ap = average_precision_score(y_true, y_scores)
        axes[0, 1].plot(recalls, precisions, color="#d9534f", lw=2.5, label=f"PR Curve (AP = {ap:.3f})")
        axes[0, 1].axhline(y=y_true.mean(), color="navy", linestyle="--", alpha=0.7, label=f"Baseline Rate ({y_true.mean():.1%})")
        axes[0, 1].set_title("Precision-Recall Trade-off", fontsize=12, fontweight="bold")
        axes[0, 1].set_xlabel("Recall")
        axes[0, 1].set_ylabel("Precision")
        axes[0, 1].set_xlim([0.0, 1.0])
        axes[0, 1].set_ylim([0.0, 1.05])
        axes[0, 1].legend(loc="upper right")
        axes[0, 1].grid(True, linestyle="--", alpha=0.6)
        
        # 3. ROC Curve
        fpr, tpr, _ = roc_curve(y_true, y_scores)
        roc_auc = auc(fpr, tpr)
        axes[0, 2].plot(fpr, tpr, color="#2b5c8f", lw=2.5, label=f"ROC Curve (AUC = {roc_auc:.3f})")
        axes[0, 2].plot([0, 1], [0, 1], color="gray", linestyle="--", label="Random Chance (0.50)")
        axes[0, 2].set_title("ROC Curve & Discrimination Power", fontsize=12, fontweight="bold")
        axes[0, 2].set_xlabel("False Positive Rate (FPR)")
        axes[0, 2].set_ylabel("True Positive Rate (TPR)")
        axes[0, 2].set_xlim([0.0, 1.0])
        axes[0, 2].set_ylim([0.0, 1.05])
        axes[0, 2].legend(loc="lower right")
        axes[0, 2].grid(True, linestyle="--", alpha=0.6)
        
        # 4. Anomaly Score Density Distribution
        normal_scores = y_scores[y_true == 0]
        anomaly_scores = y_scores[y_true == 1]
        sns.kdeplot(normal_scores, fill=True, color="#2b5c8f", label=f"Normal Baseline (n={len(normal_scores):,})", ax=axes[1, 0], alpha=0.4)
        sns.kdeplot(anomaly_scores, fill=True, color="#d9534f", label=f"True Anomalies (n={len(anomaly_scores):,})", ax=axes[1, 0], alpha=0.5)
        axes[1, 0].set_title("Isolation Score Density Distribution", fontsize=12, fontweight="bold")
        axes[1, 0].set_xlabel("Anomaly Inverted Score (Higher = Anomalous)")
        axes[1, 0].set_ylabel("Probability Density")
        axes[1, 0].legend(loc="upper right")
        axes[1, 0].grid(True, linestyle="--", alpha=0.6)
        
        # 5. Feature Correlation Heatmap
        if feature_df is not None and not feature_df.empty:
            corr_cols = [c for c in [
                "DailyCost_USD", "vCPU_Hours", "Avg_CPU_Utilization_Pct", 
                "Data_Egress_GB", "Storage_TB", "cost_zscore", 
                "cost_to_median_ratio", "cost_per_cpu_pct"
            ] if c in feature_df.columns]
            corr_mat = feature_df[corr_cols].corr()
            sns.heatmap(corr_mat, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=axes[1, 1],
                        annot_kws={"size": 8}, cbar_kws={"shrink": 0.8})
            axes[1, 1].set_title("Telemetry Feature Correlation Heatmap", fontsize=12, fontweight="bold")
            axes[1, 1].tick_params(axis='x', rotation=45)
        else:
            axes[1, 1].text(0.5, 0.5, "Feature matrix not provided", ha="center", va="center")
            
        # 6. Performance Metrics Summary
        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        metrics_names = ["Precision", "Recall", "F1-Score", "ROC-AUC", "PR-AUC"]
        metrics_vals = [p, r, f1, roc_auc, ap]
        bars = axes[1, 2].bar(metrics_names, metrics_vals, color=["#337ab7", "#5cb85c", "#f0ad4e", "#5bc0de", "#d9534f"], width=0.55)
        axes[1, 2].set_ylim([0, 1.15])
        axes[1, 2].set_title("Operational Validation Metrics", fontsize=12, fontweight="bold")
        axes[1, 2].set_ylabel("Score (0.0 to 1.0)")
        for bar in bars:
            h = bar.get_height()
            axes[1, 2].annotate(f"{h:.3f}", (bar.get_x() + bar.get_width() / 2, h + 0.02),
                                ha='center', va='bottom', fontsize=10, fontweight="bold")
        axes[1, 2].grid(axis="y", linestyle="--", alpha=0.6)
        
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"[+] Saved Anomaly Diagnostic Plot to: {save_path}")
        return fig

    @staticmethod
    def plot_forecasting_diagnostics(
        dates: pd.Series,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        lower_pred: np.ndarray,
        upper_pred: np.ndarray,
        feature_importance_df: Optional[pd.DataFrame] = None,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Renders a 6-panel diagnostic dashboard for Time-Series Spend Forecasting:
        1. Actual vs Predicted with 90% Confidence Interval Fan Bands
        2. Residuals vs Time (heteroscedasticity & drift analysis)
        3. Residual Distribution & Normality (Histogram + KDE vs Normal curve)
        4. Quantile-Quantile (Q-Q) Plot (Residuals vs Theoretical Normal Quantiles)
        5. Autocorrelation Function (ACF) Plot (Residual White-Noise Check)
        6. Top Predictive Feature Importance Rankings
        """
        residuals = y_true - y_pred
        fig, axes = plt.subplots(3, 2, figsize=(18, 14))
        fig.suptitle("FinOps Spend Forecasting — Model Diagnostic & Residual Suite", fontsize=16, fontweight="bold", y=0.98)
        
        # 1. Actual vs Predicted with 90% Confidence Interval Fan Bands
        axes[0, 0].plot(dates, y_true, color="#222222", lw=2.0, label="Actual Spend ($ USD)")
        axes[0, 0].plot(dates, y_pred, color="#0275d8", lw=2.2, linestyle="-", label="Median Forecast (Q50)")
        axes[0, 0].fill_between(dates, lower_pred, upper_pred, color="#0275d8", alpha=0.22, label="90% Risk Band (Q05 – Q95)")
        axes[0, 0].set_title("Out-of-Time Backtest with 90% Confidence Interval", fontsize=12, fontweight="bold")
        axes[0, 0].set_ylabel("Daily Spend ($ USD)")
        axes[0, 0].legend(loc="upper left")
        axes[0, 0].grid(True, linestyle="--", alpha=0.6)
        axes[0, 0].tick_params(axis='x', rotation=30)
        
        # 2. Residuals vs Time
        axes[0, 1].scatter(dates, residuals, color="#2b5c8f", alpha=0.7, edgecolors="none", s=35)
        axes[0, 1].axhline(0, color="red", linestyle="--", lw=1.5)
        axes[0, 1].axhline(residuals.mean() + 2 * residuals.std(), color="gray", linestyle=":", alpha=0.8, label="+2σ Limit")
        axes[0, 1].axhline(residuals.mean() - 2 * residuals.std(), color="gray", linestyle=":", alpha=0.8, label="-2σ Limit")
        axes[0, 1].set_title("Residuals vs Time (Homoscedasticity Check)", fontsize=12, fontweight="bold")
        axes[0, 1].set_ylabel("Residual (Actual - Pred) $")
        axes[0, 1].legend(loc="upper right")
        axes[0, 1].grid(True, linestyle="--", alpha=0.6)
        axes[0, 1].tick_params(axis='x', rotation=30)
        
        # 3. Residual Distribution & Normality Check
        sns.histplot(residuals, kde=True, stat="density", color="#5cb85c", ax=axes[1, 0], alpha=0.4, bins=20)
        # Overlay theoretical normal distribution
        mu, std = stats.norm.fit(residuals)
        xmin, xmax = axes[1, 0].get_xlim()
        x_grid = np.linspace(xmin, xmax, 100)
        p_grid = stats.norm.pdf(x_grid, mu, std)
        axes[1, 0].plot(x_grid, p_grid, 'r--', lw=2.0, label=f"Normal Curve (μ={mu:.1f}, σ={std:.1f})")
        axes[1, 0].set_title("Residual Density & Gaussian Fit", fontsize=12, fontweight="bold")
        axes[1, 0].set_xlabel("Residual ($ USD)")
        axes[1, 0].set_ylabel("Density")
        axes[1, 0].legend(loc="upper right")
        axes[1, 0].grid(True, linestyle="--", alpha=0.6)
        
        # 4. Normal Q-Q Plot
        (osm, osr), (slope, intercept, r) = stats.probplot(residuals, dist="norm")
        axes[1, 1].plot(osm, osr, 'o', color="#2b5c8f", alpha=0.7, markersize=5)
        axes[1, 1].plot(osm, slope * np.array(osm) + intercept, 'r-', lw=2.0, label=f"Theoretical Line (R²={r**2:.3f})")
        axes[1, 1].set_title("Normal Q-Q Plot (Residual Normality Check)", fontsize=12, fontweight="bold")
        axes[1, 1].set_xlabel("Theoretical Quantiles")
        axes[1, 1].set_ylabel("Sample Quantiles")
        axes[1, 1].legend(loc="upper left")
        axes[1, 1].grid(True, linestyle="--", alpha=0.6)
        
        # 5. ACF (Autocorrelation Function) Plot
        lags_to_show = min(20, len(residuals) - 2)
        acf_vals, confint = acf(residuals, nlags=lags_to_show, alpha=0.05)
        axes[2, 0].stem(range(len(acf_vals)), acf_vals, basefmt=" ", linefmt="#0275d8", markerfmt="o")
        # 95% Bartlett confidence bands
        conf_band = 1.96 / np.sqrt(len(residuals))
        axes[2, 0].axhline(conf_band, color="red", linestyle="--", alpha=0.7, label="95% Significance Bound (±1.96/√N)")
        axes[2, 0].axhline(-conf_band, color="red", linestyle="--", alpha=0.7)
        axes[2, 0].axhline(0, color="black", linestyle="-", lw=0.8)
        axes[2, 0].set_title("Residual ACF (Autocorrelation Function)", fontsize=12, fontweight="bold")
        axes[2, 0].set_xlabel("Lag (Days)")
        axes[2, 0].set_ylabel("Autocorrelation")
        axes[2, 0].set_ylim([-0.6, 1.1])
        axes[2, 0].legend(loc="upper right")
        axes[2, 0].grid(True, linestyle="--", alpha=0.6)
        
        # 6. Feature Importance Bar Chart
        if feature_importance_df is not None and not feature_importance_df.empty:
            top_features = feature_importance_df.head(10).sort_values("Importance", ascending=True)
            axes[2, 1].barh(top_features["Feature"], top_features["Importance"], color="#337ab7", height=0.6)
            axes[2, 1].set_title("Top 10 Feature Importance (Permutation / Gradient)", fontsize=12, fontweight="bold")
            axes[2, 1].set_xlabel("Relative Importance Score")
            axes[2, 1].grid(axis="x", linestyle="--", alpha=0.6)
        else:
            axes[2, 1].text(0.5, 0.5, "Feature importance data not supplied", ha="center", va="center")
            
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"[+] Saved Forecasting Diagnostic Plot to: {save_path}")
        return fig


# =====================================================================
# 4. QUANTILE CALIBRATION & INVARIANT VERIFICATION
# =====================================================================

def verify_quantile_monotonicity(lower_pred: np.ndarray, median_pred: np.ndarray, upper_pred: np.ndarray) -> Dict[str, Any]:
    """
    Formally certifies the zero quantile crossing invariant:
    Lower (Q05) <= Median (Q50) <= Upper (Q95) for all evaluation points.
    
    Returns:
        Certification dictionary with violation counts and percentage compliance.
    """
    crossing_violations = int(((lower_pred > median_pred) | (median_pred > upper_pred) | (lower_pred > upper_pred)).sum())
    total_samples = len(median_pred)
    compliance_pct = 100.0 * (1.0 - (crossing_violations / max(1, total_samples)))
    
    certified = (crossing_violations == 0)
    return {
        "is_certified": certified,
        "total_samples": total_samples,
        "crossing_violations": crossing_violations,
        "compliance_pct": round(compliance_pct, 4),
        "status": "PASSED (Zero Crossing Invariant Preserved)" if certified else f"FAILED ({crossing_violations} crossing errors)"
    }
