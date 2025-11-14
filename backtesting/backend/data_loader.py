"""
Data loader module for fetching historical stock data
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple


class DataLoader:
    """Loads historical stock data from Yahoo Finance"""

    PERIOD_MAPPING = {
        "1 month": "1mo",
        "3 months": "3mo",
        "6 months": "6mo",
        "1 year": "1y"
    }

    def __init__(self):
        self.data = None
        self.ticker = None

    def load_data(self, ticker: str, period: str) -> Tuple[bool, Optional[pd.DataFrame], Optional[str]]:
        """
        Load historical data for a ticker

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            period: Time period ('1 month', '3 months', '6 months', '1 year')

        Returns:
            Tuple of (success, dataframe, error_message)
        """
        try:
            # Map user-friendly period to yfinance format
            yf_period = self.PERIOD_MAPPING.get(period, "3mo")

            # Download data with 1-minute interval for intraday trading
            # Note: yfinance limits intraday data to last 60 days, so we'll use daily data
            # and simulate intraday with Open/High/Low/Close
            stock = yf.Ticker(ticker)
            df = stock.history(period=yf_period, interval="1d")

            if df.empty:
                return False, None, f"No data available for ticker {ticker}"

            # Validate data
            if len(df) < 20:  # Need minimum data for indicators
                return False, None, f"Insufficient data for {ticker} (only {len(df)} days)"

            # Clean data
            df = df.dropna()

            self.data = df
            self.ticker = ticker

            return True, df, None

        except Exception as e:
            return False, None, f"Error loading data: {str(e)}"

    def get_data(self) -> Optional[pd.DataFrame]:
        """Get the loaded data"""
        return self.data
