"""
Mean Reversion Strategy
Buy when price touches lower Bollinger Band, sell when it touches upper band
"""
import pandas as pd
import numpy as np

try:
    from .base_strategy import BaseStrategy
except ImportError:
    from base_strategy import BaseStrategy


class MeanReversion(BaseStrategy):
    """Mean Reversion trading strategy using Bollinger Bands"""

    def __init__(self, initial_capital: float = 10000):
        super().__init__("Mean Reversion", initial_capital)
        self.params = {
            'bb_period': 20,
            'bb_std': 2
        }

    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        return upper_band, sma, lower_band

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on Bollinger Bands"""
        df = data.copy()

        # Calculate Bollinger Bands
        bb_period = self.params.get('bb_period', 20)
        bb_std = self.params.get('bb_std', 2)

        upper_band, middle_band, lower_band = self.calculate_bollinger_bands(
            df['Close'], bb_period, bb_std
        )

        df['BB_Upper'] = upper_band
        df['BB_Middle'] = middle_band
        df['BB_Lower'] = lower_band

        # Generate signals
        df['signal'] = 0

        # Buy signal: Price touches or goes below lower band
        df.loc[df['Close'] <= df['BB_Lower'], 'signal'] = 1

        # Sell signal: Price touches or goes above upper band
        df.loc[df['Close'] >= df['BB_Upper'], 'signal'] = -1

        return df
