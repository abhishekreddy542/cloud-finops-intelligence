import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import custom FinOps ML modules
from src.data_generator import generate_finops_dataset
from src.anomaly_detection import FinOpsAnomalyDetector
from src.forecasting import FinOpsForecaster
from src.optimizer import FinOpsOptimizer

# ---------------------------------------------------------
# Page Configuration & Modern Meta Tags
# ---------------------------------------------------------
st.set_page_config(
    page_title="Abhi Cloud Tech | FinOps ML Control Plane",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Modern CSS Design System (Inter Font, Smooth Elevations, Pulse Keyframes)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Keyframe Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(14px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Custom Metric Cards */
    .metric-container {
        animation: fadeInUp 0.5s ease-out forwards;
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .metric-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        border-color: #cbd5e1;
    }

    .metric-accent {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: #2563eb;
    }

    .metric-accent.green { background: #10b981; }
    .metric-accent.red { background: #ef4444; }
    .metric-accent.amber { background: #f59e0b; }
    .metric-accent.purple { background: #8b5cf6; }

    .metric-label {
        font-size: 11.5px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }

    .metric-val {
        font-size: 27px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 6px;
        letter-spacing: -0.5px;
    }

    .metric-sub {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 500;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Sidebar Logo Header */
    .brand-banner {
        background: linear-gradient(135deg, #090d16 0%, #1e293b 100%);
        padding: 18px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .brand-title {
        font-size: 18px;
        font-weight: 800;
        letter-spacing: -0.3px;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-tag {
        font-size: 10px;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        padding: 2px 7px;
        border-radius: 4px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-top: 4px;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Status Pills */
    .status-badge {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    .status-critical {
        background-color: #fee2e2;
        color: #b91c1c;
        animation: pulseGlow 2s infinite;
    }

    .status-high {
        background-color: #ffedd5;
        color: #c2410c;
    }

    .status-medium {
        background-color: #fef3c7;
        color: #b45309;
    }

    /* Section Headers */
    .section-title {
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 6px;
        letter-spacing: -0.4px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Pipeline & Caching
# ---------------------------------------------------------
@st.cache_data
def get_or_create_dataset():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    data_path = os.path.join(data_dir, "cloud_enterprise_billing_telemetry.csv")
    if not os.path.exists(data_path):
        os.makedirs(data_dir, exist_ok=True)
        df = generate_finops_dataset()
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)
    return df

raw_df = get_or_create_dataset()

# Anomaly detection pipeline cached on raw data
@st.cache_data
def run_anomaly_pipeline(df):
    detector = FinOpsAnomalyDetector()
    return detector.fit_predict(df)

analyzed_df = run_anomaly_pipeline(raw_df)

# Forecaster model cached
@st.cache_resource
def train_forecaster(df):
    forecaster = FinOpsForecaster()
    metrics = forecaster.train_and_evaluate(df)
    return forecaster, metrics

forecaster, forecast_metrics = train_forecaster(analyzed_df)

# ---------------------------------------------------------
# Sidebar Controls & Scope Selectors
# ---------------------------------------------------------
st.sidebar.markdown("""
<div class="brand-banner">
    <div class="brand-title">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4C9.11 4 6.6 5.64 5.35 8.04C2.34 8.36 0 10.91 0 14C0 17.31 2.69 20 6 20H19C21.76 20 24 17.76 24 15C24 12.36 21.95 10.22 19.35 10.04Z" fill="#38BDF8"/>
            <path d="M13 10L9 15H13L11 19L16 13H12L13 10Z" fill="#0F172A"/>
        </svg>
        Abhi Cloud Tech
    </div>
    <div class="brand-tag">Production FinOps Engine v2.4</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🎛️ Active Telemetry Scope")

all_providers = list(analyzed_df["CloudProvider"].unique())
selected_provider = st.sidebar.multiselect(
    "Cloud Platforms:",
    options=all_providers,
    default=all_providers
)

all_depts = list(analyzed_df["Department"].unique())
selected_dept = st.sidebar.multiselect(
    "Engineering Divisions:",
    options=all_depts,
    default=all_depts
)

# Robust fallback for empty selections
if not selected_provider:
    selected_provider = all_providers
if not selected_dept:
    selected_dept = all_depts

# Filter dataset dynamically
filtered_df = analyzed_df[
    (analyzed_df["CloudProvider"].isin(selected_provider)) & 
    (analyzed_df["Department"].isin(selected_dept))
].copy()

# Dynamic optimizer execution for active filter scope
optimizer = FinOpsOptimizer(filtered_df)
portfolio = optimizer.generate_savings_portfolio()
action_table = optimizer.get_actionable_recommendations_table()

st.sidebar.divider()
st.sidebar.markdown("### 📊 Scope Statistics")
st.sidebar.write(f"**Tracked Entities**: `{len(filtered_df):,}` records")
st.sidebar.write(f"**Date Range**: `{filtered_df['Date'].min()}` to `{filtered_df['Date'].max()}`")

# Quick reset button
if st.sidebar.button("🔄 Reset Scope to Global", use_container_width=True):
    st.rerun()

# ---------------------------------------------------------
# Main Page Header
# ---------------------------------------------------------
st.title("⚡ Abhi Cloud Tech — Cloud Cost Intelligence Platform")
st.markdown("Enterprise Multi-Cloud Infrastructure Optimization, ML Telemetry Anomaly Detection & Predictive Demand Forecasting")

# Tab Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Command Center", 
    "📈 Cloud Cost Analytics", 
    "🚨 ML Anomaly Detection", 
    "🔮 Predictive Spend Forecasting", 
    "💡 Rightsizing & Optimization Plan"
])

# ================= TAB 1: EXECUTIVE COMMAND CENTER =================
with tab1:
    st.markdown('<div class="section-title">Infrastructure Financial Health & Velocity</div>', unsafe_allow_html=True)
    
    total_spend = filtered_df["DailyCost_USD"].sum()
    anomalies_filtered = filtered_df[filtered_df["detected_anomaly"] == 1]
    total_waste = anomalies_filtered["cost_spike_usd"].sum()
    avg_cpu = filtered_df["Avg_CPU_Utilization_Pct"].mean()
    annual_run_rate = portfolio["Annual_Run_Rate_USD"]
    annual_savings = portfolio["Total_Annual_Savings_USD"]
    savings_pct = portfolio["Savings_Percentage"]
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-accent"></div>
            <div class="metric-label">Total Spend (YTD)</div>
            <div class="metric-val">${total_spend:,.0f}</div>
            <div class="metric-sub">Across {len(selected_provider)} clouds, {len(selected_dept)} depts</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-accent purple"></div>
            <div class="metric-label">Annualized Run-Rate</div>
            <div class="metric-val">${annual_run_rate:,.0f}</div>
            <div class="metric-sub">Trailing 90-day baseline</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-accent green"></div>
            <div class="metric-label">Identified Savings</div>
            <div class="metric-val" style="color: #059669;">${annual_savings:,.0f}</div>
            <div class="metric-sub">{savings_pct}% of total budget</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-accent red"></div>
            <div class="metric-label">Anomalous Waste</div>
            <div class="metric-val" style="color: #dc2626;">${total_waste:,.0f}</div>
            <div class="metric-sub">{len(anomalies_filtered)} incident spikes flagged</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c5:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-accent amber"></div>
            <div class="metric-label">Compute Efficiency</div>
            <div class="metric-val" style="color: #d97706;">{avg_cpu:.1f}%</div>
            <div class="metric-sub">Avg fleet CPU utilization</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns([2, 1])
    with col_chart1:
        st.markdown("#### Cumulative Daily Spend Trajectory")
        daily_trend = filtered_df.groupby("Date")["DailyCost_USD"].sum().reset_index()
        fig_trend = px.area(
            daily_trend, 
            x="Date", 
            y="DailyCost_USD", 
            title="Abhi Cloud Tech Daily Infrastructure Spend ($ USD)",
            color_discrete_sequence=["#2563EB"]
        )
        fig_trend.update_layout(
            xaxis_title="Date", 
            yaxis_title="Daily Spend ($)", 
            height=340,
            margin=dict(l=20, r=20, t=40, b=20),
            hovermode="x unified"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### Cloud Provider Allocation")
        provider_share = filtered_df.groupby("CloudProvider")["DailyCost_USD"].sum().reset_index()
        fig_pie = px.pie(
            provider_share, 
            names="CloudProvider", 
            values="DailyCost_USD", 
            hole=0.5,
            color="CloudProvider",
            color_discrete_map={"AWS": "#FF9900", "Azure": "#0089D6", "GCP": "#4285F4"}
        )
        fig_pie.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ================= TAB 2: CLOUD COST ANALYTICS =================
with tab2:
    st.markdown('<div class="section-title">Departmental Workload & Infrastructure Analytics</div>', unsafe_allow_html=True)
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("#### Spend Allocation by Department")
        dept_spend = filtered_df.groupby(["Department", "CloudProvider"])["DailyCost_USD"].sum().reset_index()
        fig_dept = px.bar(
            dept_spend, 
            x="Department", 
            y="DailyCost_USD", 
            color="CloudProvider", 
            barmode="stack",
            title="Total Spend per Business Unit",
            color_discrete_map={"AWS": "#FF9900", "Azure": "#0089D6", "GCP": "#4285F4"}
        )
        fig_dept.update_layout(xaxis_tickangle=-25, height=380, margin=dict(l=20, r=20, t=40, b=40))
        st.plotly_chart(fig_dept, use_container_width=True)
        
    with c_right:
        st.markdown("#### Top Cloud Cost Drivers")
        srv_spend = filtered_df.groupby("Service")["DailyCost_USD"].sum().reset_index().sort_values(by="DailyCost_USD", ascending=True).tail(10)
        fig_srv = px.bar(
            srv_spend, 
            x="DailyCost_USD", 
            y="Service", 
            orientation="h",
            color="DailyCost_USD",
            color_continuous_scale="Viridis",
            title="Top 10 Infrastructure Cost Drivers"
        )
        fig_srv.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_srv, use_container_width=True)

    st.markdown("#### Compute Efficiency Quadrant (Utilization vs Cost)")
    sample_scatter = filtered_df.sample(min(1000, len(filtered_df)), random_state=42)
    fig_scatter = px.scatter(
        sample_scatter,
        x="Avg_CPU_Utilization_Pct",
        y="DailyCost_USD",
        color="CloudProvider",
        size="vCPU_Hours",
        hover_data=["Department", "Service", "Date"],
        title="Compute Efficiency: Top-Left Quadrant indicates High-Cost Idle Waste",
        labels={"Avg_CPU_Utilization_Pct": "Average CPU Utilization (%)", "DailyCost_USD": "Daily Cost ($ USD)"},
        color_discrete_map={"AWS": "#FF9900", "Azure": "#0089D6", "GCP": "#4285F4"}
    )
    fig_scatter.add_vline(x=20, line_dash="dash", line_color="#ef4444", annotation_text="Underutilized (<20%)")
    fig_scatter.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ================= TAB 3: ML ANOMALY DETECTION =================
with tab3:
    st.markdown('<div class="section-title">Machine Learning Anomaly Detection & Incident Diagnostics</div>', unsafe_allow_html=True)
    st.markdown("""
    Combines **Isolation Forest (Multivariate Outlier Mining)** and **Dynamic Rolling Z-Scores (14-Day Velocity Window)** 
    to automatically flag billing spikes, runaway egress, and zombie resources in real time.
    """)
    
    # Anomaly visual over time
    daily_agg = filtered_df.groupby("Date").agg({
        "DailyCost_USD": "sum",
        "detected_anomaly": "max",
        "cost_spike_usd": "sum"
    }).reset_index()
    
    fig_anom = go.Figure()
    fig_anom.add_trace(go.Scatter(
        x=daily_agg["Date"],
        y=daily_agg["DailyCost_USD"],
        mode="lines",
        name="Daily Spend",
        line=dict(color="#2563EB", width=2)
    ))
    
    anom_points = daily_agg[daily_agg["detected_anomaly"] == 1]
    fig_anom.add_trace(go.Scatter(
        x=anom_points["Date"],
        y=anom_points["DailyCost_USD"],
        mode="markers",
        name="ML Anomaly Spike",
        marker=dict(color="#EF4444", size=9, symbol="diamond", line=dict(width=1.5, color="#FFFFFF"))
    ))
    
    fig_anom.update_layout(
        title="Abhi Cloud Tech Daily Spend with Automated Anomaly Markers",
        xaxis_title="Date",
        yaxis_title="Daily Spend ($ USD)",
        height=380,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_anom, use_container_width=True)
    
    # Severity Filter & Anomaly Table
    st.markdown("#### 🚨 Live Anomaly Incident Feed")
    severity_choice = st.radio(
        "Filter Incident Severity:",
        ["All Incidents", "CRITICAL Only", "HIGH Only", "MEDIUM Only"],
        horizontal=True
    )
    
    anom_list = filtered_df[filtered_df["detected_anomaly"] == 1].copy()
    if severity_choice == "CRITICAL Only":
        anom_list = anom_list[anom_list["anomaly_severity"] == "CRITICAL"]
    elif severity_choice == "HIGH Only":
        anom_list = anom_list[anom_list["anomaly_severity"] == "HIGH"]
    elif severity_choice == "MEDIUM Only":
        anom_list = anom_list[anom_list["anomaly_severity"] == "MEDIUM"]
        
    anom_list = anom_list.sort_values(by="DailyCost_USD", ascending=False)
    
    if not anom_list.empty:
        display_cols = [
            "Date", "CloudProvider", "Department", "Service", 
            "DailyCost_USD", "cost_spike_usd", "anomaly_severity", "root_cause_diagnosis"
        ]
        show_table = anom_list[display_cols].rename(columns={
            "DailyCost_USD": "Total Cost ($)",
            "cost_spike_usd": "Excess Spike ($)",
            "anomaly_severity": "Severity",
            "root_cause_diagnosis": "Root Cause Diagnostic"
        }).head(25)
        
        st.dataframe(show_table, use_container_width=True)
        
        # 1-Click CSV Exporter
        csv_data = show_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Anomaly Incidents (CSV)",
            data=csv_data,
            file_name="abhi_cloud_tech_anomaly_incidents.csv",
            mime="text/csv",
            use_container_width=False
        )
    else:
        st.success("No anomalies detected in the selected filter window.")

# ================= TAB 4: DEMAND & BUDGET FORECASTING =================
with tab4:
    st.markdown('<div class="section-title">Predictive Demand & Cloud Budget Forecasting</div>', unsafe_allow_html=True)
    st.markdown(f"""
    **Forecaster Performance**: 
    - Mean Absolute Percentage Error (MAPE): **{forecast_metrics['MAPE_Pct']}%**
    - Root Mean Squared Error (RMSE): **${forecast_metrics['RMSE_USD']:,.2f}**
    - Architecture: Recursive HistGradientBoosting with Quantile Loss Bounds (5th and 95th Percentiles)
    """)
    
    # Interactive What-If Scenario Levers
    st.markdown("#### 🎯 Interactive Scenario Simulation")
    s1, s2, s3 = st.columns(3)
    with s1:
        growth_slider = st.slider("Workload Expansion / AI Scaling (%):", min_value=-20, max_value=60, value=15, step=5)
    with s2:
        opt_slider = st.slider("Rightsizing Program Savings (%):", min_value=0, max_value=35, value=10, step=5)
    with s3:
        horizon_days = st.selectbox("Forecast Horizon:", [30, 60, 90], index=1)
        
    future_forecast = forecaster.generate_future_forecast(
        days_ahead=horizon_days,
        workload_growth_pct=growth_slider,
        finops_savings_pct=opt_slider
    )
    
    hist_agg = filtered_df.groupby("Date")["DailyCost_USD"].sum().reset_index()
    
    fig_fc = go.Figure()
    
    # Historical Actuals
    fig_fc.add_trace(go.Scatter(
        x=hist_agg["Date"],
        y=hist_agg["DailyCost_USD"],
        name="Historical Actuals",
        line=dict(color="#64748B", width=1.8)
    ))
    
    # Future ML Forecast
    fig_fc.add_trace(go.Scatter(
        x=future_forecast["Date"],
        y=future_forecast["Forecasted_Spend_USD"],
        name="ML Spend Forecast",
        line=dict(color="#10B981", width=2.8)
    ))
    
    # Upper Bound
    fig_fc.add_trace(go.Scatter(
        x=future_forecast["Date"],
        y=future_forecast["Upper_Bound_95_USD"],
        name="95% Upper Bound",
        line=dict(color="rgba(16, 185, 129, 0.3)", dash="dot")
    ))
    
    # Lower Bound
    fig_fc.add_trace(go.Scatter(
        x=future_forecast["Date"],
        y=future_forecast["Lower_Bound_95_USD"],
        name="95% Lower Bound",
        line=dict(color="rgba(16, 185, 129, 0.3)", dash="dot"),
        fill="tonexty",
        fillcolor="rgba(16, 185, 129, 0.08)"
    ))
    
    fig_fc.update_layout(
        title=f"{horizon_days}-Day Spend Projection for Abhi Cloud Tech (Scenario: +{growth_slider}% Growth, -{opt_slider}% Savings)",
        xaxis_title="Date",
        yaxis_title="Daily Spend ($ USD)",
        height=420,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_fc, use_container_width=True)
    
    proj_total = future_forecast["Forecasted_Spend_USD"].sum()
    st.info(f"💡 **Projected Budget Requirement for Next {horizon_days} Days:** **${proj_total:,.2f} USD**")

# ================= TAB 5: RIGHT-SIZING & OPTIMIZATION =================
with tab5:
    st.markdown('<div class="section-title">FinOps Optimization & Rightsizing Strategy</div>', unsafe_allow_html=True)
    
    r1, r2, r3 = st.columns([1, 1, 1])
    with r1:
        st.metric("FinOps Maturity Level", portfolio.get("FinOps_Maturity_Stage", "Walk (Proactive)"))
    with r2:
        st.metric("Identified Annual Savings", f"${portfolio['Total_Annual_Savings_USD']:,.0f}")
    with r3:
        st.metric("Budget Optimization Ratio", f"{portfolio['Savings_Percentage']}%")
        
    st.markdown("#### Annual Cost Reduction Portfolio by Strategic Pillar")
    savings_data = pd.DataFrame({
        "Category": [
            "Zombie / Idle Compute Decommissioning",
            "Underutilized Instance Right-Sizing",
            "1-Yr / 3-Yr Commitment Discounts (RI/SP)",
            "Storage Lifecycle & Snapshot Purge"
        ],
        "Annual_Savings_USD": [
            portfolio["Idle_Cleanup_Savings_USD"],
            portfolio["Right_Sizing_Savings_USD"],
            portfolio["Commitment_Discounts_Savings_USD"],
            portfolio["Storage_Optimization_Savings_USD"]
        ]
    })
    
    fig_bar_sav = px.bar(
        savings_data,
        x="Annual_Savings_USD",
        y="Category",
        orientation="h",
        color="Annual_Savings_USD",
        color_continuous_scale="Tealgrn",
        text_auto="$,.0f",
        title="Annual Cost Reduction Opportunity ($ USD)"
    )
    fig_bar_sav.update_layout(height=300, showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_bar_sav, use_container_width=True)
    
    st.markdown("#### Prioritized Engineering Action Matrix")
    if not action_table.empty:
        st.dataframe(action_table, use_container_width=True)
        
        # 1-Click Action Plan Exporter
        plan_csv = action_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Engineering Action Matrix (CSV)",
            data=plan_csv,
            file_name="abhi_cloud_tech_rightsizing_action_matrix.csv",
            mime="text/csv",
            use_container_width=False
        )
    else:
        st.write("All workloads are currently operating at peak efficiency.")
        
    st.divider()
    
    # Interactive What-If Workload Cost Calculator
    st.markdown("#### 🧮 Interactive Custom Workload Cost & Rightsizing Calculator")
    st.markdown("Simulate new workloads or evaluate downsizing savings for specific instance clusters:")
    
    calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)
    with calc_col1:
        calc_vcpu = st.number_input("vCPU Count:", min_value=1, max_value=256, value=32, step=4)
    with calc_col2:
        calc_ram = st.number_input("Memory (GB RAM):", min_value=2, max_value=1024, value=128, step=16)
    with calc_col3:
        calc_hours = st.slider("Running Hours per Day:", min_value=1, max_value=24, value=24)
    with calc_col4:
        calc_downsize = st.checkbox("Simulate 50% Downsizing (Rightsize)", value=True)
        
    hourly_rate = (calc_vcpu * 0.048) + (calc_ram * 0.006)
    daily_calc = hourly_rate * calc_hours
    monthly_calc = daily_calc * 30
    savings_calc = monthly_calc * 0.50 if calc_downsize else 0.0
    
    st.markdown(f"""
    <div style="background: #f8fafc; border-radius: 10px; padding: 14px 20px; border: 1px solid #e2e8f0; margin-top: 10px;">
        <span style="font-weight: 700; color: #1e293b;">Estimated Monthly Spend:</span> <code>${monthly_calc:,.2f} USD</code> | 
        <span style="font-weight: 700; color: #059669;">Potential Downsizing Savings:</span> <code>${savings_calc:,.2f} USD/mo</code>
    </div>
    """, unsafe_allow_html=True)
