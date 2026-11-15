"""
RituChakra: Field Shift
NASA Space Apps Challenge 2026 - Team Gandharvas

Design Standards:
- Themes: Clean Light Mode (Default) & Deep Space Dark Mode
- Corner Geometry: Crisp, modern enterprise corners (3px–4px radius; zero bubbly AI-made artifacts)
- Color Harmony: Scientific NASA Blue (#0B3D91) combined with Agriculture Emerald Green (#059669),
  Harvest Gold (#CA8A04), and Earth Slate (#0F172A)
- High Contrast: 100% readable font colors, zero white-on-white or dark-on-dark text
- Robust Location Management: Direct Mapbox search selection that never gets overwritten by GPS jitter
- Restrained Vector Icons: Minimal, crisp inline SVGs placed strictly where functional clarity is needed
"""

import streamlit as st
import os
import pandas as pd
import numpy as np
import base64
import socket
from datetime import datetime

# Import modular application components
from config import (
    APP_TITLE,
    APP_SUBTITLE,
    TEAM_NAME,
    DEFAULT_LOCATIONS,
    CROP_CATALOG,
    GEOAPIFY_API_KEY,
    MAPBOX_ACCESS_TOKEN
)
from modules.geocoder import search_locations, reverse_geocode
from modules.gps import get_browser_gps
from modules.nasa_power import fetch_nasa_power_climate
from modules.community_node import CommunityNodeEngine
from modules.climate_analysis import compute_climate_shifts
from modules.ml_model import CropSuitabilityModel
from modules.rotation_engine import generate_rotation_strategies
from modules.visualizer import (
    create_climate_trend_chart,
    create_seasonality_shift_chart,
    create_calibration_comparison_chart,
    create_strategy_radar_comparison,
    create_bme280_pressure_trend_chart,
    create_digital_twin_projection_chart,
    create_field_satellite_map
)

