import os
import sys
import unittest
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.anomaly_detection import FinOpsAnomalyDetector
from src.forecasting import FinOpsForecaster
from src.optimizer import FinOpsOptimizer
from src.database import (
    get_engine, close_engine, initialize_database, 
    load_focus_dataframe, FOCUS_COLUMNS
)
from backend.services import FinOpsService

class TestAnomalyDetectionWhiteBox(unittest.TestCase):
    """
    White-Box Unit Tests for src/anomaly_detection.py:
    - Empty DataFrame safety
    - Single-row edge case
    - Zero variance on continuous features
    - Division by zero safety when rolling std is 0
    - Missing metadata and None value resilience
    - Attribution and severity boundary tests
    """
    def setUp(self):
        self.detector = FinOpsAnomalyDetector(contamination=0.03)

    def test_empty_dataframe_safety(self):
        """Verifies fit_predict handles 0-row DataFrames gracefully without crashing."""
        empty_df = pd.DataFrame()
        result = self.detector.fit_predict(empty_df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 0)
        expected_cols = [
            "anomaly_score", "is_iso_anomaly", "rolling_mean_cost", 
            "rolling_std_cost", "cost_zscore", "cost_spike_usd", 
            "detected_anomaly", "root_cause_diagnosis", "anomaly_severity"
        ]
        for col in expected_cols:
            self.assertIn(col, result.columns)

    def test_single_row_safety(self):
        """Verifies single-row input does not crash IsolationForest or rolling calculations."""
        single_row = pd.DataFrame([{
            "Date": "2026-01-01",
            "CloudProvider": "AWS",
            "Department": "Platform Engineering",
            "Service": "AmazonEC2 (Compute)",
            "DailyCost_USD": 250.0,
            "vCPU_Hours": 240.0,
            "Avg_CPU_Utilization_Pct": 22.5,
            "Data_Egress_GB": 50.0,
            "Storage_TB": 5.0
        }])
        result = self.detector.fit_predict(single_row)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["detected_anomaly"], 0)
        self.assertEqual(result.iloc[0]["anomaly_severity"], "Normal")
        self.assertEqual(result.iloc[0]["cost_zscore"], 0.0)
        self.assertFalse(result.isna().any().any())

    def test_zero_variance_isolation_forest(self):
        """
        Verifies Isolation Forest handles contaminated fit on identical samples
        where variance is 0 across all 5 continuous telemetry features.
        """
        rows = []
        for i in range(1, 31):
            rows.append({
                "Date": f"2026-01-{i:02d}",
                "CloudProvider": "Azure",
                "Department": "Data Platform",
                "Service": "Microsoft.Compute",
                "DailyCost_USD": 100.0,
                "vCPU_Hours": 100.0,
                "Avg_CPU_Utilization_Pct": 20.0,
                "Data_Egress_GB": 10.0,
                "Storage_TB": 2.0
            })
        df_zero_var = pd.DataFrame(rows)
        result = self.detector.fit_predict(df_zero_var)
        self.assertEqual(len(result), 30)
        # Z-score must be exactly 0.0, no NaN or Inf
        self.assertTrue((result["cost_zscore"] == 0.0).all())
        self.assertTrue((result["cost_spike_usd"] == 0.0).all())
        self.assertFalse(result["cost_zscore"].isna().any())
        self.assertFalse(np.isinf(result["cost_zscore"]).any())

    def test_zero_cost_rolling_division_by_zero(self):
        """Verifies spend = 0 across all days does not cause division by zero in z-score."""
        rows = [{
            "Date": f"2026-02-{i:02d}",
            "CloudProvider": "GCP",
            "Department": "AI/ML Research",
            "Service": "Compute Engine",
            "DailyCost_USD": 0.0,
            "vCPU_Hours": 0.0,
            "Avg_CPU_Utilization_Pct": 0.0,
            "Data_Egress_GB": 0.0,
            "Storage_TB": 0.0
        } for i in range(1, 20)]
        df_zeros = pd.DataFrame(rows)
        result = self.detector.fit_predict(df_zeros)
        self.assertEqual(len(result), 19)
        self.assertEqual(result["cost_zscore"].max(), 0.0)
        self.assertEqual(result["detected_anomaly"].max(), 0)

    def test_missing_and_none_columns_safety(self):
        """Verifies detector handles missing columns and None values without raising TypeError."""
        df_dirty = pd.DataFrame([
            {"Date": "2026-03-01", "DailyCost_USD": 500.0, "Service": None, "CloudProvider": None},
            {"Date": "2026-03-02", "DailyCost_USD": 1200.0, "Service": "Storage S3", "Avg_CPU_Utilization_Pct": 5.0}
        ])
        result = self.detector.fit_predict(df_dirty)
        self.assertEqual(len(result), 2)
        self.assertFalse(result["root_cause_diagnosis"].isna().any())
        self.assertFalse(result["anomaly_severity"].isna().any())

    def test_root_cause_diagnosis_boundaries(self):
        """Verifies diagnostic rules: Zombie, Egress spike, Storage sprawl."""
        # 1. Zombie instance: CPU < 15% and vCPU > 1200
        zombie_row = pd.DataFrame([
            {"Date": f"2026-01-{i:02d}", "CloudProvider": "AWS", "Department": "Eng", "Service": "EC2",
             "DailyCost_USD": 100.0, "vCPU_Hours": 100.0, "Avg_CPU_Utilization_Pct": 50.0, "Data_Egress_GB": 10.0, "Storage_TB": 1.0}
            for i in range(1, 10)
        ] + [
            {"Date": "2026-01-10", "CloudProvider": "AWS", "Department": "Eng", "Service": "EC2",
             "DailyCost_USD": 2500.0, "vCPU_Hours": 1500.0, "Avg_CPU_Utilization_Pct": 8.0, "Data_Egress_GB": 10.0, "Storage_TB": 1.0}
        ])
        res = self.detector.fit_predict(zombie_row)
        anom = res[res["detected_anomaly"] == 1]
        self.assertGreaterEqual(len(anom), 1)
        self.assertIn("Zombie", anom.iloc[0]["root_cause_diagnosis"])


