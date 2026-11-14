"""
Unit and Integration tests for modules/nasa_power.py
Validates NASA POWER REST API parsing, missing value handling, and fallback caching.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, ConnectionError

from modules.nasa_power import fetch_nasa_power_climate, generate_synthetic_fallback

EXPECTED_COLUMNS = [
    "Date", "Year", "Month", "Temperature_C", "Precipitation_mm",
    "RelativeHumidity_pct", "SolarRadiation_MJ", "Is_Fallback"
]

def test_generate_synthetic_fallback_schema_and_range():
    """Verify synthetic fallback generates complete, valid tabular records."""
    df = generate_synthetic_fallback(lat=20.9320, lon=77.7523, start_year=2020, end_year=2023)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 4 * 12 # 4 years, 12 months = 48 records
    for col in EXPECTED_COLUMNS:
        assert col in df.columns
    assert df["Is_Fallback"].all() == True
    assert df["Temperature_C"].between(-10.0, 55.0).all()
    assert (df["Precipitation_mm"] >= 0.0).all()
    assert df["RelativeHumidity_pct"].between(0.0, 100.0).all()

@patch("modules.nasa_power.requests.get")
def test_fetch_nasa_power_climate_success(mock_get, sample_nasa_api_response):
    """Verify successful parsing of NASA API response and -999 imputation."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = sample_nasa_api_response
    mock_get.return_value = mock_resp
    
    df = fetch_nasa_power_climate(lat=25.4484, lon=78.5685, start_year=2022, end_year=2023)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 24 # 2 years * 12 months (month 13 excluded)
    assert df["Is_Fallback"].iloc[0] == False
    # Verify month 13 annual averages are filtered out
    assert set(df["Month"].unique()) == set(range(1, 13))
    # Verify -999 missing values were imputed/interpolated and not left as -999
    assert (df["Temperature_C"] != -999.0).all()
    assert (df["Precipitation_mm"] != -999.0).all()
    assert not df["Temperature_C"].isna().any()

@patch("modules.nasa_power.requests.get")
def test_fetch_nasa_power_climate_timeout_fallback(mock_get):
    """Verify graceful fallback generation when NASA API times out."""
    mock_get.side_effect = Timeout("NASA POWER Gateway Timeout")
    
    df = fetch_nasa_power_climate(lat=30.9010, lon=75.8573, start_year=2020, end_year=2022)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df["Is_Fallback"].iloc[0] == True
    assert len(df) == 36

@patch("modules.nasa_power.requests.get")
def test_fetch_nasa_power_climate_http_error_fallback(mock_get):
    """Verify fallback when NASA API returns non-200 HTTP code."""
    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_get.return_value = mock_resp
    
    df = fetch_nasa_power_climate(lat=18.4088, lon=76.5604, start_year=2021, end_year=2022)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df["Is_Fallback"].iloc[0] == True

@pytest.mark.integration
def test_live_nasa_power_api_connection():
    """LIVE INTEGRATION TEST: Directly queries NASA Langley Research Center REST API."""
    df = fetch_nasa_power_climate(lat=20.9320, lon=77.7523, start_year=2023, end_year=2023, timeout=12)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12
    # Verify real NASA satellite observation values were fetched
    assert df["Is_Fallback"].iloc[0] == False
    assert 15.0 <= df["Temperature_C"].mean() <= 38.0