# Page configuration
st.set_page_config(
    page_title="RituChakra | NASA Space Apps Challenge 2026",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load official NASA logo vector
try:
    with open("assets/nasa_logo.svg", "rb") as f:
        nasa_logo_b64 = base64.b64encode(f.read()).decode()
except Exception:
    nasa_logo_b64 = ""

# Vector Icon Library (Crisp, refined 15px SVGs - Functional & Restrained)
SVG_PIN = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>'
SVG_TEMP = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path></svg>'
SVG_DROP = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></svg>'
SVG_LEAF = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path></svg>'
SVG_CHART = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
SVG_SHIELD = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
SVG_ANTENNA = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"></path><path d="M12 12v9"></path><path d="m8 17 4 4 4-4"></path></svg>'
SVG_FLASK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><path d="M10 2v7.31L4.35 19.46A2 2 0 0 0 6.09 22h11.82a2 2 0 0 0 1.74-2.54L14 9.31V2"></path><line x1="8.5" y1="2" x2="15.5" y2="2"></line><line x1="6.5" y1="16" x2="17.5" y2="16"></line></svg>'
SVG_CHECK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px;"><polyline points="20 6 9 17 4 12"></polyline></svg>'

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"
if "current_lat" not in st.session_state:
    st.session_state.current_lat = 20.9320
if "current_lon" not in st.session_state:
    st.session_state.current_lon = 77.7523
if "location_name" not in st.session_state:
    st.session_state.location_name = "Amravati, Vidarbha (MH)"
if "location_zone" not in st.session_state:
    st.session_state.location_zone = "Semi-Arid Central India"
if "location_node_id" not in st.session_state:
    st.session_state.location_node_id = "COMM_NODE_MH_042"
if "location_lock_mode" not in st.session_state:
    st.session_state.location_lock_mode = "default"

if "use_custom_node" not in st.session_state:
    st.session_state.use_custom_node = False
if "custom_node_id" not in st.session_state:
    st.session_state.custom_node_id = "MY_FARM_ESP32_01"
if "custom_telemetry_data" not in st.session_state:
    st.session_state.custom_telemetry_data = {
        "soil_moisture": 32.5,
        "soil_temp": 28.0,
        "temp": 30.5,
        "humidity": 68.0,
        "pressure": 1008.2,
        "rain_mm": 0.0
    }

is_dark = (st.session_state.theme_mode == "Dark")
theme_param = "dark" if is_dark else "light"

# Dynamic Palette Definition (Clean White Default vs Deep Space Dark)
if is_dark:
    c_bg = "#051126"
    c_text = "#FFFFFF"
    c_text_muted = "#94A3B8"
    c_card_bg = "#0B1E3F"
    c_card_border = "#1E3A6B"
    c_sidebar_bg = "#030C1C"
    c_sidebar_border = "#1E3A6B"
    c_tab_bar_bg = "#071731"
    c_tab_bar_border = "#1E3A6B"
    c_tab_inactive_color = "#94A3B8"
    c_tab_active_bg = "#0B3D91"
    c_tab_active_text = "#FFFFFF"
    c_ribbon_bg = "#030C1C"
    c_ribbon_border = "#1E3A6B"
    c_stats_grid_bg = "#071731"
    c_stats_grid_border = "#162E56"
    c_reasoning_bg = "#071731"
    c_reasoning_border = "#38BDF8"
    c_reasoning_text = "#CBD5E1"
    c_econ_bg = "#071731"
    c_econ_border = "#162E56"
    c_input_bg = "#071731"
    c_input_border = "#1E3A6B"
    c_input_text = "#FFFFFF"
    c_footer_bg = "#030C1C"
    c_footer_border = "#1E3A6B"
    c_strip_bg = "#0B1E3F"
    c_strip_border = "#1E3A6B"
    c_strip_text = "#CBD5E1"
    c_strip_logo = "#60A5FA"
    c_primary_btn = "#D4E838"
    c_primary_btn_text = "#030C1C"
    c_accent_green = "#10B981"
    c_accent_gold = "#D4E838"
    c_accent_blue = "#38BDF8"
else:
    c_bg = "#F8FAFC"
    c_text = "#0F172A"
    c_text_muted = "#475569"
    c_card_bg = "#FFFFFF"
    c_card_border = "#CBD5E1"
    c_sidebar_bg = "#F1F5F9"
    c_sidebar_border = "#CBD5E1"
    c_tab_bar_bg = "#E2E8F0"
    c_tab_bar_border = "#CBD5E1"
    c_tab_inactive_color = "#334155"
    c_tab_active_bg = "#0B3D91"
    c_tab_active_text = "#FFFFFF"
    c_ribbon_bg = "#FFFFFF"
    c_ribbon_border = "#CBD5E1"
    c_stats_grid_bg = "#F1F5F9"
    c_stats_grid_border = "#CBD5E1"
    c_reasoning_bg = "#ECFDF5"
    c_reasoning_border = "#059669"
    c_reasoning_text = "#064E3B"
    c_econ_bg = "#F8FAFC"
    c_econ_border = "#CBD5E1"
    c_input_bg = "#FFFFFF"
    c_input_border = "#94A3B8"
    c_input_text = "#0F172A"
    c_footer_bg = "#F1F5F9"
    c_footer_border = "#CBD5E1"
    c_strip_bg = "#FFFFFF"
    c_strip_border = "#CBD5E1"
    c_strip_text = "#334155"
    c_strip_logo = "#0B3D91"
    c_primary_btn = "#059669"
    c_primary_btn_text = "#FFFFFF"
    c_accent_green = "#059669"
    c_accent_gold = "#B45309"
    c_accent_blue = "#0369A1"

# Injected CSS: Universal Contrast, Crisp 4px Corners, Inter Font
st.html(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* Global Canvas */
    html, body, .stApp {{
        background-color: {c_bg} !important;
        color: {c_text} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        overflow-x: hidden !important;
    }}

    /* Universal Text Color Enforcement */
    .stApp,
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] span,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stMarkdownContainer"] div,
    .stApp [data-testid="stWidgetLabel"] label,
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stWidgetLabel"] span,
    .stApp [data-testid="stRadio"] label,
    .stApp [data-testid="stRadio"] div,
    .stApp [data-testid="stRadio"] span,
    .stApp [data-testid="stRadio"] p,
    .stApp [data-testid="stSlider"] label,
    .stApp [data-testid="stSlider"] div,
    .stApp [data-testid="stSlider"] span,
    .stApp [data-testid="stSlider"] p,
    .stApp [data-testid="stSelectbox"] label,
    .stApp [data-testid="stSelectbox"] span,
    .stApp [data-testid="stTextInput"] label,
    .stApp [data-testid="stNumberInput"] label {{
        color: {c_text} !important;
    }}

    .stApp [data-testid="stCaptionContainer"] p,
    .stApp small,
    .stApp .stCaption {{
        color: {c_text_muted} !important;
        font-weight: 500 !important;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6, .app-heading, .barlow-caps {{
        font-family: 'Inter', -apple-system, sans-serif !important;
        letter-spacing: -0.01em !important;
        font-weight: 700 !important;
        text-transform: none !important;
        color: {c_text} !important;
    }}

    /* Crisp Enterprise Buttons (4px radius - No AI bubbly capsules) */
    div.stButton > button {{
        min-height: 40px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 4px !important;
        border: 1px solid {c_card_border} !important;
        background-color: {c_card_bg} !important;
        color: {c_text} !important;
    }}

    div.stButton > button[kind="primary"] {{
        background-color: {c_primary_btn} !important;
        color: {c_primary_btn_text} !important;
        border: 1px solid {c_primary_btn} !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
    }}

    /* Inputs, Selectboxes, Number Inputs */
    div[data-baseweb="input"] input {{
        background-color: {c_input_bg} !important;
        color: {c_input_text} !important;
        border: 1px solid {c_input_border} !important;
        border-radius: 4px !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: {c_input_bg} !important;
        border: 1px solid {c_input_border} !important;
        border-radius: 4px !important;
    }}
    div[data-baseweb="select"] span {{
        color: {c_input_text} !important;
    }}

    /* Top Navbar (Clean positive flow - No negative margins) */
    .spaceapps-navbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 20px;
        background-color: #0B3D91;
        border-bottom: 1px solid #072559;
        border-radius: 4px;
        margin-bottom: 14px;
    }}

    .spaceapps-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .spaceapps-nav-links {{
        display: flex;
        align-items: center;
        gap: 18px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #E2E8F0;
    }}

    .btn-citron-cta {{
        background-color: #D4E838;
        color: #030C1C;
        font-weight: 700;
        font-size: 0.80rem;
        padding: 6px 14px;
        border-radius: 4px;
        text-decoration: none;
        display: inline-block;
    }}

    /* NASA Blue Hero Section */
    .spaceapps-hero {{
        background-color: #0B3D91;
        border-radius: 4px;
        padding: 22px 26px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #1E4CB8;
        gap: 20px;
    }}

    .hero-text-col {{
        max-width: 68%;
    }}

    .hero-title {{
        font-size: 1.80rem;
        font-weight: 800;
        line-height: 1.25;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }}

    .hero-subtitle-citron {{
        font-size: 1.15rem;
        font-weight: 700;
        color: #D4E838 !important;
        margin-bottom: 8px;
    }}

    .hero-sub {{
        font-size: 0.92rem;
        font-weight: 450;
        color: #E2E8F0 !important;
        line-height: 1.5;
        margin-bottom: 14px;
        max-width: 640px;
    }}

    .hero-badges-row {{
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }}

    .hero-badge-item {{
        background-color: #072559;
        border: 1px solid #1E4CB8;
        color: #FFFFFF !important;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 3px;
        display: inline-flex;
        align-items: center;
    }}

    /* Partner Agency Strip */
    .agency-strip {{
        background-color: {c_strip_bg};
        padding: 10px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 4px;
        margin-bottom: 18px;
        border: 1px solid {c_strip_border};
    }}

    .agency-left {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .agency-label {{
        color: {c_strip_text} !important;
        font-size: 0.80rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }}

    .agency-logos-row {{
        display: flex;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
    }}

    .agency-mark {{
        font-weight: 800;
        font-size: 0.92rem;
        color: {c_strip_logo} !important;
        letter-spacing: 0.04em;
    }}

    .agency-mark-sub {{
        font-size: 0.65rem;
        font-weight: 600;
        color: {c_text_muted} !important;
        margin-left: 2px;
    }}

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background-color: {c_tab_bar_bg};
        border-radius: 4px;
        padding: 4px;
        border: 1px solid {c_tab_bar_border};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        border-radius: 3px;
        color: {c_tab_inactive_color} !important;
        font-weight: 600;
        font-size: 0.86rem;
        padding: 0 16px;
        border: 1px solid transparent;
        white-space: nowrap;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {c_tab_active_bg} !important;
        color: {c_tab_active_text} !important;
        border: 1px solid {c_tab_active_bg} !important;
    }}

    /* Clean Enterprise Strategy Card */
    .strategy-card {{
        padding: 18px 20px;
        border-radius: 4px;
        background-color: {c_card_bg};
        border: 1px solid {c_card_border};
        margin-bottom: 14px;
        min-height: auto;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}

    .strategy-crop-title {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {c_text} !important;
        letter-spacing: -0.01em;
        margin: 0 0 10px 0;
        line-height: 1.25;
    }}

    .strategy-stats-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px 12px;
        background-color: {c_stats_grid_bg};
        padding: 10px 12px;
        border-radius: 3px;
        border: 1px solid {c_stats_grid_border};
        margin-bottom: 10px;
    }}

    .stat-item {{
        display: flex;
        flex-direction: column;
    }}

    .stat-label {{
        color: {c_text_muted} !important;
        font-size: 0.70rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }}

    .stat-value {{
        color: {c_text} !important;
        font-size: 0.95rem;
        font-weight: 700;
    }}

    .strategy-action-list {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        font-size: 0.88rem;
        color: {c_text} !important;
        line-height: 1.45;
        flex-grow: 1;
    }}

    .action-row {{
        display: flex;
        align-items: flex-start;
        gap: 8px;
        line-height: 1.45;
    }}

    .strategy-reasoning-box {{
        background-color: {c_reasoning_bg};
        border-left: 3px solid {c_reasoning_border};
        padding: 10px 12px;
        border-radius: 3px;
        margin-bottom: 10px;
        font-size: 0.82rem;
        line-height: 1.45;
        color: {c_reasoning_text} !important;
    }}

    .strategy-economic-box {{
        background-color: {c_econ_bg};
        border: 1px solid {c_econ_border};
        padding: 10px 12px;
        border-radius: 3px;
        margin-top: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .econ-label {{
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        color: {c_text_muted} !important;
        letter-spacing: 0.04em;
    }}

    /* Metric Tiles (Crisp 4px radius) */
    [data-testid="stMetric"] {{
        background-color: {c_card_bg} !important;
        border: 1px solid {c_card_border} !important;
        border-radius: 4px !important;
        padding: 12px 16px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }}

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span {{
        color: {c_text_muted} !important;
        font-size: 0.76rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        font-weight: 600 !important;
    }}

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {{
        color: {c_text} !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {c_sidebar_bg} !important;
        border-right: 1px solid {c_sidebar_border} !important;
    }}

    /* Space Apps Expander Styling */
    [data-testid="stExpander"] {{
        background-color: {c_card_bg} !important;
        border: 1px solid {c_card_border} !important;
        border-radius: 4px !important;
        margin-top: 10px !important;
    }}
    [data-testid="stExpander"] summary {{
        display: flex !important;
        align-items: center !important;
        padding: 10px 14px !important;
        color: {c_text} !important;
        cursor: pointer !important;
    }}
    [data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: {c_text} !important;
        margin: 0 !important;
        display: inline-block !important;
    }}

    /* Bulletproof expander icon suppression */
    [data-testid="stExpander"] summary span[data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {{
        font-family: 'Material Symbols Rounded', sans-serif !important;
        font-size: 0px !important;
        color: transparent !important;
        line-height: 0 !important;
        width: 18px !important;
        min-width: 18px !important;
        max-width: 18px !important;
        height: 18px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        vertical-align: middle !important;
        overflow: hidden !important;
        margin-right: 10px !important;
        flex-shrink: 0 !important;
        position: relative !important;
    }}
    [data-testid="stExpander"] summary span[data-testid="stIconMaterial"]::before,
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"]::before {{
        content: '▶' !important;
        font-size: 0.80rem !important;
        color: {c_tab_active_bg} !important;
        line-height: 1 !important;
        display: inline-block !important;
    }}
    [data-testid="stExpander"][open] summary span[data-testid="stIconMaterial"]::before,
    [data-testid="stExpander"][open] summary [data-testid="stIconMaterial"]::before,
    details[open] summary span[data-testid="stIconMaterial"]::before,
    details[open] summary [data-testid="stIconMaterial"]::before {{
        content: '▼' !important;
    }}

    /* Live Telemetry Ribbon */
    .live-data-ribbon {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: {c_ribbon_bg};
        border: 1px solid {c_ribbon_border};
        border-radius: 4px;
        padding: 10px 18px;
        margin: 12px 0 20px 0;
        gap: 16px;
        flex-wrap: wrap;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }}
    .ribbon-item {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        color: {c_text} !important;
        font-weight: 550;
    }}
    .pulse-dot-green {{
        width: 8px;
        height: 8px;
        background-color: #059669;
        border-radius: 50%;
        box-shadow: 0 0 6px #059669;
        display: inline-block;
        flex-shrink: 0;
    }}
    .pulse-dot-yellow {{
        width: 8px;
        height: 8px;
        background-color: #CA8A04;
        border-radius: 50%;
        box-shadow: 0 0 6px #CA8A04;
        display: inline-block;
        flex-shrink: 0;
    }}

    /* Space Apps Footer */
    .spaceapps-footer {{
        margin-top: 36px;
        padding: 18px;
        background-color: {c_footer_bg};
        border-top: 1px solid {c_footer_border};
        border-radius: 4px;
        text-align: center;
        font-size: 0.85rem;
        color: {c_text_muted} !important;
        line-height: 1.6;
    }}

    /* ========================================================================= */
    /* MOBILE & PHONE RESPONSIVE MEDIA QUERIES (<= 768px)                       */
    /* ========================================================================= */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: 0.8rem 0.6rem 2rem 0.6rem !important;
            max-width: 100% !important;
        }}

        [data-testid="column"] {{
            min-width: 100% !important;
            flex: 1 1 100% !important;
            width: 100% !important;
            margin-bottom: 12px !important;
        }}

        .spaceapps-navbar {{
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 10px !important;
            padding: 10px 14px !important;
        }}
        .spaceapps-nav-links {{
            display: none !important;
        }}

        .spaceapps-hero {{
            flex-direction: column !important;
            padding: 18px 16px !important;
            align-items: flex-start !important;
            gap: 14px !important;
        }}
        .hero-text-col {{
            max-width: 100% !important;
        }}
        .hero-title {{
            font-size: 1.35rem !important;
            line-height: 1.25 !important;
        }}
        .hero-subtitle-citron {{
            font-size: 1.02rem !important;
        }}
        .hero-sub {{
            font-size: 0.88rem !important;
            line-height: 1.45 !important;
        }}
        .hero-globe-wrap {{
            display: none !important;
        }}

        .agency-strip {{
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 10px !important;
            padding: 12px 14px !important;
        }}
        .agency-logos-row {{
            gap: 14px !important;
            justify-content: flex-start !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            flex-wrap: nowrap !important;
            padding-bottom: 6px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            white-space: nowrap !important;
            font-size: 0.80rem !important;
            padding: 0 10px !important;
        }}

        .strategy-card {{
            min-height: auto !important;
            margin-bottom: 14px !important;
        }}
        .strategy-stats-grid {{
            grid-template-columns: 1fr 1fr !important;
            gap: 8px !important;
        }}

        .live-data-ribbon {{
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 10px !important;
            padding: 12px 14px !important;
        }}

        [data-testid="stMetric"] {{
            margin-bottom: 8px !important;
        }}
    }}