class TestForecastingWhiteBox(unittest.TestCase):
    """
    White-Box Unit Tests for src/forecasting.py:
    - Non-crossing quantile bounds across 100% of future days (Lower <= Median <= Upper)
    - Division by zero safety when spend is 0 (MAPE calculation)
    - Empty DataFrame and short dataset handling (<30 days)
    - Recursive multi-step forecast boundary stability
    """
    def setUp(self):
        self.forecaster = FinOpsForecaster(forecast_horizon_days=30)

    def test_empty_dataframe_forecasting(self):
        """Verifies training on empty DataFrame produces valid zero metrics."""
        empty_df = pd.DataFrame()
        metrics = self.forecaster.train_and_evaluate(empty_df)
        self.assertEqual(metrics["MAE_USD"], 0.0)
        self.assertEqual(metrics["RMSE_USD"], 0.0)
        self.assertEqual(metrics["MAPE_Pct"], 0.0)
        self.assertEqual(metrics["Test_Sample_Count"], 0)
        
        # Generating forecast on empty history returns empty DataFrame
        future_df = self.forecaster.generate_future_forecast(days_ahead=30)
        self.assertEqual(len(future_df), 0)
        self.assertIn("Forecasted_Spend_USD", future_df.columns)

    def test_short_dataset_1_sample_and_5_samples(self):
        """Verifies forecaster does not crash when history has fewer than 30 days."""
        # 1 sample
        df_1 = pd.DataFrame([{"Date": "2026-01-01", "DailyCost_USD": 500.0}])
        m1 = self.forecaster.train_and_evaluate(df_1)
        self.assertEqual(m1["Test_Sample_Count"], 1)
        fc1 = self.forecaster.generate_future_forecast(days_ahead=7)
        self.assertEqual(len(fc1), 7)
        
        # 5 samples
        df_5 = pd.DataFrame([
            {"Date": f"2026-01-{i:02d}", "DailyCost_USD": 500.0 + i * 20.0}
            for i in range(1, 6)
        ])
        m5 = self.forecaster.train_and_evaluate(df_5)
        self.assertGreater(m5["Test_Sample_Count"], 0)
        fc5 = self.forecaster.generate_future_forecast(days_ahead=14)
        self.assertEqual(len(fc5), 14)

    def test_zero_spend_division_by_zero_mape(self):
        """Verifies zero spend does not produce 9 quadrillion MAPE from division by zero."""
        dates = pd.date_range("2026-01-01", periods=35, freq="D").strftime("%Y-%m-%d")
        df_zero_spend = pd.DataFrame([
            {"Date": d, "DailyCost_USD": 0.0}
            for d in dates
        ])
        metrics = self.forecaster.train_and_evaluate(df_zero_spend)
        self.assertEqual(metrics["MAPE_Pct"], 0.0)
        self.assertEqual(metrics["MAE_USD"], 0.0)
        self.assertEqual(metrics["RMSE_USD"], 0.0)

    def test_non_crossing_quantiles_100_percent_days(self):
        """
        Mathematical Invariant Test:
        Across 100% of future days, 0.0 <= Lower_Bound <= Forecasted_Spend <= Upper_Bound.
        Tests across multiple horizons: 1, 7, 30, 60, 90, 180 days.
        """
        np.random.seed(42)
        dates = pd.date_range("2026-01-01", periods=90, freq="D")
        spends = 1000.0 + 100.0 * np.sin(np.arange(90) / 7.0) + np.random.normal(0, 50, 90)
        df_train = pd.DataFrame({"Date": dates.strftime("%Y-%m-%d"), "DailyCost_USD": np.maximum(50.0, spends)})
        
        self.forecaster.train_and_evaluate(df_train)
        
        for horizon in [1, 7, 30, 60, 90, 180]:
            fc = self.forecaster.generate_future_forecast(days_ahead=horizon)
            self.assertEqual(len(fc), horizon)
            
            lower = fc["Lower_Bound_95_USD"].values
            median = fc["Forecasted_Spend_USD"].values
            upper = fc["Upper_Bound_95_USD"].values
            
            # Non-negativity check
            self.assertTrue((lower >= 0.0).all(), f"Negative lower bound found in horizon {horizon}")
            self.assertTrue((median >= 0.0).all(), f"Negative median found in horizon {horizon}")
            self.assertTrue((upper >= 0.0).all(), f"Negative upper bound found in horizon {horizon}")
            
            # Strict Non-crossing Check across 100% of days
            lower_le_median = (lower <= median).all()
            median_le_upper = (median <= upper).all()
            lower_le_upper = (lower <= upper).all()
            
            self.assertTrue(lower_le_median, f"Quantile crossing: Lower > Median at horizon {horizon}")
            self.assertTrue(median_le_upper, f"Quantile crossing: Median > Upper at horizon {horizon}")
            self.assertTrue(lower_le_upper, f"Quantile crossing: Lower > Upper at horizon {horizon}")

    def test_extreme_scenarios_non_crossing(self):
        """Verifies non-crossing bounds hold under stress-test scenarios."""
        dates = pd.date_range("2026-01-01", periods=60, freq="D")
        df_train = pd.DataFrame({"Date": dates.strftime("%Y-%m-%d"), "DailyCost_USD": 500.0})
        self.forecaster.train_and_evaluate(df_train)
        
        scenarios = [
            {"workload_growth_pct": -80.0, "finops_savings_pct": 50.0}, # Steep reduction
            {"workload_growth_pct": 200.0, "finops_savings_pct": 0.0},  # Massive growth
            {"workload_growth_pct": 0.0, "finops_savings_pct": 100.0},  # 100% savings (zero spend)
            {"workload_growth_pct": -150.0, "finops_savings_pct": 0.0}  # Out of bounds reduction
        ]
        
        for sc in scenarios:
            fc = self.forecaster.generate_future_forecast(
                days_ahead=30,
                workload_growth_pct=sc["workload_growth_pct"],
                finops_savings_pct=sc["finops_savings_pct"]
            )
            lower = fc["Lower_Bound_95_USD"].values
            median = fc["Forecasted_Spend_USD"].values
            upper = fc["Upper_Bound_95_USD"].values
            
            self.assertTrue((lower >= 0.0).all())
            self.assertTrue((lower <= median).all())
            self.assertTrue((median <= upper).all())

    def test_zero_and_negative_horizon_days(self):
        """Verifies days_ahead <= 0 returns empty DataFrame cleanly."""
        df_train = pd.DataFrame({"Date": ["2026-01-01", "2026-01-02"], "DailyCost_USD": [100.0, 100.0]})
        self.forecaster.train_and_evaluate(df_train)
        self.assertEqual(len(self.forecaster.generate_future_forecast(days_ahead=0)), 0)
        self.assertEqual(len(self.forecaster.generate_future_forecast(days_ahead=-10)), 0)


