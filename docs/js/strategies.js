// Trading Strategies in JavaScript

class BaseStrategy {
    constructor(name, initialCapital = 10000) {
        this.name = name;
        this.initialCapital = initialCapital;
        this.capital = initialCapital;
        this.position = null;
        this.trades = [];
        this.equityCurve = [];
    }

    reset() {
        this.capital = this.initialCapital;
        this.position = null;
        this.trades = [];
        this.equityCurve = [];
    }

    buy(date, price) {
        if (this.position || this.capital < price) return;

        const shares = this.capital / price;
        this.position = {
            entryDate: date,
            entryPrice: price,
            shares: shares
        };
        this.capital = 0;
    }

    sell(date, price, reason = 'Signal') {
        if (!this.position) return;

        const pnl = (price - this.position.entryPrice) * this.position.shares;
        const pnlPercent = ((price - this.position.entryPrice) / this.position.entryPrice) * 100;

        this.capital = this.initialCapital + pnl;

        this.trades.push({
            entryDate: this.position.entryDate,
            entryPrice: this.position.entryPrice,
            exitDate: date,
            exitPrice: price,
            shares: this.position.shares,
            pnl: pnl,
            pnlPercent: pnlPercent,
            exitReason: reason
        });

        this.position = null;
    }

    checkStopLossTakeProfit(date, currentPrice, stopLoss, takeProfit) {
        if (!this.position) return false;

        const pnlPercent = ((currentPrice - this.position.entryPrice) / this.position.entryPrice) * 100;

        if (pnlPercent <= -stopLoss) {
            this.sell(date, currentPrice, 'Stop Loss');
            return true;
        } else if (pnlPercent >= takeProfit) {
            this.sell(date, currentPrice, 'Take Profit');
            return true;
        }

        return false;
    }

    closeEOD(date, price) {
        if (this.position) {
            this.sell(date, price, 'End of Day');
        }
    }
}

class MomentumRSI extends BaseStrategy {
    constructor(initialCapital = 10000, rsiPeriod = 14, oversold = 30, overbought = 70) {
        super('Momentum RSI', initialCapital);
        this.rsiPeriod = rsiPeriod;
        this.oversold = oversold;
        this.overbought = overbought;
    }

    calculateRSI(prices) {
        if (prices.length < this.rsiPeriod + 1) return null;

        const changes = [];
        for (let i = 1; i < prices.length; i++) {
            changes.push(prices[i] - prices[i - 1]);
        }

        const gains = changes.map(c => c > 0 ? c : 0);
        const losses = changes.map(c => c < 0 ? -c : 0);

        const avgGain = gains.slice(-this.rsiPeriod).reduce((a, b) => a + b, 0) / this.rsiPeriod;
        const avgLoss = losses.slice(-this.rsiPeriod).reduce((a, b) => a + b, 0) / this.rsiPeriod;

        if (avgLoss === 0) return 100;

        const rs = avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));

        return rsi;
    }

    generateSignals(data) {
        const signals = [];
        const prices = data.map(d => d.close);

        for (let i = 0; i < data.length; i++) {
            const windowPrices = prices.slice(0, i + 1);
            const rsi = this.calculateRSI(windowPrices);

            let signal = 0;
            if (rsi !== null) {
                if (rsi < this.oversold) signal = 1;  // Buy
                if (rsi > this.overbought) signal = -1; // Sell
            }

            signals.push({ ...data[i], signal, rsi });
        }

        return signals;
    }
}

class MeanReversion extends BaseStrategy {
    constructor(initialCapital = 10000, bbPeriod = 20, bbStd = 2) {
        super('Mean Reversion', initialCapital);
        this.bbPeriod = bbPeriod;
        this.bbStd = bbStd;
    }

    calculateBollingerBands(prices) {
        if (prices.length < this.bbPeriod) return null;

        const recentPrices = prices.slice(-this.bbPeriod);
        const mean = recentPrices.reduce((a, b) => a + b, 0) / this.bbPeriod;
        const variance = recentPrices.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / this.bbPeriod;
        const std = Math.sqrt(variance);

        return {
            upper: mean + (std * this.bbStd),
            middle: mean,
            lower: mean - (std * this.bbStd)
        };
    }

    generateSignals(data) {
        const signals = [];
        const prices = data.map(d => d.close);

        for (let i = 0; i < data.length; i++) {
            const windowPrices = prices.slice(0, i + 1);
            const bb = this.calculateBollingerBands(windowPrices);

            let signal = 0;
            if (bb !== null) {
                if (data[i].close <= bb.lower) signal = 1;  // Buy at lower band
                if (data[i].close >= bb.upper) signal = -1; // Sell at upper band
            }

            signals.push({ ...data[i], signal, bb });
        }

        return signals;
    }
}

class GapTrading extends BaseStrategy {
    constructor(initialCapital = 10000, gapThreshold = 1.0) {
        super('Gap Trading', initialCapital);
        this.gapThreshold = gapThreshold;
    }

    generateSignals(data) {
        const signals = [];

        for (let i = 0; i < data.length; i++) {
            let signal = 0;
            let gapPct = 0;

            if (i > 0) {
                const prevClose = data[i - 1].close;
                gapPct = ((data[i].open - prevClose) / prevClose) * 100;

                if (gapPct > this.gapThreshold) {
                    signal = 1; // Buy on gap up
                }
            }

            signals.push({ ...data[i], signal, gapPct });
        }

        return signals;
    }
}

class MACDCrossover extends BaseStrategy {
    constructor(initialCapital = 10000, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
        super('MACD Crossover', initialCapital);
        this.fastPeriod = fastPeriod;
        this.slowPeriod = slowPeriod;
        this.signalPeriod = signalPeriod;
    }

    calculateEMA(prices, period) {
        if (prices.length < period) return null;

        const k = 2 / (period + 1);
        let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;

        for (let i = period; i < prices.length; i++) {
            ema = (prices[i] * k) + (ema * (1 - k));
        }

        return ema;
    }

    calculateMACD(prices) {
        if (prices.length < this.slowPeriod) return null;

        const fastEMA = this.calculateEMA(prices, this.fastPeriod);
        const slowEMA = this.calculateEMA(prices, this.slowPeriod);

        if (!fastEMA || !slowEMA) return null;

        return fastEMA - slowEMA;
    }

    generateSignals(data) {
        const signals = [];
        const prices = data.map(d => d.close);
        let prevMACD = null;
        let prevSignalLine = null;

        for (let i = 0; i < data.length; i++) {
            const windowPrices = prices.slice(0, i + 1);
            const macd = this.calculateMACD(windowPrices);

            let signal = 0;
            let macdValue = null;
            let signalLine = null;

            if (macd !== null && prevMACD !== null) {
                // Simplified signal line (would need full MACD history for accurate calculation)
                signalLine = macd * 0.9; // Approximation

                // Detect crossover
                if (prevMACD < prevSignalLine && macd > signalLine) {
                    signal = 1; // Bullish crossover
                }
                if (prevMACD > prevSignalLine && macd < signalLine) {
                    signal = -1; // Bearish crossover
                }

                macdValue = macd;
            }

            signals.push({ ...data[i], signal, macd: macdValue, signalLine });
            prevMACD = macd;
            prevSignalLine = signalLine;
        }

        return signals;
    }
}
