"""
Pytest configuration and shared test fixtures for Field Shift (RituChakra_Gandharvas)
"""

import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_nasa_api_response():
    """Simulates raw JSON dictionary returned by NASA POWER API endpoint."""
    t2m = {}
    precip = {}
    rh = {}
    solar = {}
    
    # 2 years: 2022 and 2023, 12 months each + month 13 annual
    for y in [2022, 2023]:
        for m in range(1, 13):
            k = f"{y}{m:02d}"
            t2m[k] = 25.0 + m * 0.5
            precip[k] = 150.0 if m in [6, 7, 8, 9] else 15.0
            rh[k] = 65.0
            solar[k] = 20.0
        # Include annual key (13) and test missing value (-999)
        t2m[f"{y}13"] = 28.0
        precip[f"{y}13"] = 600.0
        rh[f"{y}13"] = 65.0
        solar[f"{y}13"] = 20.0
        
    # Inject a -999 missing value into month 202203 to test imputation
    t2m["202203"] = -999.0
    precip["202203"] = -999.0

    return {
        "properties": {
            "parameter": {
                "T2M": t2m,
                "PRECTOTCORR": precip,
                "RH2M": rh,
                "ALLSKY_SFC_SW_DWN": solar
            }
        }
    }

@pytest.fixture
def sample_soil_profile():
    return {
        "n": 180,
        "p": 45,
        "k": 280,
        "ph": 7.4,
        "soil_type": "Black Cotton Soil",
        "farm_size": 5.0
    }

@pytest.fixture
def sample_climate_dataframe():
    """Generates a synthetic 10-year climate dataset for testing shift calculations."""
    records = []
    base_temp = 26.0
    for year in range(2014, 2025):
        warming = (year - 2014) * 0.1
        for month in range(1, 13):
            temp = base_temp + (month % 5) * 1.5 + warming
            precip = 200.0 if month in [7, 8] else (40.0 if month in [6, 9] else 5.0)
            records.append({
                "Date": f"{year}{month:02d}",
                "Year": year,
                "Month": month,
                "Temperature_C": temp,
                "Precipitation_mm": precip,
                "RelativeHumidity_pct": 60.0,
                "SolarRadiation_MJ": 18.0,
                "Is_Fallback": False
            })
    return pd.DataFrame(records)

@pytest.fixture
def sample_calibrated_telemetry():
    return {
        "Date": "2026-11-14",
        "Satellite_T2M_C": 28.2,
        "Ground_ESP32_Temp_C": 29.1,
        "Calibrated_Temp_C": 28.8,
        "Satellite_Precip_mm": 0.0,
        "Ground_ESP32_Rain_mm": 0.0,
        "NASA_SMAP_Moisture_pct": 21.0,
        "Ground_ESP32_SoilMoisture_pct": 24.5,
        "Calibrated_SoilMoisture_pct": 23.8,
        "Node_Battery_V": 3.92,
        "Signal_RSSI_dBm": -68
    }

