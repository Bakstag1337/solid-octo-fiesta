// Main Application

const app = {
    backtester: new Backtester(),
    optimizer: null,
    chartsManager: new ChartsManager(),
    currentResults: null,
    optimizationResults: null,

    init() {
        this.optimizer = new ParameterOptimizer(this.backtester);
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
        const selectedStrategies = document.querySelectorAll('input[name="strategy"]:checked');
        const strategyTypes = Array.from(selectedStrategies).map(cb => cb.value);

        if (strategyTypes.length === 0) {
            alert('Выберите хотя бы одну стратегию!');
            return;
        }

        const optimizeParams = document.getElementById('optimizeParams').checked;

        // Show loading
        document.getElementById('loading').style.display = 'block';
        document.getElementById('results').style.display = 'none';

        // Small delay for UI update
        await new Promise(resolve => setTimeout(resolve, 100));

        try {
            const data = await this.getData();
            const initialCapital = parseFloat(document.getElementById('initialCapital').value);

            if (optimizeParams) {
                // Run optimization
                await this.runOptimization(strategyTypes, data, initialCapital);
            } else {
                // Run regular backtest
                const strategies = this.getSelectedStrategies();
                const params = {
                    initialCapital: initialCapital,
                    stopLoss: parseFloat(document.getElementById('stopLoss').value),
                    takeProfit: parseFloat(document.getElementById('takeProfit').value)
                };

                const results = this.backtester.runBacktest(strategies, data, params);
                this.currentResults = results;
                this.displayResults(results);
            }

        } catch (error) {
            alert('Ошибка при выполнении бэктеста: ' + error.message);
            console.error(error);
        } finally {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('optimizationProgress').style.display = 'none';
        }
    },

    async runOptimization(strategyTypes, data, initialCapital) {
        const loadingText = document.getElementById('loadingText');
        const optimizationProgress = document.getElementById('optimizationProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        loadingText.textContent = 'Оптимизация параметров...';
        optimizationProgress.style.display = 'block';

        const onProgress = (strategyName, tested, total, status) => {
            if (status === 'starting') {
                progressText.textContent = `Оптимизация ${strategyName}...`;
                progressFill.style.width = '0%';
            } else if (status === 'testing') {
                const percent = (tested / total * 100).toFixed(0);
                progressFill.style.width = percent + '%';
                progressText.textContent = `${strategyName}: ${tested} / ${total} комбинаций (${percent}%)`;
            } else if (status === 'complete') {
                progressFill.style.width = '100%';
                progressText.textContent = `${strategyName}: готово!`;
            }
        };

        const optimizationResults = await this.optimizer.optimizeAll(
            strategyTypes,
            data,
            initialCapital,
            onProgress
        );

        this.optimizationResults = optimizationResults;

        // Run backtest with best parameters
        await this.runBacktestWithOptimizedParams(optimizationResults, data, initialCapital);
    },

    async runBacktestWithOptimizedParams(optimizationResults, data, initialCapital) {
        const strategies = [];

        for (const [strategyName, optResult] of Object.entries(optimizationResults)) {
            const strategyType = this.getStrategyTypeFromName(strategyName);
            const bestParams = optResult.bestResult.params;

            let strategy;
            switch(strategyType) {
                case 'momentumRSI':
                    strategy = new MomentumRSI(
                        initialCapital,
                        bestParams.rsiPeriod,
                        bestParams.oversold,
                        bestParams.overbought
                    );
                    break;
                case 'meanReversion':
                    strategy = new MeanReversion(
                        initialCapital,
                        bestParams.bbPeriod,
                        bestParams.bbStd
                    );
                    break;
                case 'gapTrading':
                    strategy = new GapTrading(initialCapital, bestParams.gapThreshold);
                    break;
                case 'macdCrossover':
                    strategy = new MACDCrossover(initialCapital);
                    break;
            }

            if (strategy) {
                strategies.push({
                    strategy: strategy,
                    stopLoss: bestParams.stopLoss,
                    takeProfit: bestParams.takeProfit
                });
            }
        }

        // Run backtest with optimized parameters
        const results = {};
        for (const { strategy, stopLoss, takeProfit } of strategies) {
            const result = this.backtester.runStrategy(strategy, data, stopLoss, takeProfit);
            const metrics = this.backtester.calculateMetrics(
                initialCapital,
                result.finalCapital,
                result.trades,
                result.equityCurve
            );

            results[strategy.name] = {
                strategyName: strategy.name,
                metrics: metrics,
                trades: result.trades,
                equityCurve: result.equityCurve,
                finalCapital: result.finalCapital
            };
        }

        this.currentResults = results;
        this.displayResults(results);
        this.displayOptimizationResults();
    },

    getStrategyTypeFromName(name) {
        const mapping = {
            'Momentum RSI': 'momentumRSI',
            'Mean Reversion': 'meanReversion',
            'Gap Trading': 'gapTrading',
            'MACD Crossover': 'macdCrossover'
        };
        return mapping[name];
    },

    displayOptimizationResults() {
        if (!this.optimizationResults) return;

        const container = document.getElementById('optimizationResults');
        const tablesContainer = document.getElementById('optimizationTables');

        container.style.display = 'block';
        tablesContainer.innerHTML = '';

        for (const [strategyName, optResult] of Object.entries(this.optimizationResults)) {
            const strategyDiv = document.createElement('div');
            strategyDiv.className = 'optimization-strategy';

            const title = document.createElement('h3');
            title.innerHTML = `
                ${strategyName}
                <span class="best-params-badge">Топ-5 комбинаций из ${optResult.totalCombinations}</span>
            `;
            strategyDiv.appendChild(title);

            const table = document.createElement('table');
            table.className = 'optimization-table';

            const strategyType = this.getStrategyTypeFromName(strategyName);

            table.innerHTML = `
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Параметры</th>
                        <th>Return %</th>
                        <th>Win Rate %</th>
                        <th>Sharpe</th>
                        <th>Trades</th>
                    </tr>
                </thead>
                <tbody>
                    ${optResult.topResults.slice(0, 5).map((result, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${this.optimizer.formatParams(strategyType, result.params)}</td>
                            <td class="${result.metrics.totalReturn >= 0 ? 'positive' : 'negative'}">
                                ${result.metrics.totalReturn > 0 ? '+' : ''}${result.metrics.totalReturn}%
                            </td>
                            <td>${result.metrics.winRate}%</td>
                            <td>${result.metrics.sharpeRatio}</td>
                            <td>${result.metrics.totalTrades}</td>
                        </tr>
                    `).join('')}
                </tbody>
            `;

            strategyDiv.appendChild(table);
            tablesContainer.appendChild(strategyDiv);
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