</style>
""")

# Cache ML Model in Streamlit session state
@st.cache_resource
def load_ml_model():
    return CropSuitabilityModel()

ml_model = load_ml_model()

# ==============================================================================
# TOP NAVBAR
# ==============================================================================
st.html("""
<div class="spaceapps-navbar">
    <div class="spaceapps-brand">
        <svg viewBox="0 0 100 100" width="36" height="36">
            <circle cx="50" cy="50" r="38" fill="none" stroke="#FFFFFF" stroke-width="3"/>
            <circle cx="78" cy="24" r="5" fill="#FFFFFF"/>
            <path d="M78 18 Q86 16 90 22" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M78 12 Q92 10 98 18" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M74 24 Q72 10 82 4" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <div style="line-height: 1.1;">
            <div style="color: #FC3D21; font-size: 0.68rem; font-weight: 800; letter-spacing: 0.12em;">NASA</div>
            <div style="color: #FFFFFF; font-size: 1.05rem; font-weight: 800; letter-spacing: -0.01em;">Space Apps Challenge</div>
            <div style="color: #E2E8F0; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.15em;">GLOBAL CHALLENGE 2026</div>
        </div>
    </div>
    <div class="spaceapps-nav-links">
        <span>Challenge: Shifting Temperatures & Water</span>
        <span>Team: Gandharvas</span>
        <span class="btn-citron-cta">Advisory Active</span>
    </div>
</div>
""")

# ==============================================================================
# SOLID NASA BLUE HERO SECTION
# ==============================================================================
st.html(f"""
<div class="spaceapps-hero">
    <div class="hero-text-col">
        <div class="hero-title">NASA Space Apps Challenge 2026</div>
        <div class="hero-subtitle-citron">
            RituChakra: Field Shift — Climate-Smart Crop Rotation
        </div>
        <div class="hero-sub">
            Empowering farmers with NASA Earth observations (POWER Climatology & SMAP Soil Moisture) fused with in-situ field telemetry to adapt to delayed monsoons, heat stress, and ground water depletion.
        </div>
        <div class="hero-badges-row">
            <span class="hero-badge-item">{SVG_ANTENNA} NASA POWER (10-Yr Climatology)</span>
            <span class="hero-badge-item">{SVG_DROP} NASA SMAP (Soil Moisture L3)</span>
            <span class="hero-badge-item">{SVG_CHART} In-Situ Ground Telemetry</span>
            <span class="hero-badge-item">{SVG_SHIELD} FAO GAEZ Standards</span>
        </div>
    </div>
    
    <div class="hero-globe-wrap" style="flex-shrink: 0;">
        <svg viewBox="0 0 240 240" width="170" height="170">
            <circle cx="120" cy="120" r="90" fill="#072559" stroke="#1E4CB8" stroke-width="2"/>
            <path d="M80 75 Q95 55 125 60 Q150 65 170 85 Q160 115 140 120 Q120 125 105 105 Z" fill="#2563EB" opacity="0.85"/>
            <path d="M100 110 Q120 100 135 115 Q145 135 130 155 Q110 160 95 135 Z" fill="#2563EB" opacity="0.85"/>
            <path d="M135 85 Q165 75 185 95 Q195 115 180 135 Q160 130 145 105 Z" fill="#2563EB" opacity="0.85"/>
            <ellipse cx="120" cy="120" rx="90" ry="32" fill="none" stroke="rgba(255, 255, 255, 0.25)" stroke-width="1.2"/>
            <ellipse cx="120" cy="120" rx="90" ry="60" fill="none" stroke="rgba(255, 255, 255, 0.2)" stroke-width="1.2"/>
            <ellipse cx="120" cy="120" rx="36" ry="90" fill="none" stroke="rgba(255, 255, 255, 0.2)" stroke-width="1.2"/>
            <circle cx="126" cy="112" r="4.5" fill="#FC3D21" stroke="#FFFFFF" stroke-width="1.5"/>
            <circle cx="122" cy="98" r="4" fill="#FC3D21" stroke="#FFFFFF" stroke-width="1.5"/>
            <circle cx="118" cy="88" r="4" fill="#FC3D21" stroke="#FFFFFF" stroke-width="1.5"/>
            <circle cx="68" cy="94" r="4" fill="#FC3D21" stroke="#FFFFFF" stroke-width="1.5"/>
        </svg>
    </div>
</div>
""")

# ==============================================================================
# SOLID PARTNER AGENCY STRIP
# ==============================================================================
agency_logo_html = f'<img src="data:image/svg+xml;base64,{nasa_logo_b64}" width="44" alt="NASA">' if nasa_logo_b64 else '<span class="agency-mark">NASA</span>'

st.html(f"""
<div class="agency-strip">
    <div class="agency-left">
        {agency_logo_html}
        <span class="agency-label">IN PARTNERSHIP WITH</span>
    </div>
    <div style="height: 20px; width: 1px; background: {c_card_border};"></div>
    <div class="agency-logos-row">
        <span class="agency-mark">GGPEN <span class="agency-mark-sub">ANGOLA</span></span>
        <span class="agency-mark">CONAE <span class="agency-mark-sub">ARGENTINA</span></span>
        <span class="agency-mark">NSSA <span class="agency-mark-sub">BAHRAIN</span></span>
        <span class="agency-mark">AEB <span class="agency-mark-sub">BRASIL</span></span>
        <span class="agency-mark">CSA <span class="agency-mark-sub">ASC CANADA</span></span>
        <span class="agency-mark">ESA <span class="agency-mark-sub">COPERNICUS</span></span>
        <span class="agency-mark">FAO <span class="agency-mark-sub">GAEZ v4</span></span>
        <span class="agency-mark">POWER <span class="agency-mark-sub">LaRC</span></span>
        <span class="agency-mark">SMAP <span class="agency-mark-sub">JPL</span></span>
    </div>
