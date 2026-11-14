"""
Field Shift: Climate-Smart Crop Rotation Decision-Support Platform
NASA Space Apps Challenge 2026 - Team Gandharvas

Architecture:
- NASA POWER API (Lightweight Tabular REST data for historical weather/climate shifts)
- Village/Tehsil Community Node (ESP32 Ground-Truth Calibration Engine)
- Scikit-Learn / Tabular ML Ensemble for Agronomic Suitability
- Optimized for Intel i5 12th Gen, 16GB RAM, RTX 2050 (4GB VRAM)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Import modular application components
from config import APP_TITLE, APP_SUBTITLE, TEAM_NAME, DEFAULT_LOCATIONS, CROP_CATALOG
from modules.nasa_power import fetch_nasa_power_climate
from modules.community_node import CommunityNodeEngine
from modules.climate_analysis import compute_climate_shifts
from modules.ml_model import CropSuitabilityModel
from modules.rotation_engine import generate_rotation_strategies
from modules.visualizer import (
    create_climate_trend_chart,
    create_seasonality_shift_chart,
    create_calibration_comparison_chart,
    create_strategy_radar_comparison
)

# Page configuration
st.set_page_config(
    page_title="Field Shift | Team Gandharvas",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished NASA Hackathon aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a365d;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4a5568;
        margin-bottom: 15px;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 8px;
    }
    .badge-nasa { background-color: #ebf8ff; color: #2b6cb0; border: 1px solid #bee3f8; }
    .badge-iot { background-color: #f0fff4; color: #276749; border: 1px solid #c6f6d5; }
    .badge-hw { background-color: #faf5ff; color: #6b46c1; border: 1px solid #e9d8fd; }
    .strategy-card {
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Cache ML Model in Streamlit session state
@st.cache_resource
def load_ml_model():
    return CropSuitabilityModel()

ml_model = load_ml_model()

# --- TOP HEADER ---
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.markdown(f"<div class='main-header'>🌾 {APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>{APP_SUBTITLE} • <b>{TEAM_NAME}</b></div>", unsafe_allow_html=True)
    st.markdown("""
        <span class='badge-pill badge-nasa'>🛰️ NASA POWER & SMAP</span>
        <span class='badge-pill badge-iot'>📡 Village Community Node (ESP32)</span>
        <span class='badge-pill badge-hw'>⚡ Tabular ML Engine (4GB VRAM Capable)</span>
    """, unsafe_allow_html=True)

st.write("")

# --- SIDEBAR: USER & FARM CONFIGURATION ---
with st.sidebar:
    st.header("📍 Farm Location & Profile")
    
    selected_preset = st.selectbox(
        "Select Agricultural Hub (or Custom):",
        list(DEFAULT_LOCATIONS.keys())
    )
    
    preset_data = DEFAULT_LOCATIONS[selected_preset]
    
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat = st.number_input("Latitude", value=float(preset_data["lat"]), format="%.4f")
    with col_lon:
        lon = st.number_input("Longitude", value=float(preset_data["lon"]), format="%.4f")
        
    st.caption(f"**Region:** {preset_data['region']}")
    st.caption(f"**Linked Community Node:** `{preset_data['node_id']}`")
    
    st.divider()
    st.subheader("🌱 Current Crop & Soil Health")
    
    current_crop = st.selectbox(
        "Current Primary Crop:",
        list(CROP_CATALOG.keys())[:5], # Primary monocultures
        index=0 if preset_data["primary_crop"] not in list(CROP_CATALOG.keys())[:5] 
              else list(CROP_CATALOG.keys())[:5].index(preset_data["primary_crop"])
    )
    
    farm_size_acres = st.number_input("Farm Size (Acres):", min_value=1.0, max_value=500.0, value=5.0, step=0.5)
    
    with st.expander("🧪 Soil Test Parameters (NPK & pH)", expanded=False):
        soil_n = st.slider("Available Nitrogen (N kg/ha):", 50, 400, preset_data["default_n"])
        soil_p = st.slider("Available Phosphorus (P kg/ha):", 10, 100, preset_data["default_p"])
        soil_k = st.slider("Available Potassium (K kg/ha):", 80, 500, preset_data["default_k"])
        soil_ph = st.slider("Soil pH:", 5.0, 9.0, preset_data["default_ph"], step=0.1)
        soil_type = st.text_input("Soil Texture / Type:", preset_data["soil_type"])
        
    soil_profile = {
        "n": soil_n,
        "p": soil_p,
        "k": soil_k,
        "ph": soil_ph,
        "soil_type": soil_type,
        "farm_size": farm_size_acres
    }
    
    st.divider()
    run_analysis = st.button("🚀 Run Climate & Rotation Analysis", type="primary", use_container_width=True)

# --- DATA INGESTION & PROCESSING ---
@st.cache_data(show_spinner=False)
def get_cached_climate(latitude: float, longitude: float):
    return fetch_nasa_power_climate(latitude, longitude, start_year=2014, end_year=2024)

with st.spinner("Connecting to NASA POWER Earth Observations & Village Node Telemetry..."):
    df_climate = get_cached_climate(lat, lon)
    climate_shifts = compute_climate_shifts(df_climate)
    
    # Community Node Instance
    node_engine = CommunityNodeEngine(node_id=preset_data.get("node_id", "COMM_NODE_001"))
    
    # Representative latest telemetry
    latest_temp = df_climate["Temperature_C"].iloc[-1] if not df_climate.empty else 28.5
    latest_precip = df_climate["Precipitation_mm"].iloc[-1] if not df_climate.empty else 45.0
    df_telemetry = node_engine.generate_ground_truth_telemetry(latest_temp, latest_precip)
    calibration_metrics = node_engine.calculate_calibration_metrics(df_telemetry)
    
    latest_calibrated = df_telemetry.iloc[-1].to_dict()
    
    # Rotation Engine Synthesis
    strategies = generate_rotation_strategies(
        current_crop=current_crop,
        climate_shifts=climate_shifts,
        soil_profile=soil_profile,
        calibrated_telemetry=latest_calibrated,
        ml_model=ml_model
    )

# --- MAIN TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🏡 Farm Profile & Status",
    "📈 Climate Shift Analysis (NASA POWER)",
    "🛰️ Community Node Calibration (USP)",
    "🔄 3-Strategy Rotation Engine"
])

# ==============================================================================
# TAB 1: FARM PROFILE & STATUS
# ==============================================================================
with tab1:
    st.subheader(f"Agro-Climatic Baseline: {selected_preset.split(' - ')[0]}")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Latitude / Longitude", f"{lat:.2f}°, {lon:.2f}°")
    with m_col2:
        st.metric("Current Primary Crop", current_crop)
    with m_col3:
        st.metric("Soil Type", soil_type)
    with m_col4:
        st.metric("Drought Vulnerability Index", f"{climate_shifts.get('drought_vulnerability_index', 50)}/100", 
                  delta=f"{climate_shifts.get('temp_delta', 0.6):+.2f}°C Warming", delta_color="inverse")
        
    st.divider()
    
    p_col1, p_col2 = st.columns([1, 1])
    with p_col1:
        st.markdown("#### 🗺️ Geographic & Satellite Grid Overview")
        map_df = pd.DataFrame([{"lat": lat, "lon": lon}])
        st.map(map_df, zoom=9)
        st.caption(f"Blue marker denotes farm centroid within NASA 9x9 km satellite footprint (Node: `{preset_data['node_id']}`).")
        
    with p_col2:
        st.markdown("#### 🧪 Field Soil Fertility Diagnostics")
        soil_n_status = "Optimal" if 200 <= soil_n <= 300 else ("Low (Nitrogen Depleted)" if soil_n < 200 else "High")
        st.write(f"• **Nitrogen (N):** `{soil_n} kg/ha` — *{soil_n_status}*")
        st.write(f"• **Phosphorus (P):** `{soil_p} kg/ha` — *{'Adequate' if soil_p >= 30 else 'Deficient'}*")
        st.write(f"• **Potassium (K):** `{soil_k} kg/ha` — *{'Optimal' if soil_k >= 200 else 'Low'}*")
        st.write(f"• **Soil pH:** `{soil_ph}` — *{'Neutral' if 6.5 <= soil_ph <= 7.5 else ('Alkaline' if soil_ph > 7.5 else 'Acidic')}*")
        
        st.markdown("#### ⚙️ Monoculture Impact Analysis")
        crop_details = CROP_CATALOG[current_crop]
        st.warning(f"**{current_crop} Vulnerability:** {crop_details['soil_impact']}. "
                   f"Requires **{crop_details['optimal_water_mm']} mm** water/season, with {crop_details['drought_tolerance'].lower()} drought tolerance.")

# ==============================================================================
# TAB 2: CLIMATE SHIFT ANALYSIS (NASA POWER DATA)
# ==============================================================================
with tab2:
    st.subheader("10-Year Agro-Climatic Trajectory (2014 – 2024)")
    st.markdown("Powered by **NASA Langley Research Center POWER API** (Solar & Meteorological Surface Climatology).")
    
    # 4 Quick Metric Badges
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1:
        st.metric("10-Yr Mean Warming", f"+{climate_shifts.get('temp_delta', 0.5):.2f} °C", 
                  f"{climate_shifts.get('temp_slope_per_decade', 0.5):+.2f}°C/decade", delta_color="inverse")
    with c_col2:
        st.metric("Annual Rainfall Shift", f"{climate_shifts.get('precip_delta_mm', -35.0):+.1f} mm",
                  f"{climate_shifts.get('precip_delta_pct', -5.0):+.1f}% vs baseline", delta_color="normal")
    with c_col3:
        st.metric("Monsoon Peak Timing", f"{climate_shifts.get('recent_peak_month', 'Aug')}", 
                  f"Baseline was {climate_shifts.get('early_peak_month', 'Jul')}")
    with c_col4:
        st.metric("Precipitation Volatility", f"{climate_shifts.get('precip_cv', 22.0):.1f}%", 
                  "Year-over-Year CV")
        
    st.write("")
    
    # Dual-Axis Plotly Chart
    fig_climate = create_climate_trend_chart(climate_shifts["annual_data"])
    st.plotly_chart(fig_climate, use_container_width=True)
    
    col_sea, col_ins = st.columns([1, 1])
    with col_sea:
        fig_season = create_seasonality_shift_chart(
            climate_shifts["monthly_early"], 
            climate_shifts["monthly_recent"],
            climate_shifts["early_period"],
            climate_shifts["recent_period"]
        )
        st.plotly_chart(fig_season, use_container_width=True)
        
    with col_ins:
        st.markdown("#### 🔍 AI Shift Diagnostics")
        for insight in climate_shifts["insights"]:
            st.markdown(insight)
        st.info("💡 **Key Takeaway for Rotation:** Prolonged dry spells during crop reproductive stages make continuous monocropping hazardous. A multi-tier rotation balances root depth, water extraction, and soil microbial vitality.")

# ==============================================================================
# TAB 3: COMMUNITY NODE CALIBRATION (USP TAB)
# ==============================================================================
with tab3:
    st.subheader("The 'Gandharvas' USP: Village/Tehsil Community Node Model")
    
    st.markdown("""
    > **The Problem:** NASA satellite observations (like SMAP and NASA POWER) have a 9x9 km grid cell. Micro-topography, canopy shading, and localized showers are blurred out. Yet, expecting smallholder farmers to buy and maintain individual IoT sensors on every plot is impractical.
    > 
    > **The Solution:** A single, rugged **Automatic Weather & Soil Station (AWS)** deployed at the Gram Panchayat / Krishi Vigyan Kendra serves a **5–10 km radius**. It acts as the local ground-truth calibration node, downscaling and bias-correcting satellite observations automatically.
    """)
    
    # Calibration KPI Cards
    k_col1, k_col2, k_col3, k_col4 = st.columns(4)
    with k_col1:
        st.metric("Node ID", calibration_metrics["node_id"], "Active Telemetry")
    with k_col2:
        st.metric("Coverage Radius", f"{calibration_metrics['coverage_radius_km']} km", "Village Radius")
    with k_col3:
        st.metric("Temp Error Reduction", f"{calibration_metrics['temp_accuracy_gain_pct']}%", 
                  f"MAE {calibration_metrics['raw_temp_mae']}°C → {calibration_metrics['calibrated_temp_mae']}°C")
    with k_col4:
        st.metric("Soil Moisture Accuracy Gain", f"{calibration_metrics['sm_accuracy_gain_pct']}%", 
                  f"MAE {calibration_metrics['raw_soil_moisture_mae']}% → {calibration_metrics['calibrated_soil_moisture_mae']}%")
        
    st.divider()
    
    # 30-Day Calibration Plot
    st.markdown("#### 📡 30-Day Ground-Truth Calibration (Satellite vs. ESP32 vs. Calibrated)")
    fig_calib = create_calibration_comparison_chart(df_telemetry)
    st.plotly_chart(fig_calib, use_container_width=True)
    
    with st.expander("🛠️ View Calibration Mathematical Framework & Hardware Specs", expanded=False):
        c_code_col, c_spec_col = st.columns(2)
        with c_code_col:
            st.markdown("**Sensor Fusion Equation:**")
            st.latex(r"X_{calibrated}(t) = \alpha \cdot X_{ground\_ESP32}(t) + (1 - \alpha) \cdot X_{satellite\_grid}(t)")
            st.markdown("Where $\\alpha = 0.75$ assigns higher statistical confidence to immediate localized ground measurements while preserving regional macro trends.")
        with c_spec_col:
            st.markdown("**Hardware Node Specifications:**")
            st.markdown("- **MCU:** ESP32 Dual-Core 240MHz with 4MB Flash\n- **Temp/RH:** Sensirion SHT31-D (±0.2°C accuracy)\n- **Soil Moisture:** Capacitive Corrosion-Resistant VWC Probe (10cm depth)\n- **Power:** 3.7V 18650 Li-Ion with 5W Monocrystalline Solar Panel")

# ==============================================================================
# TAB 4: 3-STRATEGY ROTATION ENGINE
# ==============================================================================
with tab4:
    st.subheader("Actionable Crop Rotation Advisory")
    st.markdown("Recommending 3 science-backed strategies to safeguard farm revenue, restore depleted soil organic nitrogen, and buffer against climate variability.")
    
    strat1 = strategies["strategy_1"]
    strat2 = strategies["strategy_2"]
    strat3 = strategies["strategy_3"]
    
    sc1, sc2, sc3 = st.columns(3)
    
    # Strategy 1 Card
    with sc1:
        st.markdown(f"""
        <div class='strategy-card' style='border-top: 4px solid #3182ce;'>
            <h4 style='color: #2b6cb0; margin-bottom: 4px;'>Strategy 1: Optimized Baseline</h4>
            <h3 style='margin-top: 0;'>{strat1['primary_crop']}</h3>
            <p><b>Suitability:</b> {strat1['suitability_score']}% &nbsp;|&nbsp; <b>Risk:</b> {strat1['risk_level'].split(' ')[0]}</p>
            <p><b>Water Required:</b> {strat1['water_requirement_mm']} mm (<b>{strat1['water_savings_pct']}% saved</b>)</p>
            <p><b>Soil N Balance:</b> {strat1['soil_n_balance_kg_ha']} kg/ha (Depleting)</p>
            <p><b>Cycle Duration:</b> {strat1['duration_days']} days</p>
            <hr style='margin: 10px 0;'>
            <b>Action Plan:</b>
        </div>
        """, unsafe_allow_html=True)
        for act in strat1["action_steps"]:
            st.markdown(act)
            
    # Strategy 2 Card
    with sc2:
        st.markdown(f"""
        <div class='strategy-card' style='border-top: 4px solid #38a169;'>
            <h4 style='color: #276749; margin-bottom: 4px;'>Strategy 2: Soil Builder (Legume)</h4>
            <h3 style='margin-top: 0;'>{strat2['primary_crop']}</h3>
            <p><b>Suitability:</b> {strat2['suitability_score']}% &nbsp;|&nbsp; <b>Risk:</b> {strat2['risk_level'].split(' ')[0]}</p>
            <p><b>Water Required:</b> {strat2['water_requirement_mm']} mm (<b>{strat2['water_savings_pct']}% saved</b>)</p>
            <p><b>Soil N Balance:</b> <span style='color: #22543d; font-weight: bold;'>{strat2['soil_n_balance_kg_ha']}</span></p>
            <p><b>Cycle Duration:</b> {strat2['duration_days']} days</p>
            <hr style='margin: 10px 0;'>
            <b>Action Plan:</b>
        </div>
        """, unsafe_allow_html=True)
        for act in strat2["action_steps"]:
            st.markdown(act)
            
    # Strategy 3 Card
    with sc3:
        st.markdown(f"""
        <div class='strategy-card' style='border-top: 4px solid #d69e2e;'>
            <h4 style='color: #b7791f; margin-bottom: 4px;'>Strategy 3: Climate Resilient & Cash</h4>
            <h3 style='margin-top: 0;'>{strat3['primary_crop']}</h3>
            <p><b>Suitability:</b> {strat3['suitability_score']}% &nbsp;|&nbsp; <b>Risk:</b> {strat3['risk_level'].split(' ')[0]}</p>
            <p><b>Water Required:</b> {strat3['water_requirement_mm']} mm (<b>{strat3['water_savings_pct']}% saved</b>)</p>
            <p><b>Soil N Balance:</b> {strat3['soil_n_balance_kg_ha']} kg/ha (Minimal)</p>
            <p><b>Cycle Duration:</b> {strat3['duration_days']} days</p>
            <hr style='margin: 10px 0;'>
            <b>Action Plan:</b>
        </div>
        """, unsafe_allow_html=True)
        for act in strat3["action_steps"]:
            st.markdown(act)
            
    st.write("")
    st.divider()
    
    # Side-by-side Table & Radar Comparison
    tbl_col, chart_col = st.columns([1, 1])
    with tbl_col:
        st.markdown("#### 📊 Side-by-Side Multi-Criteria Matrix")
        st.dataframe(strategies["comparison_table"], hide_index=True, use_container_width=True)
        
        # Downloadable Farmer Advisory Report
        report_text = f"""========================================================================
