"""
Base strategy class for all trading strategies
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    """Represents a single trade"""
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    shares: float = 0
    pnl: float = 0
    pnl_percent: float = 0
    exit_reason: str = ""

    def close(self, exit_date: datetime, exit_price: float, reason: str = "Signal"):
        """Close the trade"""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_reason = reason
        self.pnl = (exit_price - self.entry_price) * self.shares
        self.pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100


class BaseStrategy:
    """Base class for all trading strategies"""

    def __init__(self, name: str, initial_capital: float = 10000):
        self.name = name
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None  # Current open position
        self.trades: List[Trade] = []
        self.equity_curve = []
        self.params = {}

    def set_params(self, **kwargs):
        """Set strategy parameters"""
        self.params.update(kwargs)

    def reset(self):
        """Reset strategy state"""
        self.capital = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = []

    def can_buy(self, price: float) -> bool:
        """Check if we can buy (no open position and enough capital)"""
        return self.position is None and self.capital >= price

    def buy(self, date: datetime, price: float):
        """Open a long position"""
        if not self.can_buy(price):
            return

        shares = self.capital / price
        self.position = Trade(
            entry_date=date,
            entry_price=price,
            shares=shares
        )
        self.capital = 0  # All capital in position

    def sell(self, date: datetime, price: float, reason: str = "Signal"):
        """Close the position"""
        if self.position is None:
            return

        self.position.close(date, price, reason)
        self.capital = self.initial_capital + self.position.pnl
        self.trades.append(self.position)
        self.position = None

    def check_stop_loss_take_profit(self, date: datetime, current_price: float,
                                     stop_loss_pct: float, take_profit_pct: float) -> bool:
        """
        Check if stop loss or take profit is hit
        Returns True if position was closed
        """
        if self.position is None:
            return False

        pnl_pct = ((current_price - self.position.entry_price) / self.position.entry_price) * 100

        if pnl_pct <= -stop_loss_pct:
            self.sell(date, current_price, "Stop Loss")
            return True
        elif pnl_pct >= take_profit_pct:
            self.sell(date, current_price, "Take Profit")
            return True

        return False

    def close_eod(self, date: datetime, price: float):
        """Close position at end of day (intraday rule)"""
        if self.position is not None:
            self.sell(date, price, "End of Day")

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals
        Must be implemented by child classes
        Returns dataframe with 'signal' column (1=buy, -1=sell, 0=hold)
        """
        raise NotImplementedError("Child class must implement generate_signals()")

    def backtest(self, data: pd.DataFrame, stop_loss: float = 2.0,
                 take_profit: float = 4.0) -> Dict:
        """
        Run backtest on historical data

        Args:
            data: Historical price data
            stop_loss: Stop loss percentage
            take_profit: Take profit percentage

        Returns:
            Dictionary with backtest results
        """
        self.reset()

        # Generate trading signals
        signals = self.generate_signals(data)

        # Track equity for each day
        for i in range(len(signals)):
            row = signals.iloc[i]
            date = row.name
            open_price = row['Open']
            close_price = row['Close']
            high = row['High']
            low = row['Low']
            signal = row.get('signal', 0)

            # Check stop loss / take profit during the day
            if self.position is not None:
                # Simulate intraday check with high/low
                worst_price = low  # Worst case during the day
                if self.check_stop_loss_take_profit(date, worst_price, stop_loss, take_profit):
                    pass  # Position closed by SL/TP

            # Process trading signal at open
            if signal == 1 and self.can_buy(open_price):
                self.buy(date, open_price)
            elif signal == -1 and self.position is not None:
                self.sell(date, open_price, "Sell Signal")

            # Close position at end of day (intraday rule)
            self.close_eod(date, close_price)

            # Record equity
            self.equity_curve.append({
                'date': date,
                'equity': self.capital
            })

        return {
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'final_capital': self.capital
        }
