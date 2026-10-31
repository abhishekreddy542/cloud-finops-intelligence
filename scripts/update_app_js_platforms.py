import sys
from pathlib import Path

app_path = Path(r"C:\Users\M Abhishek Reddy\.gemini\antigravity\scratch\cloud-finops-intelligence\frontend\static\js\app.js")
content = app_path.read_text(encoding="utf-8")

# Normalize newlines
content = content.replace("\r\n", "\n")

# 1. Update State
old_state = """        anomalySeverity: 'ALL',
        allScopeAnomalies: [],
        currentAnomalies: [],
        anomalyPage: 1,
        anomalyPageSize: 25,
        anomalySearchTerm: '',
        anomalySortBy: 'date_desc',"""

new_state = """        anomalySeverity: 'ALL',
        anomalyPlatform: 'ALL',
        allScopeAnomalies: [],
        currentAnomalies: [],
        anomalyPage: 1,
        anomalyPageSize: 25,
        anomalySearchTerm: '',
        anomalySortBy: 'date_desc',"""

if old_state in content:
    content = content.replace(old_state, new_state, 1)
    print("State updated with anomalyPlatform.")
else:
    print("Warning: old_state not matched.")

# 2. Update Event Listeners in setupEventListeners
old_listeners = """        // Anomaly Severity Filter Chips
        document.querySelectorAll('.severity-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                document.querySelectorAll('.severity-chip').forEach(c => c.classList.remove('active', 'border-sky-500', 'text-sky-400'));
                chip.classList.add('active', 'border-sky-500', 'text-sky-400');
                this.state.anomalySeverity = chip.getAttribute('data-severity');
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        });

        // Anomaly Search Input
        const anomSearch = document.getElementById('anomalySearchInput');
        if (anomSearch) {
            anomSearch.addEventListener('input', (e) => {
                this.state.anomalySearchTerm = e.target.value.trim().toLowerCase();
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        }

        // Anomaly Sort Select
        const anomSort = document.getElementById('anomalySortSelect');
        if (anomSort) {
            anomSort.addEventListener('change', (e) => {
                this.state.anomalySortBy = e.target.value;
                this.renderAnomaliesTable();
            });
        }

        // Anomaly Page Size Select
        const anomPageSize = document.getElementById('anomalyPageSizeSelect');
        if (anomPageSize) {
            anomPageSize.addEventListener('change', (e) => {
                this.state.anomalyPageSize = parseInt(e.target.value) || 25;
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        }

        // Anomaly Pagination Controls
        const btnFirst = document.getElementById('btnAnomalyFirst');
        if (btnFirst) {
            btnFirst.addEventListener('click', () => {
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        }

        const btnPrev = document.getElementById('btnAnomalyPrev');
        if (btnPrev) {
            btnPrev.addEventListener('click', () => {
                if (this.state.anomalyPage > 1) {
                    this.state.anomalyPage--;
                    this.renderAnomaliesTable();
                }
            });
        }

        const btnNext = document.getElementById('btnAnomalyNext');
        if (btnNext) {
            btnNext.addEventListener('click', () => {
                this.state.anomalyPage++;
                this.renderAnomaliesTable();
            });
        }

        const btnLast = document.getElementById('btnAnomalyLast');
        if (btnLast) {
            btnLast.addEventListener('click', () => {
                this.state.anomalyPage = 999999;
                this.renderAnomaliesTable();
            });
        }"""