FIELD SHIFT: CLIMATE-SMART CROP ROTATION ADVISORY
Team Gandharvas - NASA Space Apps Challenge 2026
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================================================
FARM LOCATION: {selected_preset}
COORDINATES: {lat:.4f} N, {lon:.4f} E
COMMUNITY CALIBRATION NODE: {preset_data['node_id']}
PRIMARY CROP: {current_crop} | FARM SIZE: {farm_size_acres} Acres
------------------------------------------------------------------------
CLIMATE SHIFT SUMMARY (NASA POWER):
- 10-Year Temperature Shift: {climate_shifts.get('temp_delta', 0.5):+.2f} °C
- Annual Precipitation Shift: {climate_shifts.get('precip_delta_pct', -5.0):+.1f} %
- Drought Vulnerability Index: {climate_shifts.get('drought_vulnerability_index', 50)}/100
- Monsoon Peak Timing: Shifted to {climate_shifts.get('recent_peak_month', 'Aug')}

RECOMMENDED 3-TIER ROTATION STRATEGIES:
1. STRATEGY 1 (OPTIMIZED BASELINE): {strat1['primary_crop']}
   - Suitability: {strat1['suitability_score']}% | Water Need: {strat1['water_requirement_mm']} mm
   - Sowing Window: {strat1['sowing_action']}

2. STRATEGY 2 (SOIL BUILDER): {strat2['primary_crop']}
   - Suitability: {strat2['suitability_score']}% | Water Savings: {strat2['water_savings_pct']}%
   - Nitrogen Restored: {strat2['soil_n_balance_kg_ha']}

3. STRATEGY 3 (CLIMATE RESILIENT): {strat3['primary_crop']}
   - Suitability: {strat3['suitability_score']}% | Water Savings: {strat3['water_savings_pct']}%
   - Extreme Thermal Resilience up to 42°C
========================================================================
"""
        st.download_button(
            label="📄 Download Official Advisory Report (TXT)",
            data=report_text,
            file_name=f"FieldShift_Advisory_{lat:.2f}_{lon:.2f}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with chart_col:
        fig_radar = create_strategy_radar_comparison(strategies)
        st.plotly_chart(fig_radar, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #718096; font-size: 0.85rem;'>"
    "Developed with ❤️ by <b>Team Gandharvas</b> for the <b>NASA Space Apps Challenge 2026</b>.<br>"
    "Datasets: NASA POWER API (Solar & Meteorological) • NASA SMAP (Soil Moisture) • FAO GAEZ Standards"
    "</div>", 
    unsafe_allow_html=True
)
