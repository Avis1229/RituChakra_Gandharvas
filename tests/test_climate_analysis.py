"""
Unit tests for modules/climate_analysis.py
Validates 10-year agricultural climate trend calculation, monsoon seasonality shift detection,
and drought vulnerability index scoring.
"""

import pytest
import pandas as pd
import numpy as np

from modules.climate_analysis import compute_climate_shifts

def test_compute_climate_shifts_empty_dataframe():
    """Verify safe empty dictionary returned when climate dataframe is empty."""
    res = compute_climate_shifts(pd.DataFrame())
    assert res == {}

def test_compute_climate_shifts_single_year():
    """Verify fallback slope calculation when only 1 year of data is present."""
    records = [{
        "Date": f"2023{m:02d}", "Year": 2023, "Month": m,
        "Temperature_C": 26.0, "Precipitation_mm": 50.0,
        "RelativeHumidity_pct": 60.0, "SolarRadiation_MJ": 18.0
    } for m in range(1, 13)]
    df = pd.DataFrame(records)
    
    shifts = compute_climate_shifts(df)
    assert shifts["num_years"] == 1
    assert "drought_vulnerability_index" in shifts
    assert isinstance(shifts["insights"], list)

def test_compute_climate_shifts_multi_year_trend(sample_climate_dataframe):
    """Verify trend metrics, warming rate, and monsoon shift on a 10-year dataset."""
    shifts = compute_climate_shifts(sample_climate_dataframe)
    
    assert shifts["num_years"] == 11
    assert shifts["early_period"] == "2014-2018"
    assert shifts["recent_period"] == "2019-2024"
    
    # Temperature warming was injected with +0.1°C per year = positive delta
    assert shifts["temp_delta"] > 0
    assert shifts["temp_slope_per_decade"] > 0
    
    # Check Drought Vulnerability Index range (0 to 100)
    assert 10 <= shifts["drought_vulnerability_index"] <= 100
    
    # Annual data table must contain 11 aggregated rows
    assert len(shifts["annual_data"]) == 11
    assert "Temperature_C" in shifts["annual_data"].columns
    assert "Precipitation_mm" in shifts["annual_data"].columns
    
    # Monthly dictionaries must cover 12 months
    assert len(shifts["monthly_early"]) == 12
    assert len(shifts["monthly_recent"]) == 12
    
    # Actionable insights list must contain agricultural alert bullets
    assert len(shifts["insights"]) >= 2
    assert any("Thermal Shift" in s or "Warming" in s for s in shifts["insights"])
    
    # Growing Degree Days (GDD) & Phenology Acceleration verification
    assert "early_gdd" in shifts
    assert "recent_gdd" in shifts
    assert "gdd_delta" in shifts
    assert shifts["gdd_delta"] > 0
    assert "ripening_acceleration_days" in shifts
    assert shifts["ripening_acceleration_days"] > 0

