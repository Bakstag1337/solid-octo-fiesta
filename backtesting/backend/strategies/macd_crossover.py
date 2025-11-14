"""
MACD Crossover Strategy
Buy when MACD line crosses above signal line, sell when it crosses below
"""
import pandas as pd
import numpy as np

try:
    from .base_strategy import BaseStrategy
except ImportError:
    from base_strategy import BaseStrategy


class MACDCrossover(BaseStrategy):
    """MACD Crossover trading strategy"""

    def __init__(self, initial_capital: float = 10000):
        super().__init__("MACD Crossover", initial_capital)
        self.params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }

    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD indicator"""
        # Calculate EMAs
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # MACD histogram
        macd_histogram = macd_line - signal_line

        return macd_line, signal_line, macd_histogram

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MACD crossover"""
        df = data.copy()

        # Calculate MACD
        fast = self.params.get('fast_period', 12)
        slow = self.params.get('slow_period', 26)
        signal_period = self.params.get('signal_period', 9)

        macd_line, signal_line, macd_histogram = self.calculate_macd(
            df['Close'], fast, slow, signal_period
        )

        df['MACD'] = macd_line
        df['MACD_Signal'] = signal_line
        df['MACD_Histogram'] = macd_histogram

        # Generate signals
        df['signal'] = 0

        # Buy signal: MACD crosses above signal line (histogram goes from negative to positive)
        df['MACD_Cross'] = np.where(
            (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)),
            1, 0
        )

        # Sell signal: MACD crosses below signal line
        df['MACD_Cross_Down'] = np.where(
            (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)),
            -1, 0
        )

        df.loc[df['MACD_Cross'] == 1, 'signal'] = 1
        df.loc[df['MACD_Cross_Down'] == -1, 'signal'] = -1

        return df
