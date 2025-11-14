"""
Basic test script for backtesting platform without UI
Tests with mock data instead of yfinance
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from strategies import MomentumRSI, MeanReversion, GapTrading, MACDCrossover
from metrics import MetricsCalculator


def generate_mock_data(days=90):
    """Generate mock stock data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # Generate realistic-looking stock data
    np.random.seed(42)

    # Starting price
    start_price = 150.0

    # Generate price movements
    returns = np.random.normal(0.001, 0.02, days)  # Daily returns
    prices = [start_price]

    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))

    # Create OHLC data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        high = close * (1 + abs(np.random.normal(0, 0.01)))
        low = close * (1 - abs(np.random.normal(0, 0.01)))
        open_price = close * (1 + np.random.normal(0, 0.005))
        volume = np.random.randint(1000000, 10000000)

        data.append({
            'Open': open_price,
            'High': max(high, open_price, close),
            'Low': min(low, open_price, close),
            'Close': close,
            'Volume': volume
        })

    df = pd.DataFrame(data, index=dates)
    return df


def test_strategy(strategy, strategy_name, data):
    """Test a single strategy"""
    print(f"\n{'='*60}")
    print(f"Testing {strategy_name}")
    print(f"{'='*60}")

    # Run backtest
    results = strategy.backtest(data, stop_loss=2.0, take_profit=4.0)

    # Calculate metrics
    metrics = MetricsCalculator.calculate_all_metrics(
        initial_capital=strategy.initial_capital,
        final_capital=results['final_capital'],
        trades=results['trades'],
        equity_curve=results['equity_curve']
    )

    # Print results
    print(f"\nInitial Capital: ${strategy.initial_capital:,.2f}")
    print(f"Final Capital:   ${results['final_capital']:,.2f}")
    print(f"\nPerformance Metrics:")
    print(f"  Total Return:    {metrics['Total Return (%)']:>8.2f}%")
    print(f"  Win Rate:        {metrics['Win Rate (%)']:>8.2f}%")
    print(f"  Sharpe Ratio:    {metrics['Sharpe Ratio']:>8.2f}")
    print(f"  Max Drawdown:    {metrics['Max Drawdown (%)']:>8.2f}%")
    print(f"  Profit Factor:   {metrics['Profit Factor']:>8.2f}")
    print(f"\nTrade Statistics:")
    print(f"  Total Trades:    {metrics['Total Trades']:>8}")
    print(f"  Winning Trades:  {metrics['Winning Trades']:>8}")
    print(f"  Losing Trades:   {metrics['Losing Trades']:>8}")
    print(f"  Avg Win:         {metrics['Avg Win (%)']:>8.2f}%")
    print(f"  Avg Loss:        {metrics['Avg Loss (%)']:>8.2f}%")

    # Print first 5 trades
    if results['trades']:
        print(f"\nFirst 5 Trades:")
        print(f"  {'Date':<12} {'Entry':<10} {'Exit':<10} {'P&L %':<10} {'Reason':<15}")
        print(f"  {'-'*60}")
        for trade in results['trades'][:5]:
            date_str = trade.entry_date.strftime('%Y-%m-%d')
            entry_str = f"${trade.entry_price:.2f}"
            exit_str = f"${trade.exit_price:.2f}" if trade.exit_price else "Open"
            pnl_str = f"{trade.pnl_percent:.2f}%"
            print(f"  {date_str:<12} {entry_str:<10} {exit_str:<10} {pnl_str:<10} {trade.exit_reason:<15}")

    return metrics


def main():
    """Main test function"""
    print("="*60)
    print("Backtesting Platform - Basic Test")
    print("="*60)
    print("\nGenerating mock data (90 days)...")

    # Generate mock data
    data = generate_mock_data(days=90)

    print(f"Data shape: {data.shape}")
    print(f"Date range: {data.index[0].date()} to {data.index[-1].date()}")
    print(f"Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")

    # Initialize strategies
    strategies = {
        "Momentum RSI": MomentumRSI(initial_capital=10000),
        "Mean Reversion": MeanReversion(initial_capital=10000),
        "Gap Trading": GapTrading(initial_capital=10000),
        "MACD Crossover": MACDCrossover(initial_capital=10000)
    }

    # Test all strategies
    all_metrics = {}
    for name, strategy in strategies.items():
        metrics = test_strategy(strategy, name, data)
        all_metrics[name] = metrics

    # Print comparison
    print(f"\n{'='*60}")
    print("Strategy Comparison")
    print(f"{'='*60}")
    print(f"\n{'Strategy':<20} {'Return %':>10} {'Win %':>10} {'Sharpe':>10} {'Trades':>10}")
    print("-" * 60)

    for name, metrics in all_metrics.items():
        print(f"{name:<20} {metrics['Total Return (%)']:>10.2f} "
              f"{metrics['Win Rate (%)']:>10.2f} {metrics['Sharpe Ratio']:>10.2f} "
              f"{metrics['Total Trades']:>10}")

    # Find best strategy
    best_strategy = max(all_metrics.items(), key=lambda x: x[1]['Total Return (%)'])
    print(f"\nBest Strategy: {best_strategy[0]} with {best_strategy[1]['Total Return (%)']:.2f}% return")

    print("\n" + "="*60)
    print("Test completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
