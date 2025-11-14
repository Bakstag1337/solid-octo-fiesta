"""
Main backtester engine that coordinates strategies, data, and metrics
"""
import pandas as pd
from typing import List, Dict, Optional, Tuple

try:
    from .data_loader import DataLoader
    from .metrics import MetricsCalculator
    from .strategies import (
        BaseStrategy, MomentumRSI, MeanReversion,
        GapTrading, MACDCrossover
    )
except ImportError:
    from data_loader import DataLoader
    from metrics import MetricsCalculator
    from strategies import (
        BaseStrategy, MomentumRSI, MeanReversion,
        GapTrading, MACDCrossover
    )


class Backtester:
    """Main backtesting engine"""

    AVAILABLE_STRATEGIES = {
        'Momentum RSI': MomentumRSI,
        'Mean Reversion': MeanReversion,
        'Gap Trading': GapTrading,
        'MACD Crossover': MACDCrossover
    }

    def __init__(self):
        self.data_loader = DataLoader()
        self.data = None
        self.results = {}

    def load_data(self, ticker: str, period: str) -> Tuple[bool, Optional[str]]:
        """Load historical data"""
        success, data, error = self.data_loader.load_data(ticker, period)

        if success:
            self.data = data
            return True, None
        else:
            return False, error

    def run_strategy(self, strategy_name: str, params: Dict) -> Optional[Dict]:
        """
        Run a single strategy backtest

        Args:
            strategy_name: Name of strategy to run
            params: Strategy and risk management parameters

        Returns:
            Dictionary with strategy results or None if error
        """
        if self.data is None:
            return None

        if strategy_name not in self.AVAILABLE_STRATEGIES:
            return None

        # Create strategy instance
        strategy_class = self.AVAILABLE_STRATEGIES[strategy_name]
        strategy = strategy_class(initial_capital=params.get('initial_capital', 10000))

        # Set strategy-specific parameters
        if strategy_name == 'Momentum RSI':
            strategy.set_params(
                rsi_period=params.get('rsi_period', 14),
                rsi_oversold=params.get('rsi_buy', 30),
                rsi_overbought=params.get('rsi_sell', 70)
            )

        # Run backtest
        backtest_results = strategy.backtest(
            self.data,
            stop_loss=params.get('stop_loss', 2.0),
            take_profit=params.get('take_profit', 4.0)
        )

        # Calculate metrics
        metrics = MetricsCalculator.calculate_all_metrics(
            initial_capital=strategy.initial_capital,
            final_capital=backtest_results['final_capital'],
            trades=backtest_results['trades'],
            equity_curve=backtest_results['equity_curve']
        )

        return {
            'strategy_name': strategy_name,
            'metrics': metrics,
            'trades': backtest_results['trades'],
            'equity_curve': backtest_results['equity_curve'],
            'final_capital': backtest_results['final_capital']
        }

    def run_multiple_strategies(self, strategy_names: List[str], params: Dict) -> Dict[str, Dict]:
        """
        Run multiple strategies and return results

        Args:
            strategy_names: List of strategy names to run
            params: Common parameters for all strategies

        Returns:
            Dictionary mapping strategy names to their results
        """
        results = {}

        for strategy_name in strategy_names:
            result = self.run_strategy(strategy_name, params)
            if result:
                results[strategy_name] = result

        self.results = results
        return results

    def get_comparison_dataframe(self) -> pd.DataFrame:
        """
        Get a comparison dataframe of all strategy results

        Returns:
            DataFrame with strategies as rows and metrics as columns
        """
        if not self.results:
            return pd.DataFrame()

        comparison_data = []

        for strategy_name, result in self.results.items():
            row = {'Strategy': strategy_name}
            row.update(result['metrics'])
            comparison_data.append(row)

        df = pd.DataFrame(comparison_data)

        # Reorder columns for better presentation
        columns_order = [
            'Strategy',
            'Total Return (%)',
            'Win Rate (%)',
            'Sharpe Ratio',
            'Max Drawdown (%)',
            'Profit Factor',
            'Total Trades',
            'Winning Trades',
            'Losing Trades',
            'Avg Win (%)',
            'Avg Loss (%)'
        ]

        # Only include columns that exist
        columns_order = [col for col in columns_order if col in df.columns]

        return df[columns_order]

    def get_trades_dataframe(self, strategy_name: str) -> pd.DataFrame:
        """
        Get detailed trades dataframe for a specific strategy

        Args:
            strategy_name: Name of the strategy

        Returns:
            DataFrame with trade details
        """
        if strategy_name not in self.results:
            return pd.DataFrame()

        trades = self.results[strategy_name]['trades']

        if not trades:
            return pd.DataFrame()

        trades_data = []
        for trade in trades:
            trades_data.append({
                'Entry Date': trade.entry_date.strftime('%Y-%m-%d'),
                'Entry Price': f'${trade.entry_price:.2f}',
                'Exit Date': trade.exit_date.strftime('%Y-%m-%d') if trade.exit_date else 'Open',
                'Exit Price': f'${trade.exit_price:.2f}' if trade.exit_price else '-',
                'Shares': f'{trade.shares:.2f}',
                'P&L': f'${trade.pnl:.2f}',
                'P&L %': f'{trade.pnl_percent:.2f}%',
                'Exit Reason': trade.exit_reason
            })

        return pd.DataFrame(trades_data)