</div>
""")

# ==============================================================================
# SIDEBAR: SETUP & SOIL BASELINE
# ==============================================================================
with st.sidebar:
    st.markdown(f"<div class='app-heading' style='font-size: 1.05rem; margin-bottom: 6px;'>{SVG_PIN} Field Location & Setup</div>", unsafe_allow_html=True)
    
    # Theme Mode Selector (Crisp & Clean)
    theme_choice = st.radio(
        "Display Theme:",
        ["☀️ Clean Light Theme (Default)", "🌙 Deep Space Dark Theme"],
        index=0 if st.session_state.theme_mode == "Light" else 1,
        horizontal=True
    )
    new_theme = "Dark" if "Dark" in theme_choice else "Light"
    if new_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = new_theme
        st.rerun()

    # 1-Click Presentation & Dossier PDF Download
    try:
        pdf_path = "RituChakra_Presentation_Dossier.pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f_pdf:
                st.download_button(
                    label="📥 Download Presentation Dossier (PDF)",
                    data=f_pdf.read(),
                    file_name="RituChakra_Presentation_Dossier.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    except Exception:
        pass

    # Browser GPS Processing (Only updates if user is in GPS mode or default initial load)
    gps_payload = get_browser_gps()
    if gps_payload and isinstance(gps_payload, dict) and "latitude" in gps_payload:
        gps_lat = round(float(gps_payload["latitude"]), 4)
        gps_lon = round(float(gps_payload["longitude"]), 4)
        if st.session_state.location_lock_mode in ["gps", "default"]:
            last_locked = st.session_state.get("_last_locked_gps")
            if last_locked != (gps_lat, gps_lon):
                st.session_state._last_locked_gps = (gps_lat, gps_lon)
                st.session_state.current_lat = gps_lat
                st.session_state.current_lon = gps_lon
                try:
                    rev = reverse_geocode(gps_lat, gps_lon, mapbox_token=MAPBOX_ACCESS_TOKEN)
                    st.session_state.location_name = rev.get("formatted", f"{gps_lat:.4f}°N, {gps_lon:.4f}°E")
                    st.session_state.location_zone = rev.get("district") or rev.get("state") or "Detected Farm Area"
                    st.session_state.location_node_id = f"COMM_NODE_{abs(hash(st.session_state.location_name)) % 900 + 100}"
                except Exception:
                    pass
                st.rerun()

    # Active Location Display Card (Crisp 4px)
    st.html(f"""
    <div style="background-color: {c_card_bg}; border: 1px solid {c_card_border}; border-radius: 4px; padding: 12px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span class="pulse-dot-green"></span>
                <span style="font-size: 0.72rem; font-weight: 700; color: {c_accent_green}; letter-spacing: 0.04em; text-transform: uppercase;">Active Field</span>
            </div>
            <span style="font-size: 0.68rem; font-weight: 600; color: {c_text_muted}; text-transform: uppercase;">Source: {st.session_state.location_lock_mode}</span>
        </div>
        <div style="font-size: 0.95rem; font-weight: 700; color: {c_text}; line-height: 1.35; margin-bottom: 4px;">
            {st.session_state.location_name}
        </div>
        <div style="font-size: 0.80rem; color: {c_text_muted};">
            Coordinates: <b style="color: {c_text};">{st.session_state.current_lat:.4f}°N, {st.session_state.current_lon:.4f}°E</b>
        </div>
        <div style="font-size: 0.76rem; color: {c_text_muted}; margin-top: 2px;">
            Zone: <span style="color: {c_accent_blue}; font-weight: 600;">{st.session_state.location_zone}</span>
        </div>
    </div>
    """)

    # 1. Mapbox Search Input (Clean, Instant & Never Overwritten)
    st.markdown(f"<div style='font-size: 0.82rem; font-weight: 600; color: {c_text}; margin-bottom: 4px;'>Search Village, Tehsil, or City:</div>", unsafe_allow_html=True)
    search_query = st.text_input(
        "Search Location:",
        placeholder="e.g. Baramati, Nashik, Yavatmal, Bathinda, Amravati...",
        key="mapbox_places_search",
        label_visibility="collapsed"
    )
    if search_query and len(search_query.strip()) >= 2:
        search_results = search_locations(search_query.strip(), limit=5)
        if search_results:
            st.markdown(f"<div style='font-size: 0.76rem; font-weight: 600; color: {c_text_muted}; margin: 6px 0 4px 0;'>Select Matching Location:</div>", unsafe_allow_html=True)
            for idx, res in enumerate(search_results):
                loc_col1, loc_col2 = st.columns([3, 1])
                with loc_col1:
                    st.markdown(f"<div style='font-size: 0.80rem; color: {c_text}; line-height: 1.25; margin-top: 6px;'><b>{res['label'].split(',')[0]}</b><br><span style='font-size: 0.72rem; color: {c_text_muted};'>{res['label']}</span></div>", unsafe_allow_html=True)
                with loc_col2:
                    if st.button("Use", key=f"btn_pick_{idx}_{abs(hash(res['label']))}"):
                        st.session_state.current_lat = float(res["lat"])
                        st.session_state.current_lon = float(res["lon"])
                        st.session_state.location_name = res["label"]
                        st.session_state.location_zone = f"{res.get('district', '')}, {res.get('state', '')}".strip(", ") or "Agro-Ecological Zone"
                        st.session_state.location_node_id = f"COMM_NODE_{abs(hash(res['label'])) % 900 + 100}"
                        st.session_state.location_lock_mode = "search"
                        st.toast(f"Switched field to: {res['label'].split(',')[0]}", icon="📍")
                        st.rerun()
        else:
            st.info("No matching places found. Try typing district or nearby town.")

    # Quick action row: Re-lock GPS or Demo Hubs
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("🔄 Re-lock GPS", use_container_width=True):
            st.session_state.location_lock_mode = "gps"
            st.session_state._last_locked_gps = None
            st.toast("Re-requesting device GPS...", icon="🛰️")
            st.rerun()
    with col_act2:
        if st.button("🏛️ Regional Hubs", use_container_width=True):
            st.session_state._show_demo_hubs = not st.session_state.get("_show_demo_hubs", False)
            st.rerun()

    # Expandable Regional Benchmark Hubs
    if st.session_state.get("_show_demo_hubs", False):
        st.markdown(f"<div style='font-size: 0.80rem; font-weight: 600; color: {c_text}; margin-top: 6px;'>Benchmark Regional Hubs:</div>", unsafe_allow_html=True)
        hub_names = list(DEFAULT_LOCATIONS.keys())
        curr_idx = hub_names.index(st.session_state.location_name) if st.session_state.location_name in hub_names else 0
        sel_hub = st.selectbox("Select Benchmark Hub:", hub_names, index=curr_idx, label_visibility="collapsed")
        if st.button("Load Selected Hub", use_container_width=True):
            pdata = DEFAULT_LOCATIONS[sel_hub]
            st.session_state.current_lat = float(pdata["lat"])
            st.session_state.current_lon = float(pdata["lon"])
            st.session_state.location_name = sel_hub
            st.session_state.location_zone = pdata["region"]
            st.session_state.location_node_id = pdata["node_id"]
            st.session_state.location_lock_mode = "preset"
            st.toast(f"Loaded benchmark hub: {sel_hub}", icon="🏛️")
            st.rerun()

    # Manual Lat/Lon Coordinates (Explicit apply only - Never accidental override)
    with st.expander("🌐 Manual Coordinates Input", expanded=False):
        c_lat, c_lon = st.columns(2)
        with c_lat:
            manual_lat = st.number_input("Latitude (°N)", value=float(st.session_state.current_lat), format="%.4f", key="man_lat_input")
        with c_lon:
            manual_lon = st.number_input("Longitude (°E)", value=float(st.session_state.current_lon), format="%.4f", key="man_lon_input")
        if st.button("Apply Coordinates", use_container_width=True):
            st.session_state.current_lat = float(manual_lat)
            st.session_state.current_lon = float(manual_lon)
            st.session_state.location_name = f"Custom Field ({manual_lat:.2f}°, {manual_lon:.2f}°)"
            st.session_state.location_lock_mode = "manual"
            st.toast("Manual coordinates applied", icon="🌐")
            st.rerun()

    st.divider()

    # 4. Cultivation & Soil Details
    st.markdown(f"<div class='app-heading' style='font-size: 1.05rem; margin-bottom: 8px;'>{SVG_LEAF} Cultivation & Soil Status</div>", unsafe_allow_html=True)
    
    preset_data = DEFAULT_LOCATIONS.get(
        st.session_state.get("location_name"),
        DEFAULT_LOCATIONS.get("Amravati, Vidarbha (MH)", list(DEFAULT_LOCATIONS.values())[0])
    )
    
    current_crop = st.selectbox(
        "Current Primary Crop:",
        list(CROP_CATALOG.keys())[:5],
        index=0 if preset_data["primary_crop"] not in list(CROP_CATALOG.keys())[:5] 
              else list(CROP_CATALOG.keys())[:5].index(preset_data["primary_crop"])
    )
    farm_size_acres = st.number_input("Field Acreage (Acres):", min_value=1.0, max_value=500.0, value=5.0, step=0.5)

    with st.expander("Soil Test Parameters (NPK & pH)", expanded=False):
        soil_n = st.slider("Available Nitrogen (N kg/ha):", 50, 400, preset_data["default_n"])
        soil_p = st.slider("Available Phosphorus (P kg/ha):", 10, 100, preset_data["default_p"])
        soil_k = st.slider("Available Potassium (K kg/ha):", 80, 500, preset_data["default_k"])
        soil_ph = st.slider("Soil pH:", 5.0, 9.0, preset_data["default_ph"], step=0.1)
        soil_type = st.text_input("Soil Texture Classification:", preset_data["soil_type"])

    soil_profile = {
        "n": soil_n,
        "p": soil_p,
        "k": soil_k,
        "ph": soil_ph,
        "soil_type": soil_type,
        "farm_size": farm_size_acres
    }

    st.write("")
    run_analysis = st.button("Run Climate & Rotation Advisory", type="primary", use_container_width=True)
    if run_analysis:
        st.cache_data.clear()
        st.toast("Recalculating climate shifts and crop rotation models...", icon="🛰️")

    st.write("")
    with st.expander("📲 Mobile & Multi-Device Access", expanded=False):
        try:
            _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _sock.connect(("8.8.8.8", 80))
            local_lan_ip = _sock.getsockname()[0]
            _sock.close()
        except Exception:
            local_lan_ip = "127.0.0.1"
            
        lan_url = f"http://{local_lan_ip}:8501"
        st.markdown(f"**Wi-Fi / LAN URL:**<br>`{lan_url}`", unsafe_allow_html=True)
        st.caption("Same Wi-Fi network par kisi bhi phone ya PC par ye URL open karein ya QR scan karein:")
        st.markdown(
            f'<div style="text-align: center; margin: 8px 0;">'
            f'<img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={lan_url}" '
            f'style="border-radius: 4px; background: white; padding: 4px;" alt="Scan QR to open" />'
            f'</div>',
            unsafe_allow_html=True
        )

# ==============================================================================
# DATA INGESTION & PIPELINE EXECUTION
# ==============================================================================
@st.cache_data(show_spinner=False)
def get_cached_climate(latitude: float, longitude: float):
    return fetch_nasa_power_climate(latitude, longitude, start_year=2014, end_year=2024)

lat = float(st.session_state.current_lat)
lon = float(st.session_state.current_lon)

with st.spinner("Processing NASA Observations & Field Telemetry..."):
    df_climate = get_cached_climate(lat, lon)
    climate_shifts = compute_climate_shifts(df_climate)
    
    # Community / Custom Field Node Instance
    active_node_id = st.session_state.custom_node_id if st.session_state.use_custom_node else st.session_state.location_node_id
    node_engine = CommunityNodeEngine(node_id=active_node_id)
    
    # Inject real physical hardware telemetry if active
    if st.session_state.use_custom_node and st.session_state.custom_telemetry_data:
        ct = st.session_state.custom_telemetry_data
        try:
            node_engine.set_custom_telemetry(
                soil_moisture=float(ct.get("soil_moisture", 32.5)),
                soil_temp=float(ct.get("soil_temp", 28.0)),
                temp=float(ct.get("temp", 30.5)),
                humidity=float(ct.get("humidity", 68.0)),
                pressure=float(ct.get("pressure", 1008.2)),
                node_id=st.session_state.custom_node_id,
                rain_mm=float(ct.get("rain_mm", 0.0))
            )
        except Exception:
            # Resilient fallback: preserve satellite continuity without crash
            st.session_state.use_custom_node = False
    
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

# Live Data Telemetry Ribbon
is_fallback = bool(df_climate["Is_Fallback"].iloc[0]) if not df_climate.empty and "Is_Fallback" in df_climate.columns else False
if not is_fallback:
    api_status_html = f'<span class="pulse-dot-green"></span> <span><b>NASA POWER:</b> <span style="color: {c_accent_green}; font-weight: 600;">Stream Active</span> ({len(df_climate)} Monthly Records • {lat:.4f}°N, {lon:.4f}°E)</span>'
else:
    api_status_html = f'<span class="pulse-dot-yellow"></span> <span><b>NASA POWER:</b> <span style="color: #CA8A04; font-weight: 600;">Calibrated Cache</span> (Regional Baseline)</span>'

if st.session_state.use_custom_node:
    telemetry_status_html = f'<span class="pulse-dot-green"></span> <span><b>FIELD NODE:</b> <span style="color: {c_accent_green}; font-weight: 600;">Connected</span> <code>{st.session_state.custom_node_id}</code> (Moisture: <b>{latest_calibrated["Calibrated_SoilMoisture_pct"]:.1f}%</b> • Pressure: <b>{latest_calibrated["BME280_Pressure_hPa"]:.1f} hPa</b>)</span>'
else:
    telemetry_status_html = f'<span class="pulse-dot-green"></span> <span><b>REGIONAL IOT MESH:</b> <span style="color: {c_accent_green}; font-weight: 600;">Online</span> <code>{calibration_metrics["node_id"]}</code> (Pressure: <b>{calibration_metrics["latest_pressure_hPa"]:.1f} hPa</b>)</span>'

sar_status_html = f'<span class="pulse-dot-green"></span> <span><b>SENTINEL-1 SAR:</b> <span style="color: {c_accent_green}; font-weight: 600;">C-Band Active</span> (σ°: <b>{calibration_metrics["latest_sar_backscatter_db"]:.1f} dB</b>)</span>'

st.html(f"""
<div class="live-data-ribbon">
    <div class="ribbon-item">{api_status_html}</div>
    <div class="ribbon-item">{telemetry_status_html}</div>
    <div class="ribbon-item">{sar_status_html}</div>
