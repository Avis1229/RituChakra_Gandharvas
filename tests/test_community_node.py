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

def test_bme280_bird_effect_and_sentinel1_sar():
    """Verify BME280 barometric pressure telemetry, Bird Effect storm detection, and Sentinel-1 SAR waterlogging."""
    engine = CommunityNodeEngine()
    df = engine.generate_ground_truth_telemetry(satellite_temp=29.0, satellite_precip=25.0, days=30)
    
    # BME280 Pressure boundaries
    assert "BME280_Pressure_hPa" in df.columns
    assert df["BME280_Pressure_hPa"].between(980.0, 1040.0).all()
    assert "Pressure_Delta_3h_hPa" in df.columns
    assert "Dew_Point_Depression_C" in df.columns
    assert (df["Dew_Point_Depression_C"] >= 0.0).all()
    
    # Bird effect alert flag exists and detects storm drop
    assert "Bird_Effect_Storm_Alert" in df.columns
    assert df["Bird_Effect_Storm_Alert"].dtype == bool
    assert df["Bird_Effect_Storm_Alert"].any(), "At least one storm event should trigger Bird Effect alert"
    
    # Sentinel-1 SAR Backscatter & Waterlogging
    assert "Sentinel1_SAR_Backscatter_dB" in df.columns
    assert df["Sentinel1_SAR_Backscatter_dB"].between(-30.0, 0.0).all()
    assert "Sentinel1_Waterlogging" in df.columns
    
    metrics = engine.calculate_calibration_metrics(df)
    assert "latest_pressure_hPa" in metrics
    assert "bird_effect_storm_alert" in metrics
    assert "latest_sar_backscatter_db" in metrics
    assert "disruption_protocol_active" in metrics

def test_custom_hardware_telemetry_injection():
    """Verify that user's custom physical node readings override the latest telemetry correctly."""
    engine = CommunityNodeEngine(node_id="CUSTOM_USER_NODE", is_custom_node=True)
    engine.set_custom_telemetry(temp=33.2, humidity=48.0, pressure=1008.4, soil_moisture=19.5, rain_mm=5.0)
    
    df = engine.generate_ground_truth_telemetry(satellite_temp=30.0, satellite_precip=0.0, days=10)
    last = df.iloc[-1]
    
    assert last["Ground_ESP32_Temp_C"] == 33.2
    assert last["BME280_Humidity_pct"] == 48.0
    assert last["BME280_Pressure_hPa"] == 1008.4
    assert last["Ground_ESP32_SoilMoisture_pct"] == 19.5
    assert last["Ground_ESP32_Rain_mm"] == 5.0

def test_custom_hardware_telemetry_with_soil_temp_and_node_id():
    """Verify that set_custom_telemetry accepts soil_temp, node_id, and unexpected kwargs without error."""
    engine = CommunityNodeEngine(node_id="DEFAULT_ID")
    engine.set_custom_telemetry(
        soil_moisture=32.5,
        soil_temp=28.0,
        temp=30.5,
        humidity=68.0,
        pressure=1008.2,
        node_id="NEW_CUSTOM_NODE",
        rain_mm=0.0,
        unexpected_extra_sensor=99.9
    )
    assert engine.node_id == "NEW_CUSTOM_NODE"
    assert engine.custom_telemetry["soil_temp"] == 28.0
    assert engine.custom_telemetry["temp"] == 30.5
    assert engine.custom_telemetry["soil_moisture"] == 32.5



