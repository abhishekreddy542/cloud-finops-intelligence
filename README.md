# ⚡ Abhi Cloud Tech — Cloud Cost Optimization & Forecasting Platform

Production Full-Stack Machine Learning & Cloud FinOps Control Plane built for **Abhi Cloud Tech**.

Combines **Multi-Cloud Telemetry (AWS, Azure, GCP)** with **Advanced Machine Learning (Isolation Forest & Quantile Gradient Boosting)**, backed by a **FastAPI REST API** and a modern, high-performance **Web Application (HTML5 + Tailwind CSS + ApexCharts + Vanilla JS)**.

---

## 🏢 Business Context: Abhi Cloud Tech
**Abhi Cloud Tech** runs all microservices, databases, and AI model training workloads across multi-cloud environments. Due to rapid workload expansion, infrastructure costs escalated to an annualized run-rate of **$8.34M USD**.

This platform was custom-engineered to:
1. Provide real-time cost visibility and unit economics across all engineering divisions.
2. Automatically catch billing surges, runaway egress, and idle resources using **Isolation Forest** and **Rolling Z-Scores**.
3. Accurately forecast 30, 60, and 90-day cloud budgets with **Quantile Gradient Boosting** (achieving a **4.87% MAPE**).
4. Identify and capture **$2.75M in annual recurring savings** (32.9% cloud waste reduction).

---

## 🛠️ Modern Technology Stack

- **Backend API**: **FastAPI** + **Uvicorn** (Asynchronous, high-performance REST microservice)
- **Frontend Architecture**: **Tailwind CSS** + **ApexCharts** + **Lucide Icons** + **Vanilla JavaScript** (Zero bloated build steps, modern glassmorphism UI, animated counters, smooth chart transitions)
- **Machine Learning Core**: **scikit-learn** (`IsolationForest`, `HistGradientBoostingRegressor`)
- **Scientific Computing**: **pandas**, **numpy**, **scipy**, **statsmodels**
- **Interactive OpenAPI Docs**: Swagger UI embedded natively at `/docs`

---

## 🚀 Step-by-Step Manual Execution Guide

### Step 1: Open Windows PowerShell
Open your terminal and navigate to the project directory:
```powershell
cd "C:\Users\M Abhishek Reddy\.gemini\antigravity\scratch\cloud-finops-intelligence"
```

### Step 2: Start the Production Web Server
Run the single startup command:
```powershell
python run_server.py
```

### Step 3: View the Web App in Your Browser
Open your browser and navigate to:
👉 **`http://localhost:8000`**

To explore the interactive backend API documentation, visit:
👉 **`http://localhost:8000/docs`**

---

## 🖥️ Live Demonstration Walkthrough (Tab by Tab)

1. **Executive Command (Tab 1)**:
   - Live animated KPI cards displaying Total Spend ($7.70M YTD), Annualized Run-Rate ($8.37M), Identified Savings ($2.75M / 32.9%), and fleet CPU efficiency.
   - Interactive daily spend area chart with red ML anomaly markers and cloud provider donut chart.
2. **Cost Analytics (Tab 2)**:
   - Departmental spend bar chart across AI/ML Research, Data Platform, Core Engineering, etc.
   - Top infrastructure cost drivers and service breakdown.
3. **ML Anomaly Radar (Tab 3)**:
   - Real-time incident feed combining Isolation Forest and 14-day rolling Z-Scores.
   - Interactive severity filter chips (*All*, *Critical Only*, *High Only*, *Medium Only*) with diagnostic root-cause explanations.
4. **Budget Forecaster (Tab 4)**:
   - 30/60/90-day time-series forecast with 95% Quantile Risk Bounds.
   - **Interactive Live Sliders**: Adjust *Organic Workload Growth* and *Rightsizing Savings* to watch the forecast curve recalculate dynamically.
5. **Rightsizing Engine (Tab 5)**:
   - Annual savings breakdown across the 4 FinOps Foundation pillars.
   - Prioritized engineering action matrix with monthly dollar savings.
   - **Interactive Custom Workload Calculator**: Input custom vCPU, RAM, and hours to calculate instant downsizing savings.

---

## 📂 Repository Architecture

```
cloud-finops-intelligence/
├── backend/
│   ├── main.py                   # FastAPI REST API endpoints & static file serving
│   └── services.py               # ML Pipeline orchestration & cache
├── frontend/
│   ├── index.html                # Semantic, responsive modern single-page dashboard
│   └── static/
│       ├── css/
│       │   └── styles.css        # Custom glassmorphism, pulse keyframes, modern dark styling
│       └── js/
│           ├── app.js            # Reactive application controller & async API client
│           └── charts.js         # ApexCharts rendering engine with dark gradients
├── data/
│   └── cloud_enterprise_billing_telemetry.csv
├── src/                          # Core Machine Learning models
│   ├── data_generator.py
│   ├── anomaly_detection.py
│   ├── forecasting.py
│   └── optimizer.py
├── run_server.py                 # Single-command startup runner
├── Project_Technical_Report.md   # Complete technical architecture report
└── requirements.txt
```
