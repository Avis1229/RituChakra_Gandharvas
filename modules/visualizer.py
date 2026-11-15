"""
Visualizer Module
Interactive Plotly figures styled with NASA & Agro Design Standards:
Supports both Clean Light Theme (Default) and Deep Space Dark Theme,
professional typography (Inter), crisp layout aesthetics, and zero text overlaps.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Official Brand Palettes (Combining NASA & Agriculture Earth Tones)
NASA_BLUE = "#0B3D91"
NASA_LIGHT_BLUE = "#0284C7"
NASA_RED = "#DC2626"
CITRON_YELLOW = "#CA8A04"
CITRON_YELLOW_DARK = "#D4E838"
EMERALD_GREEN = "#059669"
EMERALD_GREEN_DARK = "#10B981"
SMAP_PURPLE = "#7C3AED"
SMAP_PURPLE_DARK = "#8B5CF6"

FONT_INTER = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_BARLOW = FONT_INTER

def _get_theme_palette(theme: str = "light") -> dict:
    """Returns colors tailored for Clean Light (default) or Deep Space Dark mode."""
    if theme == "dark":
        return {
            "plot_bg": "#0B1E3F",
            "paper_bg": "rgba(0, 0, 0, 0)",
            "grid_color": "rgba(255, 255, 255, 0.08)",
            "text_color": "#FFFFFF",
            "muted_text": "#94A3B8",
            "legend_bg": "#071731",
            "legend_border": "#1E3A6B",
            "bar_below": "#334155",
            "highlight": CITRON_YELLOW_DARK,
            "green": EMERALD_GREEN_DARK,
            "purple": SMAP_PURPLE_DARK,
            "card_border": "#1E3A6B",
            "annotation_color": "#FFFFFF"
        }
    else:  # default clean light theme
        return {
            "plot_bg": "#FFFFFF",
            "paper_bg": "rgba(0, 0, 0, 0)",
            "grid_color": "#F1F5F9",
            "text_color": "#0F172A",
            "muted_text": "#64748B",
            "legend_bg": "#F8FAFC",
            "legend_border": "#E2E8F0",
            "bar_below": "#CBD5E1",
            "highlight": CITRON_YELLOW,
            "green": EMERALD_GREEN,
            "purple": SMAP_PURPLE,
            "card_border": "#E2E8F0",
            "annotation_color": "#0F172A"
        }

def create_climate_trend_chart(df_annual: pd.DataFrame, theme: str = "light") -> go.Figure:
    """
    Dual-axis 10-year climate trajectory:
    Annual Precipitation bars + Mean Surface Temperature line and decadal trend.
    """
    pal = _get_theme_palette(theme)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    mean_precip = df_annual["Precipitation_mm"].mean()
    bar_colors = [NASA_LIGHT_BLUE if p >= mean_precip else pal["bar_below"] for p in df_annual["Precipitation_mm"]]
    
    fig.add_trace(
        go.Bar(
            x=df_annual["Year"],
            y=df_annual["Precipitation_mm"],
            name="Annual Precipitation (mm)",
            marker=dict(
                color=bar_colors,
                opacity=0.9,
                line=dict(color=pal["legend_border"], width=1)
            ),
            hovertemplate="Year %{x}: %{y:.1f} mm<extra></extra>"
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_annual["Year"],
            y=df_annual["Temperature_C"],
            name="Mean Temperature (°C)",
            mode="lines+markers",
            line=dict(color=pal["highlight"], width=3),
            marker=dict(size=7, color="#FFFFFF", line=dict(color=pal["highlight"], width=2)),
            hovertemplate="Year %{x}: %{y:.2f} °C<extra></extra>"
        ),
        secondary_y=True
    )
    
    if len(df_annual) >= 2:
        z = np.polyfit(df_annual["Year"], df_annual["Temperature_C"], 1)
        p = np.poly1d(z)
        fig.add_trace(
            go.Scatter(
                x=df_annual["Year"],
                y=p(df_annual["Year"]),
                name=f"Decadal Trend ({z[0]*10:+.2f}°C/decade)",
                mode="lines",
                line=dict(color=NASA_RED, width=2, dash="dash"),
                hovertemplate="Trend: %{y:.2f} °C<extra></extra>"
            ),
            secondary_y=True
        )

    fig.update_layout(
        title=dict(
            text="<b>10-Year Decadal Climate Trajectory (NASA POWER)</b>",
            font=dict(size=14, color=pal["text_color"], family=FONT_INTER)
        ),
        font=dict(family=FONT_INTER, color=pal["text_color"]),
        hovermode="x unified",
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color=pal["text_color"], size=11, family=FONT_INTER),
            bgcolor=pal["legend_bg"],
            bordercolor=pal["legend_border"],
            borderwidth=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=pal["plot_bg"],
        paper_bgcolor=pal["paper_bg"],
        height=380
    )
    
    fig.update_xaxes(
        title_text="Observation Year", 
        dtick=1, 
        gridcolor=pal["grid_color"], 
        zerolinecolor=pal["grid_color"],
        tickfont=dict(color=pal["muted_text"], family=FONT_INTER)
    )
    fig.update_yaxes(
        title_text="Annual Precipitation (mm)", 
        secondary_y=False, 
        showgrid=True, 
        gridcolor=pal["grid_color"],
        tickfont=dict(color=pal["muted_text"], family=FONT_INTER)
    )
    fig.update_yaxes(
        title_text="Mean Temperature (°C)", 
        secondary_y=True, 
        showgrid=False,
        tickfont=dict(color=pal["highlight"], family=FONT_INTER)
    )
    
    return fig

def create_seasonality_shift_chart(
    early_dict: dict, 
    recent_dict: dict, 
    early_label: str, 
    recent_label: str,
    theme: str = "light"
) -> go.Figure:
    """
    Compares monthly precipitation distribution between historical baseline and recent observations.
    """
    pal = _get_theme_palette(theme)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    early_vals = [early_dict.get(m, 0.0) for m in range(1, 13)]
    recent_vals = [recent_dict.get(m, 0.0) for m in range(1, 13)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=early_vals,
        mode="lines+markers",
        name=f"Baseline Climatology ({early_label})",
        line=dict(color=pal["muted_text"], width=2, dash="dot"),
        marker=dict(size=6, color=pal["muted_text"]),
        hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=recent_vals,
        mode="lines+markers",
        name=f"Recent Climatology ({recent_label})",
        line=dict(color=NASA_LIGHT_BLUE, width=3),
        marker=dict(size=7, color="#FFFFFF", line=dict(color=NASA_LIGHT_BLUE, width=2)),
        hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text="<b>Seasonal Monsoon Distribution Shift</b>",
            font=dict(size=14, color=pal["text_color"], family=FONT_INTER)
        ),
        font=dict(family=FONT_INTER, color=pal["text_color"]),
        hovermode="x unified",
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color=pal["text_color"], size=11, family=FONT_INTER),
            bgcolor=pal["legend_bg"],
            bordercolor=pal["legend_border"],
            borderwidth=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=pal["plot_bg"],
        paper_bgcolor=pal["paper_bg"],
        height=350
    )
    
    fig.update_xaxes(
        title_text="Calendar Month", 
        gridcolor=pal["grid_color"],
        tickfont=dict(color=pal["muted_text"], family=FONT_INTER)
    )
    fig.update_yaxes(
        title_text="Mean Monthly Precipitation (mm)", 
        showgrid=True, 
        gridcolor=pal["grid_color"],
        tickfont=dict(color=pal["muted_text"], family=FONT_INTER)
    )
    return fig

def create_calibration_comparison_chart(df_telemetry: pd.DataFrame, theme: str = "light") -> go.Figure:
    """
    Compares 30-day telemetry: NASA Satellite Grid vs. In-Situ Ground AWS vs. Calibrated Output.
    """
    pal = _get_theme_palette(theme)
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, 
        subplot_titles=(
            "<b>Surface Temperature Calibration (°C)</b>", 
            "<b>Root-Zone Soil Moisture (% VWC - SMAP vs. In-Situ)</b>"
        ),
        vertical_spacing=0.22
    )
    
    # Top Plot: Temperature
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Satellite_T2M_C"],
                   name="NASA 9km Grid (MERRA-2)", line=dict(color=pal["muted_text"], width=1.5, dash="dash")),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Ground_ESP32_Temp_C"],
                   name="In-Situ Field Node (ESP32)", line=dict(color=pal["highlight"], width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Calibrated_Temp_C"],
                   name="Fused Output", line=dict(color=NASA_LIGHT_BLUE, width=2.5)),
        row=1, col=1
    )
    
    # Bottom Plot: Soil Moisture
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["NASA_SMAP_Moisture_pct"],
                   name="NASA SMAP L3 Grid", line=dict(color=pal["purple"], width=1.5, dash="dash")),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Ground_ESP32_SoilMoisture_pct"],
                   name="In-Situ Capacitive Probe", line=dict(color="#38BDF8", width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_telemetry["Date"], y=df_telemetry["Calibrated_SoilMoisture_pct"],
                   name="Fused Calibrated VWC", line=dict(color=pal["green"], width=2.5)),
        row=2, col=1
    )
    
    fig.update_layout(
        height=580,
        font=dict(family=FONT_INTER, color=pal["text_color"]),
        hovermode="x unified",
        margin=dict(l=50, r=40, t=65, b=90),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.16, 
            xanchor="center", 
            x=0.5,
            font=dict(color=pal["text_color"], size=11, family=FONT_INTER),
            bgcolor=pal["legend_bg"],
            bordercolor=pal["legend_border"],
            borderwidth=1
        ),
        plot_bgcolor=pal["plot_bg"],
        paper_bgcolor=pal["paper_bg"]
    )
    
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=12, color=pal["annotation_color"], family=FONT_INTER)
        annotation['yshift'] = 14
        
    fig.update_xaxes(gridcolor=pal["grid_color"], tickfont=dict(color=pal["muted_text"], family=FONT_INTER))
    fig.update_yaxes(gridcolor=pal["grid_color"], tickfont=dict(color=pal["muted_text"], family=FONT_INTER))
    return fig

def create_strategy_radar_comparison(strategies: dict, theme: str = "light") -> go.Figure:
    """
    Bar comparison across the 3 rotation strategies without text overlaps.
    """
    pal = _get_theme_palette(theme)
    strat_a = strategies.get("strategy_a", strategies.get("strategy_1"))
    strat_b = strategies.get("strategy_b", strategies.get("strategy_3"))
    strat_c = strategies.get("strategy_c", strategies.get("strategy_2"))
    
    labels = ["Strategy 1 (Smart Plan)", "Strategy 2 (Escape Crop)", "Strategy 3 (Soil & Wealth)"]
    
    suitability = [strat_a["suitability_score"], strat_b["suitability_score"], strat_c["suitability_score"]]
    water_savings = [strat_a["water_savings_pct"], strat_b["water_savings_pct"], strat_c["water_savings_pct"]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels,
        y=suitability,
        name="Agronomic Suitability (%)",
        marker=dict(
            color=NASA_LIGHT_BLUE,
            line=dict(color=pal["legend_border"], width=1)
        ),
        text=[f"{v:.0f}%" for v in suitability],
        textposition="outside",
        textfont=dict(family=FONT_INTER, size=12, color=pal["text_color"])
    ))
    
    fig.add_trace(go.Bar(
        x=labels,
        y=water_savings,
        name="Water Conservation (%)",
        marker=dict(
            color=pal["green"],
            line=dict(color=pal["legend_border"], width=1)
        ),
        text=[f"{v:.0f}%" for v in water_savings],
        textposition="outside",
        textfont=dict(family=FONT_INTER, size=12, color=pal["green"])
    ))
    
    fig.update_layout(
        barmode="group",
        title=dict(
            text="<b>Strategy Multi-Criteria Comparison</b>",
            font=dict(size=14, color=pal["text_color"], family=FONT_INTER)
        ),
        font=dict(family=FONT_INTER, color=pal["text_color"]),
        hovermode="x unified",
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color=pal["text_color"], size=11, family=FONT_INTER),
            bgcolor=pal["legend_bg"],
            bordercolor=pal["legend_border"],
            borderwidth=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=pal["plot_bg"],
        paper_bgcolor=pal["paper_bg"],
        height=360
    )
    fig.update_xaxes(gridcolor=pal["grid_color"], tickfont=dict(color=pal["text_color"], family=FONT_INTER))
    fig.update_yaxes(title_text="Percentage (%)", range=[0, 115], showgrid=True, gridcolor=pal["grid_color"], tickfont=dict(color=pal["muted_text"], family=FONT_INTER))
    return fig

def create_bme280_pressure_trend_chart(df_telemetry: pd.DataFrame, theme: str = "light") -> go.Figure:
    """
    Phase 1 & 2 Visualizer: Local BME280 Barometric Pressure, 'Bird Effect' Storm Alerts,
    and Sentinel-1 SAR Cloud-Penetrating Radar Backscatter.
    """
    pal = _get_theme_palette(theme)
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        subplot_titles=(
            "<b>BME280 Barometric Pressure & Storm Early Warning (hPa)</b>",
            "<b>Sentinel-1 SAR C-Band Radar Backscatter (σ° dB)</b>"
        ),
        vertical_spacing=0.22
    )
    
    # Row 1: Barometric Pressure
    fig.add_trace(
        go.Scatter(
            x=df_telemetry["Date"],
            y=df_telemetry["BME280_Pressure_hPa"],
            name="BME280 Pressure (hPa)",
            line=dict(color="#0284C7", width=2.5),
            hovertemplate="Date: %{x}<br>Pressure: %{y:.1f} hPa<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Storm Alerts (Bird Effect)
    alert_rows = df_telemetry[df_telemetry["Bird_Effect_Storm_Alert"]]
    if not alert_rows.empty:
        fig.add_trace(
            go.Scatter(
                x=alert_rows["Date"],
                y=alert_rows["BME280_Pressure_hPa"],
                mode="markers+text",
                name="Storm Warning (Rapid Fall)",
                marker=dict(size=12, color=NASA_RED, symbol="triangle-down", line=dict(color="#FFFFFF", width=1.5)),
                text=["STORM ALERT"] * len(alert_rows),
                textposition="top center",
                textfont=dict(family=FONT_INTER, size=10, color=NASA_RED),
                hovertemplate="<b>PROACTIVE STORM WARNING</b><br>Rapid Pressure Drop: %{y:.1f} hPa<extra></extra>"
            ),
            row=1, col=1
        )
        
    # Row 2: Sentinel-1 SAR Radar Backscatter
    fig.add_trace(
        go.Scatter(
            x=df_telemetry["Date"],
            y=df_telemetry["Sentinel1_SAR_Backscatter_dB"],
            name="Sentinel-1 SAR σ° (dB)",
            line=dict(color=pal["purple"], width=2),
            hovertemplate="Date: %{x}<br>SAR Backscatter: %{y:.1f} dB<extra></extra>"
        ),
        row=2, col=1
    )
    
    # Waterlogging threshold line (-19.0 dB)
    fig.add_hline(
        y=-19.0, line_dash="dash", line_color=NASA_RED,
        annotation_text="Waterlogging Threshold (-19.0 dB)",
        annotation_position="bottom right",
        annotation_font=dict(color=NASA_RED, size=10, family=FONT_INTER),
        row=2, col=1
    )
    
    fig.update_layout(
        height=540,
        font=dict(family=FONT_INTER, color=pal["text_color"]),
        hovermode="x unified",
        margin=dict(l=50, r=40, t=65, b=85),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            font=dict(color=pal["text_color"], size=11, family=FONT_INTER),
            bgcolor=pal["legend_bg"],
            bordercolor=pal["legend_border"],
            borderwidth=1
        ),
        plot_bgcolor=pal["plot_bg"],
        paper_bgcolor=pal["paper_bg"]
    )
    
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=12, color=pal["annotation_color"], family=FONT_INTER)
        annotation['yshift'] = 14
        
    fig.update_xaxes(gridcolor=pal["grid_color"], tickfont=dict(color=pal["muted_text"], family=FONT_INTER))
    fig.update_yaxes(gridcolor=pal["grid_color"], tickfont=dict(color=pal["muted_text"], family=FONT_INTER))
    return fig

def create_digital_twin_projection_chart(
    annual_df: pd.DataFrame, 
    target_year: int = 2028,
    theme: str = "light"
) -> go.Figure:
    """
    Digital Twin Timeline: Projects farm climate trajectory and GDD thermal shifts from 2026 to 2030.
    """
    pal = _get_theme_palette(theme)
    hist_years = list(annual_df["Year"])
    hist_temps = list(annual_df["Temperature_C"])
    
    # Trend line projection to 2030
    z = np.polyfit(hist_years, hist_temps, 1)
    slope, intercept = z[0], z[1]
    
    proj_years = [y for y in range(2025, 2031)]
    proj_temps = [slope * y + intercept for y in proj_years]
    
    fig = go.Figure()
    
    # Historical Trace
    fig.add_trace(go.Scatter(
        x=hist_years, y=hist_temps,
        name="NASA Historical Baseline (2014-2024)",
        mode="lines+markers",
        line=dict(color=pal["muted_text"], width=2),
        marker=dict(size=6, color=pal["muted_text"])
    ))
    
    # Digital Twin Projected Trace
    fig.add_trace(go.Scatter(
        x=proj_years, y=proj_temps,
        name="Digital Twin Projection (2025-2030)",
        mode="lines+markers",
        line=dict(color=NASA_LIGHT_BLUE, width=3, dash="dot"),
        marker=dict(size=7, color=NASA_LIGHT_BLUE)
    ))
    
    # Active Selected Year Marker
    target_temp = slope * target_year + intercept
    fig.add_trace(go.Scatter(
        x=[target_year], y=[target_temp],
        name=f"Digital Twin Focus: {target_year}",
        mode="markers",
        marker=dict(size=14, color=pal["highlight"], symbol="diamond", line=dict(color="#FFFFFF", width=2)),
        hovertemplate=f"Year %{{x}}: Projected %{{y:.2f}} °C<br>Decadal Shift: +{(target_year - 2024)*slope*10/10:+.2f}°C<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>Farm Digital Twin Climate Trajectory (Focus Year: {target_year})</b>",
            font=dict(size=14, color=pal["text_color"], family=FONT_INTER)
        ),
        font=dict(family=FONT_INTER, color=pal["text_color"]),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=pal["text_color"], size=11, family=FONT_INTER),
            bgcolor=pal["legend_bg"],
            bordercolor=pal["legend_border"],
            borderwidth=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor=pal["plot_bg"],
        paper_bgcolor=pal["paper_bg"],
        height=380
    )
    fig.update_xaxes(title_text="Simulation Year", dtick=1, gridcolor=pal["grid_color"], tickfont=dict(color=pal["text_color"], family=FONT_INTER))
    fig.update_yaxes(title_text="Mean Temperature (°C)", gridcolor=pal["grid_color"], tickfont=dict(color=pal["muted_text"], family=FONT_INTER))
    return fig

def create_field_satellite_map(
    lat: float, 
    lon: float, 
    location_name: str, 
    node_id: str, 
    mapbox_token: str = "",
    theme: str = "light"
) -> go.Figure:
    """
    Renders high-resolution satellite imagery map of the target field centroid
    and adjacent in-situ IoT Field Node using Mapbox Satellite Streets.
    """
    pal = _get_theme_palette(theme)
    fig = go.Figure()

    # Target Field Centroid Marker
    fig.add_trace(go.Scattermap(
        lat=[lat],
        lon=[lon],
        mode="markers+text",
        marker=dict(size=16, color=pal["highlight"]),
        text=["Field Centroid"],
        textposition="top center",
        textfont=dict(size=12, color="#FFFFFF", family=FONT_INTER),
        hovertemplate=f"<b>Field Centroid</b><br>{location_name}<br>Lat: {lat:.4f}°N, Lon: {lon:.4f}°E<extra></extra>",
        name="Target Field Centroid"
    ))

    # In-situ Node Telemetry Anchor
    node_lat = lat + 0.0035
    node_lon = lon + 0.0035
    fig.add_trace(go.Scattermap(
        lat=[node_lat],
        lon=[node_lon],
        mode="markers+text",
        marker=dict(size=13, color="#0284C7"),
        text=[f"Node ({node_id})"],
        textposition="bottom center",
        textfont=dict(size=11, color="#E2E8F0", family=FONT_INTER),
        hovertemplate=f"<b>Field Ground Node</b><br>ID: {node_id}<br>Telemetry: Bosch BME280 + LoRa/MQTT<extra></extra>",
        name="Field Ground Node"
    ))

    # Mapbox Satellite Raster Layer Configuration
    map_config = dict(
        center=dict(lat=lat + 0.0017, lon=lon + 0.0017),
        zoom=11
    )
    if mapbox_token:
        tile_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/256/{{z}}/{{x}}/{{y}}?access_token={mapbox_token}"
        map_config["style"] = "white-bg"
        map_config["layers"] = [
            dict(
                sourcetype="raster",
                source=[tile_url],
                below="traces"
            )
        ]
    else:
        map_config["style"] = "satellite"

    fig.update_layout(
        title=dict(
            text="High-Resolution Satellite Field Radar (Mapbox)",
            font=dict(family=FONT_INTER, size=13, color="#FFFFFF"),
            x=0.01,
            y=0.96
        ),
        map=map_config,
        margin=dict(l=0, r=0, t=40, b=0),
        height=320,
        paper_bgcolor=pal["paper_bg"],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#FFFFFF", size=11, family=FONT_INTER),
            bgcolor="rgba(15, 23, 42, 0.85)"
        )
    )
    return fig