</div>
""")

# ==============================================================================
# MAIN TABS (FARMER-FIRST REORDERED STRUCTURE)
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🌾 Recommended Crop Plan (फसल सलाह)",
    "🌱 Field & Soil Health (खेत और मिट्टी)",
    "📡 Farm Sensor Node (अपना सेंसर जोड़ें)",
    "🔮 Climate & Monsoon Outlook (मौसम भविष्य)"
])

# Helper to render clean action steps
def render_actions_html(action_steps, check_color):
    rows = []
    for act in action_steps:
        clean_text = act.replace("• ", "").replace("**Adjusted Sowing Window:**", "<b>Adjusted Sowing Window:</b>").replace("**Deficit Irrigation:**", "<b>Deficit Irrigation:</b>").replace("**Mulching:**", "<b>Mulching:</b>").replace("**Residue Mulching:**", "<b>Residue Mulching:</b>").replace("**Rhizobium Inoculation:**", "<b>Rhizobium Inoculation:</b>").replace("**Water Conservation:**", "<b>Water Conservation:</b>").replace("**Fertilizer Offset:**", "<b>Fertilizer Offset:</b>").replace("**Thermal Tolerance:**", "<b>Thermal Tolerance:</b>").replace("**Drought Resilience:**", "<b>Drought Resilience:</b>").replace("**Dual-Revenue Stream:**", "<b>Dual-Revenue Stream:</b>")
        chk = f'<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="{check_color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 6px; flex-shrink: 0;"><polyline points="20 6 9 17 4 12"></polyline></svg>'
        rows.append(f'<div class="action-row">{chk} <span>{clean_text}</span></div>')
    return "".join(rows)

# ==============================================================================
# TAB 1: RECOMMENDED CROP PLAN
# ==============================================================================
with tab1:
    strat_a = strategies["strategy_a"]
    strat_b = strategies["strategy_b"]
    strat_c = strategies["strategy_c"]

    st.markdown(f"### {SVG_LEAF} Climate-Smart Crop Advisory for Your Field", unsafe_allow_html=True)
    st.caption(f"Personalized rotational pathways formulated for **{st.session_state.location_name}** ({lat:.4f}°N, {lon:.4f}°E) based on NASA 10-year historical climate patterns and live soil moisture.")
    
    # Farmer Quick Status Pill (Crisp 4px)
    st.html(f"""
    <div style="background-color: {c_card_bg}; border: 1px solid {c_card_border}; border-radius: 4px; padding: 12px 16px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);">
        <div>
            <span style="color: {c_text_muted}; font-size: 0.82rem; font-weight: 600;">CURRENT PRIMARY CROP:</span> 
            <span style="color: {c_text}; font-size: 0.95rem; font-weight: 700; margin-left: 4px;">{current_crop}</span>
            <span style="color: {c_card_border}; margin: 0 8px;">•</span>
            <span style="color: {c_text_muted}; font-size: 0.82rem; font-weight: 600;">FIELD SIZE:</span> 
            <span style="color: {c_text}; font-size: 0.95rem; font-weight: 700; margin-left: 4px;">{farm_size_acres} Acres</span>
        </div>
        <div>
            <span style="color: {c_text_muted}; font-size: 0.82rem; font-weight: 600;">DROUGHT RISK:</span> 
            <span style="color: {c_accent_gold}; font-size: 0.95rem; font-weight: 800; margin-left: 4px;">{climate_shifts.get('drought_vulnerability_index', 50)}/100</span>
            <span style="color: {c_card_border}; margin: 0 8px;">•</span>
            <span style="color: {c_text_muted}; font-size: 0.82rem; font-weight: 600;">10-YR WARMING:</span> 
            <span style="color: {c_accent_blue}; font-size: 0.95rem; font-weight: 800; margin-left: 4px;">+{climate_shifts.get('temp_delta', 0.5):.2f}°C</span>
        </div>
    </div>
    """)
    
    sc1, sc2, sc3 = st.columns(3)
    
    # Strategy 1: Recommended Smart Plan
    with sc1:
        actions_s1 = render_actions_html(strat_a["action_steps"], c_accent_green)
        st.html(f"""
        <div class="strategy-card">
            <div style="font-size: 0.74rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: {c_accent_green}; margin-bottom: 4px;">Strategy 1: Recommended Smart Plan</div>
            <div class="strategy-crop-title">{strat_a['primary_crop']}</div>
            <div class="strategy-stats-grid">
                <div class="stat-item"><span class="stat-label">Suitability</span><span class="stat-value">{strat_a['suitability_score']}%</span></div>
                <div class="stat-item"><span class="stat-label">Crop Cycle</span><span class="stat-value">{strat_a['duration_days'].split(' ')[0]}–{strat_a['duration_days'].split(' ')[2]} Days</span></div>
                <div class="stat-item"><span class="stat-label">Water Needed</span><span class="stat-value">{strat_a['water_requirement_mm'].split(' ')[0]} mm</span></div>
                <div class="stat-item"><span class="stat-label">Water Saved</span><span class="stat-value">{strat_a['water_savings_pct']}%</span></div>
                <div class="stat-item"><span class="stat-label">Soil Nitrogen</span><span class="stat-value">{strat_a['soil_n_balance_kg_ha'].split(' ')[0]}</span></div>
                <div class="stat-item"><span class="stat-label">Risk Level</span><span class="stat-value">{strat_a['risk_level'].split(' ')[0]}</span></div>
            </div>
            <div class="strategy-reasoning-box">
                <b>Climate & Sowing Window:</b><br>{strat_a['reasoning']}
            </div>
            <div style="font-size: 0.76rem; font-weight: 700; color: {c_text_muted}; text-transform: uppercase; margin-bottom: 8px;">Farmer Action Checklist:</div>
            <div class="strategy-action-list">
                {actions_s1}
            </div>
            <div class="strategy-economic-box">
                <span class="econ-label">Pumping Energy Savings</span>
                <span class="econ-gain" style="color: {c_accent_green}; font-weight: 800; font-size: 1.05rem;">{strat_a['economic_hook']['net_financial_gain']}</span>
            </div>
        </div>
        """)
            
    # Strategy 2: Fast-Maturity Escape Plan
    with sc2:
        actions_s2 = render_actions_html(strat_b["action_steps"], c_accent_gold)
        st.html(f"""
        <div class="strategy-card">
            <div style="font-size: 0.74rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: {c_accent_gold}; margin-bottom: 4px;">Strategy 2: Fast-Maturity Escape Plan</div>
            <div class="strategy-crop-title">{strat_b['primary_crop']}</div>
            <div class="strategy-stats-grid">
                <div class="stat-item"><span class="stat-label">Suitability</span><span class="stat-value">{strat_b['suitability_score']}%</span></div>
                <div class="stat-item"><span class="stat-label">Crop Cycle</span><span class="stat-value">{strat_b['duration_days'].split(' ')[0]}–{strat_b['duration_days'].split(' ')[2]} Days</span></div>
                <div class="stat-item"><span class="stat-label">Water Needed</span><span class="stat-value">{strat_b['water_requirement_mm'].split(' ')[0]} mm</span></div>
                <div class="stat-item"><span class="stat-label">Water Saved</span><span class="stat-value">{strat_b['water_savings_pct']}%</span></div>
                <div class="stat-item"><span class="stat-label">Soil Nitrogen</span><span class="stat-value">{strat_b['soil_n_balance_kg_ha'].split(' ')[0]}</span></div>
                <div class="stat-item"><span class="stat-label">Risk Level</span><span class="stat-value">Very Low</span></div>
            </div>
            <div class="strategy-reasoning-box">
                <b>Early Harvest Reasoning:</b><br>{strat_b['reasoning']}
            </div>
            <div style="font-size: 0.76rem; font-weight: 700; color: {c_text_muted}; text-transform: uppercase; margin-bottom: 8px;">Farmer Action Checklist:</div>
            <div class="strategy-action-list">
                {actions_s2}
            </div>
            <div class="strategy-economic-box">
                <span class="econ-label">Net Economic Hedging</span>
                <span class="econ-gain" style="color: {c_accent_gold}; font-weight: 800; font-size: 1.05rem;">{strat_b['economic_hook']['net_financial_gain']}</span>
            </div>
        </div>
        """)
            
    # Strategy 3: Soil Nitrogen & Wealth Restorer
    with sc3:
        actions_s3 = render_actions_html(strat_c["action_steps"], c_accent_blue)
        st.html(f"""
        <div class="strategy-card">
            <div style="font-size: 0.74rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: {c_accent_blue}; margin-bottom: 4px;">Strategy 3: Soil Nitrogen & Wealth Restorer</div>
            <div class="strategy-crop-title">{strat_c['primary_crop']}</div>
            <div class="strategy-stats-grid">
                <div class="stat-item"><span class="stat-label">Suitability</span><span class="stat-value">{strat_c['suitability_score']}%</span></div>
                <div class="stat-item"><span class="stat-label">Crop Cycle</span><span class="stat-value">{strat_c['duration_days'].split(' ')[0]}–{strat_c['duration_days'].split(' ')[2]} Days</span></div>
                <div class="stat-item"><span class="stat-label">Water Needed</span><span class="stat-value">{strat_c['water_requirement_mm'].split(' ')[0]} mm</span></div>
                <div class="stat-item"><span class="stat-label">Water Saved</span><span class="stat-value">{strat_c['water_savings_pct']}%</span></div>
                <div class="stat-item"><span class="stat-label">Soil Nitrogen</span><span class="stat-value">{strat_c['soil_n_balance_kg_ha'].split(' ')[0]}</span></div>
                <div class="stat-item"><span class="stat-label">Risk Level</span><span class="stat-value">Low</span></div>
            </div>
            <div class="strategy-reasoning-box">
                <b>Soil Regeneration Reasoning:</b><br>{strat_c['reasoning']}
            </div>
            <div style="font-size: 0.76rem; font-weight: 700; color: {c_text_muted}; text-transform: uppercase; margin-bottom: 8px;">Farmer Action Checklist:</div>
            <div class="strategy-action-list">
                {actions_s3}
            </div>
            <div class="strategy-economic-box">
                <span class="econ-label">Net Financial + Fertility Gain</span>
                <span class="econ-gain" style="color: {c_accent_blue}; font-weight: 800; font-size: 1.05rem;">{strat_c['economic_hook']['net_financial_gain']}</span>
            </div>
        </div>
        """)
            
    st.write("")
    st.divider()
    
    # Side-by-side Table & Radar Comparison
    tbl_col, chart_col = st.columns([1, 1])
    with tbl_col:
        st.markdown(f"#### {SVG_CHART} Multi-Criteria Agronomic Matrix", unsafe_allow_html=True)
        st.dataframe(strategies["comparison_table"], hide_index=True, use_container_width=True)
        
        # Downloadable Farmer Advisory Report
        report_text = f"""========================================================================
