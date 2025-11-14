// Charts Module

class ChartsManager {
    constructor() {
        this.equityChart = null;
        this.metricsChart = null;
    }

    createEquityChart(results) {
        const ctx = document.getElementById('equityChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.equityChart) {
            this.equityChart.destroy();
        }

        const datasets = [];
        const colors = [
            'rgb(31, 119, 180)',
            'rgb(255, 127, 14)',
            'rgb(44, 160, 44)',
            'rgb(214, 39, 40)'
        ];

        let colorIndex = 0;
        for (const [strategyName, result] of Object.entries(results)) {
            const data = result.equityCurve.map(point => ({
                x: point.date,
                y: point.equity
            }));

            datasets.push({
                label: strategyName,
                data: data,
                borderColor: colors[colorIndex % colors.length],
                backgroundColor: colors[colorIndex % colors.length] + '20',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            });

            colorIndex++;
        }

        this.equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'category',
                        title: {
                            display: true,
                            text: 'Дата'
                        },
                        ticks: {
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Капитал ($)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    createMetricsChart(comparisonData) {
        const ctx = document.getElementById('metricsChart');
        if (!ctx) return;

        // Destroy existing chart
        if (this.metricsChart) {
            this.metricsChart.destroy();
        }

        const strategies = comparisonData.map(d => d.strategy);
        const returns = comparisonData.map(d => d.totalReturn);
        const winRates = comparisonData.map(d => d.winRate);
        const sharpeRatios = comparisonData.map(d => d.sharpeRatio * 10); // Scale for visibility

        this.metricsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: strategies,
                datasets: [
                    {
                        label: 'Total Return (%)',
                        data: returns,
                        backgroundColor: 'rgba(31, 119, 180, 0.7)',
                        borderColor: 'rgb(31, 119, 180)',
                        borderWidth: 1
                    },
                    {
                        label: 'Win Rate (%)',
                        data: winRates,
                        backgroundColor: 'rgba(44, 160, 44, 0.7)',
                        borderColor: 'rgb(44, 160, 44)',
                        borderWidth: 1
                    },
                    {
                        label: 'Sharpe Ratio (×10)',
                        data: sharpeRatios,
                        backgroundColor: 'rgba(255, 127, 14, 0.7)',
                        borderColor: 'rgb(255, 127, 14)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (label.includes('Sharpe')) {
                                    label += (context.parsed.y / 10).toFixed(2);
                                } else {
                                    label += context.parsed.y.toFixed(2);
                                    if (!label.includes('Return')) {
                                        label += '%';
                                    }
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Значение'
                        }
                    }
                }
            }
        });
    }

    destroy() {
        if (this.equityChart) {
            this.equityChart.destroy();
            this.equityChart = null;
        }
        if (this.metricsChart) {
            this.metricsChart.destroy();
            this.metricsChart = null;
        }
    }
}
