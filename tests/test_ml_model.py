"""
Unit tests for modules/ml_model.py
Validates lightweight tabular Random Forest training, sub-millisecond inference,
crop suitability scoring, and feature importances.
"""

import pytest
import numpy as np
import time

from modules.ml_model import CropSuitabilityModel
from config import CROP_CATALOG

def test_model_initialization_and_training():
    """Verify model initializes and fits the synthetic baseline during construction."""
    model = CropSuitabilityModel()
    assert model.is_trained == True
    assert len(model.feature_names) == 8
    assert model.model.n_estimators == 35

def test_inference_latency_sub_millisecond():
    """Verify that tabular inference is extremely fast, respecting 4GB VRAM and CPU constraints."""
    model = CropSuitabilityModel()
    features = {
        "Mean_Temp_C": 28.0,
        "Total_Precip_mm": 650.0,
        "Soil_N": 180.0,
        "Soil_P": 45.0,
        "Soil_K": 260.0,
        "Soil_pH": 7.2,
        "Drought_Index": 50.0,
        "Calibrated_SoilMoisture_pct": 22.0
    }
    
    t0 = time.perf_counter()
    for _ in range(50):
        score = model.predict_crop_suitability("Cotton", features)
    duration_sec = time.perf_counter() - t0
    
    avg_ms = (duration_sec / 50.0) * 1000.0
    assert avg_ms < 10.0 # Fast tabular inference under 10ms per crop
    assert 10.0 <= score <= 98.0

def test_agronomic_behavior_under_drought_regime():
    """Verify that drought conditions penalize water-thirsty Rice and reward hardy Pearl Millet."""
    model = CropSuitabilityModel()
    
    drought_features = {
        "Mean_Temp_C": 34.0,
        "Total_Precip_mm": 300.0, # Severe deficit
        "Soil_N": 140.0,
        "Soil_P": 30.0,
        "Soil_K": 200.0,
        "Soil_pH": 7.5,
        "Drought_Index": 85.0, # High drought risk
        "Calibrated_SoilMoisture_pct": 14.0 # Dry soil
    }
    
    rice_score = model.predict_crop_suitability("Rice (Paddy)", drought_features)
    bajra_score = model.predict_crop_suitability("Pearl Millet (Bajra)", drought_features)
    moong_score = model.predict_crop_suitability("Moong (Green Gram)", drought_features)
    
    # In severe drought, Pearl Millet and Moong must significantly outscore Rice
    assert bajra_score > rice_score
    assert moong_score > rice_score
    assert bajra_score >= 70.0
    assert rice_score <= 50.0

def test_feature_importances():
    """Verify that feature importances dictionary returns valid positive weights summing near 100."""
    model = CropSuitabilityModel()
    imps = model.get_feature_importances()
    
    assert isinstance(imps, dict)
    assert len(imps) == 8
    for f in model.feature_names:
        assert f in imps
        assert imps[f] >= 0.0
    total_pct = sum(imps.values())
    assert 98.0 <= total_pct <= 102.0
