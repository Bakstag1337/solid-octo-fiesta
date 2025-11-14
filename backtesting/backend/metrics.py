"""
Performance metrics calculator for backtesting results
"""
import pandas as pd
import numpy as np
from typing import List, Dict

try:
    from .strategies.base_strategy import Trade
except ImportError:
    from strategies.base_strategy import Trade


class MetricsCalculator:
    """Calculate performance metrics for trading strategies"""

    @staticmethod
    def calculate_total_return(initial_capital: float, final_capital: float) -> float:
        """Calculate total return percentage"""
        return ((final_capital - initial_capital) / initial_capital) * 100

    @staticmethod
    def calculate_win_rate(trades: List[Trade]) -> float:
        """Calculate win rate (percentage of profitable trades)"""
        if not trades:
            return 0.0

        winning_trades = sum(1 for trade in trades if trade.pnl > 0)
        return (winning_trades / len(trades)) * 100

    @staticmethod
    def calculate_sharpe_ratio(equity_curve: List[Dict], risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe Ratio
        Annualized Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns * sqrt(252)
        """
        if len(equity_curve) < 2:
            return 0.0

        # Extract equity values
        equity_values = [e['equity'] for e in equity_curve]

        # Calculate daily returns
        returns = pd.Series(equity_values).pct_change().dropna()

        if returns.std() == 0:
            return 0.0

        # Annualize (assuming 252 trading days)
        sharpe = (returns.mean() - risk_free_rate) / returns.std() * np.sqrt(252)

        return sharpe

    @staticmethod
    def calculate_max_drawdown(equity_curve: List[Dict]) -> float:
        """Calculate maximum drawdown percentage"""
        if not equity_curve:
            return 0.0

        equity_values = [e['equity'] for e in equity_curve]
        equity_series = pd.Series(equity_values)

        # Calculate running maximum
        running_max = equity_series.expanding().max()

        # Calculate drawdown
        drawdown = (equity_series - running_max) / running_max * 100

        return abs(drawdown.min())

    @staticmethod
    def calculate_profit_factor(trades: List[Trade]) -> float:
        """
        Calculate profit factor (total wins / total losses)
        """
        if not trades:
            return 0.0

        total_wins = sum(trade.pnl for trade in trades if trade.pnl > 0)
        total_losses = abs(sum(trade.pnl for trade in trades if trade.pnl < 0))

        if total_losses == 0:
            return float('inf') if total_wins > 0 else 0.0

        return total_wins / total_losses

    @staticmethod
    def calculate_avg_win(trades: List[Trade]) -> float:
        """Calculate average winning trade percentage"""
        winning_trades = [trade.pnl_percent for trade in trades if trade.pnl > 0]

        if not winning_trades:
            return 0.0

        return sum(winning_trades) / len(winning_trades)

    @staticmethod
    def calculate_avg_loss(trades: List[Trade]) -> float:
        """Calculate average losing trade percentage"""
        losing_trades = [trade.pnl_percent for trade in trades if trade.pnl < 0]

        if not losing_trades:
            return 0.0

        return sum(losing_trades) / len(losing_trades)

    @classmethod
    def calculate_all_metrics(cls, initial_capital: float, final_capital: float,
                             trades: List[Trade], equity_curve: List[Dict]) -> Dict:
        """Calculate all performance metrics"""

        return {
            'Total Return (%)': round(cls.calculate_total_return(initial_capital, final_capital), 2),
            'Win Rate (%)': round(cls.calculate_win_rate(trades), 2),
            'Sharpe Ratio': round(cls.calculate_sharpe_ratio(equity_curve), 2),
            'Max Drawdown (%)': round(cls.calculate_max_drawdown(equity_curve), 2),
            'Profit Factor': round(cls.calculate_profit_factor(trades), 2),
            'Avg Win (%)': round(cls.calculate_avg_win(trades), 2),
            'Avg Loss (%)': round(cls.calculate_avg_loss(trades), 2),
            'Total Trades': len(trades),
            'Winning Trades': sum(1 for t in trades if t.pnl > 0),
            'Losing Trades': sum(1 for t in trades if t.pnl < 0),
        }
