// Parameter Optimizer - Grid Search for best parameters

class ParameterOptimizer {
    constructor(backtester) {
        this.backtester = backtester;
    }

    // Parameter ranges to test
    getParameterRanges() {
        return {
            rsiPeriod: [10, 12, 14, 16, 20],
            rsiOversold: [20, 25, 30, 35, 40],
            rsiOverbought: [60, 65, 70, 75, 80],
            stopLoss: [1, 1.5, 2, 2.5, 3, 4],
            takeProfit: [2, 3, 4, 5, 6, 8],
            bbPeriod: [15, 20, 25, 30],
            bbStd: [1.5, 2, 2.5, 3]
        };
    }

    // Generate all combinations for a specific strategy
    generateCombinations(strategyType) {
        const ranges = this.getParameterRanges();
        const combinations = [];

        switch(strategyType) {
            case 'momentumRSI':
                for (const rsiPeriod of ranges.rsiPeriod) {
                    for (const oversold of ranges.rsiOversold) {
                        for (const overbought of ranges.rsiOverbought) {
                            for (const stopLoss of ranges.stopLoss) {
                                for (const takeProfit of ranges.takeProfit) {
                                    if (oversold < overbought && stopLoss < takeProfit) {
                                        combinations.push({
                                            rsiPeriod,
                                            oversold,
                                            overbought,
                                            stopLoss,
                                            takeProfit
                                        });
                                    }
                                }
                            }
                        }
                    }
                }
                break;

            case 'meanReversion':
                for (const bbPeriod of ranges.bbPeriod) {
                    for (const bbStd of ranges.bbStd) {
                        for (const stopLoss of ranges.stopLoss) {
                            for (const takeProfit of ranges.takeProfit) {
                                if (stopLoss < takeProfit) {
                                    combinations.push({
                                        bbPeriod,
                                        bbStd,
                                        stopLoss,
                                        takeProfit
                                    });
                                }
                            }
                        }
                    }
                }
                break;

            case 'gapTrading':
                for (const stopLoss of ranges.stopLoss) {
                    for (const takeProfit of ranges.takeProfit) {
                        if (stopLoss < takeProfit) {
                            combinations.push({
                                gapThreshold: 1.0,
                                stopLoss,
                                takeProfit
                            });
                        }
                    }
                }
                break;

            case 'macdCrossover':
                for (const stopLoss of ranges.stopLoss) {
                    for (const takeProfit of ranges.takeProfit) {
                        if (stopLoss < takeProfit) {
                            combinations.push({
                                fastPeriod: 12,
                                slowPeriod: 26,
                                signalPeriod: 9,
                                stopLoss,
                                takeProfit
                            });
                        }
                    }
                }
                break;
        }

        return combinations;
    }

    // Test a single parameter combination
    testCombination(strategyType, params, data, initialCapital) {
        let strategy;

        switch(strategyType) {
            case 'momentumRSI':
                strategy = new MomentumRSI(
                    initialCapital,
                    params.rsiPeriod,
                    params.oversold,
                    params.overbought
                );
                break;

            case 'meanReversion':
                strategy = new MeanReversion(
                    initialCapital,
                    params.bbPeriod,
                    params.bbStd
                );
                break;

            case 'gapTrading':
                strategy = new GapTrading(
                    initialCapital,
                    params.gapThreshold
                );
                break;

            case 'macdCrossover':
                strategy = new MACDCrossover(
                    initialCapital,
                    params.fastPeriod,
                    params.slowPeriod,
                    params.signalPeriod
                );
                break;
        }

        const result = this.backtester.runStrategy(
            strategy,
            data,
            params.stopLoss,
            params.takeProfit
        );

        const metrics = this.backtester.calculateMetrics(
            initialCapital,
            result.finalCapital,
            result.trades,
            result.equityCurve
        );

        return {
            params: params,
            metrics: metrics,
            result: result
        };
    }

    // Optimize parameters for a strategy
    async optimizeStrategy(strategyType, data, initialCapital, onProgress) {
        const combinations = this.generateCombinations(strategyType);
        const results = [];

        let tested = 0;
        const total = combinations.length;

        for (const params of combinations) {
            const result = this.testCombination(strategyType, params, data, initialCapital);
            results.push(result);

            tested++;
            if (onProgress && tested % 10 === 0) {
                onProgress(tested, total);
                // Small delay to allow UI updates
                await new Promise(resolve => setTimeout(resolve, 0));
            }
        }

        // Sort by total return (descending)
        results.sort((a, b) => b.metrics.totalReturn - a.metrics.totalReturn);

        return {
            strategyType: strategyType,
            totalCombinations: total,
            topResults: results.slice(0, 10), // Top 10 combinations
            bestResult: results[0]
        };
    }

    // Optimize all selected strategies
    async optimizeAll(strategyTypes, data, initialCapital, onProgress) {
        const optimizationResults = {};

        for (const strategyType of strategyTypes) {
            const strategyName = this.getStrategyName(strategyType);

            if (onProgress) {
                onProgress(strategyName, 0, 0, 'starting');
            }

            const result = await this.optimizeStrategy(
                strategyType,
                data,
                initialCapital,
                (tested, total) => {
                    if (onProgress) {
                        onProgress(strategyName, tested, total, 'testing');
                    }
                }
            );

            optimizationResults[strategyName] = result;

            if (onProgress) {
                onProgress(strategyName, result.totalCombinations, result.totalCombinations, 'complete');
            }
        }

        return optimizationResults;
    }

    getStrategyName(strategyType) {
        const names = {
            'momentumRSI': 'Momentum RSI',
            'meanReversion': 'Mean Reversion',
            'gapTrading': 'Gap Trading',
            'macdCrossover': 'MACD Crossover'
        };
        return names[strategyType] || strategyType;
    }

    // Format parameters for display
    formatParams(strategyType, params) {
        switch(strategyType) {
            case 'momentumRSI':
                return `RSI(${params.rsiPeriod}): ${params.oversold}/${params.overbought}, SL: ${params.stopLoss}%, TP: ${params.takeProfit}%`;

            case 'meanReversion':
                return `BB(${params.bbPeriod}, ${params.bbStd}), SL: ${params.stopLoss}%, TP: ${params.takeProfit}%`;

            case 'gapTrading':
                return `Gap: ${params.gapThreshold}%, SL: ${params.stopLoss}%, TP: ${params.takeProfit}%`;

            case 'macdCrossover':
                return `MACD(${params.fastPeriod},${params.slowPeriod},${params.signalPeriod}), SL: ${params.stopLoss}%, TP: ${params.takeProfit}%`;

            default:
                return JSON.stringify(params);
        }
    }
}
