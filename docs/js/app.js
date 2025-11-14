// Main Application

const app = {
    backtester: new Backtester(),
    chartsManager: new ChartsManager(),
    currentResults: null,

    init() {
        this.bindEvents();
        this.setupDataSourceToggle();
    },

    bindEvents() {
        document.getElementById('runBacktest').addEventListener('click', () => this.runBacktest());
        document.getElementById('strategySelect')?.addEventListener('change', (e) => this.showTrades(e.target.value));
        document.getElementById('downloadCsv')?.addEventListener('click', () => this.downloadCSV());

        // Data source toggle
        document.querySelectorAll('input[name="dataSource"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.toggleDataSource(e.target.value));
        });
    },

    setupDataSourceToggle() {
        const csvFile = document.getElementById('csvFile');
        const uploadBtn = document.getElementById('uploadBtn');

        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => csvFile.click());
        }

        if (csvFile) {
            csvFile.addEventListener('change', (e) => this.handleCSVUpload(e));
        }
    },

    toggleDataSource(source) {
        const uploadBtn = document.getElementById('uploadBtn');
        if (source === 'csv') {
            uploadBtn.style.display = 'block';
        } else {
            uploadBtn.style.display = 'none';
        }
    },

    handleCSVUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        Papa.parse(file, {
            header: true,
            complete: (results) => {
                // Convert CSV to our data format
                const data = results.data.filter(row => row.date && row.close).map(row => ({
                    date: row.date || row.Date,
                    open: parseFloat(row.open || row.Open),
                    high: parseFloat(row.high || row.High),
                    low: parseFloat(row.low || row.Low),
                    close: parseFloat(row.close || row.Close),
                    volume: parseInt(row.volume || row.Volume || 0)
                }));

                if (data.length > 0) {
                    this.customData = data;
                    alert(`Загружено ${data.length} записей из CSV`);
                } else {
                    alert('Ошибка: CSV файл пустой или неверного формата');
                }
            },
            error: (error) => {
                alert('Ошибка при чтении CSV: ' + error.message);
            }
        });
    },

    getSelectedStrategies() {
        const strategies = [];
        const initialCapital = parseFloat(document.getElementById('initialCapital').value);
        const rsiPeriod = parseInt(document.getElementById('rsiPeriod').value);

        const checkboxes = document.querySelectorAll('input[name="strategy"]:checked');

        checkboxes.forEach(checkbox => {
            switch(checkbox.value) {
                case 'momentumRSI':
                    strategies.push(new MomentumRSI(initialCapital, rsiPeriod, 30, 70));
                    break;
                case 'meanReversion':
                    strategies.push(new MeanReversion(initialCapital));
                    break;
                case 'gapTrading':
                    strategies.push(new GapTrading(initialCapital));
                    break;
                case 'macdCrossover':
                    strategies.push(new MACDCrossover(initialCapital));
                    break;
            }
        });

        return strategies;
    },

    async getData() {
        const dataSource = document.querySelector('input[name="dataSource"]:checked').value;

        if (dataSource === 'csv' && this.customData) {
            return this.customData;
        }

        if (dataSource === 'demo') {
            // Generate mock data
            const period = parseInt(document.getElementById('period').value);
            return this.backtester.generateMockData(period);
        }

        // Fetch real data from Yahoo Finance
        const ticker = document.getElementById('ticker').value.trim().toUpperCase();
        if (!ticker) {
            throw new Error('Введите тикер акции');
        }

        const period = parseInt(document.getElementById('period').value);
        return await this.backtester.fetchRealData(ticker, period);
    },

    async runBacktest() {
        const strategies = this.getSelectedStrategies();

        if (strategies.length === 0) {
            alert('Выберите хотя бы одну стратегию!');
            return;
        }

        // Show loading
        document.getElementById('loading').style.display = 'block';
        document.getElementById('results').style.display = 'none';

        // Small delay for UI update
        await new Promise(resolve => setTimeout(resolve, 100));

        try {
            const data = this.getData();

            const params = {
                initialCapital: parseFloat(document.getElementById('initialCapital').value),
                stopLoss: parseFloat(document.getElementById('stopLoss').value),
                takeProfit: parseFloat(document.getElementById('takeProfit').value)
            };

            // Run backtest
            const results = this.backtester.runBacktest(strategies, data, params);
            this.currentResults = results;

            // Display results
            this.displayResults(results);

        } catch (error) {
            alert('Ошибка при выполнении бэктеста: ' + error.message);
            console.error(error);
        } finally {
            document.getElementById('loading').style.display = 'none';
        }
    },

    displayResults(results) {
        // Show results section
        document.getElementById('results').style.display = 'block';

        // Populate comparison table
        this.populateComparisonTable(results);

        // Create charts
        const comparisonData = this.backtester.getComparisonData();
        this.chartsManager.createEquityChart(results);
        this.chartsManager.createMetricsChart(comparisonData);

        // Populate strategy selector
        this.populateStrategySelector(results);

        // Show best strategy
        this.showBestStrategy();

        // Scroll to results
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    },

    populateComparisonTable(results) {
        const tbody = document.querySelector('#comparisonTable tbody');
        tbody.innerHTML = '';

        for (const [strategyName, result] of Object.entries(results)) {
            const metrics = result.metrics;
            const row = document.createElement('tr');

            const returnClass = metrics.totalReturn >= 0 ? 'positive' : 'negative';
            const profitFactorClass = metrics.profitFactor >= 1 ? 'positive' : 'negative';

            row.innerHTML = `
                <td><strong>${strategyName}</strong></td>
                <td class="${returnClass}">${metrics.totalReturn > 0 ? '+' : ''}${metrics.totalReturn}%</td>
                <td>${metrics.winRate}%</td>
                <td>${metrics.sharpeRatio}</td>
                <td class="negative">${metrics.maxDrawdown}%</td>
                <td class="${profitFactorClass}">${metrics.profitFactor}</td>
                <td>${metrics.totalTrades}</td>
            `;

            tbody.appendChild(row);
        }
    },

    populateStrategySelector(results) {
        const select = document.getElementById('strategySelect');
        select.innerHTML = '';

        for (const strategyName of Object.keys(results)) {
            const option = document.createElement('option');
            option.value = strategyName;
            option.textContent = strategyName;
            select.appendChild(option);
        }

        // Show trades for first strategy
        if (Object.keys(results).length > 0) {
            const firstStrategy = Object.keys(results)[0];
            this.showTrades(firstStrategy);
        }
    },

    showTrades(strategyName) {
        const result = this.currentResults[strategyName];
        if (!result) return;

        const tbody = document.querySelector('#tradesTable tbody');
        tbody.innerHTML = '';

        if (result.trades.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Сделок не было</td></tr>';
            return;
        }

        result.trades.forEach(trade => {
            const row = document.createElement('tr');
            const pnlClass = trade.pnl >= 0 ? 'positive' : 'negative';

            row.innerHTML = `
                <td>${trade.entryDate}</td>
                <td>$${trade.entryPrice.toFixed(2)}</td>
                <td>${trade.exitDate}</td>
                <td>$${trade.exitPrice.toFixed(2)}</td>
                <td class="${pnlClass}">${trade.pnlPercent > 0 ? '+' : ''}${trade.pnlPercent.toFixed(2)}%</td>
                <td class="${pnlClass}">$${trade.pnl.toFixed(2)}</td>
                <td>${trade.exitReason}</td>
            `;

            tbody.appendChild(row);
        });
    },

    showBestStrategy() {
        const best = this.backtester.getBestStrategy();
        if (!best) return;

        const div = document.getElementById('bestStrategy');
        div.innerHTML = `
            🏆 Лучшая стратегия: <strong>${best.strategyName}</strong>
            с доходностью <strong>${best.metrics.totalReturn > 0 ? '+' : ''}${best.metrics.totalReturn}%</strong>
        `;
    },

    downloadCSV() {
        const strategyName = document.getElementById('strategySelect').value;
        const csv = this.backtester.exportToCSV(strategyName);

        if (!csv) return;

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${strategyName.replace(/\s+/g, '_')}_trades.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
