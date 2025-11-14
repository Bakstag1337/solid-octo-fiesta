"""
Streamlit UI for Backtesting Platform
"""
import streamlit as st
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from backtester import Backtester
from components.charts import (
    create_equity_curve_comparison,
    create_single_equity_curve,
    create_metrics_dashboard
)

# Page configuration
st.set_page_config(
    page_title="Daytrading Backtesting Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'backtester' not in st.session_state:
    st.session_state.backtester = Backtester()
if 'results' not in st.session_state:
    st.session_state.results = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Header
st.markdown('<div class="main-header">📈 Daytrading Backtesting Platform</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Input Parameters
with st.sidebar:
    st.header("⚙️ Configuration")

    # Stock selection
    st.subheader("📊 Stock Selection")
    ticker = st.text_input("Ticker Symbol", value="AAPL", help="Enter stock ticker (e.g., AAPL, TSLA, MSFT)")
    period = st.selectbox(
        "Backtest Period",
        options=["1 month", "3 months", "6 months", "1 year"],
        index=1
    )

    st.markdown("---")

    # Strategy selection
    st.subheader("🎯 Strategy Selection")
    strategies = st.multiselect(
        "Select Strategies",
        options=[
            "Momentum RSI",
            "Mean Reversion",
            "Gap Trading",
            "MACD Crossover"
        ],
        default=["Momentum RSI", "Mean Reversion"]
    )

    st.markdown("---")

    # Risk management parameters
    st.subheader("💼 Risk Management")

    col1, col2 = st.columns(2)
    with col1:
        stop_loss = st.number_input("Stop Loss (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
    with col2:
        take_profit = st.number_input("Take Profit (%)", min_value=1.0, max_value=20.0, value=4.0, step=0.5)

    st.markdown("---")

    # Strategy-specific parameters
    st.subheader("📐 Strategy Parameters")

    rsi_period = st.slider("RSI Period", min_value=5, max_value=30, value=14)

    col1, col2 = st.columns(2)
    with col1:
        rsi_buy = st.number_input("RSI Buy Level", min_value=10, max_value=50, value=30)
    with col2:
        rsi_sell = st.number_input("RSI Sell Level", min_value=50, max_value=90, value=70)

    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, max_value=1000000, value=10000, step=1000)

    st.markdown("---")

    # Run button
    run_button = st.button("🚀 Run Backtest", type="primary", use_container_width=True)

# Main content area
if run_button:
    if not strategies:
        st.error("⚠️ Please select at least one strategy")
    else:
        with st.spinner("Loading data and running backtest..."):
            # Load data
            success, error = st.session_state.backtester.load_data(ticker, period)

            if not success:
                st.error(f"❌ {error}")
                st.session_state.data_loaded = False
            else:
                st.session_state.data_loaded = True

                # Prepare parameters
                params = {
                    'initial_capital': initial_capital,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'rsi_period': rsi_period,
                    'rsi_buy': rsi_buy,
                    'rsi_sell': rsi_sell
                }

                # Run backtests
                results = st.session_state.backtester.run_multiple_strategies(strategies, params)
                st.session_state.results = results

                st.success(f"✅ Backtest completed for {ticker} over {period}")

# Display results
if st.session_state.results and st.session_state.data_loaded:
    results = st.session_state.results

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Strategy Details", "📋 Trade History"])

    with tab1:
        st.header("Strategy Comparison")

        # Comparison table
        comparison_df = st.session_state.backtester.get_comparison_dataframe()

        st.subheader("Performance Metrics")
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )

        # Metrics dashboard
        st.subheader("Visual Comparison")
        fig_dashboard = create_metrics_dashboard(comparison_df)
        st.plotly_chart(fig_dashboard, use_container_width=True)

        # Equity curves comparison
        st.subheader("Equity Curves Comparison")
        fig_equity = create_equity_curve_comparison(results)
        st.plotly_chart(fig_equity, use_container_width=True)

        # Best strategy highlight
        best_strategy = comparison_df.loc[comparison_df['Total Return (%)'].idxmax(), 'Strategy']
        best_return = comparison_df.loc[comparison_df['Total Return (%)'].idxmax(), 'Total Return (%)']

        st.success(f"🏆 Best performing strategy: **{best_strategy}** with **{best_return:.2f}%** return")

    with tab2:
        st.header("Individual Strategy Details")

        selected_strategy = st.selectbox(
            "Select Strategy to View",
            options=list(results.keys())
        )

        if selected_strategy:
            result = results[selected_strategy]

            # Display key metrics in columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Return",
                    f"{result['metrics']['Total Return (%)']:.2f}%",
                    delta=f"{result['metrics']['Total Return (%)']:.2f}%"
                )

            with col2:
                st.metric(
                    "Win Rate",
                    f"{result['metrics']['Win Rate (%)']:.2f}%"
                )

            with col3:
                st.metric(
                    "Sharpe Ratio",
                    f"{result['metrics']['Sharpe Ratio']:.2f}"
                )

            with col4:
                st.metric(
                    "Max Drawdown",
                    f"{result['metrics']['Max Drawdown (%)']:.2f}%",
                    delta=f"-{result['metrics']['Max Drawdown (%)']:.2f}%",
                    delta_color="inverse"
                )

            # Additional metrics
            st.subheader("Additional Metrics")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Profit Factor", f"{result['metrics']['Profit Factor']:.2f}")
                st.metric("Total Trades", result['metrics']['Total Trades'])

            with col2:
                st.metric("Winning Trades", result['metrics']['Winning Trades'])
                st.metric("Losing Trades", result['metrics']['Losing Trades'])

            with col3:
                st.metric("Avg Win", f"{result['metrics']['Avg Win (%)']:.2f}%")
                st.metric("Avg Loss", f"{result['metrics']['Avg Loss (%)']:.2f}%")

            # Equity curve
            st.subheader("Equity Curve")
            fig_single = create_single_equity_curve(result['equity_curve'], selected_strategy)
            st.plotly_chart(fig_single, use_container_width=True)

    with tab3:
        st.header("Trade History")

        selected_strategy_trades = st.selectbox(
            "Select Strategy",
            options=list(results.keys()),
            key="trades_strategy"
        )

        if selected_strategy_trades:
            trades_df = st.session_state.backtester.get_trades_dataframe(selected_strategy_trades)

            if trades_df.empty:
                st.info("No trades were executed for this strategy")
            else:
                st.subheader(f"All Trades - {selected_strategy_trades}")
                st.dataframe(
                    trades_df,
                    use_container_width=True,
                    hide_index=True
                )

                # Download button
                csv = trades_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Trade History (CSV)",
                    data=csv,
                    file_name=f"{selected_strategy_trades}_{ticker}_trades.csv",
                    mime="text/csv"
                )

