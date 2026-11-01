/**
 * Abhi Cloud Tech — Frontend Application Controller
 * Handles reactivity, asynchronous API communications, DOM updates, enterprise CSV export,
 * interactive simulation snapshotting, and notifications.
 */

const HYPERSCALER_CATALOG = {
    'GCP': {
        provider_key: 'GCP',
        name: 'Google Cloud Platform (GCP)',
        brand_color: '#10B981',
        official_url: 'https://cloud.google.com/products/calculator',
        regions: {
            'us-central1': { name: 'us-central1 (Iowa - Google Low-Carbon DC)', multiplier: 1.00 },
            'us-east4': { name: 'us-east4 (N. Virginia - Ashburn Corridor)', multiplier: 1.09 },
            'us-west1': { name: 'us-west1 (Oregon - Dalles Hydro)', multiplier: 1.00 },
            'europe-west3': { name: 'europe-west3 (Frankfurt, Germany)', multiplier: 1.22 },
            'europe-west1': { name: 'europe-west1 (St. Ghislain, Belgium)', multiplier: 1.15 },
            'asia-south1': { name: 'asia-south1 (Mumbai, India)', multiplier: 1.11 },
            'asia-southeast1': { name: 'asia-southeast1 (Jurong West, Singapore)', multiplier: 1.14 }
        },
        machine_presets: [
            { sku: 'e2-micro', family: 'e2', name: 'e2-micro (2 shared vCPU, 1 GB RAM)', vcpu: 0.25, ram_gb: 1.0, base_monthly_usd: 6.11 },
            { sku: 'e2-small', family: 'e2', name: 'e2-small (2 shared vCPU, 2 GB RAM)', vcpu: 0.5, ram_gb: 2.0, base_monthly_usd: 12.23 },
            { sku: 'e2-medium', family: 'e2', name: 'e2-medium (2 shared vCPU, 4 GB RAM)', vcpu: 1.0, ram_gb: 4.0, base_monthly_usd: 24.46 },
            { sku: 'e2-standard-2', family: 'e2', name: 'e2-standard-2 (2 vCPU, 8 GB RAM)', vcpu: 2.0, ram_gb: 8.0, base_monthly_usd: 48.92 },
            { sku: 'e2-standard-4', family: 'e2', name: 'e2-standard-4 (4 vCPU, 16 GB RAM)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 97.85 },
            { sku: 'e2-standard-8', family: 'e2', name: 'e2-standard-8 (8 vCPU, 32 GB RAM)', vcpu: 8.0, ram_gb: 32.0, base_monthly_usd: 195.69 },
            { sku: 'e2-standard-16', family: 'e2', name: 'e2-standard-16 (16 vCPU, 64 GB RAM)', vcpu: 16.0, ram_gb: 64.0, base_monthly_usd: 391.38 },
            { sku: 'n2-standard-2', family: 'n2', name: 'n2-standard-2 (2 vCPU, 8 GB RAM - Intel Cascade/Ice Lake)', vcpu: 2.0, ram_gb: 8.0, base_monthly_usd: 71.49 },
            { sku: 'n2-standard-4', family: 'n2', name: 'n2-standard-4 (4 vCPU, 16 GB RAM - Intel Cascade/Ice Lake)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 142.98 },
            { sku: 'n2-standard-8', family: 'n2', name: 'n2-standard-8 (8 vCPU, 32 GB RAM - Intel Cascade/Ice Lake)', vcpu: 8.0, ram_gb: 32.0, base_monthly_usd: 285.96 },
            { sku: 'n2-standard-16', family: 'n2', name: 'n2-standard-16 (16 vCPU, 64 GB RAM - Intel Cascade/Ice Lake)', vcpu: 16.0, ram_gb: 64.0, base_monthly_usd: 571.91 },
            { sku: 'n2-standard-32', family: 'n2', name: 'n2-standard-32 (32 vCPU, 128 GB RAM - Intel Cascade/Ice Lake)', vcpu: 32.0, ram_gb: 128.0, base_monthly_usd: 1143.83 },
            { sku: 't2d-standard-2', family: 't2d', name: 't2d-standard-2 (2 vCPU, 8 GB RAM - AMD Tau Milan)', vcpu: 2.0, ram_gb: 8.0, base_monthly_usd: 59.28 },
            { sku: 't2d-standard-4', family: 't2d', name: 't2d-standard-4 (4 vCPU, 16 GB RAM - AMD Tau Milan)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 118.55 },
            { sku: 't2d-standard-8', family: 't2d', name: 't2d-standard-8 (8 vCPU, 32 GB RAM - AMD Tau Milan)', vcpu: 8.0, ram_gb: 32.0, base_monthly_usd: 237.10 },
            { sku: 'c2-standard-4', family: 'c2', name: 'c2-standard-4 (4 vCPU, 16 GB RAM - Compute Intensive)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 152.42 },
            { sku: 'c2-standard-8', family: 'c2', name: 'c2-standard-8 (8 vCPU, 32 GB RAM - Compute Intensive)', vcpu: 8.0, ram_gb: 32.0, base_monthly_usd: 304.85 },
            { sku: 'c2-standard-16', family: 'c2', name: 'c2-standard-16 (16 vCPU, 64 GB RAM - Compute Intensive)', vcpu: 16.0, ram_gb: 64.0, base_monthly_usd: 609.70 }
        ],
        custom_rates: { vcpu_hourly: 0.0336, ram_hourly: 0.0045 },
        storage_disk_types: {
            'pd-standard': { name: 'Standard Persistent Disk (pd-standard)', rate_per_gb_month: 0.040, note: 'HDD storage for sequential batch data' },
            'pd-balanced': { name: 'Balanced Persistent Disk (pd-balanced)', rate_per_gb_month: 0.100, note: 'Cost-effective SSD for general-purpose compute' },
            'pd-ssd': { name: 'SSD Persistent Disk (pd-ssd)', rate_per_gb_month: 0.170, note: 'High-IOPS performance SSD for database and low latency' },
            'pd-extreme': { name: 'Extreme Persistent Disk (pd-extreme)', rate_per_gb_month: 0.250, note: 'Ultra-performance for high-end SAP/RDBMS' }
        },
        commitment_discounts: {
            'on_demand': { name: 'On-Demand (Pay-As-You-Go)', discount_pct: 0.0 },
            '1yr_commitment': { name: '1-Year Committed Use Discount (CUD - 37% off)', discount_pct: 37.0 },
            '3yr_commitment': { name: '3-Year Committed Use Discount (CUD - 55% off)', discount_pct: 55.0 },
            'spot': { name: 'Spot / Preemptible VMs (70% off)', discount_pct: 70.0 }
        }
    },
    'AWS': {
        provider_key: 'AWS',
        name: 'Amazon Web Services (AWS)',
        brand_color: '#FF9900',
        official_url: 'https://calculator.aws/#/addService',
        regions: {
            'us-east-1': { name: 'us-east-1 (US East - N. Virginia)', multiplier: 1.00 },
            'us-west-2': { name: 'us-west-2 (US West - Oregon)', multiplier: 1.00 },
            'eu-central-1': { name: 'eu-central-1 (Europe - Frankfurt)', multiplier: 1.18 },
            'eu-west-1': { name: 'eu-west-1 (Europe - Ireland)', multiplier: 1.10 },
            'ap-south-1': { name: 'ap-south-1 (Asia Pacific - Mumbai)', multiplier: 1.09 },
            'ap-southeast-1': { name: 'ap-southeast-1 (Asia Pacific - Singapore)', multiplier: 1.14 },
            'sa-east-1': { name: 'sa-east-1 (South America - São Paulo)', multiplier: 1.34 }
        },
        machine_presets: [
            { sku: 't4g.nano', family: 't4g', name: 't4g.nano (2 vCPU burst, 0.5 GB RAM - Graviton2)', vcpu: 2.0, ram_gb: 0.5, base_monthly_usd: 3.07 },
            { sku: 't4g.micro', family: 't4g', name: 't4g.micro (2 vCPU burst, 1 GB RAM - Graviton2)', vcpu: 2.0, ram_gb: 1.0, base_monthly_usd: 6.13 },
            { sku: 't4g.small', family: 't4g', name: 't4g.small (2 vCPU burst, 2 GB RAM - Graviton2)', vcpu: 2.0, ram_gb: 2.0, base_monthly_usd: 12.26 },
            { sku: 't4g.medium', family: 't4g', name: 't4g.medium (2 vCPU burst, 4 GB RAM - Graviton2)', vcpu: 2.0, ram_gb: 4.0, base_monthly_usd: 24.53 },
            { sku: 'm6i.large', family: 'm6i', name: 'm6i.large (2 vCPU, 8 GB RAM - Intel Ice Lake)', vcpu: 2.0, ram_gb: 8.0, base_monthly_usd: 70.08 },
            { sku: 'm6i.xlarge', family: 'm6i', name: 'm6i.xlarge (4 vCPU, 16 GB RAM - Intel Ice Lake)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 140.16 },
            { sku: 'm6i.2xlarge', family: 'm6i', name: 'm6i.2xlarge (8 vCPU, 32 GB RAM - Intel Ice Lake)', vcpu: 8.0, ram_gb: 32.0, base_monthly_usd: 280.32 },
            { sku: 'm6i.4xlarge', family: 'm6i', name: 'm6i.4xlarge (16 vCPU, 64 GB RAM - Intel Ice Lake)', vcpu: 16.0, ram_gb: 64.0, base_monthly_usd: 560.64 },
            { sku: 'm6i.8xlarge', family: 'm6i', name: 'm6i.8xlarge (32 vCPU, 128 GB RAM - Intel Ice Lake)', vcpu: 32.0, ram_gb: 128.0, base_monthly_usd: 1121.28 },
            { sku: 'm6g.xlarge', family: 'm6g', name: 'm6g.xlarge (4 vCPU, 16 GB RAM - Graviton2 ARM - 20% off)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 112.13 },
            { sku: 'm6g.2xlarge', family: 'm6g', name: 'm6g.2xlarge (8 vCPU, 32 GB RAM - Graviton2 ARM - 20% off)', vcpu: 8.0, ram_gb: 32.0, base_monthly_usd: 224.26 },
            { sku: 'c6i.xlarge', family: 'c6i', name: 'c6i.xlarge (4 vCPU, 8 GB RAM - Compute Optimized)', vcpu: 4.0, ram_gb: 8.0, base_monthly_usd: 124.10 },
            { sku: 'c6i.2xlarge', family: 'c6i', name: 'c6i.2xlarge (8 vCPU, 16 GB RAM - Compute Optimized)', vcpu: 8.0, ram_gb: 16.0, base_monthly_usd: 248.20 },
            { sku: 'r6i.xlarge', family: 'r6i', name: 'r6i.xlarge (4 vCPU, 32 GB RAM - Memory Optimized 8:1)', vcpu: 4.0, ram_gb: 32.0, base_monthly_usd: 183.96 },
            { sku: 'r6i.2xlarge', family: 'r6i', name: 'r6i.2xlarge (8 vCPU, 64 GB RAM - Memory Optimized 8:1)', vcpu: 8.0, ram_gb: 64.0, base_monthly_usd: 367.92 }
        ],
        custom_rates: { vcpu_hourly: 0.0480, ram_hourly: 0.0060 },
        storage_disk_types: {
            'gp3': { name: 'General Purpose SSD (gp3 - 3,000 IOPS baseline)', rate_per_gb_month: 0.080, note: 'Latest gen SSD with baseline 3,000 IOPS' },
            'gp2': { name: 'General Purpose SSD (gp2)', rate_per_gb_month: 0.100, note: 'Legacy standard SSD with burstable baseline' },
            'io2': { name: 'Provisioned IOPS SSD (io2 Block Express)', rate_per_gb_month: 0.125, note: 'Sub-millisecond latency for critical databases' },
            'st1': { name: 'Throughput Optimized HDD (st1)', rate_per_gb_month: 0.045, note: 'Low-cost HDD for big data and log processing' },
            'sc1': { name: 'Cold HDD (sc1)', rate_per_gb_month: 0.025, note: 'Lowest cost magnetic storage for cold data' }
        },
        commitment_discounts: {
            'on_demand': { name: 'On-Demand (Pay-As-You-Go)', discount_pct: 0.0 },
            '1yr_commitment': { name: '1-Year Compute Savings Plan (35% off)', discount_pct: 35.0 },
            '3yr_commitment': { name: '3-Year Compute Savings Plan (55% off)', discount_pct: 55.0 },
            'spot': { name: 'EC2 Spot Instances (~70% off)', discount_pct: 70.0 }
        }
    },
    'Azure': {
        provider_key: 'Azure',
        name: 'Microsoft Azure',
        brand_color: '#0284C7',
        official_url: 'https://azure.microsoft.com/en-in/pricing/calculator/',
        regions: {
            'eastus': { name: 'eastus (East US - Virginia)', multiplier: 1.00 },
            'westus2': { name: 'westus2 (West US 2 - Washington)', multiplier: 1.00 },
            'westeurope': { name: 'westeurope (West Europe - Netherlands)', multiplier: 1.17 },
            'northeurope': { name: 'northeurope (North Europe - Ireland)', multiplier: 1.15 },
            'centralindia': { name: 'centralindia (Central India - Pune)', multiplier: 1.10 },
            'southeastasia': { name: 'southeastasia (Southeast Asia - Singapore)', multiplier: 1.13 }
        },
        machine_presets: [
            { sku: 'Standard_B1s', family: 'Standard_B', name: 'Standard_B1s (1 vCPU, 1 GB RAM - Burstable)', vcpu: 1.0, ram_gb: 1.0, base_monthly_usd: 7.59 },
            { sku: 'Standard_B2s', family: 'Standard_B', name: 'Standard_B2s (2 vCPU, 4 GB RAM - Burstable)', vcpu: 2.0, ram_gb: 4.0, base_monthly_usd: 30.37 },
            { sku: 'Standard_B4ms', family: 'Standard_B', name: 'Standard_B4ms (4 vCPU, 16 GB RAM - Burstable)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 121.47 },
            { sku: 'Standard_D2s_v5', family: 'Standard_Dsv5', name: 'Standard_D2s_v5 (2 vCPU, 8 GB RAM - Intel Ice Lake)', vcpu: 2.0, ram_gb: 8.0, base_monthly_usd: 70.08 },
            { sku: 'Standard_D4s_v5', family: 'Standard_Dsv5', name: 'Standard_D4s_v5 (4 vCPU, 16 GB RAM - Intel Ice Lake)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 140.16 },
            { sku: 'Standard_D8s_v5', family: 'Standard_Dsv5', name: 'Standard_D8s_v5 (8 vCPU, 32 GB RAM - Intel Ice Lake)', vcpu: 8.0, ram_gb: 32.0, base_monthly_usd: 280.32 },
            { sku: 'Standard_D16s_v5', family: 'Standard_Dsv5', name: 'Standard_D16s_v5 (16 vCPU, 64 GB RAM - Intel Ice Lake)', vcpu: 16.0, ram_gb: 64.0, base_monthly_usd: 560.64 },
            { sku: 'Standard_D32s_v5', family: 'Standard_Dsv5', name: 'Standard_D32s_v5 (32 vCPU, 128 GB RAM - Intel Ice Lake)', vcpu: 32.0, ram_gb: 128.0, base_monthly_usd: 1121.28 },
            { sku: 'Standard_D4as_v5', family: 'Standard_Dasv5', name: 'Standard_D4as_v5 (4 vCPU, 16 GB RAM - AMD Milan - 12% off)', vcpu: 4.0, ram_gb: 16.0, base_monthly_usd: 123.37 },
            { sku: 'Standard_D8as_v5', family: 'Standard_Dasv5', name: 'Standard_D8as_v5 (8 vCPU, 32 GB RAM - AMD Milan - 12% off)', vcpu: 8.0, ram_gb: 32.0, base_monthly_usd: 246.74 },
            { sku: 'Standard_E4s_v5', family: 'Standard_Esv5', name: 'Standard_E4s_v5 (4 vCPU, 32 GB RAM - Memory Optimized)', vcpu: 4.0, ram_gb: 32.0, base_monthly_usd: 183.96 },
            { sku: 'Standard_E8s_v5', family: 'Standard_Esv5', name: 'Standard_E8s_v5 (8 vCPU, 64 GB RAM - Memory Optimized)', vcpu: 8.0, ram_gb: 64.0, base_monthly_usd: 367.92 },
            { sku: 'Standard_F4s_v2', family: 'Standard_Fsv2', name: 'Standard_F4s_v2 (4 vCPU, 8 GB RAM - Compute Intensive)', vcpu: 4.0, ram_gb: 8.0, base_monthly_usd: 123.00 }
        ],
        custom_rates: { vcpu_hourly: 0.0475, ram_hourly: 0.0059 },
        storage_disk_types: {
            'standard-hdd': { name: 'Standard HDD Managed Disk', rate_per_gb_month: 0.040, note: 'Low cost backup and non-critical dev/test' },
            'standard-ssd': { name: 'Standard SSD Managed Disk', rate_per_gb_month: 0.075, note: 'Cost-effective SSD for web servers' },
            'premium-ssd': { name: 'Premium SSD Managed Disk (P1-P80)', rate_per_gb_month: 0.135, note: 'High performance SSD for production I/O' },
            'ultra-disk': { name: 'Ultra Disk Managed Storage', rate_per_gb_month: 0.220, note: 'Sub-millisecond latency for high-end SQL' }
        },
        commitment_discounts: {
            'on_demand': { name: 'Pay-As-You-Go (0% off)', discount_pct: 0.0 },
            '1yr_commitment': { name: '1-Year Reserved Virtual Machine (~35% off)', discount_pct: 35.0 },
            '3yr_commitment': { name: '3-Year Reserved Virtual Machine (~55% off)', discount_pct: 55.0 },
            'spot': { name: 'Azure Spot Virtual Machines (~70% off)', discount_pct: 70.0 }
        }
    }
};

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
        calcCloud: 'GCP',
        calcMode: 'preset',
        calcCatalog: null,
        calcLastEstimate: null,
        calcBOM: [],
        activeCalcService: 'compute',
        lastArbitrage: null,
        calcBOM: [],
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

    async apiCall(url, options = {}) {
        options.headers = options.headers || {};
        if (options.body && typeof options.body === 'string' && !options.headers['Content-Type']) {
            options.headers['Content-Type'] = 'application/json';
        }
        const res = await this.authFetch(url, options);
        if (!res.ok) {
            let errMsg = `Request failed (${res.status})`;
            try {
                const errData = await res.json();
                errMsg = errData.detail || errData.message || errMsg;
            } catch (e) {}
            throw new Error(errMsg);
        }
        return await res.json();
    },

    async init() {
        this.startClock();
        this.updateFamilyDropdown('AWS');
        this.updateRegionDropdown('AWS');
        this.bindEvents();
        this.initIngestionEvents();
        this.initCloudCalculator();
        this.initAuth();
        if (this.state.auth.isLoggedIn) {
            await this.fetchDatasetStatus();
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
        // Isolated Horizontal Wheel Scroll for Top App Bar
        const topBar = document.getElementById('topAppBar');
        if (topBar) {
            topBar.addEventListener('wheel', (e) => {
                if (topBar.scrollWidth > topBar.clientWidth) {
                    if (e.deltaY !== 0) {
                        e.preventDefault();
                        topBar.scrollLeft += e.deltaY;
                    }
                }
            }, { passive: false });
        }

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

        // Service Category Tab Switching
        document.querySelectorAll('.calc-service-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const sType = tab.dataset.calcService || 'compute';
                this.state.activeCalcService = sType;
                document.querySelectorAll('.calc-service-tab').forEach(t => {
                    t.classList.remove('active', 'bg-sky-500/20', 'text-sky-300', 'border-sky-500/40');
                    t.classList.add('bg-slate-900', 'text-slate-400', 'border-slate-800');
                });
                tab.classList.add('active', 'bg-sky-500/20', 'text-sky-300', 'border-sky-500/40');
                tab.classList.remove('bg-slate-900', 'text-slate-400', 'border-slate-800');
                this.runSimulation();
            });
        });

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

        // Add to Quote (BOM) Button Click
        const btnBOM = document.getElementById('btnAddToBOM');
        if (btnBOM) {
            btnBOM.addEventListener('click', () => this.addCurrentToBOM());
        }

        // Clear BOM Button
        const btnClearBOM = document.getElementById('btnClearBOM');
        if (btnClearBOM) {
            btnClearBOM.addEventListener('click', () => this.clearBOM());
        }

        // Export BOM Quote Button
        const btnExportBOM = document.getElementById('btnExportBOM');
        if (btnExportBOM) {
            btnExportBOM.addEventListener('click', () => this.exportBOMQuote());
        }

        // Calculator Inputs (Multi-Cloud Levers)
        [
            'calcCommitment', 'calcOs', 'calcHybridBenefit',
            'calcVcpu', 'calcRam', 'calcStorage', 'calcNodes', 'calcHours', 'calcDownsize'
        ].forEach(id => {
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
            activeSection.classList.remove('animate-fadeIn');
            void activeSection.offsetWidth;
            activeSection.classList.add('animate-fadeIn');
        }

        if (tabId === 'optimization') {
            this.initCloudCalculator();
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
            this.fetchDatasetStatus(),
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
            if (maturityEl) {
                const raw = (data.finops_maturity_stage || '').trim();
                let display = raw;
                if (raw.includes('Run') || raw.toLowerCase().includes('optimized')) {
                    display = 'Optimized';
                } else if (raw.includes('Walk') || raw.toLowerCase().includes('proactive')) {
                    display = 'Proactive (Walk)';
                } else if (raw.includes('Crawl') || raw.toLowerCase().includes('reactive')) {
                    display = 'Reactive (Crawl)';
                }
                maturityEl.innerText = display;
                const parent = maturityEl.closest('#maturityPillWrapper') || maturityEl.parentElement;
                if (parent) {
                    parent.title = `FinOps Maturity Framework: ${raw} (Score: ${data.finops_maturity_score || '--'}/100)`;
                }
            }
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

    // Executive Trends Chart Invocation Aliases
    async initTrendsChart() {
        return this.fetchTrends();
    },
    async renderTrendsChart() {
        return this.fetchTrends();
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
        const service = this.state.activeCalcService || 'compute';
        const vcpu = parseInt(document.getElementById('calcVcpu')?.value || 16);
        const ram = parseInt(document.getElementById('calcRam')?.value || 64);
        const storage = parseFloat(document.getElementById('calcStorage')?.value || 500);
        const nodes = parseInt(document.getElementById('calcNodes')?.value || 1);
        const egress = parseFloat(document.getElementById('calcEgress')?.value || 1000);
        const os = document.getElementById('calcOs')?.value || 'linux';
        const commitment = document.getElementById('calcCommitment')?.value || 'on_demand';
        const hybridBenefit = !!document.getElementById('calcHybridBenefit')?.checked;
        const hours = parseInt(document.getElementById('calcHours')?.value || 24);
        const downsize = document.getElementById('calcDownsize')?.checked ? 50.0 : 0.0;

        try {
            const res = await this.authFetch('/api/calculator/multicloud-compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    service_type: service,
                    vcpu: vcpu,
                    ram_gb: ram,
                    storage_gb: storage,
                    nodes_count: nodes,
                    egress_gb: egress,
                    os_type: os,
                    commitment: commitment,
                    hybrid_benefit: hybridBenefit,
                    running_hours_per_day: hours,
                    downsize_pct: downsize
                })
            });
            const data = await res.json();
            this.state.lastArbitrage = data;

            // Render AWS Card
            const aws = data.providers?.AWS;
            if (aws) {
                const elM = document.getElementById('awsMonthlyPrice');
                if (elM) elM.innerText = `$${Number(aws.monthly_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;
                const elA = document.getElementById('awsAnnualPrice');
                if (elA) elA.innerText = `$${Number(aws.annual_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /year`;
                const elSku = document.getElementById('awsSku');
                if (elSku) elSku.innerText = aws.sku_name || 'm6i.4xlarge';
                const elCom = document.getElementById('awsCommitment');
                if (elCom) elCom.innerText = aws.commitment_model_name;
                const elSav = document.getElementById('awsSavings');
                if (elSav) elSav.innerText = `$${Number(aws.commitment_discount_savings_monthly_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}/mo (${aws.commitment_discount_pct}%)`;
            }

            // Render Azure Card
            const az = data.providers?.Azure;
            if (az) {
                const elM = document.getElementById('azureMonthlyPrice');
                if (elM) elM.innerText = `$${Number(az.monthly_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;
                const elA = document.getElementById('azureAnnualPrice');
                if (elA) elA.innerText = `$${Number(az.annual_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /year`;
                const elSku = document.getElementById('azureSku');
                if (elSku) elSku.innerText = az.sku_name || 'Standard_D16s_v5';
                const elCom = document.getElementById('azureCommitment');
                if (elCom) elCom.innerText = az.commitment_model_name;
                const elSav = document.getElementById('azureSavings');
                if (elSav) elSav.innerText = `$${Number(az.commitment_discount_savings_monthly_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}/mo (${az.commitment_discount_pct}%)`;
            }

            // Render GCP Card
            const gcp = data.providers?.GCP;
            if (gcp) {
                const elM = document.getElementById('gcpMonthlyPrice');
                if (elM) elM.innerText = `$${Number(gcp.monthly_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;
                const elA = document.getElementById('gcpAnnualPrice');
                if (elA) elA.innerText = `$${Number(gcp.annual_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /year`;
                const elSku = document.getElementById('gcpSku');
                if (elSku) elSku.innerText = gcp.sku_name || 'n2-standard-16';
                const elCom = document.getElementById('gcpCommitment');
                if (elCom) elCom.innerText = gcp.commitment_model_name;
                const elSav = document.getElementById('gcpSavings');
                if (elSav) elSav.innerText = `$${Number(gcp.commitment_discount_savings_monthly_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}/mo (${gcp.commitment_discount_pct}%)`;
            }

            // Highlight Arbitrage Winner
            const winner = data.arbitrage_summary?.recommended_provider;
            ['AWS', 'Azure', 'GCP'].forEach(p => {
                const badge = document.getElementById(`badge${p}Winner`);
                const card = document.getElementById(`card${p}Arbitrage`);
                if (p === winner) {
                    if (badge) badge.classList.remove('hidden');
                    if (card) {
                        card.classList.add('border-emerald-500/80', 'shadow-emerald-500/15');
                        card.classList.remove('border-slate-800');
                    }
                } else {
                    if (badge) badge.classList.add('hidden');
                    if (card) {
                        card.classList.remove('border-emerald-500/80', 'shadow-emerald-500/15');
                        card.classList.add('border-slate-800');
                    }
                }
            });

            // Update Arbitrage Banner
            const spreadEl = document.getElementById('arbitrageSpreadPill');
            if (spreadEl) spreadEl.innerText = `${data.arbitrage_summary?.arbitrage_savings_percentage}% Cheaper`;
            const rationaleEl = document.getElementById('arbitrageRationaleText');
            if (rationaleEl) rationaleEl.innerText = data.arbitrage_summary?.recommendation_rationale || '';

            // Update Before vs After Rightsizing Impact
            const winnerProvData = data.providers?.[winner] || aws || {};
            const curBurnEl = document.getElementById('calcCurrentBurn');
            if (curBurnEl) curBurnEl.innerText = `$${Number(data.arbitrage_summary?.highest_monthly_cost_usd || winnerProvData.monthly_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;

            const rightsizedBoxEl = document.getElementById('calcRightsizedBox');
            if (rightsizedBoxEl) rightsizedBoxEl.innerText = `$${Number(winnerProvData.rightsized_monthly_cost_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;

            const recoveryEl = document.getElementById('calcNetRecovery');
            if (recoveryEl) recoveryEl.innerText = `+$${Number(winnerProvData.rightsized_monthly_savings_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;

            const recoveryAnnEl = document.getElementById('calcNetRecoveryAnnual');
            if (recoveryAnnEl) recoveryAnnEl.innerText = `+$${Number(winnerProvData.rightsized_annual_savings_usd).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /yr ROI`;

            // Backward Compatibility with legacy pods
            const legacySku = document.getElementById('calcSku');
            if (legacySku) legacySku.innerText = winnerProvData.sku_name || 'm6i.4xlarge';
            const legacyMonthly = document.getElementById('calcMonthly');
            if (legacyMonthly) legacyMonthly.innerText = `$${Number(winnerProvData.monthly_cost_usd).toFixed(2)} /mo`;
            const legacyHourly = document.getElementById('calcHourly');
            if (legacyHourly) legacyHourly.innerText = `$${(Number(winnerProvData.monthly_cost_usd) / (hours * 30)).toFixed(4)} /hr`;
            const legacySavings = document.getElementById('calcSavings');
            if (legacySavings) legacySavings.innerText = `$${Number(winnerProvData.rightsized_monthly_savings_usd).toFixed(2)}/mo`;
            const legacyAnnual = document.getElementById('calcAnnualSavings');
            if (legacyAnnual) legacyAnnual.innerText = `+$${Number(winnerProvData.rightsized_annual_savings_usd).toFixed(2)} /yr Projected ROI`;

        } catch (err) {
            console.error('Error in multi-cloud pricing calculator:', err);
        }
    },

    addCurrentToBOM() {
        const arb = this.state.lastArbitrage;
        if (!arb || !arb.arbitrage_summary) {
            this.showToast('Please execute calculation first', 'warning');
            return;
        }
        const winner = arb.arbitrage_summary.recommended_provider;
        this.addCardToBOM(winner);
    },

    addCardToBOM(provider) {
        const arb = this.state.lastArbitrage;
        if (!arb || !arb.providers || !arb.providers[provider]) {
            this.showToast('Run calculator to generate quote first', 'warning');
            return;
        }
        const pData = arb.providers[provider];
        const spec = arb.workload_spec;

        const specSummary = spec.service_type === 'compute' ? `${spec.vcpu} vCPU / ${spec.ram_gb} GB RAM` :
                            spec.service_type === 'database' ? `${spec.vcpu} vCPU / ${spec.storage_gb} GB Storage` :
                            spec.service_type === 'storage' ? `${spec.storage_gb} GB Storage` :
                            spec.service_type === 'containers' ? `${spec.nodes_count} Nodes (${spec.vcpu} vCPU)` :
                            `${spec.egress_gb} GB Egress`;

        const item = {
            id: 'bom_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6),
            service_type: spec.service_type.toUpperCase(),
            cloud_provider: provider,
            sku_name: pData.sku_name,
            spec_summary: specSummary,
            commitment_model: pData.commitment_model_name,
            monthly_cost_usd: pData.monthly_cost_usd,
            annual_cost_usd: pData.annual_cost_usd
        };

        this.state.calcBOM.push(item);
        this.renderBOMTable();
        this.showToast(`Added ${provider} ${pData.sku_name} to Quote Estimate`, 'success');
    },

    renderBOMTable() {
        const tbody = document.getElementById('bomTableBody');
        const emptyRow = document.getElementById('bomEmptyRow');
        const countEl = document.getElementById('bomItemCount');
        const totalMEl = document.getElementById('bomTotalMonthly');
        const totalAEl = document.getElementById('bomTotalAnnual');

        if (!tbody) return;

        const items = this.state.calcBOM || [];
        if (countEl) countEl.innerText = `${items.length} item${items.length === 1 ? '' : 's'}`;

        if (items.length === 0) {
            tbody.innerHTML = `
                <tr id="bomEmptyRow">
                    <td colspan="7" class="py-6 text-center text-slate-500 font-sans text-xs">
                        No workload line items added yet. Click <strong>"Add to Quote (BOM)"</strong> above to build an architecture quote.
                    </td>
                </tr>
            `;
            if (totalMEl) totalMEl.innerText = '$0.00 /mo';
            if (totalAEl) totalAEl.innerText = '$0.00 /yr';
            return;
        }

        let totalMonthly = 0;
        let totalAnnual = 0;

        tbody.innerHTML = items.map((item, idx) => {
            totalMonthly += item.monthly_cost_usd;
            totalAnnual += item.annual_cost_usd;

            const provBadgeColor = item.cloud_provider === 'AWS' ? 'bg-[#FF9900]/20 text-[#FF9900] border-[#FF9900]/40' :
                                   item.cloud_provider === 'Azure' ? 'bg-[#0284C7]/20 text-[#0284C7] border-[#0284C7]/40' :
                                   'bg-[#10B981]/20 text-[#10B981] border-[#10B981]/40';

            return `
                <tr class="hover:bg-slate-800/40 transition-colors">
                    <td class="py-3 px-4 font-bold text-white flex items-center gap-2">
                        <span class="w-1.5 h-1.5 rounded-full bg-sky-400"></span>
                        <span>${this.escapeHTML(item.service_type)}</span>
                        <span class="text-[10px] text-slate-400 font-normal">(${this.escapeHTML(item.sku_name)})</span>
                    </td>
                    <td class="py-3 px-4">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${provBadgeColor}">
                            ${this.escapeHTML(item.cloud_provider)}
                        </span>
                    </td>
                    <td class="py-3 px-4 text-slate-300">${this.escapeHTML(item.spec_summary)}</td>
                    <td class="py-3 px-4 text-amber-300/90 text-[11px]">${this.escapeHTML(item.commitment_model)}</td>
                    <td class="py-3 px-4 font-bold text-emerald-400">$${item.monthly_cost_usd.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td class="py-3 px-4 font-bold text-sky-400">$${item.annual_cost_usd.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td class="py-3 px-4 text-right">
                        <button type="button" onclick="App.removeFromBOM(${idx})" class="p-1 rounded hover:bg-rose-500/20 text-slate-500 hover:text-rose-400 transition-colors cursor-pointer" title="Remove line item">
                            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        if (totalMEl) totalMEl.innerText = `$${totalMonthly.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;
        if (totalAEl) totalAEl.innerText = `$${totalAnnual.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /yr`;

        if (window.lucide) window.lucide.createIcons({ root: tbody });
    },

    removeFromBOM(index) {
        if (this.state.calcBOM && this.state.calcBOM[index]) {
            const removed = this.state.calcBOM.splice(index, 1)[0];
            this.renderBOMTable();
            this.showToast(`Removed ${removed.cloud_provider} ${removed.sku_name}`, 'info');
        }
    },

    clearBOM() {
        if (!this.state.calcBOM || this.state.calcBOM.length === 0) return;
        this.state.calcBOM = [];
        this.renderBOMTable();
        this.showToast('Architecture BOM Quote cleared', 'info');
    },

    exportBOMQuote() {
        const items = this.state.calcBOM || [];
        if (items.length === 0) {
            this.showToast('BOM Quote Cart is empty. Add services first.', 'warning');
            return;
        }

        const headers = [
            'Line Item ID',
            'Service Category',
            'Cloud Provider',
            'Instance SKU / Resource',
            'Hardware Specification',
            'Pricing Commitment Model',
            'Monthly Cost (USD)',
            'Annual Cost (USD)'
        ];

        const rows = items.map(item => [
            item.id,
            item.service_type,
            item.cloud_provider,
            item.sku_name,
            item.spec_summary,
            item.commitment_model,
            item.monthly_cost_usd.toFixed(2),
            item.annual_cost_usd.toFixed(2)
        ]);

        const totalMonthly = items.reduce((acc, it) => acc + it.monthly_cost_usd, 0);
        const totalAnnual = items.reduce((acc, it) => acc + it.annual_cost_usd, 0);
        rows.push([
            'TOTAL_SUMMARY',
            'ALL_SERVICES',
            'MULTI_CLOUD',
            'TOTAL ARCHITECTURE ESTIMATE',
            `${items.length} Configured Items`,
            'COMBINED ESTIMATE',
            totalMonthly.toFixed(2),
            totalAnnual.toFixed(2)
        ]);

        this.downloadCSV('Abhi_Cloud_Tech_MultiCloud_Pricing_Estimate_BOM.csv', headers, rows);
        this.showToast('Exported Multi-Cloud Pricing Estimate CSV', 'success');
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
    },

    async fetchDatasetStatus() {
        try {
            const res = await this.apiCall('/api/dataset/status');
            if (res && res.source_info) {
                const info = res.source_info;
                const name = info.name || 'SQLite Warehouse';
                const count = info.records ? info.records.toLocaleString() : '32,850';
                const isCustom = res.is_custom_dataset === true;

                const topLabel = document.getElementById('activeSourceLabel');
                const topPill = document.getElementById('activeRecordCountPill');
                if (topLabel) topLabel.innerText = name;
                if (topPill) topPill.innerText = `${count} rows`;

                const ingLabel = document.getElementById('ingestionActiveSourceLabel');
                const ingCount = document.getElementById('ingestionActiveRecordCount');
                if (ingLabel) ingLabel.innerText = name;
                if (ingCount) ingCount.innerText = `${count} FOCUS records`;

                // Update Persistent Revert Buttons & Alert Banner Visibility
                const btnTopReset = document.getElementById('btnTopResetWarehouse');
                const btnSidebarReset = document.getElementById('btnSidebarResetWarehouse');
                const overviewAlert = document.getElementById('overviewCustomDatasetAlert');
                const alertName = document.getElementById('alertDatasetName');
                const alertRows = document.getElementById('alertDatasetRows');
                const scopeLabel = document.getElementById('kpiProvidersScopeLabel');

                if (isCustom) {
                    if (btnTopReset) {
                        btnTopReset.classList.remove('hidden');
                        btnTopReset.classList.add('flex');
                    }
                    if (btnSidebarReset) {
                        btnSidebarReset.classList.remove('hidden');
                        btnSidebarReset.classList.add('flex');
                    }
                    if (overviewAlert) {
                        overviewAlert.classList.remove('hidden');
                        if (alertName) alertName.innerText = name;
                        if (alertRows) alertRows.innerText = `${count} records`;
                    }
                    if (scopeLabel) {
                        const provList = (info.providers && info.providers.length) ? info.providers.join(' + ') : 'Custom Scope';
                        scopeLabel.innerText = `${provList} (Custom Dataset)`;
                        scopeLabel.className = 'text-amber-400 font-bold';
                    }
                } else {
                    if (btnTopReset) {
                        btnTopReset.classList.add('hidden');
                        btnTopReset.classList.remove('flex');
                    }
                    if (btnSidebarReset) {
                        btnSidebarReset.classList.add('hidden');
                        btnSidebarReset.classList.remove('flex');
                    }
                    if (overviewAlert) {
                        overviewAlert.classList.add('hidden');
                    }
                    if (scopeLabel) {
                        scopeLabel.innerText = 'AWS + Azure + GCP (Production Warehouse)';
                        scopeLabel.className = 'text-sky-400 font-semibold';
                    }
                }
            }
        } catch (e) {
            console.warn('[!] Failed to fetch dataset status:', e);
        }
    },

    async revertToWarehouse() {
        try {
            const res = await this.apiCall('/api/dataset/reset', { method: 'POST' });
            this.showToast('Successfully reverted to production warehouse (All 3 Cloud Providers — 32,850 records)', 'success');
            
            // Reset filter state to view all platforms & severities
            this.state.anomalyPlatform = 'ALL';
            this.state.anomalySeverity = 'ALL';
            this.state.anomalyPage = 1;
            
            // Clear result card on ingestion tab if present
            const resCard = document.getElementById('ingestionResultCard');
            if (resCard) resCard.classList.add('hidden');

            await this.loadFilterMetadata();
            await this.refreshDashboard();
        } catch (err) {
            this.showToast(`Reset error: ${err.message}`, 'error');
        }
    },

    initIngestionEvents() {
        // Quick upload button in top header
        const btnQuick = document.getElementById('btnQuickUpload');
        if (btnQuick) {
            btnQuick.addEventListener('click', () => {
                this.switchTab('ingestion');
            });
        }

        // Dropzone & File Input
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('billingFileInput');
        const selectedLabel = document.getElementById('selectedFileLabel');
        const btnUpload = document.getElementById('btnUploadAndPredict');
        let currentFile = null;

        if (dropZone && fileInput) {
            dropZone.addEventListener('click', () => fileInput.click());

            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    dropZone.classList.add('border-cyan-400', 'bg-cyan-950/40');
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    dropZone.classList.remove('border-cyan-400', 'bg-cyan-950/40');
                });
            });

            dropZone.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files && files.length > 0) {
                    handleFileSelect(files[0]);
                }
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files && e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                }
            });
        }

        const handleFileSelect = (file) => {
            currentFile = file;
            if (selectedLabel) {
                selectedLabel.innerHTML = `<span class="text-cyan-300 font-bold">Selected: ${file.name}</span> (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
            }
            if (btnUpload) {
                btnUpload.removeAttribute('disabled');
                btnUpload.classList.remove('opacity-40', 'cursor-not-allowed');
            }
        };

        // Ingest & Run Predictions Button
        if (btnUpload) {
            btnUpload.addEventListener('click', async () => {
                if (!currentFile) return;

                const progressContainer = document.getElementById('uploadProgressContainer');
                const progressBar = document.getElementById('uploadProgressBar');
                const progressPct = document.getElementById('uploadProgressPct');
                const progressText = document.getElementById('uploadProgressText');
                const btnText = document.getElementById('btnUploadText');

                try {
                    btnUpload.disabled = true;
                    if (progressContainer) progressContainer.classList.remove('hidden');
                    if (progressBar) progressBar.style.width = '35%';
                    if (progressPct) progressPct.innerText = '35%';
                    if (progressText) progressText.innerText = 'Uploading billing export & detecting schema...';
                    if (btnText) btnText.innerText = 'Processing Telemetry...';

                    const formData = new FormData();
                    formData.append('file', currentFile);

                    const token = this.state.auth.token;
                    const response = await fetch('/api/dataset/upload', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        },
                        body: formData
                    });

                    if (progressBar) progressBar.style.width = '75%';
                    if (progressPct) progressPct.innerText = '75%';
                    if (progressText) progressText.innerText = 'Running Isolation Forest & HistGradientBoosting models...';

                    const data = await response.json();
                    if (!response.ok) {
                        throw new Error(data.detail || 'Upload failed');
                    }

                    if (progressBar) progressBar.style.width = '100%';
                    if (progressPct) progressPct.innerText = '100%';

                    this.displayIngestionResult(data);
                    this.showToast(`Successfully ingested ${data.records_processed.toLocaleString()} records! (${data.detected_format})`, 'success');

                    // Reload filter options & refresh all active dashboard analytics
                    await this.loadFilterMetadata();
                    await this.refreshDashboard();

                } catch (err) {
                    this.showToast(`Upload error: ${err.message}`, 'error');
                } finally {
                    btnUpload.disabled = false;
                    if (btnText) btnText.innerText = 'Ingest Dataset & Run ML Models';
                    setTimeout(() => {
                        if (progressContainer) progressContainer.classList.add('hidden');
                        if (progressBar) progressBar.style.width = '0%';
                    }, 1200);
                }
            });
        }

        // 1-Click Sample Benchmarks
        document.querySelectorAll('.btn-sample-load').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const provider = btn.getAttribute('data-sample-btn');
                const origText = btn.innerText;
                try {
                    btn.innerText = 'Loading...';
                    btn.disabled = true;

                    const res = await this.apiCall(`/api/dataset/sample/${provider}`, { method: 'POST' });
                    this.displayIngestionResult(res);
                    this.showToast(`Loaded ${res.source_name} successfully!`, 'success');

                    await this.loadFilterMetadata();
                    await this.refreshDashboard();
                } catch (err) {
                    this.showToast(`Failed to load ${provider} sample: ${err.message}`, 'error');
                } finally {
                    btn.innerText = origText;
                    btn.disabled = false;
                }
            });
        });

        // Reset / Revert to Warehouse (All Revert Triggers across Header, Banner, Sidebar, and Ingestion Tab)
        ['btnResetToWarehouse', 'btnTopResetWarehouse', 'btnBannerRevertWarehouse', 'btnSidebarResetWarehouse'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('click', async () => {
                    el.disabled = true;
                    try {
                        await this.revertToWarehouse();
                    } finally {
                        el.disabled = false;
                    }
                });
            }
        });

        // Result Jump buttons
        const btnAnom = document.getElementById('btnJumpToAnomalies');
        if (btnAnom) {
            btnAnom.addEventListener('click', () => this.switchTab('anomalies'));
        }

        const btnFore = document.getElementById('btnJumpToForecast');
        if (btnFore) {
            btnFore.addEventListener('click', () => this.switchTab('forecasting'));
        }

        // Connector tab switching
        document.querySelectorAll('.connector-tab-btn').forEach(tabBtn => {
            tabBtn.addEventListener('click', () => {
                const target = tabBtn.getAttribute('data-connector-tab');
                document.querySelectorAll('.connector-tab-btn').forEach(b => {
                    b.classList.remove('active', 'text-amber-300', 'text-sky-300', 'text-emerald-300', 'bg-amber-500/10', 'bg-sky-500/10', 'bg-emerald-500/10', 'border-amber-500/30', 'border-sky-500/30', 'border-emerald-500/30');
                    b.classList.add('text-slate-400');
                });
                tabBtn.classList.add('active');
                if (target === 'aws') tabBtn.classList.add('text-amber-300', 'bg-amber-500/10', 'border-amber-500/30');
                if (target === 'azure') tabBtn.classList.add('text-sky-300', 'bg-sky-500/10', 'border-sky-500/30');
                if (target === 'gcp') tabBtn.classList.add('text-emerald-300', 'bg-emerald-500/10', 'border-emerald-500/30');

                document.querySelectorAll('.connector-form').forEach(f => f.classList.add('hidden'));
                const form = document.getElementById(`connector-form-${target}`);
                if (form) form.classList.remove('hidden');
            });
        });

        // Save & Test Cloud Connector
        const btnSaveConn = document.getElementById('btnSaveConnector');
        if (btnSaveConn) {
            btnSaveConn.addEventListener('click', async () => {
                const activeTab = document.querySelector('.connector-tab-btn.active');
                const connType = activeTab ? activeTab.getAttribute('data-connector-tab').toUpperCase() : 'AWS';
                try {
                    btnSaveConn.innerText = 'Validating IAM Handshake...';
                    btnSaveConn.disabled = true;

                    await this.apiCall('/api/connectors/cloud', {
                        method: 'POST',
                        body: JSON.stringify({
                            connector_type: connType,
                            config: { status: 'Connected', verified_at: new Date().toISOString() }
                        })
                    });

                    this.showToast(`Cloud Connector for ${connType} verified and scheduled!`, 'success');
                } catch (err) {
                    this.showToast(`Connector error: ${err.message}`, 'error');
                } finally {
                    btnSaveConn.innerText = 'Save & Test Connection';
                    btnSaveConn.disabled = false;
                }
            });
        }
    },

    displayIngestionResult(data) {
        const card = document.getElementById('ingestionResultCard');
        if (!card) return;

        card.classList.remove('hidden');
        const setTxt = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.innerText = val;
        };

        setTxt('resSourceName', data.source_name || 'Uploaded Dataset');
        setTxt('resDetectedFormatBadge', data.detected_format || 'FOCUS 1.0');
        setTxt('resDateRange', data.date_range || 'Active Span');
        setTxt('resRecordsCount', data.records_processed ? data.records_processed.toLocaleString() : '0');
        setTxt('resTotalSpend', `$${(data.total_spend_usd || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`);
        setTxt('resAnomaliesCount', (data.anomalies_detected || 0).toLocaleString());
        setTxt('resWasteUsd', `$${(data.total_waste_usd || 0).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`);
        setTxt('resMapePct', `${data.forecasting_mape_pct ? data.forecasting_mape_pct.toFixed(2) : 0}%`);
        setTxt('resQuantileViolations', data.quantile_crossing_violations || 0);

        // Scroll into view smoothly
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },

    // =========================================================================
    // DEDICATED HYPERSCALER PRICING CALCULATOR (GCP, AWS & AZURE)
    // =========================================================================
    async initCloudCalculator() {
        if (!this.state.calcCatalog) {
            this.state.calcCatalog = HYPERSCALER_CATALOG;
        }

        // Fetch dynamic catalog from backend in background to keep in sync
        try {
            const res = await this.authFetch('/api/calculator/catalog');
            if (res.ok) {
                const dynamicCat = await res.json();
                if (dynamicCat && Object.keys(dynamicCat).length > 0) {
                    this.state.calcCatalog = dynamicCat;
                }
            }
        } catch (e) {
            console.warn('Using built-in hyperscaler catalog:', e);
        }

        // Wire click events on cloud selection buttons
        const cloudMapping = {
            'btnSelectCloudGcp': 'GCP',
            'btnSelectCloudAws': 'AWS',
            'btnSelectCloudAzure': 'Azure'
        };
        Object.keys(cloudMapping).forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn && !btn._hasCalcListener) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.selectCalculatorCloud(cloudMapping[btnId], true);
                });
                btn._hasCalcListener = true;
            }
        });

        // Set default cloud & populate dropdowns immediately
        const activeCloud = this.state.calcCloud || 'GCP';
        this.selectCalculatorCloud(activeCloud, false);

        // Wire change listeners on all calculator inputs
        [
            'calcRegionSelect', 'calcPresetSelect', 'calcCustomVcpu', 'calcCustomRam',
            'calcStorageTypeSelect', 'calcStorageGb', 'calcInstanceCount', 'calcDailyHours',
            'calcCommitmentSelect', 'calcOsSelect', 'calcAhbToggle'
        ].forEach(id => {
            const el = document.getElementById(id);
            if (el && !el._hasCalcListener) {
                el.addEventListener('change', () => this.runCloudCalculator());
                if (id === 'calcCustomVcpu' || id === 'calcCustomRam' || id === 'calcStorageGb') {
                    el.addEventListener('input', () => {
                        const vcpuEl = document.getElementById('customVcpuDisplay');
                        const ramEl = document.getElementById('customRamDisplay');
                        if (vcpuEl && id === 'calcCustomVcpu') vcpuEl.innerText = `${el.value} vCPU`;
                        if (ramEl && id === 'calcCustomRam') ramEl.innerText = `${el.value} GB`;
                        this.runCloudCalculator();
                    });
                }
                el._hasCalcListener = true;
            }
        });

        // Run initial calculation
        this.runCloudCalculator();
    },

    selectCalculatorCloud(cloud, runCalc = true) {
        this.state.calcCloud = cloud;
        if (!this.state.calcCatalog) {
            this.state.calcCatalog = HYPERSCALER_CATALOG;
        }
        const provData = this.state.calcCatalog[cloud] || HYPERSCALER_CATALOG[cloud];
        if (!provData) return;

        // 1. Update Cloud Button Styles with distinctive provider palettes
        const cloudBtns = {
            'GCP': document.getElementById('btnSelectCloudGcp'),
            'AWS': document.getElementById('btnSelectCloudAws'),
            'Azure': document.getElementById('btnSelectCloudAzure')
        };

        const activeClasses = {
            'GCP': ['border-emerald-500', 'bg-emerald-950/60', 'shadow-md', 'shadow-emerald-500/10'],
            'AWS': ['border-amber-500', 'bg-amber-950/60', 'shadow-md', 'shadow-amber-500/10'],
            'Azure': ['border-sky-500', 'bg-sky-950/60', 'shadow-md', 'shadow-sky-500/10']
        };

        const removeClasses = [
            'border-emerald-500', 'bg-emerald-950/60', 'shadow-emerald-500/10',
            'border-amber-500', 'bg-amber-950/60', 'shadow-amber-500/10',
            'border-sky-500', 'bg-sky-950/60', 'shadow-sky-500/10',
            'border-emerald-500/60', 'bg-emerald-950/40', 'shadow-md', 'active'
        ];

        Object.keys(cloudBtns).forEach(k => {
            const btn = cloudBtns[k];
            if (!btn) return;
            btn.classList.remove(...removeClasses);
            if (k === cloud) {
                btn.classList.add(...activeClasses[k]);
                btn.classList.remove('border-slate-800', 'bg-slate-900/60');
            } else {
                btn.classList.add('border-slate-800', 'bg-slate-900/60');
            }
        });

        // 2. Populate Region Dropdown
        const regSelect = document.getElementById('calcRegionSelect');
        if (regSelect && provData.regions) {
            regSelect.innerHTML = Object.keys(provData.regions).map(rk => {
                const r = provData.regions[rk];
                return `<option value="${rk}">${r.name} [${r.multiplier}x]</option>`;
            }).join('');
        }

        // 3. Populate Preset Machine Dropdown
        const presetSelect = document.getElementById('calcPresetSelect');
        if (presetSelect && provData.machine_presets) {
            presetSelect.innerHTML = provData.machine_presets.map(p => {
                return `<option value="${p.sku}">${p.name} — $${p.base_monthly_usd.toFixed(2)}/mo base</option>`;
            }).join('');
            if (provData.machine_presets.length > 4) {
                presetSelect.selectedIndex = 4;
            } else {
                presetSelect.selectedIndex = 0;
            }
            this.updatePresetBadge();
        }

        // 4. Populate Storage Disk Types
        const diskSelect = document.getElementById('calcStorageTypeSelect');
        if (diskSelect && provData.storage_disk_types) {
            diskSelect.innerHTML = Object.keys(provData.storage_disk_types).map(dk => {
                const d = provData.storage_disk_types[dk];
                return `<option value="${dk}">${d.name} — $${d.rate_per_gb_month.toFixed(3)}/GB-mo (${d.note})</option>`;
            }).join('');
        }

        // 5. Populate Commitment Plans
        const comSelect = document.getElementById('calcCommitmentSelect');
        if (comSelect && provData.commitment_discounts) {
            comSelect.innerHTML = Object.keys(provData.commitment_discounts).map(ck => {
                const c = provData.commitment_discounts[ck];
                return `<option value="${ck}">${c.name}</option>`;
            }).join('');
        }

        // 6. Azure Hybrid Benefit Toggle visibility
        const ahbContainer = document.getElementById('azureHybridBenefitContainer');
        if (ahbContainer) {
            if (cloud === 'Azure') {
                ahbContainer.classList.remove('opacity-40', 'pointer-events-none');
            } else {
                ahbContainer.classList.add('opacity-40', 'pointer-events-none');
                const ahbInput = document.getElementById('calcAhbToggle');
                if (ahbInput) ahbInput.checked = false;
            }
        }

        if (runCalc) {
            this.runCloudCalculator();
        }
    },

    setProvisioningMode(mode) {
        this.state.calcMode = mode;
        const btnPreset = document.getElementById('btnModePreset');
        const btnCustom = document.getElementById('btnModeCustom');
        const contPreset = document.getElementById('containerPresetMode');
        const contCustom = document.getElementById('containerCustomMode');

        if (mode === 'preset') {
            if (btnPreset) {
                btnPreset.className = 'py-1.5 px-3 rounded-lg font-bold bg-sky-600 text-white transition-all cursor-pointer';
            }
            if (btnCustom) {
                btnCustom.className = 'py-1.5 px-3 rounded-lg font-semibold text-slate-400 hover:text-white transition-all cursor-pointer';
            }
            if (contPreset) contPreset.classList.remove('hidden');
            if (contCustom) contCustom.classList.add('hidden');
        } else {
            if (btnPreset) {
                btnPreset.className = 'py-1.5 px-3 rounded-lg font-semibold text-slate-400 hover:text-white transition-all cursor-pointer';
            }
            if (btnCustom) {
                btnCustom.className = 'py-1.5 px-3 rounded-lg font-bold bg-indigo-600 text-white transition-all cursor-pointer';
            }
            if (contPreset) contPreset.classList.add('hidden');
            if (contCustom) contCustom.classList.remove('hidden');
        }

        this.runCloudCalculator();
    },

    updatePresetBadge() {
        const select = document.getElementById('calcPresetSelect');
        const badge = document.getElementById('presetSpecsBadge');
        if (!select || !badge || !this.state.calcCatalog) return;
        const cloud = this.state.calcCloud || 'GCP';
        const presets = this.state.calcCatalog[cloud]?.machine_presets || [];
        const match = presets.find(p => p.sku === select.value);
        if (match) {
            badge.innerText = `${match.vcpu} vCPU / ${match.ram_gb} GB RAM`;
        }
    },

    async runCloudCalculator() {
        const cloud = this.state.calcCloud || 'GCP';
        const region = document.getElementById('calcRegionSelect')?.value || 'us-central1';
        const mode = this.state.calcMode || 'preset';
        const sku = document.getElementById('calcPresetSelect')?.value || 'e2-standard-4';
        const customVcpu = parseFloat(document.getElementById('calcCustomVcpu')?.value || 4);
        const customRam = parseFloat(document.getElementById('calcCustomRam')?.value || 16);
        const storageType = document.getElementById('calcStorageTypeSelect')?.value || 'pd-balanced';
        const storageGb = parseFloat(document.getElementById('calcStorageGb')?.value || 100);
        const instances = parseInt(document.getElementById('calcInstanceCount')?.value || 1);
        const hours = parseInt(document.getElementById('calcDailyHours')?.value || 24);
        const commitment = document.getElementById('calcCommitmentSelect')?.value || 'on_demand';
        const os = document.getElementById('calcOsSelect')?.value || 'linux';
        const ahb = !!document.getElementById('calcAhbToggle')?.checked;

        this.updatePresetBadge();

        try {
            const res = await this.authFetch('/api/calculator/estimate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cloud_provider: cloud,
                    region: region,
                    provisioning_mode: mode,
                    machine_sku: sku,
                    custom_vcpu: customVcpu,
                    custom_ram_gb: customRam,
                    storage_type: storageType,
                    storage_gb: storageGb,
                    instance_count: instances,
                    operating_hours_per_day: hours,
                    commitment: commitment,
                    os_type: os,
                    azure_hybrid_benefit: ahb,
                    downsize_pct: 50.0
                })
            });

            if (!res.ok) return;
            const data = await res.json();
            this.state.calcLastEstimate = data;
            const sel = data.selected_cloud;

            // 1. Update Selected Cloud Header Badge
            const badgeEl = document.getElementById('activeCloudBadge');
            if (badgeEl) {
                badgeEl.innerText = sel.provider_key;
                badgeEl.style.color = sel.brand_color;
                badgeEl.style.borderColor = `${sel.brand_color}40`;
                badgeEl.style.backgroundColor = `${sel.brand_color}15`;
            }
            const titleEl = document.getElementById('activeCloudTitle');
            if (titleEl) titleEl.innerText = sel.provider_name;
            const subEl = document.getElementById('activeRegionSubtitle');
            if (subEl) subEl.innerText = `${sel.region_name} &bull; ${sel.commitment_model}`;

            // 2. Primary Spend Display
            const mCostEl = document.getElementById('estMonthlyCost');
            if (mCostEl) mCostEl.innerText = `$${sel.monthly_cost_usd.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /mo`;
            const aCostEl = document.getElementById('estAnnualCost');
            if (aCostEl) aCostEl.innerText = `$${sel.annual_cost_usd.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} /year`;
            const hCostEl = document.getElementById('estHourlyCost');
            if (hCostEl) hCostEl.innerText = `$${sel.hourly_cost_usd.toFixed(4)} /hr`;
            const discEl = document.getElementById('estDiscountSavings');
            if (discEl) {
                if (sel.discount_savings_monthly_usd > 0) {
                    discEl.innerText = `-$${sel.discount_savings_monthly_usd.toFixed(2)}/mo (${sel.commitment_discount_pct}% savings applied)`;
                } else {
                    discEl.innerText = 'On-Demand / Pay-As-You-Go tariff';
                }
            }

            // 3. Itemized Breakdown
            const bMachine = document.getElementById('breakdownMachineName');
            if (bMachine) bMachine.innerText = `${sel.instance_count}x ${sel.machine_name} (${sel.vcpu} vCPU, ${sel.ram_gb} GB RAM)`;
            const bCompute = document.getElementById('breakdownComputeCost');
            if (bCompute) bCompute.innerText = `$${sel.breakdown.compute_monthly_usd.toFixed(2)} /mo`;

            const bDisk = document.getElementById('breakdownDiskName');
            if (bDisk) bDisk.innerText = `${sel.instance_count}x ${sel.storage_type_name} (${sel.storage_gb} GB)`;
            const bStorage = document.getElementById('breakdownStorageCost');
            if (bStorage) bStorage.innerText = `$${sel.breakdown.storage_monthly_usd.toFixed(2)} /mo`;

            const bSav = document.getElementById('breakdownRightsizingSavings');
            if (bSav) bSav.innerText = `-$${sel.rightsized_monthly_savings_usd.toFixed(2)} /mo (+$${sel.rightsized_annual_savings_usd.toFixed(2)} /yr ROI)`;

            // 4. Cross-Cloud 1:1 Parity Comparison List
            const parityList = document.getElementById('crossCloudParityList');
            if (parityList && data.cross_cloud_parity) {
                const winner = data.arbitrage_summary.recommended_provider;
                parityList.innerHTML = Object.keys(data.cross_cloud_parity).map(pk => {
                    const item = data.cross_cloud_parity[pk];
                    const isSelected = pk === sel.provider_key;
                    const isWinner = pk === winner;
                    const borderCls = isWinner ? 'border-emerald-500/60 bg-emerald-950/20' : 'border-slate-800 bg-slate-950/70';

                    return `
                        <div class="p-3 rounded-xl border ${borderCls} flex items-center justify-between text-xs font-mono">
                            <div class="flex items-center gap-2">
                                <span class="w-6 h-6 rounded flex items-center justify-center font-bold text-[10px]" style="background-color: ${item.brand_color}25; color: ${item.brand_color}; border: 1px solid ${item.brand_color}50;">
                                    ${pk}
                                </span>
                                <div>
                                    <div class="text-white font-semibold flex items-center gap-1.5">
                                        <span>${item.provider_name}</span>
                                        ${isWinner ? '<span class="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">LOWEST</span>' : ''}
                                        ${isSelected ? '<span class="text-[9px] px-1.5 py-0.2 rounded bg-sky-500/20 text-sky-300">ACTIVE</span>' : ''}
                                    </div>
                                    <div class="text-[10px] text-slate-400 mt-0.5">${item.equivalent_sku} &bull; ${item.equivalent_disk}</div>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="font-bold text-white">$${item.monthly_cost_usd.toFixed(2)}/mo</div>
                                <div class="text-[10px] ${item.delta_vs_current_usd <= 0 ? 'text-emerald-400' : 'text-slate-400'}">
                                    ${item.delta_vs_current_usd === 0 ? 'Current' : item.delta_vs_current_usd < 0 ? `-$${Math.abs(item.delta_vs_current_usd).toFixed(2)}/mo` : `+$${item.delta_vs_current_usd.toFixed(2)}/mo`}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
            }

            // 5. Arbitrage Recommendation Banner
            const winPill = document.getElementById('arbitrageWinnerPill');
            if (winPill && data.arbitrage_summary) {
                const s = data.arbitrage_summary;
                if (s.recommendation_message) {
                    winPill.innerHTML = s.recommendation_message;
                } else if (s.savings_vs_current_usd > 0) {
                    winPill.innerHTML = `<strong>FinOps Arbitrage Alert:</strong> Migrating this workload to <strong>${s.recommended_provider_name}</strong> saves <strong>$${s.savings_vs_current_usd.toFixed(2)}/month</strong> ($${s.savings_vs_current_annual_usd.toFixed(2)}/year).`;
                } else {
                    winPill.innerHTML = `<strong>Optimal Placement:</strong> <strong>${sel.provider_name}</strong> is currently your lowest-cost provider for this workload configuration.`;
                }
            }

            // 6. Update legacy pods for backwards compatibility with tests
            const legSku = document.getElementById('calcSku');
            if (legSku) legSku.innerText = sel.machine_sku;
            const legHourly = document.getElementById('calcHourly');
            if (legHourly) legHourly.innerText = `$${sel.hourly_cost_usd.toFixed(4)} /hr`;
            const legMonthly = document.getElementById('calcMonthly');
            if (legMonthly) legMonthly.innerText = `$${sel.monthly_cost_usd.toFixed(2)} /mo`;
            const legSavings = document.getElementById('calcSavings');
            if (legSavings) legSavings.innerText = `$${sel.rightsized_monthly_savings_usd.toFixed(2)}/mo`;
            const legAnnual = document.getElementById('calcAnnualSavings');
            if (legAnnual) legAnnual.innerText = `+$${sel.rightsized_annual_savings_usd.toFixed(2)} /yr Projected ROI`;

        } catch (err) {
            console.error('Error running cloud calculator:', err);
        }
    },

    addActiveEstimateToBOM() {
        const est = this.state.calcLastEstimate;
        if (!est || !est.selected_cloud) {
            this.showToast('Please calculate a workload estimate first', 'warning');
            return;
        }
        const s = est.selected_cloud;
        const item = {
            id: 'bom_' + Date.now(),
            cloud_provider: s.provider_key,
            region: s.region_name,
            machine_type: `${s.instance_count}x ${s.machine_sku} (${s.vcpu} vCPU / ${s.ram_gb} GB RAM)`,
            storage: `${s.instance_count}x ${s.storage_type_name} (${s.storage_gb} GB)`,
            commitment: s.commitment_model,
            monthly_cost_usd: s.monthly_cost_usd,
            annual_cost_usd: s.annual_cost_usd
        };

        this.state.calcBOM.push(item);
        this.renderBOMTable();
        this.showToast(`Added ${s.provider_key} ${s.machine_sku} to Architecture Quote`, 'success');
    },

    renderBOMTable() {
        const tbody = document.getElementById('bomTableBody');
        const countEl = document.getElementById('bomItemCount');
        const totalMEl = document.getElementById('bomTotalMonthly');
        const totalAEl = document.getElementById('bomTotalAnnual');
        if (!tbody) return;

        const items = this.state.calcBOM || [];
        if (countEl) countEl.innerText = `${items.length} item${items.length === 1 ? '' : 's'}`;

        if (items.length === 0) {
            tbody.innerHTML = `
                <tr id="bomEmptyRow">
                    <td colspan="8" class="py-6 text-center text-slate-500 font-sans text-xs">
                        No workload line items added yet. Click <strong>"Add to Quote (BOM)"</strong> above to build an architecture quote.
                    </td>
                </tr>
            `;
            if (totalMEl) totalMEl.innerText = '$0.00 /mo';
            if (totalAEl) totalAEl.innerText = '$0.00 /yr';
            return;
        }

        let totalM = 0;
        let totalA = 0;

        tbody.innerHTML = items.map((it, idx) => {
            totalM += it.monthly_cost_usd;
            totalA += it.annual_cost_usd;

            const provBadgeColor = it.cloud_provider === 'AWS' ? 'bg-[#FF9900]/20 text-[#FF9900] border-[#FF9900]/40' :
                                   it.cloud_provider === 'Azure' ? 'bg-[#0284C7]/20 text-[#0284C7] border-[#0284C7]/40' :
                                   'bg-[#10B981]/20 text-[#10B981] border-[#10B981]/40';

            return `
                <tr class="hover:bg-slate-800/40 transition-colors">
                    <td class="py-3 px-4">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${provBadgeColor}">
                            ${this.escapeHTML(it.cloud_provider)}
                        </span>
                    </td>
                    <td class="py-3 px-4 text-slate-300">${this.escapeHTML(it.region)}</td>
                    <td class="py-3 px-4 font-bold text-white">${this.escapeHTML(it.machine_type)}</td>
                    <td class="py-3 px-4 text-slate-300">${this.escapeHTML(it.storage)}</td>
                    <td class="py-3 px-4 text-amber-300/90 text-[11px]">${this.escapeHTML(it.commitment)}</td>
                    <td class="py-3 px-4 font-bold text-emerald-400">$${it.monthly_cost_usd.toFixed(2)}</td>
                    <td class="py-3 px-4 font-bold text-sky-400">$${it.annual_cost_usd.toFixed(2)}</td>
                    <td class="py-3 px-4 text-right">
                        <button type="button" onclick="App.removeFromBOM(${idx})" class="p-1 rounded hover:bg-rose-500/20 text-slate-500 hover:text-rose-400 transition-colors cursor-pointer" title="Remove line item">
                            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        if (totalMEl) totalMEl.innerText = `$${totalM.toFixed(2)} /mo`;
        if (totalAEl) totalAEl.innerText = `$${totalA.toFixed(2)} /yr`;
        if (window.lucide) window.lucide.createIcons({ root: tbody });
    },

    removeFromBOM(idx) {
        if (this.state.calcBOM && this.state.calcBOM[idx]) {
            const removed = this.state.calcBOM.splice(idx, 1)[0];
            this.renderBOMTable();
            this.showToast(`Removed item from Quote`, 'info');
        }
    },

    clearBOM() {
        if (!this.state.calcBOM || this.state.calcBOM.length === 0) return;
        this.state.calcBOM = [];
        this.renderBOMTable();
        this.showToast('Architecture Quote cleared', 'info');
    },

    exportBOMQuote() {
        const items = this.state.calcBOM || [];
        if (items.length === 0) {
            this.showToast('Quote is empty. Add services first.', 'warning');
            return;
        }

        const headers = [
            'Line Item ID', 'Cloud Provider', 'Deployment Region', 'Machine Type & Hardware',
            'Boot Storage', 'Commitment Model', 'Monthly Cost (USD)', 'Annual Cost (USD)'
        ];

        const rows = items.map(it => [
            it.id, it.cloud_provider, it.region, it.machine_type,
            it.storage, it.commitment, it.monthly_cost_usd.toFixed(2), it.annual_cost_usd.toFixed(2)
        ]);

        const totalM = items.reduce((acc, it) => acc + it.monthly_cost_usd, 0);
        const totalA = items.reduce((acc, it) => acc + it.annual_cost_usd, 0);
        rows.push([
            'TOTAL_ESTIMATE', 'ALL_CLOUDS', 'GLOBAL_FLEET', `${items.length} Configured Items`,
            'COMBINED_STORAGE', 'MIXED_COMMITMENTS', totalM.toFixed(2), totalA.toFixed(2)
        ]);

        this.downloadCSV('Abhi_Cloud_Tech_MultiCloud_Architecture_Estimate.csv', headers, rows);
        this.showToast('Exported Multi-Cloud Architecture Quote CSV', 'success');
    },

};

document.addEventListener('DOMContentLoaded', () => App.init());

