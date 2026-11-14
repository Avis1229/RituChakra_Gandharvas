"""
Unit tests for modules/visualizer.py
Validates interactive Plotly figures: climate trends, seasonality shift,
community node calibration, and strategy comparison radar/bar.
"""

import pytest
import pandas as pd
import plotly.graph_objects as go

from modules.visualizer import (
    create_climate_trend_chart,
    create_seasonality_shift_chart,
    create_calibration_comparison_chart,
    create_strategy_radar_comparison
)

def test_create_climate_trend_chart():
    """Verify dual-axis climate trend chart creation with precipitation bars and temperature line."""
    df_annual = pd.DataFrame({
        "Year": [2018, 2019, 2020, 2021, 2022],
        "Temperature_C": [26.2, 26.5, 26.8, 27.1, 27.3],
        "Precipitation_mm": [850.0, 720.0, 910.0, 640.0, 780.0]
    })
    
    fig = create_climate_trend_chart(df_annual)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 2 # Bars + Temp Line (+ optional trend line)
    # Check trace types
    types = [t.type for t in fig.data]
    assert "bar" in types
    assert "scatter" in types

def test_create_seasonality_shift_chart():
    """Verify seasonality comparison area chart."""
    early_dict = {m: 40.0 + m * 5.0 for m in range(1, 13)}
    recent_dict = {m: 35.0 + m * 6.0 for m in range(1, 13)}
    
    fig = create_seasonality_shift_chart(early_dict, recent_dict, "2014-2018", "2019-2023")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
    assert fig.data[0].name.startswith("Baseline")
    assert fig.data[1].name.startswith("Recent")

def test_create_calibration_comparison_chart():
    """Verify 2-row subplot comparing satellite vs ESP32 temperature and soil moisture."""
    df_telemetry = pd.DataFrame({
        "Date": [f"2026-11-{i:02d}" for i in range(1, 11)],
        "Satellite_T2M_C": [27.0 + i * 0.1 for i in range(10)],
        "Ground_ESP32_Temp_C": [27.8 + i * 0.1 for i in range(10)],
        "Calibrated_Temp_C": [27.5 + i * 0.1 for i in range(10)],
        "NASA_SMAP_Moisture_pct": [22.0] * 10,
        "Ground_ESP32_SoilMoisture_pct": [24.0] * 10,
        "Calibrated_SoilMoisture_pct": [23.5] * 10
    })
    
    fig = create_calibration_comparison_chart(df_telemetry)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 6 # 3 traces for temp + 3 traces for soil moisture

def test_create_strategy_radar_comparison():
    """Verify multi-criteria bar/radar comparison across the 3 strategies."""
    strategies = {
        "strategy_1": {"primary_crop": "Cotton", "suitability_score": 72.0, "water_savings_pct": 12},
        "strategy_2": {"primary_crop": "Chickpea", "suitability_score": 86.0, "water_savings_pct": 55},
        "strategy_3": {"primary_crop": "Bajra", "suitability_score": 91.0, "water_savings_pct": 70}
    }
    
    fig = create_strategy_radar_comparison(strategies)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2 # Trace 1: Suitability, Trace 2: Water savings
    assert len(fig.data[0].x) == 3

