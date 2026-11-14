"""
Configuration and constants for Field Shift (RituChakra_Gandharvas)
NASA Space Apps Challenge 2026 - Team Gandharvas
"""

APP_TITLE = "Field Shift: Climate-Smart Crop Rotation"
APP_SUBTITLE = "Decision-Support Powered by NASA Earth Observations & Village Community IoT"
TEAM_NAME = "Team Gandharvas"

# Curated Agricultural Test Hubs across India and Global Benchmarks
DEFAULT_LOCATIONS = {
    "Vidarbha (Amravati, Maharashtra) - High Heat & Drought Vulnerability": {
        "lat": 20.9320,
        "lon": 77.7523,
        "region": "Semi-Arid Central India",
        "primary_crop": "Cotton",
        "soil_type": "Black Cotton Soil (Vertisol)",
        "default_n": 180,
        "default_p": 45,
        "default_k": 320,
        "default_ph": 7.6,
        "elevation_m": 343,
        "node_id": "COMM_NODE_MH_042"
    },
    "Bundelkhand (Jhansi, Uttar Pradesh) - Severe Water Scarcity": {
        "lat": 25.4484,
        "lon": 78.5685,
        "region": "Drought-prone Plateau",
        "primary_crop": "Wheat",
        "soil_type": "Mixed Red & Black Soil",
        "default_n": 160,
        "default_p": 35,
        "default_k": 260,
        "default_ph": 7.2,
        "elevation_m": 284,
        "node_id": "COMM_NODE_UP_109"
    },
    "Malwa / Punjab (Ludhiana) - Groundwater Depletion & Heat Stress": {
        "lat": 30.9010,
        "lon": 75.8573,
        "region": "Intensive Indo-Gangetic Plains",
        "primary_crop": "Rice (Paddy)",
        "soil_type": "Alluvial Loam",
        "default_n": 240,
        "default_p": 55,
        "default_k": 210,
        "default_ph": 8.0,
        "elevation_m": 244,
        "node_id": "COMM_NODE_PB_018"
    },
    "Marathwada (Latur, Maharashtra) - Rainshadow & Delayed Monsoon": {
        "lat": 18.4088,
        "lon": 76.5604,
        "region": "Rain Shadow Deccan",
        "primary_crop": "Soybean",
        "soil_type": "Medium Black Soil",
        "default_n": 190,
        "default_p": 40,
        "default_k": 290,
        "default_ph": 7.4,
        "elevation_m": 631,
        "node_id": "COMM_NODE_MH_088"
    },
    "US Midwest (Ames, Iowa) - Global Benchmark": {
        "lat": 42.0308,
        "lon": -93.6319,
        "region": "US Corn Belt",
        "primary_crop": "Corn (Maize)",
        "soil_type": "Mollisol (Prairie Soil)",
        "default_n": 210,
        "default_p": 60,
        "default_k": 300,
        "default_ph": 6.8,
        "elevation_m": 287,
        "node_id": "COMM_NODE_US_001"
    }
}

