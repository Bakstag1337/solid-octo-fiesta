// Backtester Engine with Real Data Support

class Backtester {
    constructor() {
        this.data = null;
        this.results = {};
    }

    // Fetch real data - multiple sources with fallback
    async fetchRealData(ticker, days = 90) {
        // Try multiple data sources in order
        const methods = [
            () => this.fetchFromYahooProxy(ticker, days),
            () => this.fetchFromAlphaVantage(ticker, days),
            () => this.fetchFromPolygon(ticker, days)
        ];

        for (const method of methods) {
            try {
                const data = await method();
                if (data && data.length > 0) {
                    console.log(`✅ Data loaded successfully: ${data.length} days`);
                    return data;
                }
            } catch (error) {
                console.warn('Data source failed, trying next...', error.message);
            }
        }

        // If all methods fail
        throw new Error(`Не удалось загрузить данные для ${ticker}. Используйте Demo данные или загрузите CSV.`);
    }

    // Method 1: Yahoo Finance via CORS proxy
    async fetchFromYahooProxy(ticker, days) {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        // Using CORS proxy
        const baseUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}`;
        const params = `?period1=${Math.floor(startDate.getTime()/1000)}&period2=${Math.floor(endDate.getTime()/1000)}&interval=1d`;

        // Try with CORS proxy
        const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(baseUrl + params)}`;

        const response = await fetch(proxyUrl, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Yahoo Finance failed');
        }

        const json = await response.json();
        const result = json.chart.result[0];

        if (!result || !result.timestamp) {
            throw new Error('Invalid data format');
        }

        const timestamps = result.timestamp;
        const quotes = result.indicators.quote[0];

        const data = timestamps.map((timestamp, i) => ({
            date: new Date(timestamp * 1000).toISOString().split('T')[0],
            open: parseFloat(quotes.open[i]?.toFixed(2)) || 0,
            high: parseFloat(quotes.high[i]?.toFixed(2)) || 0,
            low: parseFloat(quotes.low[i]?.toFixed(2)) || 0,
            close: parseFloat(quotes.close[i]?.toFixed(2)) || 0,
            volume: quotes.volume[i] || 0
        })).filter(d => d.close > 0);

