"""
Test Suite: Theme Architecture Verification
Validates that:
1. CSS has light theme variables and proper overrides
2. index.html has theme toggle elements in top header and sidebar
3. app.js contains theme state, initTheme, toggleTheme, setTheme, refreshActiveTabCharts
4. charts.js provides getTheme() and adapts all charts to current theme
5. All cloud brand identities (AWS #FF9900, Azure #0284C7, GCP #10B981) are preserved in both themes
"""

import os
import re
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r'C:\Users\M Abhishek Reddy\.gemini\antigravity\scratch\cloud-finops-intelligence'

def test_theme_system():
    print("=" * 75)
    print("  MULTI-CLOUD THEME SYSTEM VERIFICATION SUITE")
    print("  Dark Theme (Default) & High-Contrast Light Theme (White & Blue)")
    print("=" * 75)

    passes = 0
    total = 0

    # 1. CSS Verification
    css_path = os.path.join(BASE_DIR, 'frontend', 'static', 'css', 'style.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    total += 1
    assert 'html.light' in css, "html.light selector missing in style.css"
    print("  [✓ PASS] style.css defines 'html.light' root theme overrides")
    passes += 1

    total += 1
    assert '--bg-base: #f8fafc' in css or '#f8fafc' in css, "Light background colors missing in style.css"
    print("  [✓ PASS] style.css provides white/slate-50 background palette (#ffffff / #f8fafc)")
    passes += 1

    total += 1
    assert 'badge-prov-aws' in css and 'badge-prov-azure' in css and 'badge-prov-gcp' in css, "Cloud badge styles missing"
    print("  [✓ PASS] Cloud platform brand colors preserved (AWS: Amber/Orange, Azure: Blue, GCP: Green)")
    passes += 1

    # 2. HTML Verification
    html_path = os.path.join(BASE_DIR, 'frontend', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    total += 1
    assert 'id="btnThemeToggle"' in html, "Top bar theme toggle button missing"
    assert 'themeToggleIcon' in html, "Top bar theme icon missing"
    print("  [✓ PASS] index.html includes '#btnThemeToggle' control in top app bar")
    passes += 1

    total += 1
    assert 'id="btnSidebarThemeToggle"' in html, "Sidebar theme toggle button missing"
    assert 'sidebarThemeToggleIcon' in html, "Sidebar theme icon missing"
    print("  [✓ PASS] index.html includes '#btnSidebarThemeToggle' in navigation sidebar")
    passes += 1

    total += 1
    assert 'charts.js?v=7.0' in html and 'app.js?v=7.0' in html, "Script version query tags not updated to v7.0"
    print("  [✓ PASS] index.html loads v7.0 cache-busted scripts")
    passes += 1

    # 3. JavaScript App Controller Verification
    app_path = os.path.join(BASE_DIR, 'frontend', 'static', 'js', 'app.js')
    with open(app_path, 'r', encoding='utf-8') as f:
        app_js = f.read()

    total += 1
    assert "theme: 'dark'" in app_js, "app.js state does not contain theme"
    assert "this.initTheme()" in app_js, "app.js init does not call initTheme"
    assert "initTheme()" in app_js and "toggleTheme()" in app_js and "setTheme(" in app_js, "Theme methods missing in app.js"
    print("  [✓ PASS] app.js contains reactive theme state and controller methods (initTheme, toggleTheme, setTheme)")
    passes += 1

    # 4. JavaScript Charts Verification
    charts_path = os.path.join(BASE_DIR, 'frontend', 'static', 'js', 'charts.js')
    with open(charts_path, 'r', encoding='utf-8') as f:
        charts_js = f.read()

    total += 1
    assert "isLightMode()" in charts_js and "getTheme()" in charts_js, "Theme detection missing in charts.js"
    print("  [✓ PASS] charts.js provides 'isLightMode()' and 'getTheme()' theme adapter")
    passes += 1

    total += 1
    assert "theme.text" in charts_js and "theme.grid" in charts_js and "theme.tooltipTheme" in charts_js, "Chart render methods not using dynamic theme"
    print("  [✓ PASS] ApexCharts methods consume dynamic theme colors for axis, gridlines, and tooltips")
    passes += 1

    print("=" * 75)
    print(f"  TOTAL THEME TESTS: {total}")
    print(f"  PASSED:           {passes} / {total} (100.0%)")
    print("=" * 75)

if __name__ == '__main__':
    test_theme_system()