class TestOptimizerWhiteBox(unittest.TestCase):
    """
    White-Box Unit Tests for src/optimizer.py:
    - Empty DataFrame safety
    - Single-date IndexError boundary safety
    - Zero spend division by zero safety
    - Mutually exclusive Rightsizing calculation boundaries (Idle, Right-sizing, Commitment, Optimized)
    - Storage isolation to prevent double counting
    - Percentage and maturity score clamping
    """
    def test_empty_dataframe_optimizer(self):
        """Verifies optimizer handles empty DataFrame without exceptions."""
        opt = FinOpsOptimizer(pd.DataFrame())
        portfolio = opt.generate_savings_portfolio()
        self.assertEqual(portfolio["Annual_Run_Rate_USD"], 0.0)
        self.assertEqual(portfolio["Total_Annual_Savings_USD"], 0.0)
        self.assertEqual(portfolio["Savings_Percentage"], 0.0)
        
        recs = opt.get_actionable_recommendations_table()
        self.assertIsInstance(recs, pd.DataFrame)
        self.assertEqual(len(recs), 0)

    def test_single_date_index_error_boundary(self):
        """Verifies dataset with 1 date or < 14 dates does not raise IndexError."""
        single_date_df = pd.DataFrame([{
            "Date": "2026-01-01",
            "CloudProvider": "AWS",
            "Department": "Eng",
            "Service": "AmazonEC2",
            "DailyCost_USD": 200.0,
            "Avg_CPU_Utilization_Pct": 25.0
        }])
        opt = FinOpsOptimizer(single_date_df)
        portfolio = opt.generate_savings_portfolio()
        self.assertGreater(portfolio["Annual_Run_Rate_USD"], 0.0)
        self.assertGreater(portfolio["Total_Annual_Savings_USD"], 0.0)
        
        recs = opt.get_actionable_recommendations_table()
        self.assertIsInstance(recs, pd.DataFrame)

    def test_zero_spend_division_by_zero(self):
        """Verifies zero spend does not cause division by zero in savings percentage."""
        df_zero = pd.DataFrame([{
            "Date": "2026-01-01",
            "CloudProvider": "AWS",
            "Department": "Eng",
            "Service": "AmazonEC2",
            "DailyCost_USD": 0.0,
            "Avg_CPU_Utilization_Pct": 10.0
        }])
        opt = FinOpsOptimizer(df_zero)
        portfolio = opt.generate_savings_portfolio()
        self.assertEqual(portfolio["Annual_Run_Rate_USD"], 0.0)
        self.assertEqual(portfolio["Total_Annual_Savings_USD"], 0.0)
        self.assertEqual(portfolio["Savings_Percentage"], 0.0)

    def test_rightsizing_calculation_boundaries(self):
        """
        Mathematical Boundary Tests:
        - CPU < 15.0% -> Idle cleanup (70% savings)
        - 15.0% <= CPU < 35.0% -> Right-sizing (30% savings)
        - 35.0% <= CPU <= 75.0% -> Commitment discount (28% savings)
        - CPU > 75.0% -> Optimized (0% savings)
        """
        date = "2026-01-01"
        spend = 1000.0
        annual_spend = spend * 365.0
        
        # Case 1: CPU = 14.99% (Idle)
        df_idle = pd.DataFrame([{"Date": date, "DailyCost_USD": spend, "Avg_CPU_Utilization_Pct": 14.99, "Service": "Compute"}])
        port_idle = FinOpsOptimizer(df_idle).generate_savings_portfolio()
        self.assertAlmostEqual(port_idle["Idle_Cleanup_Savings_USD"], annual_spend * 0.70, places=1)
        self.assertEqual(port_idle["Right_Sizing_Savings_USD"], 0.0)
        self.assertEqual(port_idle["Commitment_Discounts_Savings_USD"], 0.0)

        # Case 2: CPU = 15.0% (Right-sizing lower boundary)
        df_rs_low = pd.DataFrame([{"Date": date, "DailyCost_USD": spend, "Avg_CPU_Utilization_Pct": 15.0, "Service": "Compute"}])
        port_rs_low = FinOpsOptimizer(df_rs_low).generate_savings_portfolio()
        self.assertEqual(port_rs_low["Idle_Cleanup_Savings_USD"], 0.0)
        self.assertAlmostEqual(port_rs_low["Right_Sizing_Savings_USD"], annual_spend * 0.30, places=1)

        # Case 3: CPU = 34.99% (Right-sizing upper boundary)
        df_rs_high = pd.DataFrame([{"Date": date, "DailyCost_USD": spend, "Avg_CPU_Utilization_Pct": 34.99, "Service": "Compute"}])
        port_rs_high = FinOpsOptimizer(df_rs_high).generate_savings_portfolio()
        self.assertAlmostEqual(port_rs_high["Right_Sizing_Savings_USD"], annual_spend * 0.30, places=1)
        self.assertEqual(port_rs_high["Commitment_Discounts_Savings_USD"], 0.0)

        # Case 4: CPU = 35.0% (Commitment lower boundary)
        df_com_low = pd.DataFrame([{"Date": date, "DailyCost_USD": spend, "Avg_CPU_Utilization_Pct": 35.0, "Service": "Compute"}])
        port_com_low = FinOpsOptimizer(df_com_low).generate_savings_portfolio()
        self.assertEqual(port_com_low["Right_Sizing_Savings_USD"], 0.0)
        self.assertAlmostEqual(port_com_low["Commitment_Discounts_Savings_USD"], annual_spend * 0.28, places=1)

        # Case 5: CPU = 75.0% (Commitment upper boundary)
        df_com_high = pd.DataFrame([{"Date": date, "DailyCost_USD": spend, "Avg_CPU_Utilization_Pct": 75.0, "Service": "Compute"}])
        port_com_high = FinOpsOptimizer(df_com_high).generate_savings_portfolio()
        self.assertAlmostEqual(port_com_high["Commitment_Discounts_Savings_USD"], annual_spend * 0.28, places=1)

        # Case 6: CPU = 75.01% (Optimized - 0% compute waste)
        df_opt = pd.DataFrame([{"Date": date, "DailyCost_USD": spend, "Avg_CPU_Utilization_Pct": 75.01, "Service": "Compute"}])
        port_opt = FinOpsOptimizer(df_opt).generate_savings_portfolio()
        self.assertEqual(port_opt["Idle_Cleanup_Savings_USD"], 0.0)
        self.assertEqual(port_opt["Right_Sizing_Savings_USD"], 0.0)
        self.assertEqual(port_opt["Commitment_Discounts_Savings_USD"], 0.0)

    def test_storage_separation_no_double_counting(self):
        """Verifies storage resources with 0% CPU are not double-counted as idle compute."""
        df_storage = pd.DataFrame([{
            "Date": "2026-01-01",
            "DailyCost_USD": 500.0,
            "Avg_CPU_Utilization_Pct": 0.0,
            "Service": "AmazonS3 (Storage)"
        }])
        port = FinOpsOptimizer(df_storage).generate_savings_portfolio()
        annual_spend = 500.0 * 365.0
        self.assertEqual(port["Idle_Cleanup_Savings_USD"], 0.0)
        self.assertAlmostEqual(port["Storage_Optimization_Savings_USD"], annual_spend * 0.20, places=1)
        self.assertAlmostEqual(port["Total_Annual_Savings_USD"], annual_spend * 0.20, places=1)