        return data;
    }

    // Method 2: Alpha Vantage (free, no key needed for demo)
    async fetchFromAlphaVantage(ticker, days) {
        // Free API key for demo purposes (limited to 5 calls/min)
        const apiKey = 'demo'; // Users can replace with their own key
        const url = `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${ticker}&apikey=${apiKey}&outputsize=compact`;

        const response = await fetch(url);
        if (!response.ok) throw new Error('Alpha Vantage failed');

        const json = await response.json();
        const timeSeries = json['Time Series (Daily)'];

        if (!timeSeries) {
            throw new Error('No data from Alpha Vantage');
        }

        const data = Object.entries(timeSeries)
            .slice(0, days)
            .map(([date, values]) => ({
                date: date,
                open: parseFloat(values['1. open']),
                high: parseFloat(values['2. high']),
                low: parseFloat(values['3. low']),
                close: parseFloat(values['4. close']),
                volume: parseInt(values['5. volume'])
            }))
            .reverse();

        return data;
    }

    // Method 3: Polygon.io (free tier available)
    async fetchFromPolygon(ticker, days) {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        const formatDate = (date) => date.toISOString().split('T')[0];

        // Free API for limited use
        const url = `https://api.polygon.io/v2/aggs/ticker/${ticker}/range/1/day/${formatDate(startDate)}/${formatDate(endDate)}?adjusted=true&sort=asc&limit=500`;

        const response = await fetch(url);
        if (!response.ok) throw new Error('Polygon failed');

        const json = await response.json();

        if (!json.results || json.results.length === 0) {
            throw new Error('No data from Polygon');
        }

        const data = json.results.map(bar => ({
            date: new Date(bar.t).toISOString().split('T')[0],
            open: parseFloat(bar.o.toFixed(2)),
            high: parseFloat(bar.h.toFixed(2)),
            low: parseFloat(bar.l.toFixed(2)),
            close: parseFloat(bar.c.toFixed(2)),
            volume: bar.v
        }));

        return data;
    }

    generateMockData(days = 90) {
        const data = [];
        const startPrice = 150;
        let price = startPrice;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);

        for (let i = 0; i < days; i++) {
            const date = new Date(startDate);
            date.setDate(date.getDate() + i);

            // Generate realistic price movements
            const dailyReturn = (Math.random() - 0.48) * 0.04; // Slight upward bias
            price = price * (1 + dailyReturn);

            const high = price * (1 + Math.abs(Math.random() * 0.02));
            const low = price * (1 - Math.abs(Math.random() * 0.02));
            const open = price * (1 + (Math.random() - 0.5) * 0.01);
            const close = price;
            const volume = Math.floor(Math.random() * 5000000 + 1000000);

            data.push({
                date: date.toISOString().split('T')[0],
                open: parseFloat(open.toFixed(2)),
                high: parseFloat(Math.max(high, open, close).toFixed(2)),
                low: parseFloat(Math.min(low, open, close).toFixed(2)),
                close: parseFloat(close.toFixed(2)),
                volume: volume
            });
        }

        return data;
    }

    runStrategy(strategy, data, stopLoss, takeProfit) {
        strategy.reset();
        const signals = strategy.generateSignals(data);

        for (let i = 0; i < signals.length; i++) {
            const row = signals[i];
            const date = row.date;
            const open = row.open;
            const close = row.close;
            const low = row.low;
            const signal = row.signal || 0;

            // Check stop loss / take profit
            if (strategy.position) {
                strategy.checkStopLossTakeProfit(date, low, stopLoss, takeProfit);
            }

            // Process trading signals
            if (signal === 1 && !strategy.position) {
                strategy.buy(date, open);
            } else if (signal === -1 && strategy.position) {
                strategy.sell(date, open, 'Sell Signal');
            }

            // Close at end of day
            strategy.closeEOD(date, close);

            // Record equity
            strategy.equityCurve.push({
                date: date,
                equity: strategy.capital
            });
        }

        return {
            trades: strategy.trades,
            equityCurve: strategy.equityCurve,
            finalCapital: strategy.capital
        };
    }

    calculateMetrics(initialCapital, finalCapital, trades, equityCurve) {
        const totalReturn = ((finalCapital - initialCapital) / initialCapital) * 100;

        const winningTrades = trades.filter(t => t.pnl > 0);
        const losingTrades = trades.filter(t => t.pnl < 0);
        const winRate = trades.length > 0 ? (winningTrades.length / trades.length) * 100 : 0;

        const totalWins = winningTrades.reduce((sum, t) => sum + t.pnl, 0);
        const totalLosses = Math.abs(losingTrades.reduce((sum, t) => sum + t.pnl, 0));
        const profitFactor = totalLosses > 0 ? totalWins / totalLosses : (totalWins > 0 ? Infinity : 0);

        const avgWin = winningTrades.length > 0
            ? winningTrades.reduce((sum, t) => sum + t.pnlPercent, 0) / winningTrades.length
            : 0;

        const avgLoss = losingTrades.length > 0
            ? losingTrades.reduce((sum, t) => sum + t.pnlPercent, 0) / losingTrades.length
            : 0;

        // Calculate Sharpe Ratio
        let sharpeRatio = 0;
        if (equityCurve.length > 1) {
            const returns = [];
            for (let i = 1; i < equityCurve.length; i++) {
                const dailyReturn = (equityCurve[i].equity - equityCurve[i-1].equity) / equityCurve[i-1].equity;
                returns.push(dailyReturn);
            }

            const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
            const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
            const stdDev = Math.sqrt(variance);

            if (stdDev > 0) {
                sharpeRatio = (avgReturn / stdDev) * Math.sqrt(252); // Annualized
            }
        }

        // Calculate Max Drawdown
        let maxDrawdown = 0;
        let peak = equityCurve[0]?.equity || initialCapital;

        for (const point of equityCurve) {
            if (point.equity > peak) {
                peak = point.equity;
            }
            const drawdown = ((point.equity - peak) / peak) * 100;
            if (drawdown < maxDrawdown) {
                maxDrawdown = drawdown;
            }
        }

        return {
            totalReturn: parseFloat(totalReturn.toFixed(2)),
            winRate: parseFloat(winRate.toFixed(2)),
            sharpeRatio: parseFloat(sharpeRatio.toFixed(2)),
            maxDrawdown: parseFloat(Math.abs(maxDrawdown).toFixed(2)),
            profitFactor: parseFloat(profitFactor.toFixed(2)),
            avgWin: parseFloat(avgWin.toFixed(2)),
            avgLoss: parseFloat(avgLoss.toFixed(2)),
            totalTrades: trades.length,
            winningTrades: winningTrades.length,
            losingTrades: losingTrades.length
        };
    }

    runBacktest(strategies, data, params) {
        this.data = data;
        this.results = {};

        const { initialCapital, stopLoss, takeProfit } = params;

        for (const strategy of strategies) {
            const result = this.runStrategy(strategy, data, stopLoss, takeProfit);
            const metrics = this.calculateMetrics(
                initialCapital,
                result.finalCapital,
                result.trades,
                result.equityCurve
            );

            this.results[strategy.name] = {
                strategyName: strategy.name,
                metrics: metrics,
                trades: result.trades,
                equityCurve: result.equityCurve,
                finalCapital: result.finalCapital
            };
        }

        return this.results;
    }

    getComparisonData() {
        return Object.values(this.results).map(r => ({
            strategy: r.strategyName,
            ...r.metrics
        }));
    }

    getBestStrategy() {
        const strategies = Object.values(this.results);
        if (strategies.length === 0) return null;

        return strategies.reduce((best, current) =>
            current.metrics.totalReturn > best.metrics.totalReturn ? current : best
        );
    }

    exportToCSV(strategyName) {
        const result = this.results[strategyName];
        if (!result) return '';

        const headers = ['Entry Date', 'Entry Price', 'Exit Date', 'Exit Price', 'P&L %', 'P&L $', 'Reason'];
        const rows = result.trades.map(t => [
            t.entryDate,
            t.entryPrice.toFixed(2),
            t.exitDate,
            t.exitPrice.toFixed(2),
            t.pnlPercent.toFixed(2),
            t.pnl.toFixed(2),
            t.exitReason
        ]);

        let csv = headers.join(',') + '\n';
        csv += rows.map(row => row.join(',')).join('\n');

        return csv;
    }
}
