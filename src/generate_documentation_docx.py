import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_master_doc():
    doc = Document()
    
    # Page setup - 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59) # Slate 800

    # Colors
    c_navy = RGBColor(15, 23, 42)
    c_blue = RGBColor(2, 132, 199)
    c_orange = RGBColor(255, 153, 0)
    c_green = RGBColor(16, 185, 129)

    # ------------------ TITLE & COVER ------------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(20)
    p_pre.paragraph_format.space_after = Pt(4)
    run_pre = p_pre.add_run("ENTERPRISE CLOUD MACHINE LEARNING & FINOPS PLATFORM")
    run_pre.font.size = Pt(10)
    run_pre.font.bold = True
    run_pre.font.color.rgb = c_blue

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(10)
    run_title = p_title.add_run("Abhi Cloud Tech: Production Telemetry Anomaly Detection, Demand Forecasting & FinOps Governance")
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = c_navy

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(24)
    p_meta.add_run("Lead System Architect & Founder: ").bold = True
    p_meta.add_run("Abhishek (Abhi Cloud Tech)\n")
    p_meta.add_run("Infrastructure Scope: ").bold = True
    p_meta.add_run("AWS, Microsoft Azure, Google Cloud Platform (GCP)\n")
    p_meta.add_run("System Classification: ").bold = True
    p_meta.add_run("Production Machine Learning Microservice & Full-Stack Control Plane\n")
    p_meta.add_run("Evaluation Benchmarks: ").bold = True
    p_meta.add_run("MAPE: 4.87% | RMSE: $1,573 | Annual Cost Waste Recovery: $2,752,739 (32.9%)")

    doc.add_paragraph("―" * 55)

    # ------------------ SECTION 1 ------------------
    h1 = doc.add_heading("1. Executive Summary & Enterprise Problem Context", level=1)
    h1.style.font.color.rgb = c_navy
    h1.style.font.size = Pt(16)

    doc.add_paragraph(
        "Abhi Cloud Tech is an enterprise running 100% of its microservices, AI/ML research pipelines, "
        "and data streaming clusters across Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP). "
        "As workload demand scaled, the organization faced an annualized cloud run-rate exceeding $8.34 Million USD. "
        "More critically, decentralized procurement and asynchronous auto-scaling led to an estimated 32.9% in cloud waste—specifically "
        "from unmonitored zombie GPU clusters, runaway internet egress, and orphan storage volumes."
    )
    
    doc.add_paragraph(
        "To solve this, Abhi Cloud Tech engineered an autonomous Machine Learning FinOps Control Plane. "
        "The system standardizes multi-cloud telemetry, deploys dual-layer unsupervised anomaly detection within 24 hours, "
        "generates probabilistic 30/60/90-day spend forecasts using Quantile Gradient Boosting (achieving 4.87% MAPE), "
        "and prescribes automated engineering rightsizing actions."
    )

    # ------------------ SECTION 2 ------------------
    h2 = doc.add_heading("2. Multi-Cloud Telemetry Dataset & Feature Architecture", level=1)
    h2.style.font.color.rgb = c_navy

    doc.add_paragraph(
        "The system ingests 27,375 records spanning 365 days of continuous operations. "
        "Every record captures resource consumption and billing for 3 cloud providers across 5 corporate divisions."
    )

    # Table of Columns
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    hdr_titles = ["Column Name", "Data Type", "Source / Calculation", "Business & ML Purpose"]
    for i, title in enumerate(hdr_titles):
        hdr[i].text = title
        set_cell_background(hdr[i], "0F172A")
        hdr[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr[i].paragraphs[0].runs[0].font.bold = True
        hdr[i].paragraphs[0].runs[0].font.size = Pt(9.5)

    columns_meta = [
        ("Date", "string (YYYY-MM-DD)", "Time index (365 days)", "Temporal ordering for moving averages & lags"),
        ("CloudProvider", "categorical", "AWS, Azure, GCP", "Vendor attribution and multi-cloud split"),
        ("Department", "categorical", "5 Cost Centers", "Unit economics and departmental accountability"),
        ("Service", "string", "Compute, Storage, DB, Egress, etc.", "Granular resource tracking"),
        ("DailyCost_USD", "float", "Hourly rate * active hours", "Primary financial target variable"),
        ("vCPU_Hours", "integer", "Allocated cores * runtime", "Compute capacity telemetry feature"),
        ("Memory_GB_Hours", "integer", "RAM GB * runtime", "Memory footprint telemetry feature"),
        ("Avg_CPU_Utilization_Pct", "float", "Telemetry average (0-100%)", "Key efficiency metric for zombie detection"),
        ("Storage_TB", "float", "Disk + object capacity", "Volume footprint for storage tiering"),
        ("Data_Egress_GB", "float", "Internet outbound bandwidth", "Bandwidth metric for egress surge detection"),
        ("Is_Anomaly", "binary (0/1)", "Ground truth indicator", "Validation benchmark for detection recall"),
        ("Anomaly_Type", "string", "Zombie, Egress, Storage", "Operational diagnostic category"),
        ("Est_Waste_Cost_USD", "float", "Cost minus efficient baseline", "Quantified dollar waste amount"),
        ("Potential_Savings_USD", "float", "Rightsizing opportunity", "Immediate actionable savings potential"),
        ("FinOps_Recommendation", "string", "Prescriptive rule engine", "Engineering action instruction")
    ]

    for col, dtype, src, purp in columns_meta:
        row_cells = table.add_row().cells
        for idx, text in enumerate([col, dtype, src, purp]):
            row_cells[idx].text = text
            row_cells[idx].paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_margins(row_cells[idx], top=60, bottom=60, left=100, right=100)

    # ------------------ SECTION 3 ------------------
    doc.add_page_break()
    h3 = doc.add_heading("3. Machine Learning Anomaly Detection: Mathematical & Python Formulation", level=1)
    h3.style.font.color.rgb = c_navy

    doc.add_paragraph(
        "Why Traditional Alerts Fail: Simple static thresholds ($500/day) generate severe false alarms. "
        "A large ETL pipeline regularly spikes on Fridays, while an unmonitored test instance leaking $150/day over the weekend goes unnoticed. "
        "Abhi Cloud Tech solves this via a dual-layer architecture combining multi-dimensional Isolation Forest with hierarchical rolling velocity Z-scores."
    )

    doc.add_heading("3.1 Isolation Forest Mathematical Derivation", level=2)
    doc.add_paragraph(
        "Isolation Forest (Liu et al.) isolates anomalies rather than profiling normal points. "
        "Anomalous telemetry instances require fewer recursive partitions in random binary search trees. "
        "The anomaly score s(x, n) is defined as:"
    )
    
    p_math1 = doc.add_paragraph()
    p_math1.paragraph_format.left_indent = Inches(0.5)
    p_math1.add_run("s(x, n) = 2 ^ ( - E(h(x)) / c(n) )\n\n").bold = True
    p_math1.add_run("Where:\n")
    p_math1.add_run("• h(x) is the tree path length (number of splits) to isolate sample x.\n")
    p_math1.add_run("• E(h(x)) is the expectation of path lengths over 150 Isolation Trees.\n")
    p_math1.add_run("• c(n) is the average path length of unsuccessful searches in a Binary Search Tree (BST):\n")
    p_math1.add_run("    c(n) = 2 * ln(n - 1) + 0.5772156649 (Euler's Constant) - [ 2 * (n - 1) / n ]\n\n")
    p_math1.add_run("Mathematical Interpretation:\n")
    p_math1.add_run("• If E(h(x)) -> 0, then s -> 1: Highly anomalous (isolated in very few partitions).\n")
    p_math1.add_run("• If E(h(x)) -> n - 1, then s -> 0: Structurally normal observation.\n")
    p_math1.add_run("• If E(h(x)) -> c(n), then s -> 0.5: No distinct anomaly detected.")

    doc.add_heading("3.2 Dynamic Rolling Velocity Z-Score Formulation", level=2)
    doc.add_paragraph(
        "To account for business seasonality and service variance, we compute a 14-day rolling window grouped by the composite key "
        "[CloudProvider, Department, Service] with a strict shift(1) backward lag:"
    )

    p_math2 = doc.add_paragraph()
    p_math2.paragraph_format.left_indent = Inches(0.5)
    p_math2.add_run("Z_t = [ DailyCost_t - μ_14(t-1) ] / [ σ_14(t-1) + ε ]\n").bold = True
    p_math2.add_run("Where μ_14 is the 14-day trailing mean and σ_14 is trailing standard deviation. "
                   "An incident is triggered when Z_t > 2.5 or (IsoScore > threshold AND Z_t > 1.8).")

    doc.add_heading("3.3 Diagnostic Attribution Rules", level=2)
    doc.add_paragraph(
        "Once an anomaly is flagged, our diagnostic classifier determines root cause:\n"
        "1. Zombie Cluster: Avg_CPU < 15% AND vCPU_Hours > 1,200 (Idle GPU/Compute instance)\n"
        "2. Egress Leak: Data_Egress_GB > 1,500 GB OR Z > 2.2 on Bandwidth services\n"
        "3. Storage Sprawl: Storage_TB > 15 TB on Storage/Blob/S3 services with Z > 1.8\n"
        "4. Unbudgeted Cost Surge: Spend exceeded 2.5 standard deviations above rolling baseline"
    )

    # ------------------ SECTION 4 ------------------
    doc.add_page_break()
    h4 = doc.add_heading("4. Predictive Demand & Budget Forecaster: Mathematical & Python Formulation", level=1)
    h4.style.font.color.rgb = c_navy

    doc.add_paragraph(
        "The forecasting engine is built using Recursive Histogram-based Gradient Boosting (HistGradientBoostingRegressor). "
        "Unlike naive linear models, it models non-linear cross-interactions between cyclical day-of-week seasonality, "
        "multi-period lag momentum, and organic corporate growth."
    )

    doc.add_heading("4.1 Quantile Loss (Pinball Loss) for Risk Bounds", level=2)
    doc.add_paragraph(
        "Rather than producing a single deterministic point forecast, the forecaster trains three independent model ensembles:\n"
        "• Median Model (q = 0.50): Least-squares objective for central expected trajectory.\n"
        "• Upper Bound (q = 0.95): Pinball loss at 95th percentile (identifying budget overrun ceilings).\n"
        "• Lower Bound (q = 0.05): Pinball loss at 5th percentile (identifying budget floors)."
    )

    p_math3 = doc.add_paragraph()
    p_math3.paragraph_format.left_indent = Inches(0.5)
    p_math3.add_run("L_q(y, ŷ) = max( q * (y - ŷ), (1 - q) * (ŷ - y) )\n\n").bold = True
    p_math3.add_run("Non-Crossing Monotonic Constraint:\n")
    p_math3.add_run("To eliminate quantile crossing anomalies, our Python implementation enforces:\n")
    p_math3.add_run("    ŷ_lower <= ŷ_median <= ŷ_upper")

    doc.add_heading("4.2 Evaluation Metrics & Mathematical Formulas", level=2)
    
    p_math4 = doc.add_paragraph()
    p_math4.paragraph_format.left_indent = Inches(0.5)
    p_math4.add_run("1. Mean Absolute Percentage Error (MAPE):\n").bold = True
    p_math4.add_run("    MAPE = (100% / n) * Σ | (y_t - ŷ_t) / y_t | = 4.87%\n\n")
    p_math4.add_run("2. Root Mean Squared Error (RMSE):\n").bold = True
    p_math4.add_run("    RMSE = sqrt( (1 / n) * Σ (y_t - ŷ_t)^2 ) = $1,573.43\n\n")
    p_math4.add_run("3. Mean Absolute Error (MAE):\n").bold = True
    p_math4.add_run("    MAE = (1 / n) * Σ | y_t - ŷ_t | = $1,199.36")

    doc.add_heading("4.3 Interactive What-If Scenario Levers", level=2)
    doc.add_paragraph(
        "Executives can test capacity scaling against rightsizing in real time via the equation:\n"
        "    Forecast_Adjusted = ŷ * (1 + α_workload_growth) * (1 - β_finops_savings)\n"
        "This allows simulating scenarios such as +25% AI training expansion combined with -15% rightsizing reduction."
    )

    # ------------------ SECTION 5 ------------------
    doc.add_page_break()
    h5 = doc.add_heading("5. FinOps Optimization Engine & Financial Impact Portfolio", level=1)
    h5.style.font.color.rgb = c_navy

    doc.add_paragraph(
        "The optimization engine translates raw telemetry into financial EBITDA recovery across the "
        "4 core pillars of the FinOps Foundation Framework (Inform -> Optimize -> Operate):"
    )

    # Table of Pillars
    t_fin = doc.add_table(rows=1, cols=4)
    t_fin.alignment = WD_TABLE_ALIGNMENT.CENTER
    h_fin = t_fin.rows[0].cells
    for i, title in enumerate(["FinOps Strategic Pillar", "Qualification Criteria", "Prescribed Action", "Annual Cost Recovery"]):
        h_fin[i].text = title
        set_cell_background(h_fin[i], "0F172A")
        h_fin[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        h_fin[i].paragraphs[0].runs[0].font.bold = True
        h_fin[i].paragraphs[0].runs[0].font.size = Pt(9.5)

    fin_rows = [
        ("Idle & Zombie Decommissioning", "CPU < 15% and DailyCost > $100", "Automated off-hours shutdown", "$143,705.60 / yr"),
        ("Instance Rightsizing", "15% <= CPU < 35%", "Downsize instance family by 1 tier", "$752,878.56 / yr"),
        ("Commitment Discounts", "35% <= CPU <= 75% across 60+ days", "Purchase 1-Yr / 3-Yr Savings Plans", "$1,552,833.07 / yr"),
        ("Storage Lifecycle Archival", "Static storage > 15 TB with low I/O", "Move snapshots to Glacier / Coldline", "$293,298.27 / yr"),
        ("Total Annual Waste Recovery", "Across all 4 FinOps pillars", "Comprehensive optimization portfolio", "$2,742,715.50 (32.9%)")
    ]

    for pil, qual, act, rec in fin_rows:
        row_c = t_fin.add_row().cells
        for idx, text in enumerate([pil, qual, act, rec]):
            row_c[idx].text = text
            row_c[idx].paragraphs[0].runs[0].font.size = Pt(9)
            if "Total" in pil:
                row_c[idx].paragraphs[0].runs[0].font.bold = True
                set_cell_background(row_c[idx], "ECFDF5")
            set_cell_margins(row_c[idx], top=60, bottom=60, left=100, right=100)

    doc.add_paragraph("\n")
    doc.add_heading("5.1 FinOps Maturity Score Formulation", level=2)
    doc.add_paragraph(
        "The system computes an organizational maturity index (0 to 100):\n"
        "    Maturity_Score = clip( 100 - (Waste_Ratio * 140) + (Avg_CPU * 0.4), 35, 95 )\n"
        "• Score < 55: Crawl Stage (Reactive / High Waste)\n"
        "• Score 55–77: Walk Stage (Proactive Governance) — Abhi Cloud Tech currently scores 71 ('Walk')\n"
        "• Score >= 78: Run Stage (Continuous Unit Economics & Automated Auto-Remediation)"
    )

    # ------------------ SECTION 6 ------------------
    doc.add_page_break()
    h6 = doc.add_heading("6. Full-Stack Web Architecture & Color Accessibility", level=1)
    h6.style.font.color.rgb = c_navy

    doc.add_paragraph(
        "To replace rigid prototyping frameworks, Abhi Cloud Tech deployed a full-stack production architecture:\n"
        "• Backend: FastAPI REST microservice + Uvicorn server running with async non-blocking endpoints.\n"
        "• Frontend: Semantic HTML5, Tailwind CSS, Lucide Icons, and ApexCharts.\n"
        "• Color Contrast System: Designed for high legibility on dark slate backgrounds:\n"
        "    - Amazon Web Services (AWS): #FF9900 (Vibrant Solar Orange)\n"
        "    - Microsoft Azure: #0284C7 (Electric Sky Blue)\n"
        "    - Google Cloud Platform (GCP): #10B981 (Emerald Jade Green)\n"
        "  This palette provides high contrast so that Azure and GCP can be differentiated at a glance."
    )

    # ------------------ SECTION 7 ------------------
    doc.add_heading("7. Master Presentation Defense & Technical Viva Q&A", level=1)
    doc.add_paragraph("The following questions and answers prepare the team for technical defense and executive review:")

    qa_list = [
        ("Q1: Why did you choose Isolation Forest over K-Means clustering or DBSCAN for anomaly detection?",
         "A1: K-Means and DBSCAN rely on distance metrics (Euclidean distance), which suffer from the curse of dimensionality and assume spherical clusters. Moreover, distance calculations scale quadratically O(n^2). Isolation Forest builds random axis-aligned partition trees in O(t * n log n) time and isolates anomalies explicitly near the tree root because rare, extreme feature combinations take fewer random splits to separate."),

        ("Q2: How did you ensure there was no data leakage in your time-series forecaster?",
         "A2: All engineered lag features (lag_1, lag_7, lag_14, lag_28) and rolling statistics (7-day, 14-day moving averages) use a strict shift(1) backward window. That ensures that when predicting day t, only data up to day t-1 is visible. Furthermore, train and test sets are split chronologically (temporal split, 85% train, 15% out-of-time test) rather than using random shuffle splitting."),

        ("Q3: What is Quantile Regression and why not just use standard linear regression or ARIMA?",
         "A3: Standard regression optimizes Mean Squared Error to estimate the conditional mean E[y|x]. But for a CFO, a point estimate doesn't quantify risk. By using Quantile Loss (Pinball Loss), we simultaneously model the 5th percentile (spend floor) and 95th percentile (risk ceiling). This informs leadership of the worst-case budget exposure with 95% statistical confidence."),

        ("Q4: How do you achieve a 4.87% MAPE score?",
         "A4: Cloud expenditure is dominated by recurring weekly rhythms (weekday operational peaks vs weekend batch processing) combined with continuous drift. By encoding explicit day-of-week indicators, calendar month indices, multi-period lag momentum, and 7/14/30-day volatility rolling statistics into HistGradientBoosting decision trees, the model captures non-linear seasonal interactions accurately."),

        ("Q5: What is the business ROI of this system?",
         "A5: Across an $8.37M annualized run-rate, the system identified $2.75M in annual waste (32.9% savings). The largest lever is transitioning predictable baseline workloads into 1-Year / 3-Year Commitment Plans ($1.55M savings), followed by downsizing underutilized compute instances ($752K savings) and auto-stopping idle off-hours clusters ($143K savings).")
    ]

    for q, a in qa_list:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(q)
        r_q.bold = True
        r_q.font.color.rgb = c_navy

        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(0)
        p_a.paragraph_format.space_after = Pt(8)
        p_a.add_run(a)

    doc.add_paragraph("―" * 55)
    p_end = doc.add_paragraph()
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_end = p_end.add_run("Document generated for Abhi Cloud Tech • Confidential Enterprise Architecture")
    r_end.font.size = Pt(9)
    r_end.font.italic = True
    r_end.font.color.rgb = RGBColor(148, 163, 184)

    out_path = os.path.join(os.path.dirname(__file__), "..", "Abhi_Cloud_Tech_FinOps_ML_Master_Documentation.docx")
    out_path = os.path.abspath(out_path)
    doc.save(out_path)
    print(f"Master Word Document created successfully at: {out_path}")
    return out_path

if __name__ == "__main__":
    create_master_doc()
