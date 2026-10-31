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

        // Provider-colored Anomaly Annotations
        const anomalyPoints = anomalies.slice(0, 10).map(a => {
            const provColor = CLOUD_COLORS[a.CloudProvider] || '#f43f5e';
            return {
                x: a.Date,
                y: Math.round(a.DailyCost_USD),
                marker: {
                    size: 7,
                    fillColor: provColor,
                    strokeColor: '#ffffff',
                    strokeWidth: 2.5,
                    shape: 'circle'
                },
                label: {
                    borderColor: provColor,
                    offsetY: -6,
                    style: {
                        color: '#ffffff',
                        background: provColor,
                        fontSize: '9px',
                        fontFamily: 'JetBrains Mono',
                        fontWeight: 700,
                        padding: { left: 5, right: 5, top: 3, bottom: 3 }
                    },
                    text: `${a.CloudProvider} SPIKE`
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
            colors: [CLOUD_COLORS.AWS, CLOUD_COLORS.Azure, CLOUD_COLORS.GCP],
            fill: {
                type: 'gradient',
                gradient: {
                    shade: 'dark',
                    type: 'vertical',
                    shadeIntensity: 0.5,
                    opacityFrom: 0.38,
                    opacityTo: 0.03,
                    stops: [0, 95, 100]
                }
            },
            stroke: {
                curve: 'smooth',
                width: 2.5
            },
            xaxis: {
                categories: dates,
                labels: {
                    style: { colors: '#64748b', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    rotate: -20,
                    hideOverlappingLabels: true
                },
                axisBorder: { show: false },
                axisTicks: { show: false }
            },
            yaxis: {
                labels: {
                    style: { colors: '#64748b', fontSize: '11px', fontFamily: 'JetBrains Mono' },
                    formatter: val => `$${Math.round(val).toLocaleString()}`
                }
            },
            grid: {
                borderColor: 'rgba(255, 255, 255, 0.05)',
                strokeDashArray: 4
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
                y: {
                    formatter: val => `$${Math.round(val).toLocaleString()}`
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
    }
};
