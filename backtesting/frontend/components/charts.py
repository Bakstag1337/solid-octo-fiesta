"""
Chart components for visualization
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List


def create_equity_curve_comparison(results: Dict[str, Dict]) -> go.Figure:
    """
    Create a comparison chart of equity curves for all strategies

    Args:
        results: Dictionary of strategy results

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    for strategy_name, result in results.items():
        equity_curve = result['equity_curve']

        dates = [e['date'] for e in equity_curve]
        equity = [e['equity'] for e in equity_curve]

        fig.add_trace(go.Scatter(
            x=dates,
            y=equity,
            mode='lines',
            name=strategy_name,
            line=dict(width=2),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x|%Y-%m-%d}<br>' +
                         'Equity: $%{y:,.2f}<br>' +
                         '<extra></extra>'
        ))

    # Add horizontal line for initial capital
    if results:
        first_result = next(iter(results.values()))
        initial_capital = first_result['equity_curve'][0]['equity']

        fig.add_hline(
            y=initial_capital,
            line_dash="dash",
            line_color="gray",
            annotation_text="Initial Capital",
            annotation_position="right"
        )

    fig.update_layout(
        title="Equity Curve Comparison",
        xaxis_title="Date",
        yaxis_title="Equity ($)",
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return fig


def create_single_equity_curve(equity_curve: List[Dict], strategy_name: str) -> go.Figure:
    """
    Create equity curve for a single strategy

    Args:
        equity_curve: List of equity data points
        strategy_name: Name of the strategy

    Returns:
        Plotly figure object
    """
    dates = [e['date'] for e in equity_curve]
    equity = [e['equity'] for e in equity_curve]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=equity,
        mode='lines',
        name=strategy_name,
        line=dict(width=2, color='#1f77b4'),
        fill='tonexty',
        hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                     'Equity: $%{y:,.2f}<br>' +
                     '<extra></extra>'
    ))

    # Add initial capital line
    if equity_curve:
        initial_capital = equity_curve[0]['equity']
        fig.add_hline(
            y=initial_capital,
            line_dash="dash",
            line_color="gray",
            annotation_text="Initial Capital"
        )

    fig.update_layout(
        title=f"Equity Curve - {strategy_name}",
        xaxis_title="Date",
        yaxis_title="Equity ($)",
        template='plotly_white',
        height=400
    )

    return fig


def create_metrics_comparison_bar(comparison_df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Create a bar chart comparing a specific metric across strategies

    Args:
        comparison_df: DataFrame with strategy comparison
        metric: Metric to compare

    Returns:
        Plotly figure object
    """
    fig = go.Figure()

    # Color coding based on metric values
    colors = []
    for value in comparison_df[metric]:
        if metric in ['Total Return (%)', 'Win Rate (%)', 'Sharpe Ratio', 'Profit Factor']:
            # Higher is better
            if value > 5:
                colors.append('green')
            elif value > 0:
                colors.append('orange')
            else:
                colors.append('red')
        elif metric == 'Max Drawdown (%)':
            # Lower is better
            if value < 5:
                colors.append('green')
            elif value < 15:
                colors.append('orange')
            else:
                colors.append('red')
        else:
            colors.append('blue')

    fig.add_trace(go.Bar(
        x=comparison_df['Strategy'],
        y=comparison_df[metric],
        marker_color=colors,
        text=comparison_df[metric],
        texttemplate='%{text:.2f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' +
                     f'{metric}: %{{y:.2f}}<br>' +
                     '<extra></extra>'
    ))

    fig.update_layout(
        title=f"{metric} Comparison",
        xaxis_title="Strategy",
        yaxis_title=metric,
        template='plotly_white',
        height=400,
        showlegend=False
    )

    return fig


def create_metrics_dashboard(comparison_df: pd.DataFrame) -> go.Figure:
    """
    Create a multi-metric comparison dashboard

    Args:
        comparison_df: DataFrame with strategy comparison

    Returns:
        Plotly figure object with subplots
    """
    from plotly.subplots import make_subplots

    metrics_to_plot = [
        'Total Return (%)',
        'Win Rate (%)',
        'Sharpe Ratio',
        'Max Drawdown (%)'
    ]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=metrics_to_plot,
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    for idx, metric in enumerate(metrics_to_plot):
        row = (idx // 2) + 1
        col = (idx % 2) + 1

        fig.add_trace(
            go.Bar(
                x=comparison_df['Strategy'],
                y=comparison_df[metric],
                name=metric,
                showlegend=False,
                marker_color='#1f77b4',
                text=comparison_df[metric],
                texttemplate='%{text:.2f}',
                textposition='outside'
            ),
            row=row, col=col
        )

    fig.update_layout(
        title_text="Strategy Performance Dashboard",
        template='plotly_white',
        height=600,
        showlegend=False
    )

    return fig
