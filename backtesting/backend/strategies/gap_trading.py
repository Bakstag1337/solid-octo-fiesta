"""
Gap Trading Strategy
Buy when stock opens with gap up > 1%, sell when gap fills 50%
"""
import pandas as pd
import numpy as np

try:
    from .base_strategy import BaseStrategy
except ImportError:
    from base_strategy import BaseStrategy


class GapTrading(BaseStrategy):
    """Gap Trading strategy"""

    def __init__(self, initial_capital: float = 10000):
        super().__init__("Gap Trading", initial_capital)
        self.params = {
            'gap_threshold': 1.0,  # Gap threshold in percentage
            'gap_fill_target': 0.5  # Target gap fill (50%)
        }

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on gap analysis"""
        df = data.copy()

        # Calculate gap percentage
        df['Prev_Close'] = df['Close'].shift(1)
        df['Gap_Pct'] = ((df['Open'] - df['Prev_Close']) / df['Prev_Close']) * 100

        # Calculate gap fill target price (50% of gap)
        df['Gap_Fill_Target'] = df['Prev_Close'] + (df['Open'] - df['Prev_Close']) * 0.5

        # Generate signals
        df['signal'] = 0
        gap_threshold = self.params.get('gap_threshold', 1.0)

        # Buy signal: Gap up > threshold
        df.loc[df['Gap_Pct'] > gap_threshold, 'signal'] = 1

        # Sell signal: Price reaches gap fill target (we'll handle this in backtest logic)
        # For simplicity, we'll sell if price goes below gap fill target during the day
        # This will be checked using Low price
        for i in range(1, len(df)):
            if df.iloc[i-1]['signal'] == 1:  # If we bought on previous signal
                if df.iloc[i]['Low'] <= df.iloc[i]['Gap_Fill_Target']:
                    df.iloc[i, df.columns.get_loc('signal')] = -1

        return df

    def backtest(self, data: pd.DataFrame, stop_loss: float = 2.0,
                 take_profit: float = 4.0):
        """
        Custom backtest for gap trading with specific exit rules
        """
        self.reset()
        signals = self.generate_signals(data)

        for i in range(len(signals)):
            row = signals.iloc[i]
            date = row.name
            open_price = row['Open']
            close_price = row['Close']
            low = row['Low']
            signal = row.get('signal', 0)
            gap_fill_target = row.get('Gap_Fill_Target', 0)

            # Buy on gap up
            if signal == 1 and self.can_buy(open_price):
                self.buy(date, open_price)

            # Check if gap fills during the day
            if self.position is not None and gap_fill_target > 0:
                if low <= gap_fill_target:
                    self.sell(date, gap_fill_target, "Gap Fill 50%")

            # Check stop loss / take profit
            if self.position is not None:
                self.check_stop_loss_take_profit(date, low, stop_loss, take_profit)

            # Close at end of day
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