new_listeners = """        // Anomaly Severity Filter Chips
        document.querySelectorAll('.severity-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                document.querySelectorAll('.severity-chip').forEach(c => c.classList.remove('active', 'border-sky-500', 'text-sky-400'));
                chip.classList.add('active', 'border-sky-500', 'text-sky-400');
                this.state.anomalySeverity = chip.getAttribute('data-severity');
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        });

        // Cloud Platform Filter Chips
        document.querySelectorAll('.platform-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                document.querySelectorAll('.platform-chip').forEach(c => c.classList.remove('active', 'border-sky-500', 'text-sky-400', 'text-white'));
                chip.classList.add('active', 'border-sky-500', 'text-white');
                this.state.anomalyPlatform = chip.getAttribute('data-platform');
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        });

        // Anomaly Search Input
        const anomSearch = document.getElementById('anomalySearchInput');
        if (anomSearch) {
            anomSearch.addEventListener('input', (e) => {
                this.state.anomalySearchTerm = e.target.value.trim().toLowerCase();
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        }

        // Anomaly Sort Select
        const anomSort = document.getElementById('anomalySortSelect');
        if (anomSort) {
            anomSort.addEventListener('change', (e) => {
                this.state.anomalySortBy = e.target.value;
                this.renderAnomaliesTable();
            });
        }

        // Anomaly Page Size Select
        const anomPageSize = document.getElementById('anomalyPageSizeSelect');
        if (anomPageSize) {
            anomPageSize.addEventListener('change', (e) => {
                const val = e.target.value;
                this.state.anomalyPageSize = val === 'ALL' ? 999999 : (parseInt(val) || 25);
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        }

        // Anomaly Pagination Controls
        const btnFirst = document.getElementById('btnAnomalyFirst');
        if (btnFirst) {
            btnFirst.addEventListener('click', () => {
                this.state.anomalyPage = 1;
                this.renderAnomaliesTable();
            });
        }

        const btnPrev = document.getElementById('btnAnomalyPrev');
        if (btnPrev) {
            btnPrev.addEventListener('click', () => {
                if (this.state.anomalyPage > 1) {
                    this.state.anomalyPage--;
                    this.renderAnomaliesTable();
                }
            });
        }

        const btnNext = document.getElementById('btnAnomalyNext');
        if (btnNext) {
            btnNext.addEventListener('click', () => {
                this.state.anomalyPage++;
                this.renderAnomaliesTable();
            });
        }

        const btnLast = document.getElementById('btnAnomalyLast');
        if (btnLast) {
            btnLast.addEventListener('click', () => {
                this.state.anomalyPage = 999999;
                this.renderAnomaliesTable();
            });
        }"""

if old_listeners in content:
    content = content.replace(old_listeners, new_listeners, 1)
    print("Event listeners updated with platform chips.")
else:
    print("Warning: old_listeners not matched.")