RITUCHAKRA: CLIMATE-SMART CROP ROTATION ADVISORY
Project Field Shift • Team Gandharvas - NASA Space Apps Challenge 2026
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================================================
LOCATION: {st.session_state.get('location_name', 'Custom Field Centroid')}
COORDINATES: {lat:.4f} N, {lon:.4f} E | NODE ID: {active_node_id}
PRIMARY CROP: {current_crop} | FIELD SIZE: {farm_size_acres} Acres
------------------------------------------------------------------------
CLIMATE TRENDS (NASA POWER 10-YEAR HISTORICAL OBSERVATIONS):
- 10-Year Temperature Anomaly: {climate_shifts.get('temp_delta', 0.5):+.2f} °C
- Annual Precipitation Shift: {climate_shifts.get('precip_delta_pct', -5.0):+.1f} %
- Drought Vulnerability Index: {climate_shifts.get('drought_vulnerability_index', 50)}/100
- Recent Monsoon Peak Month: {climate_shifts.get('recent_peak_month', 'Aug')}

ROTATION STRATEGIES:
1. STRATEGY 1 (RECOMMENDED SMART PLAN): {strat_a['primary_crop']}
   - Suitability: {strat_a['suitability_score']}% | Water Need: {strat_a['water_requirement_mm']}
   - Sowing Window: {strat_a['sowing_action']}
   - Net Gain: {strat_a['economic_hook']['net_financial_gain']}
   - Reasoning: {strat_a['reasoning']}

2. STRATEGY 2 (FAST-MATURITY ESCAPE PLAN): {strat_b['primary_crop']}
   - Suitability: {strat_b['suitability_score']}% | Water Savings: {strat_b['water_savings_pct']}%
   - Duration: {strat_b['duration_days']}
   - Net Gain: {strat_b['economic_hook']['net_financial_gain']}
   - Reasoning: {strat_b['reasoning']}

3. STRATEGY 3 (SOIL NITROGEN RESTORER): {strat_c['primary_crop']}
   - Suitability: {strat_c['suitability_score']}% | Water Savings: {strat_c['water_savings_pct']}%
   - Nitrogen Restored: {strat_c['soil_n_balance_kg_ha']}
   - Net Gain: {strat_c['economic_hook']['net_financial_gain']}
   - Reasoning: {strat_c['reasoning']}