else:
    # Welcome screen
    st.info("👈 Configure your backtest parameters in the sidebar and click 'Run Backtest' to get started!")

    st.markdown("""
    ## 📖 How to Use

    1. **Select a Stock**: Enter a ticker symbol (e.g., AAPL, TSLA, MSFT)
    2. **Choose Period**: Select the backtesting timeframe
    3. **Pick Strategies**: Select one or more strategies to test
    4. **Set Parameters**: Configure risk management and strategy parameters
    5. **Run Backtest**: Click the button to execute the backtest

    ## 🎯 Available Strategies

    - **Momentum RSI**: Buy when RSI is oversold, sell when overbought
    - **Mean Reversion**: Buy at lower Bollinger Band, sell at upper band
    - **Gap Trading**: Trade gap-up openings with 50% fill target
    - **MACD Crossover**: Buy on MACD bullish cross, sell on bearish cross

    ## 📊 Metrics Explained

    - **Total Return**: Percentage gain/loss from initial capital
    - **Win Rate**: Percentage of profitable trades
    - **Sharpe Ratio**: Risk-adjusted return (higher is better)
    - **Max Drawdown**: Largest peak-to-trough decline
    - **Profit Factor**: Ratio of total wins to total losses

    ## ⚠️ Important Notes

    - All strategies use **intraday trading** rules (positions closed by EOD)
    - Initial capital: $10,000 (configurable)
    - Position size: 100% of capital per trade
    - Data source: Yahoo Finance (yfinance)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built for daytrading strategy analysis | Not financial advice</p>
</div>
""", unsafe_allow_html=True)
