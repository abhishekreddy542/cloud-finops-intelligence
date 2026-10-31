/**
 * Abhi Cloud Tech — Frontend Application Controller
 * Handles reactivity, asynchronous API communications, DOM updates, enterprise CSV export,
 * interactive simulation snapshotting, and notifications.
 */

const LOCAL_CATALOG = {
    'AWS': {
        families: [
            { code: 'm6i', name: 'm6i (General Purpose - Intel Xeon Ice Lake)', note: 'Intel x86_64 Base' },
            { code: 'm6g', name: 'm6g (AWS Graviton2 ARM - 20% Cheaper)', note: 'Graviton ARM64 (-20%)' },
            { code: 'c6i', name: 'c6i (Compute Optimized - High Clock)', note: 'Compute Heavy' },
            { code: 'r6i', name: 'r6i (Memory Optimized - 8:1 RAM-to-CPU)', note: 'RAM Intensive' }
        ],
        regions: [
            { code: 'us-east-1', name: 'us-east-1 (US East - N. Virginia)', mult: '1.00x', note: 'Global Baseline' },
            { code: 'us-west-2', name: 'us-west-2 (US West - Oregon)', mult: '1.00x', note: 'US West Baseline' },
            { code: 'eu-central-1', name: 'eu-central-1 (Europe - Frankfurt)', mult: '1.18x', note: 'Frankfurt (+18%)' },
            { code: 'eu-west-1', name: 'eu-west-1 (Europe - Ireland)', mult: '1.10x', note: 'Dublin (+10%)' },
            { code: 'ap-south-1', name: 'ap-south-1 (Asia Pacific - Mumbai)', mult: '1.09x', note: 'Mumbai (+9%)' },
            { code: 'ap-southeast-1', name: 'ap-southeast-1 (Asia Pacific - Singapore)', mult: '1.14x', note: 'Singapore (+14%)' },
            { code: 'sa-east-1', name: 'sa-east-1 (South America - São Paulo)', mult: '1.34x', note: 'São Paulo (+34%)' }
        ]
    },
    'Azure': {
        families: [
            { code: 'Standard_Dsv5', name: 'Standard_Dsv5 (General Purpose - Intel/AMD)', note: 'Azure Standard Tier' },
            { code: 'Standard_B', name: 'Standard_B (Burstable Economy - 25% Cheaper)', note: 'Dev / Burstable (-25%)' },
            { code: 'Standard_Dasv5', name: 'Standard_Dasv5 (AMD EPYC Balanced)', note: 'AMD EPYC Milan (-12%)' },
            { code: 'Standard_Esv5', name: 'Standard_Esv5 (Memory Optimized - 8:1 RAM)', note: 'Enterprise In-Memory' }
        ],
        regions: [
            { code: 'eastus', name: 'eastus (East US - Virginia)', mult: '1.00x', note: 'Azure East Baseline' },
            { code: 'westus2', name: 'westus2 (West US 2 - Washington)', mult: '1.00x', note: 'Azure West Baseline' },
            { code: 'westeurope', name: 'westeurope (West Europe - Netherlands)', mult: '1.17x', note: 'Amsterdam (+17%)' },
            { code: 'northeurope', name: 'northeurope (North Europe - Ireland)', mult: '1.15x', note: 'Dublin (+15%)' },
            { code: 'centralindia', name: 'centralindia (Central India - Pune)', mult: '1.10x', note: 'Pune (+10%)' },
            { code: 'southeastasia', name: 'southeastasia (Southeast Asia - Singapore)', mult: '1.13x', note: 'Singapore (+13%)' }
        ]
    },
    'GCP': {
        families: [
            { code: 'e2', name: 'e2 (Cost-Optimized Dynamic Resource - 28% Cheaper)', note: 'E2 Cost-Optimized (-28%)' },
            { code: 'n2', name: 'n2 (Balanced Intel Cascade/Ice Lake)', note: 'Google N2 Production Tier' },
            { code: 't2d', name: 't2d (AMD Tau EPYC Milan - High Perf/Cost)', note: 'AMD Tau Performance (-17%)' },
            { code: 'c2', name: 'c2 (Compute-Optimized Intel Turbo)', note: 'Compute Engine Turbo' }
        ],
        regions: [
            { code: 'us-central1', name: 'us-central1 (US Central - Iowa)', mult: '1.00x', note: 'Low-Carbon Baseline' },
            { code: 'us-east4', name: 'us-east4 (US East - Northern Virginia)', mult: '1.09x', note: 'Ashburn (+9%)' },
            { code: 'europe-west3', name: 'europe-west3 (Europe - Frankfurt)', mult: '1.22x', note: 'Frankfurt (+22%)' },
            { code: 'europe-west1', name: 'europe-west1 (Europe - Belgium)', mult: '1.15x', note: 'Belgium (+15%)' },
            { code: 'asia-south1', name: 'asia-south1 (Asia South - Mumbai)', mult: '1.11x', note: 'Mumbai (+11%)' },
            { code: 'asia-southeast1', name: 'asia-southeast1 (Asia Southeast - Singapore)', mult: '1.14x', note: 'Singapore (+14%)' }
        ]
    }
};

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
        anomalySeverity: 'ALL',
        anomalyPlatform: 'ALL',
        allScopeAnomalies: [],
        currentAnomalies: [],
        anomalyPage: 1,
        anomalyPageSize: 25,
        anomalySearchTerm: '',
        anomalySortBy: 'date_desc',
        currentActions: [],
        lastSimulation: null,
        snapshots: [],
        auth: {
            isLoggedIn: false,
            userId: '',
            fullName: '',
            token: ''
        }
    },

    escapeHTML(str) {
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    },

    async authFetch(url, options = {}) {
        options.headers = options.headers || {};
        if (this.state.auth && this.state.auth.token) {
            options.headers['Authorization'] = `Bearer ${this.state.auth.token}`;
        }
        const res = await fetch(url, options);
        if (res.status === 401) {
            console.warn('Session expired or unauthorized request to:', url);
            this.logout(true);
            throw new Error('Unauthorized');
        }
        return res;
    },

    async init() {
        this.startClock();
        this.updateFamilyDropdown('AWS');
        this.updateRegionDropdown('AWS');
        this.bindEvents();
        this.initAuth();
        if (this.state.auth.isLoggedIn) {
            await this.loadFilterMetadata();
            await this.refreshDashboard();
        }
    },

    initAuth() {
        try {
            const saved = localStorage.getItem('act_auth_user');
            if (saved) {
                const user = JSON.parse(saved);
                if (user && user.user_id && user.token) {
                    this.state.auth = {
                        isLoggedIn: true,
                        userId: user.user_id,
                        fullName: user.full_name || user.user_id,
                        token: user.token
                    };
                }
            }
        } catch (e) {
            console.warn('Could not read saved auth session:', e);
        }
        this.renderAuthUI();
    },

    getInitials(name) {
        if (!name || typeof name !== 'string') return 'AR';
        const parts = name.trim().split(/\s+/);
        if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    },

    renderAuthUI() {
        const gate = document.getElementById('authGate');
        const auth = this.state.auth;

        if (auth.isLoggedIn) {
            if (gate) gate.classList.add('hidden');

            const avatarEl = document.getElementById('userAvatarText');
            const nameEl = document.getElementById('userDisplayName');
            const handleEl = document.getElementById('userHandle');

            const displayName = auth.fullName || auth.userId || 'M Abhishek Reddy';
            if (avatarEl) avatarEl.innerText = this.getInitials(displayName);
            if (nameEl) nameEl.innerText = displayName;
            if (handleEl) handleEl.innerText = `@${auth.userId}`;
        } else {
            if (gate) {
                gate.classList.remove('hidden');
                if (window.lucide) window.lucide.createIcons({ root: gate });
            }
        }
    },

    showAuthGateMessage(msg, isError = true) {
        const el = document.getElementById('authGateMsg');
        if (!el) return;
        el.classList.remove('hidden', 'bg-rose-950/80', 'text-rose-300', 'border-rose-800/80', 'bg-emerald-950/80', 'text-emerald-300', 'border-emerald-800/80');
        const safeMsg = this.escapeHTML(msg);
        if (isError) {
            el.classList.add('bg-rose-950/80', 'text-rose-300', 'border-rose-800/80');
            el.innerHTML = `<i data-lucide="alert-circle" class="w-4 h-4 text-rose-400 shrink-0"></i><span>${safeMsg}</span>`;
        } else {
            el.classList.add('bg-emerald-950/80', 'text-emerald-300', 'border-emerald-800/80');
            el.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4 text-emerald-400 shrink-0"></i><span>${safeMsg}</span>`;
        }
        if (window.lucide) window.lucide.createIcons({ root: el });
    },

    switchAuthTab(tab) {
        const tabSignIn = document.getElementById('tabBtnSignIn');
        const tabSignUp = document.getElementById('tabBtnSignUp');
        const formSignIn = document.getElementById('formSignIn');
        const formSignUp = document.getElementById('formSignUp');
        const msgEl = document.getElementById('authGateMsg');
        if (msgEl) msgEl.classList.add('hidden');

        if (tab === 'signin') {
            if (tabSignIn) tabSignIn.className = 'w-1/2 py-2 rounded-lg text-xs font-bold transition-all bg-sky-500/20 text-sky-300 border border-sky-500/30 shadow-sm cursor-pointer';
            if (tabSignUp) tabSignUp.className = 'w-1/2 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-white transition-all border border-transparent cursor-pointer';
            if (formSignIn) formSignIn.classList.remove('hidden');
            if (formSignUp) formSignUp.classList.add('hidden');
        } else {
            if (tabSignUp) tabSignUp.className = 'w-1/2 py-2 rounded-lg text-xs font-bold transition-all bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shadow-sm cursor-pointer';
            if (tabSignIn) tabSignIn.className = 'w-1/2 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-white transition-all border border-transparent cursor-pointer';
            if (formSignUp) formSignUp.classList.remove('hidden');
            if (formSignIn) formSignIn.classList.add('hidden');
        }
        if (window.lucide) window.lucide.createIcons();
    },

    async login(userId, password) {
        const btn = document.getElementById('btnSubmitLogin');
        if (btn) btn.disabled = true;
        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, password: password })
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAuthGateMessage(data.detail || 'Invalid User ID or password.', true);
                return;
            }

            this.state.auth = {
                isLoggedIn: true,
                userId: data.user.user_id,
                fullName: data.user.full_name,
                token: data.token
            };
            localStorage.setItem('act_auth_user', JSON.stringify({
                user_id: data.user.user_id,
                full_name: data.user.full_name,
                token: data.token
            }));

            this.renderAuthUI();
            await this.loadFilterMetadata();
            await this.refreshDashboard();
            this.showToast(`Signed in as ${data.user.full_name}`, 'success');
        } catch (err) {
            console.error('Login error:', err);
            this.showAuthGateMessage('Network error connecting to authentication service.', true);
        } finally {
            if (btn) btn.disabled = false;
        }
    },

    async signup(userId, password, fullName) {
        const btn = document.getElementById('btnSubmitSignup');
        if (btn) btn.disabled = true;
        try {
            const res = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, password: password, full_name: fullName })
            });
            const data = await res.json();
            if (!res.ok) {
                this.showAuthGateMessage(data.detail || 'Error creating account.', true);
                return;
            }

            this.state.auth = {
                isLoggedIn: true,
                userId: data.user.user_id,
                fullName: data.user.full_name,
                token: data.token
            };
            localStorage.setItem('act_auth_user', JSON.stringify({
                user_id: data.user.user_id,
                full_name: data.user.full_name,
                token: data.token
            }));

            this.renderAuthUI();
            await this.loadFilterMetadata();
            await this.refreshDashboard();
            this.showToast(`Account created! Welcome, ${data.user.full_name}`, 'success');
        } catch (err) {
            console.error('Signup error:', err);
            this.showAuthGateMessage('Network error during account registration.', true);
        } finally {
            if (btn) btn.disabled = false;
        }
    },

    async logout(isExpired = false) {
        try {
            if (this.state.auth && this.state.auth.token) {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${this.state.auth.token}` }
                });
            }
        } catch (e) {}
        localStorage.removeItem('act_auth_user');
        this.state.auth = {
            isLoggedIn: false,
            userId: '',
            fullName: '',
            token: ''
        };
        this.renderAuthUI();
        if (isExpired) {
            this.showAuthGateMessage('Your session has expired. Please sign in again.', true);
            this.showToast('Session expired. Please sign in again.', 'warning');
        } else {
            this.showAuthGateMessage('You have logged out. Sign in to access the control plane.', false);
            this.showToast('Logged out of control plane.', 'info');
        }
    },

    startClock() {
        const updateTime = () => {
            const clockEl = document.getElementById('liveClockDisplay');
            if (clockEl) {
                const now = new Date();
                clockEl.innerText = 'UTC ' + now.toUTCString().slice(17, 25);
            }
        };
        updateTime();
        setInterval(updateTime, 1000);
    },

    updateFamilyDropdown(provider) {
        const familySelect = document.getElementById('calcFamilySelect');
        if (!familySelect) return;
        const prov = provider || 'AWS';
        const catalogEntry = LOCAL_CATALOG[prov] || LOCAL_CATALOG['AWS'];
        const families = catalogEntry.families || [];
        familySelect.innerHTML = families.map((f, idx) => {
            const isSelected = idx === 0 ? 'selected' : '';
            return `<option value="${f.code}" ${isSelected}>${f.name}</option>`;
        }).join('');
        familySelect.selectedIndex = 0;
    },

    updateRegionDropdown(provider) {
        const regionSelect = document.getElementById('calcRegion');
        if (!regionSelect) return;
        const prov = provider || 'AWS';
        const catalogEntry = LOCAL_CATALOG[prov] || LOCAL_CATALOG['AWS'];
        const regions = catalogEntry.regions || (Array.isArray(catalogEntry) ? catalogEntry : []);
        regionSelect.innerHTML = regions.map((r, idx) => {
            const isSelected = idx === 0 ? 'selected' : '';
            return `<option value="${r.code}" ${isSelected}>${r.name} [${r.mult} - ${r.note}]</option>`;
        }).join('');
        regionSelect.selectedIndex = 0;
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
        }

        // Provider dropdown change: immediately update machine families and regions
        const provSelect = document.getElementById('calcProvider');
        if (provSelect) {
            provSelect.addEventListener('change', (e) => {
                this.updateFamilyDropdown(e.target.value);
                this.updateRegionDropdown(e.target.value);
                this.runSimulation();
            });
        }

        // Machine Family dropdown change: update price & SKU immediately
        const famSelect = document.getElementById('calcFamilySelect');
        if (famSelect) {
            famSelect.addEventListener('change', () => this.runSimulation());
        }

        // Region dropdown change: update price
        const regSelect = document.getElementById('calcRegion');
        if (regSelect) {
            regSelect.addEventListener('change', () => this.runSimulation());
        }

        // Calculate Button Click
        const btnCalc = document.getElementById('btnRunCalculate');
        if (btnCalc) {
            btnCalc.addEventListener('click', () => {
                btnCalc.classList.add('opacity-80', 'scale-[0.98]');
                this.runSimulation().finally(() => {
                    setTimeout(() => btnCalc.classList.remove('opacity-80', 'scale-[0.98]'), 200);
                });
            });
        }

        // Custom Calculator Inputs
        ['calcVcpu', 'calcRam', 'calcHours', 'calcDownsize'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', () => this.runSimulation());
                el.addEventListener('change', () => this.runSimulation());
            }
        });

        // Reset Filters Button
        const resetBtn = document.getElementById('resetFiltersBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.state.selectedProviders = [...this.state.providers];
                this.state.selectedDepartments = [...this.state.departments];
                this.renderFilterCheckboxes();
                this.refreshDashboard();
                this.showToast('Active scope reset to default (All Clouds & Departments)', 'success');
            });
        }

        // Live Telemetry Refresh Button
        const refreshBtn = document.getElementById('btnRefreshTelemetry');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                const icon = document.getElementById('refreshIcon');
                if (icon) icon.classList.add('animate-spin');
                await this.refreshDashboard();
                if (icon) {
                    setTimeout(() => icon.classList.remove('animate-spin'), 600);
                }
                this.showToast('Multi-cloud telemetry & analytics refreshed', 'info');
            });
        }

        // Export Anomaly Report to CSV
        const exportAnomBtn = document.getElementById('btnExportAnomalies');
        if (exportAnomBtn) {
            exportAnomBtn.addEventListener('click', () => this.exportAnomaliesToCSV());
        }

        // Export Action Matrix to CSV
        const exportActionsBtn = document.getElementById('btnExportActions');
        if (exportActionsBtn) {
            exportActionsBtn.addEventListener('click', () => this.exportActionsToCSV());
        }

        // Save Simulation Snapshot
        const saveSnapBtn = document.getElementById('btnSaveSnapshot');
        if (saveSnapBtn) {
            saveSnapBtn.addEventListener('click', () => this.saveSimulationSnapshot());
        }

        // Copy Scenario Summary
        const copySummaryBtn = document.getElementById('btnCopyScenarioSummary');
        if (copySummaryBtn) {
            copySummaryBtn.addEventListener('click', () => this.copyScenarioSummary());
        }

        // Clear Scenarios
        const clearSnapsBtn = document.getElementById('btnClearSnapshots');
        if (clearSnapsBtn) {
            clearSnapsBtn.addEventListener('click', () => this.clearSnapshots());
        }

        // Auth Gate Tab Switchers
        const tabBtnSignIn = document.getElementById('tabBtnSignIn');
        if (tabBtnSignIn) {
            tabBtnSignIn.addEventListener('click', () => this.switchAuthTab('signin'));
        }

        const tabBtnSignUp = document.getElementById('tabBtnSignUp');
        if (tabBtnSignUp) {
            tabBtnSignUp.addEventListener('click', () => this.switchAuthTab('signup'));
        }

        // Sign In Form Submission
        const formSignIn = document.getElementById('formSignIn');
        if (formSignIn) {
            formSignIn.addEventListener('submit', (e) => {
                e.preventDefault();
                const uid = document.getElementById('loginUserId')?.value?.trim();
                const pwd = document.getElementById('loginPassword')?.value;
                if (!uid || !pwd) {
                    this.showAuthGateMessage('Please enter both User ID and password.', true);
                    return;
                }
                this.login(uid, pwd);
            });
        }

        // Sign Up Form Submission
        const formSignUp = document.getElementById('formSignUp');
        if (formSignUp) {
            formSignUp.addEventListener('submit', (e) => {
                e.preventDefault();
                const uid = document.getElementById('signupUserId')?.value?.trim();
                const pwd = document.getElementById('signupPassword')?.value;
                const name = document.getElementById('signupFullName')?.value?.trim() || uid;
                if (!uid || !pwd) {
                    this.showAuthGateMessage('Please enter User ID and password.', true);
                    return;
                }
                if (pwd.length < 8) {
                    this.showAuthGateMessage('Password must be at least 8 characters long.', true);
                    return;
                }
                this.signup(uid, pwd, name);
            });
        }

        // Quick Demo Fill
        const demoBtn = document.getElementById('btnQuickDemoLogin');
        if (demoBtn) {
            demoBtn.addEventListener('click', () => {
                const uidInput = document.getElementById('loginUserId');
                const pwdInput = document.getElementById('loginPassword');
                if (uidInput) uidInput.value = 'abhishek';
                if (pwdInput) pwdInput.value = 'password123';
                this.login('abhishek', 'password123');
            });
        }

        // Explicit Logout Button
        const btnLogout = document.getElementById('btnLogout');
        if (btnLogout) {
            btnLogout.addEventListener('click', () => this.logout());
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
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 50);
    },

    async loadFilterMetadata() {
        try {
            const res = await this.authFetch('/api/meta/filters');
            const data = await res.json();
            this.state.providers = data.providers;
            this.state.departments = data.departments;
            this.state.selectedProviders = [...data.providers];
            this.state.selectedDepartments = [...data.departments];
            this.renderFilterCheckboxes();

            const rangeEl = document.getElementById('telemetryDateRange');
            if (rangeEl && data.date_min && data.date_max) {
                rangeEl.innerText = `${data.date_min} to ${data.date_max}`;
                rangeEl.title = `Full Telemetry Span: ${data.date_min} to ${data.date_max}`;
            }
            const countEl = document.getElementById('telemetryRecordCount');
            if (countEl && data.total_records) {
                countEl.innerText = `${Number(data.total_records).toLocaleString()} records`;
            }
        } catch (err) {
            console.error('Failed to load filter metadata:', err);
        }
    },

    renderFilterCheckboxes() {
        const provContainer = document.getElementById('providerFilters');
        if (provContainer) {
            const providerMeta = {
                'AWS': { dotColor: '#FF9900', label: 'AWS Cloud' },
                'Azure': { dotColor: '#0284C7', label: 'Microsoft Azure' },
                'GCP': { dotColor: '#10B981', label: 'Google Cloud' }
            };

            provContainer.innerHTML = this.state.providers.map(p => {
                const meta = providerMeta[p] || { dotColor: '#38bdf8', label: p };
                const isChecked = this.state.selectedProviders.includes(p);
                return `
                    <label class="flex items-center justify-between p-2 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 cursor-pointer select-none transition-all">
                        <div class="flex items-center gap-2.5">
                            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${meta.dotColor}"></span>
                            <span class="text-xs font-semibold text-slate-200">${meta.label}</span>
                        </div>
                        <input type="checkbox" value="${p}" ${isChecked ? 'checked' : ''} class="provider-checkbox rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0 focus:ring-offset-0">
                    </label>
                `;
            }).join('');

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
            deptContainer.innerHTML = this.state.departments.map(d => {
                const isChecked = this.state.selectedDepartments.includes(d);
                return `
                    <label class="flex items-center justify-between p-1.5 px-2.5 rounded-lg hover:bg-slate-800/60 cursor-pointer select-none text-xs transition-colors">
                        <span class="text-slate-300 truncate pr-2">${d}</span>
                        <input type="checkbox" value="${d}" ${isChecked ? 'checked' : ''} class="dept-checkbox rounded bg-slate-800 border-slate-700 text-sky-500 focus:ring-0 focus:ring-offset-0 shrink-0">
                    </label>
                `;
            }).join('');

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
        this.updateLastRefreshed();
    },

    updateLastRefreshed() {
        const pill = document.getElementById('lastRefreshedPill');
        if (pill) {
            const now = new Date();
            pill.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        }
    },

    async fetchKPIs() {
        try {
            const res = await this.authFetch(`/api/kpis?${this.buildQueryString()}`);
            const data = await res.json();

            this.animateValue('kpiTotalSpend', data.total_spend_ytd, '$');
            this.animateValue('kpiRunRate', data.annual_run_rate, '$');
            this.animateValue('kpiSavings', data.identifiable_annual_savings, '$');
            this.animateValue('kpiWaste', data.anomalous_waste_usd, '$');
            
            const cpuEl = document.getElementById('kpiCpu');
            if (cpuEl) cpuEl.innerText = `${data.average_cpu_utilization}%`;
            
            const savPctEl = document.getElementById('kpiSavingsPct');
            if (savPctEl) savPctEl.innerText = `${data.savings_percentage}% spend reduction`;
            
            const incCountEl = document.getElementById('kpiIncidentsCount');
            if (incCountEl) incCountEl.innerText = `${data.anomaly_incident_count} spikes detected`;
            
            const maturityEl = document.getElementById('kpiMaturityStage');
            if (maturityEl) maturityEl.innerText = data.finops_maturity_stage;
        } catch (err) {
            console.error('Error fetching KPIs:', err);
        }
    },

    async fetchTrends() {
        try {
            const res = await this.authFetch(`/api/trends?${this.buildQueryString()}`);
            const data = await res.json();
            Charts.renderDailySpend('dailySpendChart', data);
            Charts.renderProviderDonut('providerDonutChart', data.provider_breakdown);
        } catch (err) {
            console.error('Error fetching trends:', err);
        }
    },

    async fetchDepartmentAnalytics() {
        try {
            const res = await this.authFetch(`/api/departments?${this.buildQueryString()}`);
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
    },

    debounceTimer: null,
    debounceForecast() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => this.fetchForecast(), 200);
    },

    async fetchForecast() {
        try {
            const res = await this.authFetch('/api/forecast', {
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
            document.getElementById('forecastTotalBudget').innerText = `$${data.projected_total_usd.toLocaleString()} USD`;
        } catch (err) {
            console.error('Error fetching forecast:', err);
        }
    },

    async fetchOptimizer() {
        try {
            const res = await this.authFetch(`/api/optimizer?${this.buildQueryString()}`);
            const data = await res.json();
            this.state.currentActions = data.action_matrix || [];

            Charts.renderOptimizationPillars('optimizationPillarsChart', data.portfolio);

            const tbody = document.getElementById('actionTableBody');
            if (tbody) {
                if (!data.action_matrix.length) {
                    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-10 text-slate-500 font-mono">All workloads operating at optimal FinOps efficiency.</td></tr>`;
                    return;
                }

                tbody.innerHTML = data.action_matrix.map(row => {
                    const provClass = row.Cloud_Provider.includes('AWS') ? 'badge-prov-aws' :
                                      row.Cloud_Provider.includes('Azure') ? 'badge-prov-azure' : 'badge-prov-gcp';
                    const effortClass = row.Implementation_Effort.includes('Low') ? 'text-emerald-400 bg-emerald-950/60 border-emerald-800/60' :
                                        row.Implementation_Effort.includes('Medium') ? 'text-amber-400 bg-amber-950/60 border-amber-800/60' :
                                        'text-indigo-400 bg-indigo-950/60 border-indigo-800/60';
                    const safePriority = this.escapeHTML(row.Priority);
                    const safeDept = this.escapeHTML(row.Department);
                    const safeProv = this.escapeHTML(row.Cloud_Provider);
                    const safeService = this.escapeHTML(row.Resource_Service);
                    const safeIssue = this.escapeHTML(row.Issue_Identified);
                    const safeAction = this.escapeHTML(row.Action_Required);
                    const safeEffort = this.escapeHTML(row.Implementation_Effort);
                    return `
                        <tr class="border-b border-slate-800/60 hover:bg-slate-800/40 transition-colors">
                            <td class="py-3 px-4 whitespace-nowrap">
                                <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold ${row.Priority.includes('Critical') ? 'badge-critical' : 'badge-high'}">${safePriority}</span>
                            </td>
                            <td class="py-3 px-4 text-xs font-semibold text-slate-200 whitespace-nowrap">${safeDept}</td>
                            <td class="py-3 px-4 text-xs whitespace-nowrap">
                                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${provClass} mr-1.5">${safeProv}</span>
                                <span class="font-mono text-slate-300 font-medium">${safeService}</span>
                            </td>
                            <td class="py-3 px-4 text-xs text-slate-300">${safeIssue}</td>
                            <td class="py-3 px-4 text-xs text-sky-400 font-medium">${safeAction}</td>
                            <td class="py-3 px-4 text-xs font-mono font-bold text-emerald-400 whitespace-nowrap">+$${Number(row.Est_Monthly_Savings_USD).toLocaleString()}/mo</td>
                            <td class="py-3 px-4 whitespace-nowrap">
                                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${effortClass}">${safeEffort}</span>
                            </td>
                        </tr>
                    `;
                }).join('');
            }
        } catch (err) {
            console.error('Error fetching optimizer portfolio:', err);
        }
    },

    async runSimulation() {
        const provider = document.getElementById('calcProvider')?.value || 'AWS';
        const family = document.getElementById('calcFamilySelect')?.value || '';
        const region = document.getElementById('calcRegion')?.value || 'us-east-1';
        const vcpu = parseInt(document.getElementById('calcVcpu')?.value || 32);
        const ram = parseInt(document.getElementById('calcRam')?.value || 128);
        const hours = parseInt(document.getElementById('calcHours')?.value || 24);
        const downsize = document.getElementById('calcDownsize')?.checked ? 50.0 : 0.0;

        try {
            const res = await this.authFetch('/api/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cloud_provider: provider,
                    machine_family: family,
                    region: region,
                    vcpu_count: vcpu,
                    ram_gb: ram,
                    daily_hours: hours,
                    downsize_pct: downsize
                })
            });
            const data = await res.json();
            this.state.lastSimulation = data;

            // Pod 1: SKU & Family
            const skuEl = document.getElementById('calcSku');
            if (skuEl) {
                skuEl.innerText = `${data.instance_sku} [${data.multiplier}x]`;
                skuEl.title = `${data.region_name} - ${data.region_note}`;
            }
            const familyEl = document.getElementById('calcFamily');
            if (familyEl) {
                familyEl.innerText = `${data.machine_family_name || data.family} (${data.machine_family_note || 'Standard'})`;
            }

            // Pod 2: Hourly Rate
            const hourlyEl = document.getElementById('calcHourly');
            if (hourlyEl) {
                hourlyEl.innerText = `$${Number(data.hourly_cost_usd).toFixed(4)} /hr`;
            }

            // Pod 3: Monthly Burn
            const monthlyEl = document.getElementById('calcMonthly');
            if (monthlyEl) {
                monthlyEl.innerText = `$${Number(data.monthly_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;
            }

            // Pod 4: Rightsizing Savings
            const savingsEl = document.getElementById('calcSavings');
            if (savingsEl) {
                savingsEl.innerText = `$${Number(data.potential_monthly_savings_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}/mo`;
            }

            const annualSavingsEl = document.getElementById('calcAnnualSavings');
            if (annualSavingsEl) {
                const annualVal = data.potential_annual_savings_usd || (data.potential_monthly_savings_usd * 12);
                annualSavingsEl.innerText = `+$${Number(annualVal).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /yr Projected ROI`;
            }
        } catch (err) {
            console.error('Error in workload simulator:', err);
        }
    },

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        const borderColor = type === 'success' ? 'border-emerald-500/60 text-emerald-300' :
                            type === 'warning' ? 'border-amber-500/60 text-amber-300' :
                            type === 'error' ? 'border-rose-500/60 text-rose-300' :
                            'border-sky-500/60 text-sky-300';
        const iconName = type === 'success' ? 'check-circle-2' :
                         type === 'warning' ? 'alert-triangle' :
                         type === 'error' ? 'alert-octagon' :
                         'info';

        toast.className = `pointer-events-auto flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-slate-900/95 border ${borderColor} shadow-2xl backdrop-blur-md text-xs font-semibold transform transition-all duration-300 translate-y-4 opacity-0`;
        toast.innerHTML = `
            <i data-lucide="${iconName}" class="w-4 h-4 shrink-0"></i>
            <span class="text-white">${this.escapeHTML(message)}</span>
        `;
        container.appendChild(toast);
        if (window.lucide) window.lucide.createIcons({ root: toast });

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-4', 'opacity-0');
            toast.classList.add('translate-y-0', 'opacity-100');
        });

        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-y-2');
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    },

    downloadCSV(filename, headers, rows) {
        const escapeCell = (val) => {
            if (val === null || val === undefined) return '""';
            const str = String(val).replace(/"/g, '""');
            return `"${str}"`;
        };
        const csvContent = [
            headers.map(escapeCell).join(','),
            ...rows.map(row => row.map(escapeCell).join(','))
        ].join('\r\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    },

    exportAnomaliesToCSV() {
        if (!this.state.currentAnomalies || !this.state.currentAnomalies.length) {
            this.showToast('No anomaly records to export in current scope.', 'warning');
            return;
        }
        const headers = [
            'Event_Date', 'Cloud_Provider', 'Cost_Center_Department', 'Service',
            'Region', 'Resource_Id', 'Daily_Spend_USD', 'Excess_Surge_USD',
            'Severity', 'ML_Root_Cause_Diagnosis'
        ];
        const rows = this.state.currentAnomalies.map(a => [
            a.Date || '',
            a.CloudProvider || '',
            a.Department || '',
            a.Service || '',
            a.RegionName || '',
            a.ResourceId || '',
            a.DailyCost_USD || 0,
            a.cost_spike_usd || 0,
            a.anomaly_severity || '',
            a.root_cause_diagnosis || ''
        ]);
        const dateStr = new Date().toISOString().slice(0, 10);
        this.downloadCSV(`FinOps_Anomaly_Incidents_${dateStr}.csv`, headers, rows);
        this.showToast(`Exported ${rows.length} anomaly incidents to CSV.`, 'success');
    },

    exportActionsToCSV() {
        if (!this.state.currentActions || !this.state.currentActions.length) {
            this.showToast('No optimization recommendations to export.', 'warning');
            return;
        }
        const headers = [
            'Priority', 'Department', 'Cloud_Provider', 'Resource_Service',
            'Issue_Identified', 'Action_Required', 'Est_Monthly_Savings_USD',
            'Implementation_Effort'
        ];
        const rows = this.state.currentActions.map(r => [
            r.Priority || '',
            r.Department || '',
            r.Cloud_Provider || '',
            r.Resource_Service || '',
            r.Issue_Identified || '',
            r.Action_Required || '',
            r.Est_Monthly_Savings_USD || 0,
            r.Implementation_Effort || ''
        ]);
        const dateStr = new Date().toISOString().slice(0, 10);
        this.downloadCSV(`FinOps_Prioritized_Remediation_Plan_${dateStr}.csv`, headers, rows);
        this.showToast(`Exported ${rows.length} remediation actions to CSV.`, 'success');
    },

    saveSimulationSnapshot() {
        if (!this.state.lastSimulation) {
            this.showToast('Run a simulation calculation first.', 'warning');
            return;
        }
        const sim = this.state.lastSimulation;
        const snapshot = {
            id: 'snap-' + Date.now(),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            provider: sim.cloud_provider,
            family: sim.machine_family_name || sim.family || '',
            region: sim.region_name || sim.region_key,
            sku: sim.instance_sku,
            hourly: sim.hourly_cost_usd,
            monthly: sim.monthly_cost_usd,
            monthlySavings: sim.potential_monthly_savings_usd,
            annualSavings: sim.potential_annual_savings_usd
        };
        this.state.snapshots.unshift(snapshot);
        if (this.state.snapshots.length > 6) this.state.snapshots.pop();
        this.renderSnapshots();
        this.showToast(`Saved snapshot for ${sim.cloud_provider} ${sim.instance_sku}`, 'success');
    },

    renderSnapshots() {
        const container = document.getElementById('simulationSnapshotsContainer');
        const list = document.getElementById('simulationSnapshotsList');
        const count = document.getElementById('snapshotCount');
        if (!container || !list) return;

        if (this.state.snapshots.length === 0) {
            container.classList.add('hidden');
            return;
        }

        container.classList.remove('hidden');
        if (count) count.innerText = this.state.snapshots.length;

        list.innerHTML = this.state.snapshots.map(s => {
            const safeProv = this.escapeHTML(s.provider);
            const safeSku = this.escapeHTML(s.sku);
            const safeTime = this.escapeHTML(s.timestamp);
            const safeFam = this.escapeHTML(s.family || '');
            const safeReg = this.escapeHTML(s.region || '');
            return `
            <div class="p-3 rounded-xl bg-slate-900/90 border border-slate-800 relative group text-xs font-mono shadow-sm">
                <div class="flex items-center justify-between mb-1">
                    <span class="font-bold text-white">${safeProv} &bull; ${safeSku}</span>
                    <span class="text-[10px] text-slate-500">${safeTime}</span>
                </div>
                ${safeFam ? `<div class="text-[10px] text-sky-400 font-sans truncate mb-0.5">${safeFam}</div>` : ''}
                <div class="text-[11px] text-slate-400 truncate mb-1.5" title="${safeReg}">${safeReg}</div>
                <div class="flex justify-between items-center text-[11px] pt-1.5 border-t border-slate-800/80">
                    <span class="text-slate-400">Monthly: <span class="text-white font-bold">$${Number(s.monthly).toLocaleString()}</span></span>
                    <span class="text-emerald-400 font-bold">-$${Number(s.monthlySavings).toLocaleString()}/mo</span>
                </div>
            </div>
            `;
        }).join('');
    },

    copyScenarioSummary() {
        if (!this.state.snapshots.length) {
            this.showToast('No saved scenarios to copy.', 'warning');
            return;
        }
        const text = this.state.snapshots.map((s, i) => 
            `Scenario ${i + 1}: ${s.provider} | SKU: ${s.sku} | Region: ${s.region} | Monthly Burn: $${Number(s.monthly).toLocaleString()} | Monthly Savings: $${Number(s.monthlySavings).toLocaleString()} | Annual ROI: $${Number(s.annualSavings).toLocaleString()}`
        ).join('\n');

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Scenario summary copied to clipboard!', 'success');
            }).catch(() => {
                this.showToast('Scenario summary ready.', 'info');
            });
        } else {
            this.showToast('Scenario summary compiled.', 'info');
        }
    },

    clearSnapshots() {
        this.state.snapshots = [];
        this.renderSnapshots();
        this.showToast('Cleared saved scenarios.', 'info');
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