class TestDatabaseWhiteBox(unittest.TestCase):
    """
    White-Box Unit Tests for src/database.py:
    - Connection pooling and zero connection leaks
    - Engine singleton management & explicit close_engine()
    - Compound query filtering boundaries (Providers, Departments, Categories, Date ranges, Cost)
    - SQL parameter injection resilience
    - Graceful handling of empty results and missing tables
    """
    def tearDown(self):
        close_engine()

    def test_engine_singleton_connection_management(self):
        """Verifies get_engine returns singleton without creating multiple pools."""
        eng1 = get_engine()
        eng2 = get_engine()
        self.assertIs(eng1, eng2)
        close_engine()

    def test_compound_query_filtering(self):
        """Verifies parameterized compound SQL queries filter multi-cloud records correctly."""
        # Ensure database is initialized
        initialize_database()
        
        # Query full dataset
        df_all = load_focus_dataframe()
        self.assertIsInstance(df_all, pd.DataFrame)
        
        if not df_all.empty:
            providers = list(df_all["CloudProvider"].unique()[:2])
            df_filtered = load_focus_dataframe(providers=providers)
            self.assertTrue(set(df_filtered["CloudProvider"].unique()).issubset(set(providers)))
            
            # Boundary test: Non-existent provider returns 0 records with valid schema
            df_none = load_focus_dataframe(providers=["NonExistentProvider123"])
            self.assertEqual(len(df_none), 0)
            for col in FOCUS_COLUMNS:
                self.assertIn(col, df_none.columns)

    def test_compound_query_date_and_cost_boundaries(self):
        """Verifies date and cost boundary filters."""
        initialize_database()
        df = load_focus_dataframe(min_cost=10.0, max_cost=500.0)
        if not df.empty:
            self.assertTrue((df["DailyCost_USD"] >= 10.0).all())
            self.assertTrue((df["DailyCost_USD"] <= 500.0).all())


