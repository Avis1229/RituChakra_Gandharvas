"""
Unit tests for modules/rotation_engine.py
Validates 3-Strategy rotation synthesis: Optimized Baseline, Soil Builder, and Climate Resilient Cash Crop.
"""

import pytest
import pandas as pd

from modules.rotation_engine import generate_rotation_strategies
from modules.ml_model import CropSuitabilityModel

@pytest.fixture
def trained_model():
    return CropSuitabilityModel()

def test_generate_rotation_strategies_structure(sample_soil_profile, sample_calibrated_telemetry, trained_model):
    """Verify that all 3 strategies and the comparison matrix are generated with valid fields."""
    climate_shifts = {
        "temp_delta": 0.8,
        "precip_delta_pct": -12.0,
        "recent_annual_precip": 680.0,
        "recent_peak_month": "Aug",
        "drought_vulnerability_index": 65
    }
    
    res = generate_rotation_strategies(
        current_crop="Cotton",
        climate_shifts=climate_shifts,
        soil_profile=sample_soil_profile,
        calibrated_telemetry=sample_calibrated_telemetry,
        ml_model=trained_model
    )
    
    assert "strategy_1" in res
    assert "strategy_2" in res
    assert "strategy_3" in res
    assert "comparison_table" in res
    
    s1 = res["strategy_1"]
    s2 = res["strategy_2"]
    s3 = res["strategy_3"]
    
    # Strategy 1: Optimized Baseline
    assert s1["primary_crop"] == "Cotton"
    assert "Delay sowing" in s1["sowing_action"]
    assert len(s1["action_steps"]) >= 3
    
    # Strategy 2: Soil Builder (Legume)
    assert s2["primary_crop"] in ["Chickpea (Gram)", "Moong (Green Gram)", "Pigeon Pea (Arhar / Tur)", "Cowpea (Lobia)"]
    assert "Biological N Fixation" in str(s2["soil_n_balance_kg_ha"])
    assert s2["water_savings_pct"] >= 40
    
    # Strategy 3: Climate Resilient & Cash Crop
    assert s3["primary_crop"] in ["Pearl Millet (Bajra)", "Sorghum (Jowar)", "Finger Millet (Ragi)", "Mustard (Rabi Oilseed)"]
    assert s3["water_savings_pct"] >= 50
    assert "Very Low" in s3["risk_level"]
    
    # Comparison table verification
    comp_df = res["comparison_table"]
    assert isinstance(comp_df, pd.DataFrame)
    assert len(comp_df) == 3
    assert "Strategy" in comp_df.columns
    assert "Suitability Score" in comp_df.columns
    assert "Water Savings" in comp_df.columns

def test_rotation_sowing_shift_early_monsoon(sample_soil_profile, sample_calibrated_telemetry, trained_model):
    """Verify that when peak monsoon is early (e.g. July), planting window recommends early sowing."""
    climate_shifts = {
        "temp_delta": 0.4,
        "precip_delta_pct": -5.0,
        "recent_annual_precip": 850.0,
        "recent_peak_month": "Jul",
        "drought_vulnerability_index": 45
    }
    
    res = generate_rotation_strategies(
        current_crop="Rice (Paddy)",
        climate_shifts=climate_shifts,
        soil_profile=sample_soil_profile,
        calibrated_telemetry=sample_calibrated_telemetry,
        ml_model=trained_model
    )
    
    s1 = res["strategy_1"]
    assert "Advance sowing" in s1["sowing_action"]

def test_no_ghapla_dynamic_ranges_and_reasoning(sample_soil_profile, sample_calibrated_telemetry, trained_model):
    """Verify the 'No Ghapla' protocol: Dynamic ranges, mandatory reasoning, and economic hooks."""
    climate_shifts = {
        "temp_delta": 0.7,
        "gdd_delta": 135.0,
        "ripening_acceleration_days": 12,
        "precip_delta_pct": -8.0,
        "recent_annual_precip": 710.0,
        "recent_peak_month": "Aug",
        "drought_vulnerability_index": 58
    }
    
    res = generate_rotation_strategies(
        current_crop="Cotton",
        climate_shifts=climate_shifts,
        soil_profile=sample_soil_profile,
        calibrated_telemetry=sample_calibrated_telemetry,
        ml_model=trained_model
    )
    
    # Test strategy A, B, C availability
    assert "strategy_a" in res
    assert "strategy_b" in res
    assert "strategy_c" in res
    
    for key in ["strategy_a", "strategy_b", "strategy_c"]:
        strat = res[key]
        # Mandatory Reasoning
        assert "reasoning" in strat
        assert len(strat["reasoning"]) > 25
        
        # Dynamic confidence interval ranges
        assert "to" in strat["duration_days"], f"Duration must be a range in {key}"
        assert "to" in strat["water_requirement_mm"], f"Water requirement must be a range in {key}"
        
        # Economic Hook
        assert "economic_hook" in strat
        assert "pumping_energy_saved" in strat["economic_hook"]
        assert "net_financial_gain" in strat["economic_hook"]
        assert "₹" in strat["economic_hook"]["net_financial_gain"]
    
    # Check specific data driver mentions
    assert "NASA POWER" in res["strategy_a"]["reasoning"]
    assert "BME280" in res["strategy_b"]["reasoning"] or "Community Node" in res["strategy_b"]["reasoning"]
    assert "Sentinel-1 SAR" in res["strategy_c"]["reasoning"]

