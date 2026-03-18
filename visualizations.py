"""
Enhanced Visualizations for Water Quality Dashboard
Includes gauges, heatmaps, and alert visualizations
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_gauge_chart(value: float, min_val: float, max_val: float, 
                       title: str, unit: str = "", 
                       threshold_low: float = None, threshold_high: float = None) -> go.Figure:
    """
    Create a gauge chart for a single parameter
    
    Args:
        value: Current value
        min_val: Minimum value for gauge
        max_val: Maximum value for gauge
        title: Chart title
        unit: Unit of measurement
        threshold_low: Low threshold (optional)
        threshold_high: High threshold (optional)
    """
    # Determine color based on value
    if threshold_low and threshold_high:
        if value < threshold_low or value > threshold_high:
            color = '#ef4444'  # Modern red
        elif value < threshold_low * 1.1 or value > threshold_high * 0.9:
            color = '#f59e0b'  # Modern amber
        else:
            color = '#86efac'  # Light aesthetic green
    else:
        # Simple color scheme
        range_val = max_val - min_val
        normalized = (value - min_val) / range_val if range_val > 0 else 0.5
        if normalized < 0.2 or normalized > 0.8:
            color = '#ef4444'
        elif normalized < 0.3 or normalized > 0.7:
            color = '#f59e0b'
        else:
            color = '#86efac'
    
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title},
            delta={"reference": (min_val + max_val) / 2},
            gauge={
                "axis": {"range": [min_val, max_val]},
                "bar": {"color": color},
                "bgcolor": "#f3f4f6",  # light grey gauge background
                "steps": [
                    {
                        "range": [
                            min_val,
                            threshold_low if threshold_low else min_val * 1.2,
                        ],
                        "color": "#e5e7eb",
                    },
                    {
                        "range": [
                            threshold_high if threshold_high else max_val * 0.8,
                            max_val,
                        ],
                        "color": "#e5e7eb",
                    },
                ],
                "threshold": {
                    "line": {"color": "#dc2626", "width": 4},
                    "thickness": 0.75,
                    "value": threshold_high if threshold_high else max_val * 0.9,
                },
            },
            number={"suffix": f" {unit}"},
        )
    )

    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a"),
    )
    
    return fig

def create_health_score_gauge(health_score: float) -> go.Figure:
    """Create a gauge chart for overall health score"""
    # Determine color
    if health_score >= 80:
        color = '#86efac'
    elif health_score >= 60:
        color = '#f59e0b'
    else:
        color = '#ef4444'
    
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=health_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Overall Health Score"},
            gauge={
                "axis": {"range": [None, 100]},
                "bar": {"color": color},
                "bgcolor": "#f3f4f6",
                "steps": [
                    {"range": [0, 60], "color": "#fee2e2"},
                    {"range": [60, 80], "color": "#fef3c7"},
                    {"range": [80, 100], "color": "#dcfce7"},
                ],
                "threshold": {
                    "line": {"color": "#dc2626", "width": 4},
                    "thickness": 0.75,
                    "value": 60,
                },
            },
            number={"suffix": " / 100"},
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a"),
    )
    
    return fig

def create_heatmap_chart(df: pd.DataFrame, hours: int = 24) -> go.Figure:
    """
    Create a heatmap showing parameter values over time
    
    Args:
        df: DataFrame with timestamp and sensor columns
        hours: Number of hours to display
    """
    # Filter data
    cutoff = datetime.now() - timedelta(hours=hours)
    df_filtered = df[df['timestamp'] >= cutoff].copy()
    
    if len(df_filtered) == 0:
        # Return empty figure
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Resample to hourly if needed
    df_filtered = df_filtered.set_index('timestamp')
    df_hourly = df_filtered.resample('1H').mean()
    
    # Prepare data for heatmap
    parameters = ['pH', 'Temperature', 'TDS', 'Turbidity']
    z_data = []
    
    for param in parameters:
        if param in df_hourly.columns:
            z_data.append(df_hourly[param].values)
        else:
            z_data.append([0] * len(df_hourly))
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=df_hourly.index.strftime('%H:%M'),
        y=parameters,
        colorscale='RdYlGn',
        showscale=True,
        colorbar=dict(title="Value")
    ))
    
    fig.update_layout(
        title=f"Parameter Heatmap (Last {hours} hours)",
        xaxis_title="Time",
        yaxis_title="Parameter",
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a")
    )
    
    return fig

def create_alert_timeline(alerts: list) -> go.Figure:
    """
    Create a timeline visualization of alerts
    
    Args:
        alerts: List of alert dictionaries
    """
    if not alerts:
        fig = go.Figure()
        fig.add_annotation(
            text="No alerts in the selected time period",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Prepare data
    df_alerts = pd.DataFrame(alerts)
    df_alerts['timestamp'] = pd.to_datetime(df_alerts['timestamp'])
    
    # Color mapping
    color_map = {
        'critical': '#ef4444',
        'warning': '#f59e0b',
        'anomaly': '#8b5cf6'
    }
    
    fig = go.Figure()
    
    for severity in ['critical', 'warning', 'anomaly']:
        df_severity = df_alerts[df_alerts['severity'] == severity]
        if len(df_severity) > 0:
            fig.add_trace(go.Scatter(
                x=df_severity['timestamp'],
                y=[severity] * len(df_severity),
                mode='markers',
                name=severity.capitalize(),
                marker=dict(
                    size=15,
                    color=color_map.get(severity, 'gray'),
                    symbol='diamond' if severity == 'critical' else 'circle'
                ),
                text=df_severity['message'],
                hovertemplate='<b>%{text}</b><br>Time: %{x}<extra></extra>'
            ))
    
    fig.update_layout(
        title="Alert Timeline",
        xaxis_title="Time",
        yaxis_title="Alert Type",
        height=200,
        hovermode='closest',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a")
    )
    
    return fig

def create_correlation_matrix(df: pd.DataFrame) -> go.Figure:
    """Create a correlation matrix heatmap"""
    # Select numeric columns
    numeric_cols = ['pH', 'Temperature', 'TDS', 'Turbidity']
    df_numeric = df[numeric_cols].dropna()
    
    if len(df_numeric) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough data for correlation",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Calculate correlation
    corr_matrix = df_numeric.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 12},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Parameter Correlation Matrix",
        height=400,
        xaxis_title="",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a")
    )
    
    return fig

def create_parameter_distribution(df: pd.DataFrame) -> go.Figure:
    """Create distribution plots for all parameters"""
    parameters = ['pH', 'Temperature', 'TDS', 'Turbidity']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=parameters,
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    colors = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444']
    
    for idx, param in enumerate(parameters):
        if param in df.columns:
            row = (idx // 2) + 1
            col = (idx % 2) + 1
            
            fig.add_trace(
                go.Histogram(
                    x=df[param].dropna(),
                    nbinsx=20,
                    name=param,
                    marker_color=colors[idx],
                    showlegend=False
                ),
                row=row, col=col
            )
    
    fig.update_layout(
        title_text="Parameter Value Distributions",
        height=500,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#0f172a")
    )
    
    return fig