# 3. Update fetchAnomalies & renderAnomaliesTable
old_fetch = """    async fetchAnomalies() {
        try {
            const q = this.buildQueryString();
            const res = await this.authFetch(`/api/anomalies?${q}&severity=ALL`);
            const data = await res.json();
            this.state.allScopeAnomalies = Array.isArray(data) ? data : [];
            
            // Dynamic chip badge counts
            const total = this.state.allScopeAnomalies.length;
            const crit = this.state.allScopeAnomalies.filter(x => (x.anomaly_severity || '').toUpperCase() === 'CRITICAL').length;
            const high = this.state.allScopeAnomalies.filter(x => (x.anomaly_severity || '').toUpperCase() === 'HIGH').length;
            const med = this.state.allScopeAnomalies.filter(x => (x.anomaly_severity || '').toUpperCase() === 'MEDIUM').length;

            const cAll = document.getElementById('chipCountAll');
            if (cAll) cAll.innerText = total.toLocaleString();
            const cCrit = document.getElementById('chipCountCritical');
            if (cCrit) cCrit.innerText = crit.toLocaleString();
            const cHigh = document.getElementById('chipCountHigh');
            if (cHigh) cHigh.innerText = high.toLocaleString();
            const cMed = document.getElementById('chipCountMedium');
            if (cMed) cMed.innerText = med.toLocaleString();

            this.renderAnomaliesTable();
        } catch (err) {
            console.error('Error fetching anomalies:', err);
        }
    },

    renderAnomaliesTable() {
        const tbody = document.getElementById('anomalyTableBody');
        if (!tbody) return;

        let items = [...(this.state.allScopeAnomalies || [])];

        // 1. Filter by Severity Tab
        const activeSev = (this.state.anomalySeverity || 'ALL').toUpperCase();
        if (activeSev !== 'ALL') {
            items = items.filter(x => (x.anomaly_severity || '').toUpperCase() === activeSev);
        }

        // 2. Filter by Search Query
        if (this.state.anomalySearchTerm) {
            const term = this.state.anomalySearchTerm;
            items = items.filter(x => {
                const s1 = (x.Service || '').toLowerCase();
                const s2 = (x.ResourceId || '').toLowerCase();
                const s3 = (x.Department || '').toLowerCase();
                const s4 = (x.CloudProvider || '').toLowerCase();
                const s5 = (x.root_cause_diagnosis || '').toLowerCase();
                const s6 = (x.RegionName || '').toLowerCase();
                return s1.includes(term) || s2.includes(term) || s3.includes(term) || s4.includes(term) || s5.includes(term) || s6.includes(term);
            });
        }

        // 3. Sorting
        const sortBy = this.state.anomalySortBy || 'date_desc';
        const sevOrder = { 'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3 };
        items.sort((a, b) => {
            if (sortBy === 'date_desc') {
                return (b.Date || '').localeCompare(a.Date || '') || (b.DailyCost_USD - a.DailyCost_USD);
            } else if (sortBy === 'date_asc') {
                return (a.Date || '').localeCompare(b.Date || '') || (b.DailyCost_USD - a.DailyCost_USD);
            } else if (sortBy === 'severity_desc') {
                const rA = sevOrder[(a.anomaly_severity || '').toUpperCase()] ?? 4;
                const rB = sevOrder[(b.anomaly_severity || '').toUpperCase()] ?? 4;
                if (rA !== rB) return rA - rB;
                return (b.DailyCost_USD - a.DailyCost_USD);
            } else if (sortBy === 'spend_desc') {
                return (b.DailyCost_USD || 0) - (a.DailyCost_USD || 0);
            } else if (sortBy === 'surge_desc') {
                return (b.cost_spike_usd || 0) - (a.cost_spike_usd || 0);
            }
            return 0;
        });

        // Store filtered items for CSV export
        this.state.currentAnomalies = items;

        const totalItems = items.length;
        const pageSize = this.state.anomalyPageSize || 25;
        const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
        
        if (this.state.anomalyPage > totalPages) {
            this.state.anomalyPage = totalPages;
        }
        if (this.state.anomalyPage < 1) {
            this.state.anomalyPage = 1;
        }
        const currentPage = this.state.anomalyPage;

        const startIdx = totalItems > 0 ? (currentPage - 1) * pageSize : 0;
        const endIdx = Math.min(startIdx + pageSize, totalItems);
        const pageItems = items.slice(startIdx, endIdx);

        // Update Pagination Indicators
        const elStart = document.getElementById('anomalyStartIdx');
        if (elStart) elStart.innerText = totalItems > 0 ? (startIdx + 1).toLocaleString() : '0';
        const elEnd = document.getElementById('anomalyEndIdx');
        if (elEnd) elEnd.innerText = endIdx.toLocaleString();
        const elTotal = document.getElementById('anomalyTotalCount');
        if (elTotal) elTotal.innerText = totalItems.toLocaleString();
        const elCurrent = document.getElementById('anomalyCurrentPage');
        if (elCurrent) elCurrent.innerText = currentPage.toLocaleString();
        const elPages = document.getElementById('anomalyTotalPages');
        if (elPages) elPages.innerText = totalPages.toLocaleString();

        const btnFirst = document.getElementById('btnAnomalyFirst');
        if (btnFirst) btnFirst.disabled = (currentPage <= 1);
        const btnPrev = document.getElementById('btnAnomalyPrev');
        if (btnPrev) btnPrev.disabled = (currentPage <= 1);
        const btnNext = document.getElementById('btnAnomalyNext');
        if (btnNext) btnNext.disabled = (currentPage >= totalPages);
        const btnLast = document.getElementById('btnAnomalyLast');
        if (btnLast) btnLast.disabled = (currentPage >= totalPages);

        if (!pageItems.length) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center py-12 text-slate-500 font-mono">No matching anomalies found. Adjust filters or search query.</td></tr>`;
            return;
        }

        tbody.innerHTML = pageItems.map(item => {
            const sevUpper = (item.anomaly_severity || 'MEDIUM').toUpperCase();
            const badgeClass = sevUpper === 'CRITICAL' ? 'badge-critical' :
                               sevUpper === 'HIGH' ? 'badge-high' : 'badge-medium';
            const provClass = item.CloudProvider === 'AWS' ? 'badge-prov-aws' :
                              item.CloudProvider === 'Azure' ? 'badge-prov-azure' : 'badge-prov-gcp';
            const safeDate = this.escapeHTML(item.Date);
            const safeProv = this.escapeHTML(item.CloudProvider);
            const safeDept = this.escapeHTML(item.Department);
            const safeServ = this.escapeHTML(item.Service);
            const safeResId = this.escapeHTML(item.ResourceId || '');
            const safeRegion = this.escapeHTML(item.RegionName || '');
            const safeSev = this.escapeHTML(item.anomaly_severity);
            const safeDiagnosis = this.escapeHTML(item.root_cause_diagnosis);
            return `
                <tr class="border-b border-slate-800/60 hover:bg-slate-800/40 transition-colors">
                    <td class="py-3 px-4 text-xs font-mono text-slate-400 whitespace-nowrap">${safeDate}</td>
                    <td class="py-3 px-4 text-xs font-semibold whitespace-nowrap">
                        <span class="px-2.5 py-1 rounded-md text-[10px] font-bold ${provClass}">${safeProv}</span>
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-200 font-medium whitespace-nowrap">${safeDept}</td>
                    <td class="py-3 px-4 text-xs text-slate-300 font-medium">
                        <div class="font-semibold text-white">${safeServ}</div>
                        ${safeResId ? `<div class="text-[10px] font-mono text-sky-400/80 truncate max-w-xs" title="${safeResId}">${safeRegion ? safeRegion + ' • ' : ''}${safeResId}</div>` : ''}
                    </td>
                    <td class="py-3 px-4 text-xs font-mono font-bold text-white whitespace-nowrap">$${Number(item.DailyCost_USD).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td class="py-3 px-4 text-xs font-mono font-bold text-rose-400 whitespace-nowrap">+$${Number(item.cost_spike_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td class="py-3 px-4 whitespace-nowrap">
                        <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-extrabold ${badgeClass}">${safeSev}</span>
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-300 max-w-sm truncate" title="${safeDiagnosis}">
                        ${safeDiagnosis}
                    </td>
                </tr>
            `;
        }).join('');
    },"""

