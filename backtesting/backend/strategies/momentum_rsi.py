"""
Momentum RSI Strategy
Buy when RSI falls below oversold threshold, sell when it rises above overbought threshold
"""
import pandas as pd
import numpy as np

try:
    from .base_strategy import BaseStrategy
except ImportError:
    from base_strategy import BaseStrategy


class MomentumRSI(BaseStrategy):
    """Momentum RSI trading strategy"""

    def __init__(self, initial_capital: float = 10000):
        super().__init__("Momentum RSI", initial_capital)
        self.params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70
        }

    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = data.diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on RSI"""
        df = data.copy()

        # Calculate RSI
        rsi_period = self.params.get('rsi_period', 14)
        rsi_oversold = self.params.get('rsi_oversold', 30)
        rsi_overbought = self.params.get('rsi_overbought', 70)

        df['RSI'] = self.calculate_rsi(df['Close'], rsi_period)

        # Generate signals
        df['signal'] = 0

        # Buy signal: RSI crosses below oversold level
        df.loc[df['RSI'] < rsi_oversold, 'signal'] = 1

        # Sell signal: RSI crosses above overbought level
        df.loc[df['RSI'] > rsi_overbought, 'signal'] = -1

        return df
