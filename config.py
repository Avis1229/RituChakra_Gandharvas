"""
Configuration and constants for Field Shift (RituChakra_Gandharvas)
NASA Space Apps Challenge 2026 - Team Gandharvas
"""

import os

APP_TITLE = "RituChakra: Field Shift"
APP_SUBTITLE = "Decision-Support Powered by NASA Earth Observations & Village Community IoT"
TEAM_NAME = "Team Gandharvas"

# Mapbox Public Access Token (Optional: Set MAPBOX_ACCESS_TOKEN env var for high-precision satellite basemaps)
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "")

# Geoapify Geocoding API Key (Optional: Set GEOAPIFY_API_KEY env var for live IP geolocation)
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY", "")

# Curated Agricultural Test Hubs across India and Global Benchmarks
DEFAULT_LOCATIONS = {
    # --- MAHARASHTRA & CENTRAL DECCAN ---
    "Amravati, Vidarbha (MH)": {
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
    "Nagpur, Vidarbha (MH)": {
        "lat": 21.1458,
        "lon": 79.0882,
        "region": "Central Citrus & Cotton Belt",
        "primary_crop": "Cotton",
        "soil_type": "Deep Black Clay Soil",
        "default_n": 190,
        "default_p": 48,
        "default_k": 310,
        "default_ph": 7.5,
        "elevation_m": 310,
        "node_id": "COMM_NODE_MH_012"
    },
    "Latur, Marathwada (MH)": {
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
    "Nashik, Khandesh (MH)": {
        "lat": 19.9975,
        "lon": 73.7898,
        "region": "Western Ghats Transition",
        "primary_crop": "Soybean",
        "soil_type": "Reddish Brown Loam",
        "default_n": 200,
        "default_p": 50,
        "default_k": 280,
        "default_ph": 7.1,
        "elevation_m": 600,
        "node_id": "COMM_NODE_MH_055"
    },
    "Solapur, Western MH (MH)": {
        "lat": 17.6599,
        "lon": 75.9064,
        "region": "Drought-prone Southern Deccan",
        "primary_crop": "Cotton",
        "soil_type": "Shallow to Medium Vertisol",
        "default_n": 160,
        "default_p": 38,
        "default_k": 340,
        "default_ph": 7.8,
        "elevation_m": 458,
        "node_id": "COMM_NODE_MH_093"
    },
    
    # --- UTTAR PRADESH & NORTHERN BELT ---
    "Jhansi, Bundelkhand (UP)": {
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
    "Varanasi, Eastern UP (UP)": {
        "lat": 25.3176,
        "lon": 82.9739,
        "region": "Middle Gangetic Alluvial Plain",
        "primary_crop": "Rice (Paddy)",
        "soil_type": "Alluvial Silt Loam",
        "default_n": 220,
        "default_p": 50,
        "default_k": 220,
        "default_ph": 7.5,
        "elevation_m": 81,
        "node_id": "COMM_NODE_UP_067"
    },
    "Bareilly, Rohilkhand (UP)": {
        "lat": 28.3670,
        "lon": 79.4304,
        "region": "Upper Gangetic Plain",
        "primary_crop": "Wheat",
        "soil_type": "Sandy Clay Loam",
        "default_n": 210,
        "default_p": 48,
        "default_k": 230,
        "default_ph": 7.3,
        "elevation_m": 166,
        "node_id": "COMM_NODE_UP_044"
    },
    "Gorakhpur, Terai Plain (UP)": {
        "lat": 26.7606,
        "lon": 83.3732,
        "region": "Sub-Himalayan Terai",
        "primary_crop": "Rice (Paddy)",
        "soil_type": "Clayey Alluvial Soil",
        "default_n": 230,
        "default_p": 52,
        "default_k": 210,
        "default_ph": 7.8,
        "elevation_m": 84,
        "node_id": "COMM_NODE_UP_082"
    },
    
    # --- PUNJAB & HARYANA ---
    "Ludhiana, Punjab (PB)": {
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
    "Bathinda, Cotton Belt (PB)": {
        "lat": 30.2110,
        "lon": 74.9455,
        "region": "Southwestern Malwa Cotton Belt",
        "primary_crop": "Cotton",
        "soil_type": "Sandy Loam to Calcareous",
        "default_n": 210,
        "default_p": 45,
        "default_k": 240,
        "default_ph": 8.2,
        "elevation_m": 211,
        "node_id": "COMM_NODE_PB_031"
    },
    "Karnal, Basmati Belt (HR)": {
        "lat": 29.6857,
        "lon": 76.9905,
        "region": "Western Indo-Gangetic Plain",
        "primary_crop": "Rice (Paddy)",
        "soil_type": "Deep Alluvial Loam",
        "default_n": 250,
        "default_p": 58,
        "default_k": 200,
        "default_ph": 7.9,
        "elevation_m": 252,
        "node_id": "COMM_NODE_HR_009"
    },
    
    # --- MADHYA PRADESH ---
    "Indore, Malwa (MP)": {
        "lat": 22.7196,
        "lon": 75.8577,
        "region": "Malwa Semi-Arid Plateau",
        "primary_crop": "Soybean",
        "soil_type": "Deep Black Clay (Vertisol)",
        "default_n": 200,
        "default_p": 46,
        "default_k": 310,
        "default_ph": 7.4,
        "elevation_m": 553,
        "node_id": "COMM_NODE_MP_034"
    },
    "Hoshangabad, Narmada Valley (MP)": {
        "lat": 22.7519,
        "lon": 77.7289,
        "region": "Narmada Alluvial Basin",
        "primary_crop": "Wheat",
        "soil_type": "Deep Alluvial Black Soil",
        "default_n": 220,
        "default_p": 50,
        "default_k": 270,
        "default_ph": 7.6,
        "elevation_m": 278,
        "node_id": "COMM_NODE_MP_071"
    },
    
    # --- RAJASTHAN ---
    "Jodhpur, Thar Arid Zone (RJ)": {
        "lat": 26.2389,
        "lon": 73.0243,
        "region": "Hyper-Arid Western Basin",
        "primary_crop": "Cotton",
        "soil_type": "Desert Sandy Soil",
        "default_n": 130,
        "default_p": 25,
        "default_k": 180,
        "default_ph": 8.4,
        "elevation_m": 231,
        "node_id": "COMM_NODE_RJ_019"
    },
    "Kota, Hadoti Chambal Basin (RJ)": {
        "lat": 25.2138,
        "lon": 75.8648,
        "region": "Chambal Valley Irrigated Belt",
        "primary_crop": "Soybean",
        "soil_type": "Medium Black Soil",
        "default_n": 185,
        "default_p": 42,
        "default_k": 290,
        "default_ph": 7.6,
        "elevation_m": 271,
        "node_id": "COMM_NODE_RJ_048"
    },
    
    # --- GUJARAT ---
    "Rajkot, Saurashtra (GJ)": {
        "lat": 22.3039,
        "lon": 70.8022,
        "region": "Saurashtra Peninsula",
        "primary_crop": "Cotton",
        "soil_type": "Medium Black to Calcareous Soil",
        "default_n": 175,
        "default_p": 38,
        "default_k": 320,
        "default_ph": 7.9,
        "elevation_m": 128,
        "node_id": "COMM_NODE_GJ_023"
    },
    "Anand, Charotar Belt (GJ)": {
        "lat": 22.5645,
        "lon": 72.9289,
        "region": "Central Gujarat Fertile Plains",
        "primary_crop": "Wheat",
        "soil_type": "Goradu Sandy Loam",
        "default_n": 210,
        "default_p": 52,
        "default_k": 260,
        "default_ph": 7.5,
        "elevation_m": 39,
        "node_id": "COMM_NODE_GJ_008"
    },
    
    # --- KARNATAKA ---
    "Dharwad, Transition Zone (KA)": {
        "lat": 15.4589,
        "lon": 75.0078,
        "region": "Northern Transition Agro Zone",
        "primary_crop": "Soybean",
        "soil_type": "Mixed Red Loam & Black Soil",
        "default_n": 180,
        "default_p": 44,
        "default_k": 280,
        "default_ph": 7.0,
        "elevation_m": 750,
        "node_id": "COMM_NODE_KA_036"
    },
    "Raichur, Krishna-Doab (KA)": {
        "lat": 16.2120,
        "lon": 77.3439,
        "region": "Dry North Eastern Plateau",
        "primary_crop": "Cotton",
        "soil_type": "Deep Black Vertisol",
        "default_n": 170,
        "default_p": 36,
        "default_k": 330,
        "default_ph": 8.1,
        "elevation_m": 407,
        "node_id": "COMM_NODE_KA_072"
    },
    
    # --- ANDHRA PRADESH & TELANGANA ---
    "Warangal, Telangana (TS)": {
        "lat": 17.9689,
        "lon": 79.5941,
        "region": "Telangana Semi-Arid Plateau",
        "primary_crop": "Cotton",
        "soil_type": "Chalka Red Sandy Loam",
        "default_n": 175,
        "default_p": 40,
        "default_k": 270,
        "default_ph": 6.8,
        "elevation_m": 266,
        "node_id": "COMM_NODE_TS_015"
    },
    "Guntur, Krishna Delta (AP)": {
        "lat": 16.3067,
        "lon": 80.4365,
        "region": "Coastal Krishna Alluvial Delta",
        "primary_crop": "Cotton",
        "soil_type": "Heavy Coastal Clay Vertisol",
        "default_n": 220,
        "default_p": 54,
        "default_k": 310,
        "default_ph": 7.7,
        "elevation_m": 30,
        "node_id": "COMM_NODE_AP_052"
    },
    "Anantapur, Rayalaseema (AP)": {
        "lat": 14.6819,
        "lon": 77.6006,
        "region": "Scarce Rainfall Rayalaseema",
        "primary_crop": "Cotton",
        "soil_type": "Red Gravelly Sandy Loam",
        "default_n": 140,
        "default_p": 28,
        "default_k": 220,
        "default_ph": 6.9,
        "elevation_m": 335,
        "node_id": "COMM_NODE_AP_088"
    },
    
    # --- TAMIL NADU ---
    "Thanjavur, Cauvery Delta (TN)": {
        "lat": 10.7870,
        "lon": 79.1378,
        "region": "Cauvery Delta Rice Bowl",
        "primary_crop": "Rice (Paddy)",
        "soil_type": "Coastal Alluvial Clay",
        "default_n": 230,
        "default_p": 55,
        "default_k": 240,
        "default_ph": 7.4,
        "elevation_m": 57,
        "node_id": "COMM_NODE_TN_029"
    },
    
    # --- BIHAR & BENGAL ---
    "Patna, Gangetic Basin (BR)": {
        "lat": 25.5941,
        "lon": 85.1376,
        "region": "Middle Gangetic Floodplain",
        "primary_crop": "Rice (Paddy)",
        "soil_type": "Gangetic Alluvial Silt",
        "default_n": 215,
        "default_p": 48,
        "default_k": 225,
        "default_ph": 7.6,
        "elevation_m": 53,
        "node_id": "COMM_NODE_BR_011"
    },
    "Bardhaman, Damodar Basin (WB)": {
        "lat": 23.2324,
        "lon": 87.8615,
        "region": "Lower Gangetic Delta Basin",
        "primary_crop": "Rice (Paddy)",
        "soil_type": "Alluvial Loam to Clayey",
        "default_n": 225,
        "default_p": 52,
        "default_k": 215,
        "default_ph": 6.8,
        "elevation_m": 30,
        "node_id": "COMM_NODE_WB_041"
    },
    
    # --- GLOBAL BENCHMARKS ---
    "Ames, Iowa (US Corn Belt)": {
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
    },
    "Fresno, California (US Central Valley)": {
        "lat": 36.7468,
        "lon": -119.7726,
        "region": "San Joaquin Valley Irrigated",
        "primary_crop": "Cotton",
        "soil_type": "Alluvial Sandy Loam",
        "default_n": 200,
        "default_p": 50,
        "default_k": 280,
        "default_ph": 7.3,
        "elevation_m": 90,
        "node_id": "COMM_NODE_US_002"
    },
    "Mato Grosso, Cerrado (Brazil)": {
        "lat": -12.6819,
        "lon": -55.6989,
        "region": "Tropical Savanna Cerrado",
        "primary_crop": "Soybean",
        "soil_type": "Oxisol / Red Clay",
        "default_n": 170,
        "default_p": 35,
        "default_k": 220,
        "default_ph": 5.8,
        "elevation_m": 360,
        "node_id": "COMM_NODE_BR_003"
    },
    
    # --- CUSTOM GPS COORDINATES (ANY FARM WORLDWIDE) ---
    "📍 Custom GPS Coordinates (Worldwide)": {
        "lat": 20.0000,
        "lon": 77.0000,
        "region": "User Custom Field Centroid",
        "primary_crop": "Cotton",
        "soil_type": "Loam / User Defined",
        "default_n": 180,
        "default_p": 40,
        "default_k": 250,
        "default_ph": 7.0,
        "elevation_m": 300,
        "node_id": "COMM_NODE_CUSTOM"
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