========================================================================
"""
        st.download_button(
            label="Download Advisory Technical Report (TXT)",
            data=report_text,
            file_name=f"RituChakra_Advisory_{lat:.2f}_{lon:.2f}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with chart_col:
        fig_radar = create_strategy_radar_comparison(strategies, theme=theme_param)
        st.plotly_chart(fig_radar, use_container_width=True)

# ==============================================================================
# TAB 2: FIELD & SOIL HEALTH
# ==============================================================================
with tab2:
    st.markdown(f"### {SVG_PIN} Field & Soil Health Overview", unsafe_allow_html=True)
    st.caption("Satellite parcel imagery and in-situ soil test diagnostics for precision nutrient and water management.")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Coordinates", f"{lat:.4f}°N, {lon:.4f}°E")
    with m_col2:
        st.metric("Primary Crop", current_crop)
    with m_col3:
        st.metric("Soil Texture", soil_type)
    with m_col4:
        st.metric("Drought Vulnerability", f"{climate_shifts.get('drought_vulnerability_index', 50)}/100", 
                  delta=f"{climate_shifts.get('temp_delta', 0.6):+.2f}°C Warming", delta_color="inverse")
        
    st.divider()
    
    p_col1, p_col2 = st.columns([1, 1])
    with p_col1:
        st.markdown(f"#### {SVG_PIN} High-Resolution Satellite Field Radar (Mapbox)", unsafe_allow_html=True)
        st.caption(f"📍 Centroid: **{st.session_state.get('location_name', 'Custom Field')}** | Node: `{'Real Field Node: ' + active_node_id if st.session_state.use_custom_node else active_node_id}`")
        fig_map = create_field_satellite_map(
            lat=lat,
            lon=lon,
            location_name=st.session_state.get('location_name', 'Custom Field Centroid'),
            node_id=active_node_id,
            mapbox_token=MAPBOX_ACCESS_TOKEN,
            theme=theme_param
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
    with p_col2:
        st.markdown(f"#### {SVG_FLASK} Soil Chemistry Diagnostics", unsafe_allow_html=True)
        soil_n_status = "Optimal" if 200 <= soil_n <= 300 else ("Depleted (Needs Compost / Legume)" if soil_n < 200 else "High")
        st.write(f"{SVG_CHECK} **Available Nitrogen (N):** `{soil_n} kg/ha` — <span style='color: {c_accent_green}; font-weight: 600;'>{soil_n_status}</span>", unsafe_allow_html=True)
        st.write(f"{SVG_CHECK} **Available Phosphorus (P):** `{soil_p} kg/ha` — <span style='color: {'#059669' if soil_p >= 30 else '#DC2626'}; font-weight: 600;'>{'Adequate' if soil_p >= 30 else 'Deficient'}</span>", unsafe_allow_html=True)
        st.write(f"{SVG_CHECK} **Available Potassium (K):** `{soil_k} kg/ha` — <span style='color: {'#059669' if soil_k >= 200 else '#DC2626'}; font-weight: 600;'>{'Optimal' if soil_k >= 200 else 'Low'}</span>", unsafe_allow_html=True)
        st.write(f"{SVG_CHECK} **Soil pH Value:** `{soil_ph}` ({'Slightly Acidic' if soil_ph < 6.5 else ('Alkaline' if soil_ph > 7.5 else 'Neutral / Ideal')})", unsafe_allow_html=True)
        
        st.markdown(f"#### {SVG_SHIELD} Monoculture Risk Assessment", unsafe_allow_html=True)
        crop_details = CROP_CATALOG[current_crop]
        st.info(f"**Baseline Crop Risk ({current_crop}):** Requires **{crop_details['optimal_water_mm']} mm** water per cycle with {crop_details['drought_tolerance'].lower()} drought tolerance. {crop_details['soil_impact']}.")

# ==============================================================================
# TAB 3: FARM SENSOR NODE (REASSURING & GENTLE HARDWARE CONNECTION)
# ==============================================================================
with tab3:
    st.markdown(f"### {SVG_ANTENNA} Farm Microclimate Node & Hardware Connection", unsafe_allow_html=True)
    st.caption("Real-time ground truth telemetry. RituChakra automatically provides satellite and regional telemetry — or you can connect your own personal farm sensor.")
    
    # Simple, Friendly Node Source Selector
    node_mode_options = [
        "🛰️ NASA Satellite & Regional Mesh (Ready to Use)", 
        "🔌 Connect My Own Farm Node (ESP32 / Custom Sensor - Optional)"
    ]
    curr_node_mode_idx = 1 if st.session_state.use_custom_node else 0
    node_mode_choice = st.radio(
        "Select Field Telemetry Source:",
        node_mode_options,
        index=curr_node_mode_idx,
        key="telemetry_source_selector_radio",
        horizontal=True
    )
    
    is_custom_selected = ("Connect My Own Farm Node" in node_mode_choice)
    if is_custom_selected != st.session_state.use_custom_node:
        st.session_state.use_custom_node = is_custom_selected
        st.rerun()
    
    if st.session_state.use_custom_node:
        st.html(f"""
        <div style="background-color: {c_card_bg}; border: 1px solid {c_card_border}; border-radius: 4px; padding: 14px; margin-bottom: 14px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="pulse-dot-green"></span>
                    <b style="color: {c_accent_green}; font-size: 0.95rem;">Field Hardware Connection (ESP32 / Custom IoT Node)</b>
                </div>
            </div>
            <p style="color: {c_text_muted}; font-size: 0.84rem; margin-bottom: 0;">
                No physical sensor connected right now? No problem! RituChakra automatically falls back to NASA satellite observations and regional mesh telemetry. You can test custom sensor readings below or enter your hardware webhook URL whenever ready.
            </p>
        </div>
        """)
        
        btn_sw_col1, btn_sw_col2 = st.columns([3, 1])
        with btn_sw_col2:
            if st.button("← Switch to NASA Satellite", use_container_width=True):
                st.session_state.use_custom_node = False
                st.rerun()

        hw_tab1, hw_tab2 = st.tabs(["📝 Test Sensor Readings", "🌐 Sensor Webhook URL"])
        
        with hw_tab1:
            hw_col1, hw_col2 = st.columns(2)
            with hw_col1:
                custom_id = st.text_input("Custom Node Identifier:", value=st.session_state.custom_node_id)
                cust_sm = st.slider("Soil Moisture (% VWC):", 5.0, 65.0, float(st.session_state.custom_telemetry_data.get("soil_moisture", 32.5)), 0.5)
                cust_st = st.slider("Soil Temperature (°C):", 10.0, 50.0, float(st.session_state.custom_telemetry_data.get("soil_temp", 28.0)), 0.5)
            with hw_col2:
                cust_at = st.slider("Air Temperature (°C):", 10.0, 50.0, float(st.session_state.custom_telemetry_data.get("temp", 30.5)), 0.5)
                cust_rh = st.slider("Relative Humidity (%):", 15.0, 100.0, float(st.session_state.custom_telemetry_data.get("humidity", 68.0)), 1.0)
                cust_press = st.number_input("Barometric Pressure (hPa):", min_value=950.0, max_value=1050.0, value=float(st.session_state.custom_telemetry_data.get("pressure", 1008.2)), step=0.1)
            
            if st.button("⚡ Apply Field Sensor Readings", type="primary", use_container_width=True):
                st.session_state.custom_node_id = custom_id.strip() or "MY_FARM_NODE_01"
                st.session_state.custom_telemetry_data = {
                    "soil_moisture": cust_sm,
                    "soil_temp": cust_st,
                    "temp": cust_at,
                    "humidity": cust_rh,
                    "pressure": cust_press,
                    "rain_mm": 0.0
                }
                st.session_state.use_custom_node = True
                st.toast(f"Field readings active from node: {st.session_state.custom_node_id}", icon="🌱")
                st.rerun()

        with hw_tab2:
            st.markdown("""
            <div style="font-size:0.85rem; color:#64748B; margin-bottom:10px;">
                Connect your real ESP32 node or the running virtual hardware simulation. Telemetry syncs in real-time.
            </div>
            """, unsafe_allow_html=True)
            
            # Quick 1-click connect to local virtual node server
            col_local_btn, col_local_info = st.columns([1.5, 1])
            with col_local_btn:
                if st.button("⚡ Connect Simulated Node (127.0.0.1:8000)", type="primary", use_container_width=True):
                    with st.spinner("Connecting to virtual node server..."):
                        fetched = node_engine.fetch_from_http_endpoint("http://127.0.0.1:8000/data")
                        if fetched and isinstance(fetched, dict):
                            st.session_state.custom_telemetry_data.update(fetched)
                            if "node_id" in fetched:
                                st.session_state.custom_node_id = fetched["node_id"]
                            st.session_state.use_custom_node = True
                            st.toast(f"Connected to node: {st.session_state.custom_node_id}", icon="✅")
                            st.rerun()
                        else:
                            st.error("Mock node server not running on port 8000. Start it via: python3 mock_node_server.py")
            with col_local_info:
                st.caption("Control panel active at: [http://localhost:8000](http://localhost:8000)")

            st.markdown("<div style='margin: 8px 0; border-top: 1px dashed #CBD5E1;'></div>", unsafe_allow_html=True)

            webhook_url = st.text_input(
                "Or Enter Custom Sensor Webhook / HTTP Endpoint:",
                value="http://127.0.0.1:8000/data",
                placeholder="e.g. http://192.168.1.100/data or http://127.0.0.1:8000/data",
                help="URL returning JSON with keys: temp, humidity, pressure, soil_moisture"
            )
            if st.button("📡 Connect to Hardware URL", use_container_width=True):
                if webhook_url and webhook_url.strip():
                    with st.spinner("Connecting to sensor node..."):
                        try:
                            fetched = node_engine.fetch_from_http_endpoint(webhook_url.strip())
                            if fetched and isinstance(fetched, dict):
                                st.session_state.custom_telemetry_data.update(fetched)
                                if "node_id" in fetched:
                                    st.session_state.custom_node_id = fetched["node_id"]
                                st.session_state.use_custom_node = True
                                st.toast(f"Successfully connected to node: {st.session_state.custom_node_id}!", icon="✅")
                                st.rerun()
                            else:
                                st.info("ℹ️ Field node not responding on this network. No problem — RituChakra is automatically maintaining high-accuracy NASA satellite and regional mesh telemetry.")
                        except Exception:
                            st.info("ℹ️ Unable to reach sensor endpoint. NASA satellite stream remains active without interruption.")
                else:
                    st.info("💡 Enter your ESP32 or IoT device URL to stream live ground readings.")

    st.write("")
    st.divider()

    # Telemetry KPI Metrics
    k_col1, k_col2, k_col3, k_col4 = st.columns(4)
    with k_col1:
        st.metric("Node Identifier", active_node_id, "Connected Field Anchor")
    with k_col2:
        st.metric("Barometric Pressure", f"{calibration_metrics['latest_pressure_hPa']:.1f} hPa", 
                  f"ΔP/3h: {calibration_metrics['latest_delta_p_3h']:+.1f} hPa", delta_color="normal" if calibration_metrics['latest_delta_p_3h'] >= -1.5 else "inverse")
    with k_col3:
        st.metric("Sentinel-1 SAR Radar", f"{calibration_metrics['latest_sar_backscatter_db']:.1f} dB", 
                  "Cloud-Penetrating C-Band")
    with k_col4:
        st.metric("Sensor Fusion Gain", f"+{calibration_metrics['temp_accuracy_gain_pct']}%", 
                  f"MAE {calibration_metrics['raw_temp_mae']}°C → {calibration_metrics['calibrated_temp_mae']}°C")
        
    st.write("")
    
    # Phase 1 & Phase 2 Alert Banners
    if calibration_metrics.get("bird_effect_storm_alert", False):
        st.warning("⚠️ **Storm Early Warning:** Sudden barometric pressure drop detected (rapid fall with high moisture saturation). High probability of sudden convective downpour before standard weather forecasts catch it.")
    else:
        st.success("🟢 **Atmospheric Stability:** Barometric pressure nominal. No sudden squall alerts active across your field.")
        
    if calibration_metrics.get("disruption_protocol_active", False):
        st.warning("🛰️ **Sentinel-1 SAR Radar Alert:** C-band satellite radar detected topsoil specular backscatter indicating waterlogging. Shifting recommended rotation to Strategy 3 (Regenerative cover crop).")
    else:
        st.info("🛰️ **Sentinel-1 SAR Status:** Radar backscatter nominal. Farm parcel is well-drained with zero standing water detected through overcast skies.")
        
    st.divider()
    
    st.markdown("#### 30-Day Sensor Fusion Telemetry (Satellite vs. Ground Station vs. Calibrated Output)")
    fig_calib = create_calibration_comparison_chart(df_telemetry, theme=theme_param)
    st.plotly_chart(fig_calib, use_container_width=True)
    
    st.markdown("#### Barometric Pressure & Sentinel-1 SAR Radar Trends")
    fig_bme = create_bme280_pressure_trend_chart(df_telemetry, theme=theme_param)
    st.plotly_chart(fig_bme, use_container_width=True)
    
    with st.expander("Sensor Fusion Mathematical Framework & Hardware Specifications", expanded=False):
        c_code_col, c_spec_col = st.columns(2)
        with c_code_col:
            st.latex(r"X_{calibrated}(t) = \alpha \cdot X_{ground\_ESP32}(t) + (1 - \alpha) \cdot X_{satellite\_grid}(t)")
            st.caption(r"Statistical weighting: $\alpha = 0.75$ prioritizes direct localized in-situ observations while preserving broad regional climatological continuity.")
            st.markdown(r"- **Storm Early Warning Condition:** $\Delta P / \Delta t \le -1.5\text{ hPa/3hr} \land (T - T_{dew}) \le 3.0^\circ\text{C}$" "\n" r"- **Sentinel-1 SAR Radar Waterlogging:** $\sigma^0_{VH} \le -19.0\text{ dB}$ (specular reflectance of standing water)")
        with c_spec_col:
            st.markdown("- **MCU:** ESP32 Dual-Core 240MHz (FreeRTOS with MQTT & HTTP Client)\n- **Atmospheric Sensor:** Bosch BME280 (±0.5 hPa barometric pressure, ±0.5°C temperature, ±3% RH)\n- **Soil Moisture:** Capacitive Corrosion-Resistant VWC Probe (10cm depth)\n- **Radar Pipeline:** ESA Sentinel-1 C-band SAR (5.405 GHz) via Google Earth Engine API\n- **Power Subsystem:** 3.7V 18650 Li-Ion with 5W Solar Panel")

# ==============================================================================
# TAB 4: CLIMATE & MONSOON OUTLOOK
# ==============================================================================
with tab4:
    st.markdown(f"### {SVG_CHART} 10-Year Climatological Trajectory (2014 – 2024)", unsafe_allow_html=True)
    st.caption("Decadal observations from NASA Langley Research Center POWER API (MERRA-2 atmospheric model and CERES satellite climatology).")
    
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1:
        st.metric("10-Yr Mean Warming", f"+{climate_shifts.get('temp_delta', 0.5):.2f} °C", 
                  f"{climate_shifts.get('temp_slope_per_decade', 0.5):+.2f}°C/decade", delta_color="inverse")
    with c_col2:
        st.metric("Annual Rainfall Delta", f"{climate_shifts.get('precip_delta_mm', -35.0):+.1f} mm",
                  f"{climate_shifts.get('precip_delta_pct', -5.0):+.1f}% vs baseline", delta_color="normal")
    with c_col3:
        st.metric("Monsoon Peak Shift", f"{climate_shifts.get('recent_peak_month', 'Aug')}", 
                  f"Baseline: {climate_shifts.get('early_peak_month', 'Jul')}")
    with c_col4:
        st.metric("Rainfall Volatility", f"{climate_shifts.get('precip_cv', 22.0):.1f}%", 
                  "Interannual CV")
        
    st.write("")
    
    # Dual-Axis Plotly Chart
    fig_climate = create_climate_trend_chart(climate_shifts["annual_data"], theme=theme_param)
    st.plotly_chart(fig_climate, use_container_width=True)
    
    col_sea, col_ins = st.columns([1, 1])
    with col_sea:
        fig_season = create_seasonality_shift_chart(
            climate_shifts["monthly_early"], 
            climate_shifts["monthly_recent"],
            climate_shifts["early_period"],
            climate_shifts["recent_period"],
            theme=theme_param
        )
        st.plotly_chart(fig_season, use_container_width=True)
        
    with col_ins:
        st.markdown(f"#### {SVG_TEMP} Climate Shift Insights", unsafe_allow_html=True)
        for insight in climate_shifts["insights"]:
            clean_insight = insight.replace("• ", "").replace("**Thermal Shift Analysis:**", "<b>Thermal Shift Analysis:</b>").replace("**Terminal Heat Exposure:**", "<b>Terminal Heat Exposure:</b>").replace("**Hydrological Deficit:**", "<b>Hydrological Deficit:</b>").replace("**Precipitation Distribution Shift:**", "<b>Precipitation Distribution Shift:</b>").replace("**Interannual Rainfall Volatility:**", "<b>Interannual Rainfall Volatility:</b>")
            st.html(f'<div class="action-row" style="margin-bottom: 8px;">{SVG_CHECK} <span>{clean_insight}</span></div>')
        st.caption("Prolonged dry intervals during reproductive stages make continuous monocropping hazardous. Multi-tier crop rotation balances root depth, water extraction, and soil microbial carbon.")

    st.divider()
    st.markdown(f"#### {SVG_CHART} Farm Digital Twin 5-Year Outlook (2026 – 2030)", unsafe_allow_html=True)
    st.caption("Decadal simulation engine applying NASA POWER historical warming and GDD acceleration rates to project microclimate stress on your farm.")
    
    dt_col1, dt_col2 = st.columns([1, 2])
    with dt_col1:
        sim_year = st.slider("Select Simulation Horizon Year:", 2026, 2030, 2028, help="Projects warming anomalies, cumulative GDD, and water stress for the selected year.")
        years_ahead = sim_year - 2024
        proj_warming = (climate_shifts.get('temp_slope_per_decade', 0.5) / 10.0) * years_ahead
        st.metric("Projected Thermal Delta", f"+{proj_warming:.2f} °C", f"Year {sim_year} Horizon")
        st.metric("Projected GDD Acceleration", f"+{int(proj_warming * 180)} GDD", f"{int(proj_warming * 12)} Days Earlier Maturity")
        st.caption("Without adaptive crop rotation, monoculture yield losses are projected at 14% to 22% due to terminal heat stress during grain filling.")
    with dt_col2:
        fig_twin = create_digital_twin_projection_chart(climate_shifts["annual_data"], target_year=sim_year, theme=theme_param)
        st.plotly_chart(fig_twin, use_container_width=True)

# Official Space Apps Footer
st.html(f"""
<div class="spaceapps-footer">
    <b>NASA SPACE APPS CHALLENGE 2026</b> • PROJECT: RITUCHAKRA (FIELD SHIFT) • TEAM: <b>GANDHARVAS</b><br>
    Data Partners: NASA Langley Research Center (POWER) • NASA JPL (SMAP) • European Space Agency (Copernicus) • FAO GAEZ
</div>
""")
