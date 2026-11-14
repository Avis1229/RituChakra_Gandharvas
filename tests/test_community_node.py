"""
Unit tests for modules/community_node.py
Validates ESP32 community ground-truth telemetry generation, sensor fusion calibration,
and MAE accuracy gain calculations.
"""

import pytest
import pandas as pd
import numpy as np
from modules.community_node import CommunityNodeEngine

def test_community_node_initialization():
    """Verify default engine properties and node identification."""
    engine = CommunityNodeEngine(node_id="TEST_NODE_999", radius_km=10.0)
    assert engine.node_id == "TEST_NODE_999"
    assert engine.radius_km == 10.0
    assert "ONLINE" in engine.status

def test_generate_ground_truth_telemetry_bounds():
    """Verify that simulated 30-day ESP32 telemetry conforms to physical sensor constraints."""
    engine = CommunityNodeEngine()
    df = engine.generate_ground_truth_telemetry(satellite_temp=28.5, satellite_precip=40.0, days=30)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 30
    
    # Check physical constraints
    assert df["Ground_ESP32_Temp_C"].between(-5.0, 55.0).all()
    assert (df["Ground_ESP32_Rain_mm"] >= 0.0).all()
    assert df["Ground_ESP32_SoilMoisture_pct"].between(0.0, 100.0).all()
    assert df["NASA_SMAP_Moisture_pct"].between(0.0, 100.0).all()
    assert df["Calibrated_SoilMoisture_pct"].between(0.0, 100.0).all()
    assert df["Node_Battery_V"].between(3.0, 4.3).all()
    assert (df["Signal_RSSI_dBm"] < 0).all()

def test_sensor_fusion_formula():
    """Verify that calibrated values lie strictly between satellite and ground observations."""
    engine = CommunityNodeEngine()
    df = engine.generate_ground_truth_telemetry(satellite_temp=27.0, satellite_precip=20.0, days=15)
    
    for _, row in df.iterrows():
        sat_t = row["Satellite_T2M_C"]
        grd_t = row["Ground_ESP32_Temp_C"]
        cal_t = row["Calibrated_Temp_C"]
        
        # Calibrated temp must fall within the range defined by satellite and ground
        min_t, max_t = min(sat_t, grd_t), max(sat_t, grd_t)
        assert min_t - 0.01 <= cal_t <= max_t + 0.01

def test_calculate_calibration_metrics():
    """Verify MAE error reduction and accuracy gain calculation for hackathon presentation."""
    engine = CommunityNodeEngine()
    df = engine.generate_ground_truth_telemetry(satellite_temp=30.0, satellite_precip=15.0, days=30)
    metrics = engine.calculate_calibration_metrics(df)
    
    assert metrics["node_id"] == engine.node_id
    assert metrics["coverage_radius_km"] == engine.radius_km
    
    # Calibrated MAE must be strictly less than Raw Satellite MAE
    assert metrics["calibrated_temp_mae"] < metrics["raw_temp_mae"]
    assert metrics["calibrated_soil_moisture_mae"] < metrics["raw_soil_moisture_mae"]
    
    # Accuracy gains must be positive percentages (>50%)
    assert metrics["temp_accuracy_gain_pct"] > 50.0
    assert metrics["sm_accuracy_gain_pct"] > 50.0
    assert len(metrics["active_sensors"]) >= 4

