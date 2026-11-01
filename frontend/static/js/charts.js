/**
 * Abhi Cloud Tech — ApexCharts Visualization Suite v4.0
 * Distinct Multi-Cloud Executive Palette:
 *   AWS:   #FF9900 (Vibrant Orange)
 *   Azure: #0284C7 (Electric Blue)
 *   GCP:   #10B981 (Emerald Green - High Contrast against Azure)
 */

const CLOUD_COLORS = {
    'AWS': '#FF9900',
    'Azure': '#0284C7',
    'GCP': '#10B981'
};

const Charts = {
    instances: {},

    destroyAll() {
        Object.keys(this.instances).forEach(key => {
            if (this.instances[key]) {
                this.instances[key].destroy();
                delete this.instances[key];
            }
        });
    },

    // 1. Daily Multi-Cloud Spend Chart with Provider-Color-Coded Lines & Anomaly Markers
    renderDailySpend(containerId, trendsData) {
        if (this.instances[containerId]) this.instances[containerId].destroy();

        const dailyByProv = trendsData.daily_by_provider || [];
        const anomalies = trendsData.anomalies_summary || [];

        // Unique sorted dates
        const dates = [...new Set(dailyByProv.map(d => d.Date))].sort();
        const providers = ['AWS', 'Azure', 'GCP'];

        // Build series for each provider
        const series = providers.map(prov => {
            const provMap = {};
            dailyByProv.filter(d => d.CloudProvider === prov).forEach(d => {
                provMap[d.Date] = Math.round(d.DailyCost_USD);
            });
            return {
                name: `${prov} Daily Spend`,
                data: dates.map(dt => provMap[dt] || 0)
            };
        });

        // Top 3 highest severity anomalies with subtle, elegant markers (no dense label clutter)
        const topAnomalies = [...anomalies]
            .sort((a, b) => (b.cost_spike_usd || b.DailyCost_USD || 0) - (a.cost_spike_usd || a.DailyCost_USD || 0))
            .slice(0, 3);

        const anomalyPoints = topAnomalies.map(a => {
            const provColor = CLOUD_COLORS[a.CloudProvider] || '#f43f5e';
            return {
                x: a.Date,
                y: Math.round(a.DailyCost_USD),
                marker: {
                    size: 5,
                    fillColor: provColor,
                    strokeColor: '#030712',
                    strokeWidth: 2,
                    shape: 'circle'
                },
                label: {
                    borderColor: 'rgba(244, 63, 94, 0.4)',
                    offsetY: -6,
                    style: {
                        color: '#f8fafc',
                        background: 'rgba(15, 23, 42, 0.92)',
                        fontSize: '10px',
                        fontFamily: 'JetBrains Mono',
                        fontWeight: 600,
                        padding: { left: 6, right: 6, top: 2, bottom: 2 }
                    },
                    text: `⚠ ${a.CloudProvider} Spike`
                }
            };
        });

        const options = {
            series: series,
            chart: {
                type: 'area',
                height: 350,
                background: 'transparent',
                toolbar: { show: false },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 650
                }
            },
            dataLabels: {
                enabled: false
            },
            colors: [CLOUD_COLORS.AWS, CLOUD_COLORS.Azure, CLOUD_COLORS.GCP],
            fill: {
                type: 'gradient',
                gradient: {
                    shade: 'dark',
                    type: 'vertical',
                    shadeIntensity: 0.4,
                    opacityFrom: 0.35,
                    opacityTo: 0.02,
                    stops: [0, 92, 100]
                }
            },
            stroke: {
                curve: 'smooth',
                width: 2.2
            },
            xaxis: {
                categories: dates,
                labels: {
                    style: { colors: '#94a3b8', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    rotate: -20,
                    hideOverlappingLabels: true
                },
                axisBorder: { show: false },
                axisTicks: { show: false }
            },
            yaxis: {
                labels: {
                    style: { colors: '#94a3b8', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    formatter: val => `$${Math.round(val).toLocaleString()}`
                }
            },
            grid: {
                borderColor: 'rgba(255, 255, 255, 0.04)',
                strokeDashArray: 3,
                xaxis: { lines: { show: false } },
                yaxis: { lines: { show: true } }
            },
            legend: {
                position: 'top',
                labels: { colors: '#94a3b8' },
                fontSize: '12px',
                markers: { radius: 12 }
            },
            annotations: {
                points: anomalyPoints
            },
            tooltip: {
                theme: 'dark',
                shared: true,
                intersect: false,
                custom: function({ series, seriesIndex, dataPointIndex, w }) {
                    const date = w.globals.categoryLabels[dataPointIndex] || dates[dataPointIndex] || '';
                    const awsVal = series[0] && series[0][dataPointIndex] !== undefined ? series[0][dataPointIndex] : 0;
                    const azureVal = series[1] && series[1][dataPointIndex] !== undefined ? series[1][dataPointIndex] : 0;
                    const gcpVal = series[2] && series[2][dataPointIndex] !== undefined ? series[2][dataPointIndex] : 0;
                    const totalVal = (awsVal || 0) + (azureVal || 0) + (gcpVal || 0);

                    const matchedAnom = anomalies.find(a => a.Date === date);

                    let html = `<div class="p-3 bg-slate-900/95 border border-slate-700/80 rounded-xl shadow-2xl backdrop-blur-md min-w-[220px] text-xs font-sans">`;
                    html += `<div class="font-mono text-slate-400 font-semibold mb-2 pb-1.5 border-b border-slate-800/80 flex items-center justify-between">
                                <span class="text-white">${date}</span>
                                <span class="text-[10px] text-sky-400 font-mono tracking-wider">DAILY TOTAL</span>
                             </div>`;
                    
                    html += `<div class="space-y-1.5 mb-2">
                                <div class="flex items-center justify-between gap-4">
                                    <span class="flex items-center gap-1.5 text-slate-300">
                                        <span class="w-2 h-2 rounded-full" style="background:#FF9900"></span>
                                        <span>AWS Spend</span>
                                    </span>
                                    <span class="font-mono font-bold text-white">$${(awsVal || 0).toLocaleString()}</span>
                                </div>
                                <div class="flex items-center justify-between gap-4">
                                    <span class="flex items-center gap-1.5 text-slate-300">
                                        <span class="w-2 h-2 rounded-full" style="background:#0284C7"></span>
                                        <span>Azure Spend</span>
                                    </span>
                                    <span class="font-mono font-bold text-white">$${(azureVal || 0).toLocaleString()}</span>
                                </div>
                                <div class="flex items-center justify-between gap-4">
                                    <span class="flex items-center gap-1.5 text-slate-300">
                                        <span class="w-2 h-2 rounded-full" style="background:#10B981"></span>
                                        <span>GCP Spend</span>
                                    </span>
                                    <span class="font-mono font-bold text-white">$${(gcpVal || 0).toLocaleString()}</span>
                                </div>
                             </div>`;

                    html += `<div class="pt-1.5 border-t border-slate-800/80 flex items-center justify-between font-semibold text-slate-200">
                                <span>Total Expenditure</span>
                                <span class="font-mono font-bold text-sky-400">$${totalVal.toLocaleString()}</span>
                             </div>`;

                    if (matchedAnom) {
                        html += `<div class="mt-2.5 px-2 py-1 rounded-md bg-rose-500/10 border border-rose-500/30 text-rose-300 text-[10px] font-mono flex items-center gap-1.5">
                                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400 animate-pulse"></span>
                                    <span>${matchedAnom.anomaly_severity || 'SPIKE'}: ${matchedAnom.CloudProvider} ${matchedAnom.Service || ''} (+$${Math.round(matchedAnom.cost_spike_usd || 0).toLocaleString()})</span>
                                 </div>`;
                    }

                    html += `</div>`;
                    return html;
                }
            }
        };

        const chart = new ApexCharts(document.getElementById(containerId), options);
        chart.render();
        this.instances[containerId] = chart;
    },

    // 2. Cloud Provider Allocation Donut (AWS: Orange, Azure: Blue, GCP: Green)
    renderProviderDonut(containerId, providerBreakdown) {
        if (this.instances[containerId]) this.instances[containerId].destroy();

        const labels = providerBreakdown.map(p => p.CloudProvider);
        const series = providerBreakdown.map(p => Math.round(p.DailyCost_USD));
        const colors = labels.map(l => CLOUD_COLORS[l] || '#38bdf8');

        const options = {
            series: series,
            labels: labels,
            chart: {
                type: 'donut',
                height: 340,
                background: 'transparent'
            },
            colors: colors,
            stroke: { width: 0 },
            legend: {
                position: 'bottom',
                labels: { colors: '#94a3b8' },
                fontSize: '12px'
            },
            plotOptions: {
                pie: {
                    donut: {
                        size: '72%',
                        labels: {
                            show: true,
                            total: {
                                show: true,
                                label: 'Multi-Cloud Spend',
                                color: '#94a3b8',
                                fontSize: '11px',
                                fontWeight: 700,
                                formatter: w => '$' + w.globals.seriesTotals.reduce((a, b) => a + b, 0).toLocaleString()
                            },
                            value: {
                                color: '#f8fafc',
                                fontSize: '22px',
                                fontWeight: 800,
                                fontFamily: 'JetBrains Mono',
                                formatter: val => '$' + parseInt(val).toLocaleString()
                            }
                        }
                    }
                }
            },
            dataLabels: { enabled: false },
            tooltip: {
                theme: 'dark',
                y: { formatter: val => '$' + val.toLocaleString() }
            }
        };

        const chart = new ApexCharts(document.getElementById(containerId), options);
        chart.render();
        this.instances[containerId] = chart;
    },

    // 3. Department Breakdown Stacked Bar Chart
    renderDepartmentSpend(containerId, departmentSpend) {
        if (this.instances[containerId]) this.instances[containerId].destroy();

        const depts = [...new Set(departmentSpend.map(d => d.Department))];
        const providers = ['AWS', 'Azure', 'GCP'];

        const series = providers.map(prov => {
            return {
                name: prov,
                data: depts.map(dept => {
                    const row = departmentSpend.find(r => r.Department === dept && r.CloudProvider === prov);
                    return row ? Math.round(row.DailyCost_USD) : 0;
                })
            };
        });

        const options = {
            series: series,
            chart: {
                type: 'bar',
                height: 360,
                stacked: true,
                background: 'transparent',
                toolbar: { show: false }
            },
            dataLabels: {
                enabled: false
            },
            colors: [CLOUD_COLORS.AWS, CLOUD_COLORS.Azure, CLOUD_COLORS.GCP],
            plotOptions: {
                bar: {
                    horizontal: false,
                    borderRadius: 6,
                    columnWidth: '45%'
                }
            },
            xaxis: {
                categories: depts,
                labels: {
                    style: { colors: '#94a3b8', fontSize: '11px' },
                    rotate: -20
                },
                axisBorder: { show: false }
            },
            yaxis: {
                labels: {
                    style: { colors: '#64748b', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    formatter: val => '$' + Math.round(val).toLocaleString()
                }
            },
            grid: {
                borderColor: 'rgba(255, 255, 255, 0.05)',
                strokeDashArray: 4
            },
            legend: {
                position: 'top',
                labels: { colors: '#94a3b8' }
            },
            tooltip: {
                theme: 'dark',
                y: { formatter: val => '$' + val.toLocaleString() }
            }
        };

        const chart = new ApexCharts(document.getElementById(containerId), options);
        chart.render();
        this.instances[containerId] = chart;
    },

    // 4. Top Services Horizontal Bar
    renderTopServices(containerId, topServices) {
        if (this.instances[containerId]) this.instances[containerId].destroy();

        const categories = topServices.map(s => s.Service);
        const data = topServices.map(s => Math.round(s.DailyCost_USD));

        const options = {
            series: [{
                name: 'Daily Spend ($)',
                data: data
            }],
            chart: {
                type: 'bar',
                height: 360,
                background: 'transparent',
                toolbar: { show: false }
            },
            dataLabels: {
                enabled: false
            },
            colors: ['#6366f1'],
            plotOptions: {
                bar: {
                    horizontal: true,
                    borderRadius: 6,
                    barHeight: '52%'
                }
            },
            xaxis: {
                categories: categories,
                labels: {
                    style: { colors: '#64748b', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    formatter: val => '$' + Math.round(val).toLocaleString()
                }
            },
            yaxis: {
                labels: {
                    style: { colors: '#94a3b8', fontSize: '11px', fontWeight: 600 }
                }
            },
            grid: {
                borderColor: 'rgba(255, 255, 255, 0.05)',
                strokeDashArray: 4
            },
            tooltip: {
                theme: 'dark',
                y: { formatter: val => '$' + val.toLocaleString() }
            }
        };

        const chart = new ApexCharts(document.getElementById(containerId), options);
        chart.render();
        this.instances[containerId] = chart;
    },

    // 5. Predictive Multi-Horizon Spend Forecast
    renderForecast(containerId, historical, forecast) {
        if (this.instances[containerId]) this.instances[containerId].destroy();

        const allDates = [...historical.map(h => h.Date), ...forecast.map(f => f.Date)];
        const histData = historical.map(h => h.DailyCost_USD);
        const lastHistVal = histData[histData.length - 1];
        
        const forecastData = new Array(historical.length - 1).fill(null);
        forecastData.push(lastHistVal);
        forecast.forEach(f => forecastData.push(f.Forecasted_Spend_USD));

        const upperData = new Array(historical.length - 1).fill(null);
        upperData.push(lastHistVal);
        forecast.forEach(f => upperData.push(f.Upper_Bound_95_USD));

        const lowerData = new Array(historical.length - 1).fill(null);
        lowerData.push(lastHistVal);
        forecast.forEach(f => lowerData.push(f.Lower_Bound_95_USD));

        const options = {
            series: [
                {
                    name: 'Historical Actual Spend',
                    data: histData.concat(new Array(forecast.length).fill(null))
                },
                {
                    name: 'Forecasted Spend Trajectory',
                    data: forecastData
                },
                {
                    name: 'Upper 95% Risk Bound',
                    data: upperData
                },
                {
                    name: 'Lower 95% Bound',
                    data: lowerData
                }
            ],
            chart: {
                type: 'line',
                height: 400,
                background: 'transparent',
                toolbar: { show: false },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 700
                }
            },
            dataLabels: {
                enabled: false
            },
            colors: ['#64748b', '#10b981', '#38bdf8', '#0284c7'],
            stroke: {
                width: [2, 3, 1.8, 1.8],
                curve: 'smooth',
                dashArray: [0, 0, 4, 4]
            },
            xaxis: {
                categories: allDates,
                labels: {
                    style: { colors: '#64748b', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    rotate: -20,
                    hideOverlappingLabels: true
                },
                axisBorder: { show: false }
            },
            yaxis: {
                labels: {
                    style: { colors: '#64748b', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    formatter: val => val ? `$${Math.round(val).toLocaleString()}` : ''
                }
            },
            grid: {
                borderColor: 'rgba(255, 255, 255, 0.05)',
                strokeDashArray: 4
            },
            legend: {
                position: 'top',
                labels: { colors: '#94a3b8' }
            },
            tooltip: {
                theme: 'dark',
                y: {
                    formatter: val => val !== null && val !== undefined ? `$${Math.round(val).toLocaleString()}` : ''
                }
            }
        };

        const chart = new ApexCharts(document.getElementById(containerId), options);
        chart.render();
        this.instances[containerId] = chart;
    },

    // 6. FinOps Optimization Pillars Bar Chart
    renderOptimizationPillars(containerId, portfolio) {
        if (this.instances[containerId]) this.instances[containerId].destroy();

        const categories = [
            'Idle & Zombie Decommissioning',
            'Instance Rightsizing',
            '1-Yr/3-Yr Commitment Plans',
            'Storage Lifecycle Archival'
        ];
        const data = [
            portfolio.Idle_Cleanup_Savings_USD,
            portfolio.Right_Sizing_Savings_USD,
            portfolio.Commitment_Discounts_Savings_USD,
            portfolio.Storage_Optimization_Savings_USD
        ];

        const options = {
            series: [{
                name: 'Identified Annual Savings ($)',
                data: data
            }],
            chart: {
                type: 'bar',
                height: 280,
                background: 'transparent',
                toolbar: { show: false }
            },
            dataLabels: {
                enabled: false
            },
            colors: ['#10b981'],
            plotOptions: {
                bar: {
                    horizontal: true,
                    borderRadius: 6,
                    barHeight: '50%'
                }
            },
            xaxis: {
                categories: categories,
                labels: {
                    style: { colors: '#64748b', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    formatter: val => '$' + Math.round(val).toLocaleString()
                }
            },
            yaxis: {
                labels: { style: { colors: '#94a3b8', fontSize: '11px', fontWeight: 600 } }
            },
            grid: {
                borderColor: 'rgba(255, 255, 255, 0.05)',
                strokeDashArray: 4
            },
            tooltip: {
                theme: 'dark',
                y: { formatter: val => '$' + val.toLocaleString() }
            }
        };

        const chart = new ApexCharts(document.getElementById(containerId), options);
        chart.render();
        this.instances[containerId] = chart;
    },

    // Executive Aliases for Trends Chart compatibility
    initTrendsChart(containerId, trendsData) {
        return this.renderDailySpend(containerId, trendsData);
    },
    renderTrendsChart(containerId, trendsData) {
        return this.renderDailySpend(containerId, trendsData);
    }
};