# Crop Knowledge Base based on FAO GAEZ, ICAR & USDA Agricultural Extension data
CROP_CATALOG = {
    "Cotton": {
        "category": "Cash Crop (High Water / High Input)",
        "optimal_temp_c": [21, 35],
        "min_water_mm": 700,
        "optimal_water_mm": 1100,
        "optimal_ph": [6.0, 8.0],
        "n_demand": "High (120-150 kg/ha)",
        "soil_impact": "Heavy nutrient depleter, prone to soil compaction",
        "drought_tolerance": "Moderate",
        "duration_days": 160
    },
    "Rice (Paddy)": {
        "category": "Cereal (Extremely High Water)",
        "optimal_temp_c": [22, 32],
        "min_water_mm": 1000,
        "optimal_water_mm": 1500,
        "optimal_ph": [5.5, 7.5],
        "n_demand": "Very High (150-180 kg/ha)",
        "soil_impact": "Causes severe groundwater drawdown and methane emissions",
        "drought_tolerance": "Very Low",
        "duration_days": 130
    },
    "Wheat": {
        "category": "Rabi Cereal (Terminal Heat Vulnerable)",
        "optimal_temp_c": [15, 25],
        "min_water_mm": 400,
        "optimal_water_mm": 600,
        "optimal_ph": [6.0, 7.5],
        "n_demand": "High (120-140 kg/ha)",
        "soil_impact": "Moderate depleter; vulnerable to March terminal heatwaves",
        "drought_tolerance": "Moderate",
        "duration_days": 125
    },
    "Soybean": {
        "category": "Oilseed / Legume",
        "optimal_temp_c": [20, 30],
        "min_water_mm": 450,
        "optimal_water_mm": 700,
        "optimal_ph": [6.0, 7.0],
        "n_demand": "Self-fixing (Rhizobia)",
        "soil_impact": "Fixes 40-70 kg N/ha; improves organic matter",
        "drought_tolerance": "Moderate",
        "duration_days": 100
    },
    "Corn (Maize)": {
        "category": "Cereal (C4 photosynthesis)",
        "optimal_temp_c": [18, 32],
        "min_water_mm": 500,
        "optimal_water_mm": 800,
        "optimal_ph": [5.8, 7.2],
        "n_demand": "High (140-160 kg/ha)",
        "soil_impact": "Depletes nitrogen and potassium",
        "drought_tolerance": "Moderate",
        "duration_days": 110
    },
    # Soil Builder Candidates (Strategy 2)
    "Chickpea (Gram)": {
        "category": "Soil Builder / Pulses",
        "optimal_temp_c": [18, 28],
        "min_water_mm": 250,
        "optimal_water_mm": 400,
        "optimal_ph": [6.0, 8.0],
        "n_fixation_kg_ha": 65,
        "water_saving_pct": 55,
        "soil_impact": "Deep taproot breaks hardpans; fixes 60-80 kg N/ha",
        "drought_tolerance": "High",
        "market_demand": "High (Major Indian Staple / MSP backed)",
        "duration_days": 105
    },
    "Moong (Green Gram)": {
        "category": "Soil Builder / Short-Duration Pulse",
        "optimal_temp_c": [25, 35],
        "min_water_mm": 200,
        "optimal_water_mm": 350,
        "optimal_ph": [6.2, 7.8],
        "n_fixation_kg_ha": 45,
        "water_saving_pct": 65,
        "soil_impact": "Rapid 65-day catch crop; enriches topsoil nitrogen",
        "drought_tolerance": "High",
        "market_demand": "Very High",
        "duration_days": 65
    },
    "Pigeon Pea (Arhar / Tur)": {
        "category": "Soil Builder / Deep Root Legume",
        "optimal_temp_c": [22, 35],
        "min_water_mm": 350,
        "optimal_water_mm": 550,
        "optimal_ph": [5.5, 7.5],
        "n_fixation_kg_ha": 85,
        "water_saving_pct": 45,
        "soil_impact": "Extreme deep rooting extracts subsoil moisture; fixes 70-90 kg N/ha",
        "drought_tolerance": "Very High",
        "market_demand": "High",
        "duration_days": 150
    },
    "Cowpea (Lobia)": {
        "category": "Soil Builder / Cover & Fodder Legume",
        "optimal_temp_c": [24, 35],
        "min_water_mm": 250,
        "optimal_water_mm": 400,
        "optimal_ph": [5.5, 7.5],
        "n_fixation_kg_ha": 55,
        "water_saving_pct": 60,
        "soil_impact": "Excellent living mulch; suppresses weeds and fixes nitrogen",
        "drought_tolerance": "High",
        "market_demand": "Moderate-High",
        "duration_days": 75
    },
    # Climate Resilient & Cash Candidates (Strategy 3)
    "Pearl Millet (Bajra)": {
        "category": "Climate Resilient / Super Cereal",
        "optimal_temp_c": [25, 42],
        "min_water_mm": 200,
        "optimal_water_mm": 350,
        "optimal_ph": [6.5, 8.5],
        "water_saving_pct": 70,
        "soil_impact": "Survives poor sandy/saline soils; high biomass return",
        "drought_tolerance": "Extremely High (Heat resilient up to 45°C)",
        "market_demand": "Surging (Global Year of Millets, Superfood demand)",
        "duration_days": 85
    },
    "Sorghum (Jowar)": {
        "category": "Climate Resilient / Dual Grain-Fodder",
        "optimal_temp_c": [24, 38],
        "min_water_mm": 300,
        "optimal_water_mm": 500,
        "optimal_ph": [5.5, 8.5],
        "water_saving_pct": 60,
        "soil_impact": "Waxy leaf cuticle halts evapotranspiration; dormancy during dry spells",
        "drought_tolerance": "Extremely High",
        "market_demand": "High (Ethanol, Brewery, Grain & Green Fodder)",
        "duration_days": 105
    },
    "Finger Millet (Ragi)": {
        "category": "Climate Resilient / Nutrient Dense",
        "optimal_temp_c": [22, 34],
        "min_water_mm": 350,
        "optimal_water_mm": 550,
        "optimal_ph": [5.0, 7.5],
        "water_saving_pct": 55,
        "soil_impact": "Dense fibrous root system prevents erosion on sloping fields",
        "drought_tolerance": "High",
        "market_demand": "Premium Pricing (High calcium/iron wellness market)",
        "duration_days": 100
    },
    "Mustard (Rabi Oilseed)": {
        "category": "Climate Resilient / Low Moisture Oilseed",
        "optimal_temp_c": [15, 27],
        "min_water_mm": 200,
        "optimal_water_mm": 350,
        "optimal_ph": [6.0, 7.5],
        "water_saving_pct": 50,
        "soil_impact": "Glucosinolates in roots provide bio-fumigation effect against pests",
        "drought_tolerance": "High",
        "market_demand": "Very High (Domestic edible oil deficit)",
        "duration_days": 110
    }
}
