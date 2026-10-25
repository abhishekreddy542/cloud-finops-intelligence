/**
 * Abhi Cloud Tech — Frontend Application Controller
 * Handles reactivity, asynchronous API communications, DOM updates & animations.
 */

const App = {
    state: {
        activeTab: 'overview',
        providers: [],
        departments: [],
        selectedProviders: [],
        selectedDepartments: [],
        forecastHorizon: 60,
        workloadGrowth: 15,
        finopsSavings: 10,
        anomalySeverity: 'ALL'
    },

    async init() {
        this.bindEvents();
        await this.loadFilterMetadata();
        await this.refreshDashboard();
    },

    bindEvents() {
        // Tab switching
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = link.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });

        // Scenario Sliders
        const growthSlider = document.getElementById('workloadGrowthSlider');
        const savingsSlider = document.getElementById('finopsSavingsSlider');
        const horizonSelect = document.getElementById('forecastHorizonSelect');

        if (growthSlider) {
            growthSlider.addEventListener('input', (e) => {
                document.getElementById('growthVal').innerText = `+${e.target.value}%`;
                this.state.workloadGrowth = parseFloat(e.target.value);
                this.debounceForecast();
            });
        }

        if (savingsSlider) {
            savingsSlider.addEventListener('input', (e) => {
                document.getElementById('savingsVal').innerText = `-${e.target.value}%`;
                this.state.finopsSavings = parseFloat(e.target.value);
                this.debounceForecast();
            });
        }

        if (horizonSelect) {
            horizonSelect.addEventListener('change', (e) => {
                this.state.forecastHorizon = parseInt(e.target.value);
                this.fetchForecast();
            });
        }

        // Anomaly Severity Filter Chips
        document.querySelectorAll('.severity-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                document.querySelectorAll('.severity-chip').forEach(c => c.classList.remove('active', 'border-sky-500', 'text-sky-400'));
                chip.classList.add('active', 'border-sky-500', 'text-sky-400');
                this.state.anomalySeverity = chip.getAttribute('data-severity');
                this.fetchAnomalies();
            });
        });

        // Custom Calculator Inputs
        ['calcVcpu', 'calcRam', 'calcHours', 'calcDownsize'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('input', () => this.runSimulation());
        });

        // Reset Filters Button
        const resetBtn = document.getElementById('resetFiltersBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.state.selectedProviders = [...this.state.providers];
                this.state.selectedDepartments = [...this.state.departments];
                this.renderFilterCheckboxes();
                this.refreshDashboard();
            });
        }
    },

    switchTab(tabId) {
        this.state.activeTab = tabId;
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        const activeLink = document.querySelector(`[data-tab="${tabId}"]`);
        if (activeLink) activeLink.classList.add('active');

        document.querySelectorAll('.tab-content').forEach(section => {
            section.classList.add('hidden');
        });

        const activeSection = document.getElementById(`tab-${tabId}`);
        if (activeSection) {
            activeSection.classList.remove('hidden');
            activeSection.classList.add('animate-fadeIn');
        }

        // Trigger chart resizes
        window.dispatchEvent(new Event('resize'));
    },

    async loadFilterMetadata() {
        try {
            const res = await fetch('/api/meta/filters');
            const data = await res.json();
            this.state.providers = data.providers;
            this.state.departments = data.departments;
            this.state.selectedProviders = [...data.providers];
            this.state.selectedDepartments = [...data.departments];
            this.renderFilterCheckboxes();
        } catch (err) {
            console.error('Failed to load filter metadata:', err);
        }
    },

    renderFilterCheckboxes() {
        const provContainer = document.getElementById('providerFilters');
        if (provContainer) {
            provContainer.innerHTML = this.state.providers.map(p => `
                <label class="flex items-center gap-2 text-xs text-slate-300 hover:text-white cursor-pointer select-none">
                    <input type="checkbox" value="${p}" ${this.state.selectedProviders.includes(p) ? 'checked' : ''} class="provider-checkbox rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0 focus:ring-offset-0">
                    <span>${p}</span>
                </label>
            `).join('');

            provContainer.querySelectorAll('.provider-checkbox').forEach(cb => {
                cb.addEventListener('change', () => {
                    const checked = Array.from(provContainer.querySelectorAll('.provider-checkbox:checked')).map(c => c.value);
                    this.state.selectedProviders = checked.length ? checked : [...this.state.providers];
                    this.refreshDashboard();
                });
            });
        }

        const deptContainer = document.getElementById('deptFilters');
        if (deptContainer) {
            deptContainer.innerHTML = this.state.departments.map(d => `
                <label class="flex items-center gap-2 text-xs text-slate-300 hover:text-white cursor-pointer select-none">
                    <input type="checkbox" value="${d}" ${this.state.selectedDepartments.includes(d) ? 'checked' : ''} class="dept-checkbox rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0 focus:ring-offset-0">
                    <span>${d}</span>
                </label>
            `).join('');

            deptContainer.querySelectorAll('.dept-checkbox').forEach(cb => {
                cb.addEventListener('change', () => {
                    const checked = Array.from(deptContainer.querySelectorAll('.dept-checkbox:checked')).map(c => c.value);
                    this.state.selectedDepartments = checked.length ? checked : [...this.state.departments];
                    this.refreshDashboard();
                });
            });
        }
    },

    buildQueryString() {
        const params = new URLSearchParams();
        this.state.selectedProviders.forEach(p => params.append('providers', p));
        this.state.selectedDepartments.forEach(d => params.append('departments', d));
        return params.toString();
    },

    async refreshDashboard() {
        await Promise.all([
            this.fetchKPIs(),
            this.fetchTrends(),
            this.fetchDepartmentAnalytics(),
            this.fetchAnomalies(),
            this.fetchForecast(),
            this.fetchOptimizer(),
            this.runSimulation()
        ]);
    },

    async fetchKPIs() {
        try {
            const res = await fetch(`/api/kpis?${this.buildQueryString()}`);
            const data = await res.json();

            this.animateValue('kpiTotalSpend', data.total_spend_ytd, '$');
            this.animateValue('kpiRunRate', data.annual_run_rate, '$');
            this.animateValue('kpiSavings', data.identifiable_annual_savings, '$');
            this.animateValue('kpiWaste', data.anomalous_waste_usd, '$');
            
            document.getElementById('kpiCpu').innerText = `${data.average_cpu_utilization}%`;
            document.getElementById('kpiSavingsPct').innerText = `${data.savings_percentage}% of total spend`;
            document.getElementById('kpiIncidentsCount').innerText = `${data.anomaly_incident_count} spikes detected`;
            document.getElementById('kpiMaturityStage').innerText = data.finops_maturity_stage;
        } catch (err) {
            console.error('Error fetching KPIs:', err);
        }
    },

    async fetchTrends() {
        try {
            const res = await fetch(`/api/trends?${this.buildQueryString()}`);
            const data = await res.json();
            Charts.renderDailySpend('dailySpendChart', data);
            Charts.renderProviderDonut('providerDonutChart', data.provider_breakdown);
        } catch (err) {
            console.error('Error fetching trends:', err);
        }
    },

    async fetchDepartmentAnalytics() {
        try {
            const res = await fetch(`/api/departments?${this.buildQueryString()}`);
            const data = await res.json();
            Charts.renderDepartmentSpend('deptSpendChart', data.department_spend);
            Charts.renderTopServices('topServicesChart', data.top_services);
        } catch (err) {
            console.error('Error fetching department analytics:', err);
        }
    },

    async fetchAnomalies() {
        try {
            const q = this.buildQueryString();
            const res = await fetch(`/api/anomalies?${q}&severity=${this.state.anomalySeverity}`);
            const data = await res.json();
            
            const tbody = document.getElementById('anomalyTableBody');
            if (tbody) {
                if (!data.length) {
                    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-slate-500">No anomalies detected in selected scope.</td></tr>`;
                    return;
                }

                tbody.innerHTML = data.map(item => {
                    const badgeClass = item.anomaly_severity === 'CRITICAL' ? 'badge-critical' :
                                       item.anomaly_severity === 'HIGH' ? 'badge-high' : 'badge-medium';
                    return `
                        <tr class="border-b border-slate-800/60 hover:bg-slate-800/30 transition-colors">
                            <td class="py-3 px-4 text-xs font-mono text-slate-400">${item.Date}</td>
                            <td class="py-3 px-4 text-xs font-semibold text-slate-200">
                                <span class="px-2 py-0.5 rounded text-[10px] bg-slate-800 border border-slate-700">${item.CloudProvider}</span>
                            </td>
                            <td class="py-3 px-4 text-xs text-slate-300">${item.Department}</td>
                            <td class="py-3 px-4 text-xs text-slate-300 font-medium">${item.Service}</td>
                            <td class="py-3 px-4 text-xs font-mono font-bold text-white">$${item.DailyCost_USD.toLocaleString()}</td>
                            <td class="py-3 px-4 text-xs font-mono font-bold text-rose-400">+$${item.cost_spike_usd.toLocaleString()}</td>
                            <td class="py-3 px-4">
                                <span class="inline-block px-2 py-0.5 rounded text-[10px] font-bold ${badgeClass}">${item.anomaly_severity}</span>
                            </td>
                            <td class="py-3 px-4 text-xs text-slate-400 max-w-xs truncate" title="${item.root_cause_diagnosis}">
                                ${item.root_cause_diagnosis}
                            </td>
                        </tr>
                    `;
                }).join('');
            }
        } catch (err) {
            console.error('Error fetching anomalies:', err);
        }
    },

    debounceTimer: null,
    debounceForecast() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this.fetchForecast(), 200);
    },

    async fetchForecast() {
        try {
            const res = await fetch('/api/forecast', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    horizon_days: this.state.forecastHorizon,
                    workload_growth_pct: this.state.workloadGrowth,
                    finops_savings_pct: this.state.finopsSavings
                })
            });
            const data = await res.json();
            Charts.renderForecast('forecastChart', data.historical, data.forecast);

            document.getElementById('forecastMape').innerText = `${data.metrics.MAPE_Pct}%`;
            document.getElementById('forecastRmse').innerText = `$${data.metrics.RMSE_USD.toLocaleString()}`;
            document.getElementById('forecastTotalBudget').innerText = `$${data.projected_total_usd.toLocaleString()}`;
        } catch (err) {
            console.error('Error fetching forecast:', err);
        }
    },

    async fetchOptimizer() {
        try {
            const res = await fetch(`/api/optimizer?${this.buildQueryString()}`);
            const data = await res.json();

            Charts.renderOptimizationPillars('optimizationPillarsChart', data.portfolio);

            const tbody = document.getElementById('actionTableBody');
            if (tbody) {
                if (!data.action_matrix.length) {
                    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-500">All workloads operating optimally.</td></tr>`;
                    return;
                }

                tbody.innerHTML = data.action_matrix.map(row => `
                    <tr class="border-b border-slate-800/60 hover:bg-slate-800/30 transition-colors">
                        <td class="py-3 px-4">
                            <span class="inline-block px-2 py-0.5 rounded text-[10px] font-bold ${row.Priority.includes('Critical') ? 'badge-critical' : 'badge-high'}">${row.Priority}</span>
                        </td>
                        <td class="py-3 px-4 text-xs font-semibold text-slate-200">${row.Department}</td>
                        <td class="py-3 px-4 text-xs text-slate-300 font-mono">${row.Cloud_Provider} - ${row.Resource_Service}</td>
                        <td class="py-3 px-4 text-xs text-slate-400">${row.Issue_Identified}</td>
                        <td class="py-3 px-4 text-xs text-sky-400 font-medium">${row.Action_Required}</td>
                        <td class="py-3 px-4 text-xs font-mono font-bold text-emerald-400">+$${row.Est_Monthly_Savings_USD.toLocaleString()}/mo</td>
                        <td class="py-3 px-4 text-xs text-slate-400">${row.Implementation_Effort}</td>
                    </tr>
                `).join('');
            }
        } catch (err) {
            console.error('Error fetching optimizer portfolio:', err);
        }
    },

    async runSimulation() {
        const vcpu = parseInt(document.getElementById('calcVcpu')?.value || 32);
        const ram = parseInt(document.getElementById('calcRam')?.value || 128);
        const hours = parseInt(document.getElementById('calcHours')?.value || 24);
        const downsize = document.getElementById('calcDownsize')?.checked ? 50.0 : 0.0;

        try {
            const res = await fetch('/api/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    vcpu_count: vcpu,
                    ram_gb: ram,
                    daily_hours: hours,
                    downsize_pct: downsize
                })
            });
            const data = await res.json();

            document.getElementById('calcHourly').innerText = `$${data.hourly_cost_usd}`;
            document.getElementById('calcMonthly').innerText = `$${data.monthly_cost_usd.toLocaleString()}`;
            document.getElementById('calcSavings').innerText = `$${data.potential_monthly_savings_usd.toLocaleString()}/mo`;
        } catch (err) {
            console.error('Error in workload simulator:', err);
        }
    },

    animateValue(id, targetVal, prefix = '') {
        const el = document.getElementById(id);
        if (!el) return;

        const start = 0;
        const duration = 600;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // EaseOutCubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + (targetVal - start) * easeProgress);

            el.innerText = `${prefix}${current.toLocaleString()}`;

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.innerText = `${prefix}${Math.round(targetVal).toLocaleString()}`;
            }
        }
        requestAnimationFrame(update);
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
