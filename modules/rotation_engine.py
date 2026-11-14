"""
3-Strategy Crop Rotation Engine
Generates tailored agricultural rotation recommendations based on 
NASA climate trends and local community node soil telemetry.
"""

from config import CROP_CATALOG
import pandas as pd
import numpy as np

def generate_rotation_strategies(current_crop: str, 
                                 climate_shifts: dict, 
                                 soil_profile: dict, 
                                 calibrated_telemetry: dict, 
                                 ml_model) -> dict:
    """
    Synthesize 3 distinct agricultural adaptation strategies:
      1. Strategy 1: Optimized Baseline (Current crop with climate-adjusted agronomy)
      2. Strategy 2: Soil Builder (Leguminous N-fixing crop to regenerate depleted soil)
      3. Strategy 3: Climate Resilient (Drought/heat hardy crop hedging against water crisis)
    """
    crop_info = CROP_CATALOG.get(current_crop, CROP_CATALOG["Cotton"])
    temp_delta = climate_shifts.get("temp_delta", 0.6)
    precip_delta_pct = climate_shifts.get("precip_delta_pct", -8.0)
    drought_idx = climate_shifts.get("drought_vulnerability_index", 55)
    
    # Feature vector for ML scoring
    features = {
        "Mean_Temp_C": calibrated_telemetry.get("Calibrated_Temp_C", 27.5),
        "Total_Precip_mm": climate_shifts.get("recent_annual_precip", 720.0),
        "Soil_N": soil_profile.get("n", 180),
        "Soil_P": soil_profile.get("p", 45),
        "Soil_K": soil_profile.get("k", 280),
        "Soil_pH": soil_profile.get("ph", 7.4),
        "Drought_Index": drought_idx,
        "Calibrated_SoilMoisture_pct": calibrated_telemetry.get("Calibrated_SoilMoisture_pct", 23.0)
    }
    
    # ML Suitability Score for Baseline
    baseline_suitability = ml_model.predict_crop_suitability(current_crop, features)
    
    # --- STRATEGY 1: OPTIMIZED BASELINE ---
    # Shift planting calendar depending on monsoon delay / heat trend
    peak_month = climate_shifts.get("recent_peak_month", "Aug")
    if peak_month in ["Aug", "Sep"]:
        sowing_shift = "Delay sowing by 10 to 14 days"
        sowing_rationale = f"NASA data confirms monsoon peak has shifted to {peak_month}. Early sowing risks seed rotting or seedling desiccation."
    else:
        sowing_shift = "Advance sowing by 7 to 10 days"
        sowing_rationale = "Early establishment captures early residual moisture before peak terminal heat."
        
    strategy_1 = {
        "strategy_id": "STRAT_1",
        "name": f"Optimized Baseline: {current_crop} with Climate Adjustments",
        "type": "Optimization",
        "primary_crop": current_crop,
        "suitability_score": baseline_suitability,
        "water_requirement_mm": crop_info["optimal_water_mm"],
        "water_savings_pct": 12, # Achieved via micro-irrigation & adjusted dates
        "soil_n_balance_kg_ha": -90, # Net extraction
        "duration_days": crop_info["duration_days"],
        "sowing_action": sowing_shift,
        "action_steps": [
            f"📅 **Adjusted Sowing Window:** {sowing_shift}. ({sowing_rationale})",
            "💧 **Deficit Irrigation:** Switch to alternate-furrow or pulse-drip during flowering stage to curb 20% water loss.",
            "🌾 **Mulching:** Retain crop residue or apply 5 tonnes/ha straw mulch to buffer against +1.2°C surface heating."
        ],
        "risk_level": "Moderate to High (Sensitive to unmitigated heatwaves/dry spells)",
        "economic_outlook": "Familiar market channels, but vulnerable to rising input and irrigation costs."
    }
    
    # --- STRATEGY 2: SOIL BUILDER (Nitrogen-Fixing Legume) ---
    # Pick optimal soil builder depending on soil pH and current season
    soil_builders = ["Chickpea (Gram)", "Moong (Green Gram)", "Pigeon Pea (Arhar / Tur)", "Cowpea (Lobia)"]
    builder_scores = {c: ml_model.predict_crop_suitability(c, features) for c in soil_builders}
    best_builder_crop = max(builder_scores, key=builder_scores.get)
    best_builder_info = CROP_CATALOG[best_builder_crop]
    
    strategy_2 = {
        "strategy_id": "STRAT_2",
        "name": f"Soil Builder Rotation: {best_builder_crop}",
        "type": "Regenerative / Soil Restoration",
        "primary_crop": best_builder_crop,
        "suitability_score": builder_scores[best_builder_crop],
        "water_requirement_mm": best_builder_info["optimal_water_mm"],
        "water_savings_pct": best_builder_info.get("water_saving_pct", 55),
        "soil_n_balance_kg_ha": f"+{best_builder_info.get('n_fixation_kg_ha', 60)} (Biological N Fixation)",
        "duration_days": best_builder_info["duration_days"],
        "sowing_action": "Plant immediately after Kharif harvest or as pre-monsoon catch crop",
        "action_steps": [
            f"🌱 **Rhizobium Inoculation:** Treat seeds with *Rhizobium leguminosarum* culture to maximize biological nitrogen fixation (+{best_builder_info.get('n_fixation_kg_ha', 60)} kg N/ha).",
            f"💧 **Water Conservation:** Requires only {best_builder_info['optimal_water_mm']} mm water, saving ~{best_builder_info.get('water_saving_pct', 55)}% compared to {current_crop}.",
            f"🧪 **Fertilizer Offset:** Reduces next season's synthetic urea purchase by 40-50%, saving approx ₹1,800/acre in input costs."
        ],
        "risk_level": "Low (Deep taproot system tolerates moderate dry spells)",
        "economic_outlook": f"Strong commercial demand with Government MSP price support; restores degraded soil organic carbon."
    }
    
    # --- STRATEGY 3: CLIMATE RESILIENT (Drought-Tolerant Cash Crop) ---
    resilient_candidates = ["Pearl Millet (Bajra)", "Sorghum (Jowar)", "Finger Millet (Ragi)", "Mustard (Rabi Oilseed)"]
    resilient_scores = {c: ml_model.predict_crop_suitability(c, features) for c in resilient_candidates}
    best_resilient_crop = max(resilient_scores, key=resilient_scores.get)
    best_resilient_info = CROP_CATALOG[best_resilient_crop]
    
    strategy_3 = {
        "strategy_id": "STRAT_3",
        "name": f"Climate Resilient & Cash Crop: {best_resilient_crop}",
        "type": "Climate Adaptation & High Resilience",
        "primary_crop": best_resilient_crop,
        "suitability_score": resilient_scores[best_resilient_crop],
        "water_requirement_mm": best_resilient_info["optimal_water_mm"],
        "water_savings_pct": best_resilient_info.get("water_saving_pct", 65),
        "soil_n_balance_kg_ha": -35, # Low depletion
        "duration_days": best_resilient_info["duration_days"],
        "sowing_action": "Direct seeding with broad-bed furrow on first steady monsoon shower",
        "action_steps": [
            f"☀️ **Extreme Thermal Tolerance:** Photosynthesizes effectively up to 42°C with minimal leaf scorching.",
            f"🛡️ **Drought Insurance:** Requires only {best_resilient_info['optimal_water_mm']} mm total water ({best_resilient_info.get('water_saving_pct', 65)}% water saving), thriving even during 20-day dry spells.",
            "🌾 **Dual-Revenue Stream:** High grain yield + valuable dry fodder/biofuel biomass creates dual revenue security."
        ],
        "risk_level": "Very Low (Highest climate resilience index in the portfolio)",
        "economic_outlook": "Rapidly expanding market value driven by nutritional superfood demand and industrial bio-ethanol processing."
    }
    
    # Comparative summary table
    comparison_df = pd.DataFrame([
        {
            "Strategy": "1. Optimized Baseline",
            "Crop": strategy_1["primary_crop"],
            "Suitability Score": f"{strategy_1['suitability_score']}%",
            "Water Needed (mm)": f"{strategy_1['water_requirement_mm']} mm",
            "Water Savings": f"{strategy_1['water_savings_pct']}%",
            "Soil N Impact": f"{strategy_1['soil_n_balance_kg_ha']} kg/ha",
            "Duration": f"{strategy_1['duration_days']} days",
            "Drought Resilience": "Medium"
        },
        {
            "Strategy": "2. Soil Builder (Legume)",
            "Crop": strategy_2["primary_crop"],
            "Suitability Score": f"{strategy_2['suitability_score']}%",
            "Water Needed (mm)": f"{strategy_2['water_requirement_mm']} mm",
            "Water Savings": f"{strategy_2['water_savings_pct']}%",
            "Soil N Impact": str(strategy_2['soil_n_balance_kg_ha']),
            "Duration": f"{strategy_2['duration_days']} days",
            "Drought Resilience": "High"
        },
        {
            "Strategy": "3. Climate Resilient",
            "Crop": strategy_3["primary_crop"],
            "Suitability Score": f"{strategy_3['suitability_score']}%",
            "Water Needed (mm)": f"{strategy_3['water_requirement_mm']} mm",
            "Water Savings": f"{strategy_3['water_savings_pct']}%",
            "Soil N Impact": f"{strategy_3['soil_n_balance_kg_ha']} kg/ha",
            "Duration": f"{strategy_3['duration_days']} days",
            "Drought Resilience": "Extreme"
        }
    ])
    
    return {
        "strategy_1": strategy_1,
        "strategy_2": strategy_2,
        "strategy_3": strategy_3,
        "comparison_table": comparison_df
    }