new_fetch = """    async fetchAnomalies() {
        try {
            const q = this.buildQueryString();
            const res = await this.authFetch(`/api/anomalies?${q}&severity=ALL`);
            const data = await res.json();
            this.state.allScopeAnomalies = Array.isArray(data) ? data : [];
            
            // Dynamic chip badge counts
            const total = this.state.allScopeAnomalies.length;
            const crit = this.state.allScopeAnomalies.filter(x => (x.anomaly_severity || '').toUpperCase() === 'CRITICAL').length;
            const high = this.state.allScopeAnomalies.filter(x => (x.anomaly_severity || '').toUpperCase() === 'HIGH').length;
            const med = this.state.allScopeAnomalies.filter(x => (x.anomaly_severity || '').toUpperCase() === 'MEDIUM').length;

            const awsCount = this.state.allScopeAnomalies.filter(x => (x.CloudProvider || '').toUpperCase() === 'AWS').length;
            const azureCount = this.state.allScopeAnomalies.filter(x => (x.CloudProvider || '').toUpperCase() === 'AZURE').length;
            const gcpCount = this.state.allScopeAnomalies.filter(x => (x.CloudProvider || '').toUpperCase() === 'GCP').length;

            const cAll = document.getElementById('chipCountAll');
            if (cAll) cAll.innerText = total.toLocaleString();
            const cCrit = document.getElementById('chipCountCritical');
            if (cCrit) cCrit.innerText = crit.toLocaleString();
            const cHigh = document.getElementById('chipCountHigh');
            if (cHigh) cHigh.innerText = high.toLocaleString();
            const cMed = document.getElementById('chipCountMedium');
            if (cMed) cMed.innerText = med.toLocaleString();

            const cCloudAll = document.getElementById('chipCountCloudAll');
            if (cCloudAll) cCloudAll.innerText = total.toLocaleString();
            const cAws = document.getElementById('chipCountAWS');
            if (cAws) cAws.innerText = awsCount.toLocaleString();
            const cAzure = document.getElementById('chipCountAzure');
            if (cAzure) cAzure.innerText = azureCount.toLocaleString();
            const cGcp = document.getElementById('chipCountGCP');
            if (cGcp) cGcp.innerText = gcpCount.toLocaleString();

            this.renderAnomaliesTable();
        } catch (err) {
            console.error('Error fetching anomalies:', err);
        }
    },

    renderAnomaliesTable() {
        const tbody = document.getElementById('anomalyTableBody');
        if (!tbody) return;

        let items = [...(this.state.allScopeAnomalies || [])];

        // 1. Filter by Severity Chip
        const activeSev = (this.state.anomalySeverity || 'ALL').toUpperCase();
        if (activeSev !== 'ALL') {
            items = items.filter(x => (x.anomaly_severity || '').toUpperCase() === activeSev);
        }

        // 2. Filter by Cloud Platform Chip
        const activePlat = (this.state.anomalyPlatform || 'ALL').toUpperCase();
        if (activePlat !== 'ALL') {
            items = items.filter(x => (x.CloudProvider || '').toUpperCase() === activePlat);
        }

        // 3. Filter by Search Query
        if (this.state.anomalySearchTerm) {
            const term = this.state.anomalySearchTerm;
            items = items.filter(x => {
                const s1 = (x.Service || '').toLowerCase();
                const s2 = (x.ResourceId || '').toLowerCase();
                const s3 = (x.Department || '').toLowerCase();
                const s4 = (x.CloudProvider || '').toLowerCase();
                const s5 = (x.root_cause_diagnosis || '').toLowerCase();
                const s6 = (x.RegionName || '').toLowerCase();
                return s1.includes(term) || s2.includes(term) || s3.includes(term) || s4.includes(term) || s5.includes(term) || s6.includes(term);
            });
        }

        // 4. Multi-Dimension Sorting
        const sortBy = this.state.anomalySortBy || 'date_desc';
        const sevOrder = { 'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3 };
        const provOrderAws = { 'AWS': 0, 'AZURE': 1, 'GCP': 2 };
        const provOrderGcp = { 'GCP': 0, 'AZURE': 1, 'AWS': 2 };

        items.sort((a, b) => {
            if (sortBy === 'date_desc') {
                return (b.Date || '').localeCompare(a.Date || '') || (b.DailyCost_USD - a.DailyCost_USD);
            } else if (sortBy === 'date_asc') {
                return (a.Date || '').localeCompare(b.Date || '') || (b.DailyCost_USD - a.DailyCost_USD);
            } else if (sortBy === 'provider_aws') {
                const pA = provOrderAws[(a.CloudProvider || '').toUpperCase()] ?? 3;
                const pB = provOrderAws[(b.CloudProvider || '').toUpperCase()] ?? 3;
                if (pA !== pB) return pA - pB;
                return (b.Date || '').localeCompare(a.Date || '') || (b.DailyCost_USD - a.DailyCost_USD);
            } else if (sortBy === 'provider_gcp') {
                const pA = provOrderGcp[(a.CloudProvider || '').toUpperCase()] ?? 3;
                const pB = provOrderGcp[(b.CloudProvider || '').toUpperCase()] ?? 3;
                if (pA !== pB) return pA - pB;
                return (b.Date || '').localeCompare(a.Date || '') || (b.DailyCost_USD - a.DailyCost_USD);
            } else if (sortBy === 'severity_desc') {
                const rA = sevOrder[(a.anomaly_severity || '').toUpperCase()] ?? 4;
                const rB = sevOrder[(b.anomaly_severity || '').toUpperCase()] ?? 4;
                if (rA !== rB) return rA - rB;
                return (b.DailyCost_USD - a.DailyCost_USD);
            } else if (sortBy === 'spend_desc') {
                return (b.DailyCost_USD || 0) - (a.DailyCost_USD || 0);
            } else if (sortBy === 'surge_desc') {
                return (b.cost_spike_usd || 0) - (a.cost_spike_usd || 0);
            }
            return 0;
        });

        // Store filtered items for CSV export
        this.state.currentAnomalies = items;

        const totalItems = items.length;
        const pageSize = this.state.anomalyPageSize || 25;
        const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
        
        if (this.state.anomalyPage > totalPages) {
            this.state.anomalyPage = totalPages;
        }
        if (this.state.anomalyPage < 1) {
            this.state.anomalyPage = 1;
        }
        const currentPage = this.state.anomalyPage;

        const startIdx = totalItems > 0 ? (currentPage - 1) * pageSize : 0;
        const endIdx = Math.min(startIdx + pageSize, totalItems);
        const pageItems = items.slice(startIdx, endIdx);

        // Update Pagination Indicators
        const elStart = document.getElementById('anomalyStartIdx');
        if (elStart) elStart.innerText = totalItems > 0 ? (startIdx + 1).toLocaleString() : '0';
        const elEnd = document.getElementById('anomalyEndIdx');
        if (elEnd) elEnd.innerText = endIdx.toLocaleString();
        const elTotal = document.getElementById('anomalyTotalCount');
        if (elTotal) elTotal.innerText = totalItems.toLocaleString();
        const elCurrent = document.getElementById('anomalyCurrentPage');
        if (elCurrent) elCurrent.innerText = currentPage.toLocaleString();
        const elPages = document.getElementById('anomalyTotalPages');
        if (elPages) elPages.innerText = totalPages.toLocaleString();

        const btnFirst = document.getElementById('btnAnomalyFirst');
        if (btnFirst) btnFirst.disabled = (currentPage <= 1);
        const btnPrev = document.getElementById('btnAnomalyPrev');
        if (btnPrev) btnPrev.disabled = (currentPage <= 1);
        const btnNext = document.getElementById('btnAnomalyNext');
        if (btnNext) btnNext.disabled = (currentPage >= totalPages);
        const btnLast = document.getElementById('btnAnomalyLast');
        if (btnLast) btnLast.disabled = (currentPage >= totalPages);

        if (!pageItems.length) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center py-12 text-slate-500 font-mono">No matching anomalies found. Adjust filters or search query.</td></tr>`;
            return;
        }

        tbody.innerHTML = pageItems.map(item => {
            const sevUpper = (item.anomaly_severity || 'MEDIUM').toUpperCase();
            const badgeClass = sevUpper === 'CRITICAL' ? 'badge-critical' :
                               sevUpper === 'HIGH' ? 'badge-high' : 'badge-medium';
            const provClass = item.CloudProvider === 'AWS' ? 'badge-prov-aws' :
                              item.CloudProvider === 'Azure' ? 'badge-prov-azure' : 'badge-prov-gcp';
            const safeDate = this.escapeHTML(item.Date);
            const safeProv = this.escapeHTML(item.CloudProvider);
            const safeDept = this.escapeHTML(item.Department);
            const safeServ = this.escapeHTML(item.Service);
            const safeResId = this.escapeHTML(item.ResourceId || '');
            const safeRegion = this.escapeHTML(item.RegionName || '');
            const safeSev = this.escapeHTML(item.anomaly_severity);
            const safeDiagnosis = this.escapeHTML(item.root_cause_diagnosis);
            return `
                <tr class="border-b border-slate-800/60 hover:bg-slate-800/40 transition-colors">
                    <td class="py-3 px-4 text-xs font-mono text-slate-400 whitespace-nowrap">${safeDate}</td>
                    <td class="py-3 px-4 text-xs font-semibold whitespace-nowrap">
                        <span class="px-2.5 py-1 rounded-md text-[10px] font-bold ${provClass}">${safeProv}</span>
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-200 font-medium whitespace-nowrap">${safeDept}</td>
                    <td class="py-3 px-4 text-xs text-slate-300 font-medium">
                        <div class="font-semibold text-white">${safeServ}</div>
                        ${safeResId ? `<div class="text-[10px] font-mono text-sky-400/80 truncate max-w-xs" title="${safeResId}">${safeRegion ? safeRegion + ' • ' : ''}${safeResId}</div>` : ''}
                    </td>
                    <td class="py-3 px-4 text-xs font-mono font-bold text-white whitespace-nowrap">$${Number(item.DailyCost_USD).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td class="py-3 px-4 text-xs font-mono font-bold text-rose-400 whitespace-nowrap">+$${Number(item.cost_spike_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td class="py-3 px-4 whitespace-nowrap">
                        <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-extrabold ${badgeClass}">${safeSev}</span>
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-300 max-w-sm truncate" title="${safeDiagnosis}">
                        ${safeDiagnosis}
                    </td>
                </tr>
            `;
        }).join('');
    },"""

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch, 1)
    print("fetchAnomalies & renderAnomaliesTable updated with platform filtering and multi-sort.")
else:
    print("Warning: old_fetch not matched.")

app_path.write_text(content, encoding="utf-8")
print("app.js updated successfully.")
