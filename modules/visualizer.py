"""
Visualizer Module
Creates interactive, publication-quality Plotly figures for Streamlit dashboard.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_climate_trend_chart(df_annual: pd.DataFrame) -> go.Figure:
    """
    Dual-axis 10-year climate shift chart:
    Bar chart for Annual Precipitation + Line chart for Mean Temperature with trend line.
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Precipitation bars
    mean_precip = df_annual["Precipitation_mm"].mean()
    bar_colors = ["#2b6cb0" if p >= mean_precip else "#e53e3e" for p in df_annual["Precipitation_mm"]]
    
    fig.add_trace(
        go.Bar(
            x=df_annual["Year"],
            y=df_annual["Precipitation_mm"],
            name="Annual Precipitation (mm)",
            marker_color=bar_colors,
            opacity=0.75,
            hovertemplate="Year %{x}: %{y:.1f} mm<extra></extra>"
        ),
        secondary_y=False
    )
    
    # Temperature line
    fig.add_trace(
        go.Scatter(
            x=df_annual["Year"],
            y=df_annual["Temperature_C"],
            name="Mean Temperature (°C)",
            mode="lines+markers",
            line=dict(color="#ed8936", width=3),
            marker=dict(size=8, color="#dd6b20"),
            hovertemplate="Year %{x}: %{y:.2f} °C<extra></extra>"
        ),
        secondary_y=True
    )
    
    # Linear trend line for temperature
    if len(df_annual) >= 2:
        z = np.polyfit(df_annual["Year"], df_annual["Temperature_C"], 1)
        p = np.poly1d(z)
        fig.add_trace(
            go.Scatter(
                x=df_annual["Year"],
                y=p(df_annual["Year"]),
                name=f"Warming Trend ({z[0]*10:+.2f}°C/decade)",
                mode="lines",
                line=dict(color="#c53030", width=2, dash="dash"),
                hovertemplate="Trend: %{y:.2f} °C<extra></extra>"
            ),
            secondary_y=True
        )

    fig.update_layout(
        title="<b>10-Year Climate Trajectory (NASA POWER Earth Observations)</b>",
        title_font=dict(size=16),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="rgba(240, 244, 248, 0.4)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380
    )
    
    fig.update_xaxes(title_text="Year", dtick=1)
    fig.update_yaxes(title_text="Annual Precipitation (mm)", secondary_y=False, showgrid=True)
    fig.update_yaxes(title_text="Mean Temperature (°C)", secondary_y=True, showgrid=False)
    
    return fig

def create_seasonality_shift_chart(early_dict: dict, recent_dict: dict, early_label: str, recent_label: str) -> go.Figure:
    """
    Compares monthly rainfall distribution between historical baseline and recent years
    to visualize the monsoon shift and extended dry windows.
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    early_vals = [early_dict.get(m, 0.0) for m in range(1, 13)]
    recent_vals = [recent_dict.get(m, 0.0) for m in range(1, 13)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=early_vals,
        mode="lines+markers",
        name=f"Baseline Period ({early_label})",
        line=dict(color="#4299e1", width=2.5, dash="dot"),
        marker=dict(size=7),
        fill="tozeroy",
        fillcolor="rgba(66, 153, 225, 0.15)",
        hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=recent_vals,
        mode="lines+markers",
        name=f"Recent Shift ({recent_label})",
        line=dict(color="#319795", width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(49, 151, 149, 0.25)",
        hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"
    ))
    
    fig.update_layout(
        title="<b>Seasonal Monsoon Distribution Shift (Early vs. Recent Decades)</b>",
        title_font=dict(size=16),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="rgba(240, 244, 248, 0.4)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=350
    )
    
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Average Monthly Rainfall (mm)", showgrid=True)
    return fig

def create_calibration_comparison_chart(df_telemetry: pd.DataFrame) -> go.Figure:
    """
    Compares 30 days of Raw NASA Satellite Grid vs. Ground ESP32 Node vs. Calibrated Output.
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        subplot_titles=("Temperature Downscaling & Bias Correction (°C)", 
                                        "Root-Zone Soil Moisture (% VWC - SMAP vs ESP32)"),
                        vertical_spacing=0.12)
    
    # Top Plot: Temperature
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Satellite_T2M_C"],
                   name="NASA 9km Grid T2M", line=dict(color="#a0aec0", width=2, dash="dash")),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Ground_ESP32_Temp_C"],
                   name="ESP32 Ground Station", line=dict(color="#e53e3e", width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Calibrated_Temp_C"],
                   name="Fused Calibrated Temp", line=dict(color="#38a169", width=3)),
        row=1, col=1
    )
    
    # Bottom Plot: Soil Moisture
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["NASA_SMAP_Moisture_pct"],
                   name="NASA SMAP L3 (Smoothed)", line=dict(color="#805ad5", width=2, dash="dash")),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Ground_ESP32_SoilMoisture_pct"],
                   name="ESP32 Capacitive VWC", line=dict(color="#3182ce", width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Calibrated_SoilMoisture_pct"],
                   name="Fused Calibrated Moisture", line=dict(color="#2b6cb0", width=3)),
        row=2, col=1
    )
    
    fig.update_layout(
        height=520,
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(240, 244, 248, 0.4)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def create_strategy_radar_comparison(strategies: dict) -> go.Figure:
    """
    Radar/Bar chart comparing key sustainability metrics across the 3 strategies.
    """
    strat1 = strategies["strategy_1"]
    strat2 = strategies["strategy_2"]
    strat3 = strategies["strategy_3"]
    
    names = [strat1["primary_crop"], strat2["primary_crop"], strat3["primary_crop"]]
    labels = ["1. Optimized Baseline", "2. Soil Builder (Legume)", "3. Climate Resilient"]
    
    suitability = [strat1["suitability_score"], strat2["suitability_score"], strat3["suitability_score"]]
    water_savings = [strat1["water_savings_pct"], strat2["water_savings_pct"], strat3["water_savings_pct"]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels,
        y=suitability,
        name="Suitability Score (%)",
        marker_color="#3182ce",
        text=[f"{v}%" for v in suitability],
        textposition="auto"
    ))
    
    fig.add_trace(go.Bar(
        x=labels,
        y=water_savings,
        name="Water Savings vs Baseline (%)",
        marker_color="#38a169",
        text=[f"{v}%" for v in water_savings],
        textposition="auto"
    ))
    
    fig.update_layout(
        barmode="group",
        title="<b>Rotation Strategies: Suitability vs Water Conservation</b>",
        title_font=dict(size=16),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor="rgba(240, 244, 248, 0.4)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=360
    )
    fig.update_yaxes(title_text="Percentage (%)", range=[0, 105], showgrid=True)
    return fig