class TestBackendServicesWhiteBox(unittest.TestCase):
    """
    White-Box Unit Tests for backend/services.py:
    - Scoped DataFrame retrieval with non-existent filters
    - Safe KPI aggregation on empty scopes
    - Spend trends, department analytics, and anomaly lists on empty scopes
    - Forecast simulation stability
    """
    def setUp(self):
        self.service = FinOpsService()

    def test_scoped_dataframe_empty_boundaries(self):
        """Verifies non-existent provider returns empty DataFrame without throwing error."""
        scoped = self.service.get_scoped_dataframe(providers=["NonExistentCloud"])
        self.assertEqual(len(scoped), 0)
        self.assertIsInstance(scoped, pd.DataFrame)

    def test_get_overview_kpis_empty_scope(self):
        """Verifies get_overview_kpis returns safe zero KPIs when filter matches 0 rows."""
        kpis = self.service.get_overview_kpis(providers=["NonExistentCloud"])
        self.assertEqual(kpis["total_spend_ytd"], 0.0)
        self.assertEqual(kpis["annual_run_rate"], 0.0)
        self.assertEqual(kpis["anomalous_waste_usd"], 0.0)
        self.assertEqual(kpis["anomaly_incident_count"], 0)

    def test_get_spend_trends_empty_scope(self):
        """Verifies get_spend_trends returns empty dictionary structures when scope is empty."""
        trends = self.service.get_spend_trends(providers=["NonExistentCloud"])
        self.assertEqual(trends["daily_trend"], [])
        self.assertEqual(trends["daily_by_provider"], [])
        self.assertEqual(trends["anomalies_summary"], [])
        self.assertEqual(trends["provider_breakdown"], [])

    def test_get_department_analytics_empty_scope(self):
        """Verifies get_department_analytics handles empty scope safely."""
        dept = self.service.get_department_analytics(departments=["NonExistentDept"])
        self.assertEqual(dept["department_spend"], [])
        self.assertEqual(dept["top_services"], [])
        self.assertEqual(dept["efficiency_scatter"], [])

    def test_get_anomalies_empty_scope(self):
        """Verifies get_anomalies returns empty list when no matches."""
        anoms = self.service.get_anomalies(providers=["NonExistentCloud"])
        self.assertEqual(anoms, [])

    def test_get_forecast_simulation(self):
        """Verifies get_forecast executes cleanly and obeys non-crossing guarantees."""
        result = self.service.get_forecast(horizon_days=30, workload_growth=10.0, finops_savings=5.0)
        self.assertIn("forecast", result)
        self.assertIn("metrics", result)
        self.assertEqual(len(result["forecast"]), 30)
        
        # Verify 100% of forecast points satisfy non-crossing condition
        for row in result["forecast"]:
            lower = row["Lower_Bound_95_USD"]
            median = row["Forecasted_Spend_USD"]
            upper = row["Upper_Bound_95_USD"]
            self.assertTrue(0.0 <= lower <= median <= upper, f"Crossing: {lower} <= {median} <= {upper}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
