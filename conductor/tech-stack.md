# Technology Stack: Field Shift

## 1. Application Layer & Frontend
- **Framework:** Streamlit (`>=1.38.0`)
- **UI Architecture:** 4-Tab modular navigation (Farm Profile, NASA Climate Shift, Community Node Calibration, 3-Strategy Rotation Engine).
- **Interactive Visualization:** Plotly (`>=5.24.0`) delivering responsive, dual-axis meteorological charts, seasonal distribution overlays, and multi-sensor calibration graphs.

## 2. Data Processing & Computation
- **Core Runtime:** Python 3.14 (Virtual Environment at `.venv/`)
- **Data Manipulation:** Pandas (`>=2.2.0`), NumPy (`>=1.26.0`)
- **HTTP & Networking:** Requests (`>=2.32.0`) with robust local fallback caching for venue connectivity resilience.

## 3. Machine Learning & Predictive Modeling
- **Frameworks:** Scikit-Learn (`>=1.5.0`), XGBoost (`>=2.1.0`)
- **Model Architecture:** Pure tabular `RandomForestRegressor` (35 estimators, max depth 6) scoring crop suitability across 12+ FAO GAEZ agro-climatic profiles.
- **Memory Footprint:** < 50MB RAM, sub-millisecond CPU inference, zero GPU VRAM locking.

## 4. Earth Observation & External APIs
- **Primary Climatology:** NASA POWER REST API (`https://power.larc.nasa.gov/api/temporal/monthly/point`)
  - Parameters: `T2M` (Temperature at 2m), `PRECTOTCORR` (Corrected Precipitation), `RH2M` (Relative Humidity), `ALLSKY_SFC_SW_DWN` (Solar Radiation).
- **Soil Moisture Proxy:** NASA SMAP L3 9km Enhanced Passive Surface Soil Moisture.
- **Agronomic Benchmarks:** FAO GAEZ v4 & ICAR Crop Requirement Matrices.

## 5. IoT & Hardware Infrastructure (Community Node)
- **Controller:** ESP32 Dual-Core Tensilica Xtensa 32-bit LX6 @ 240MHz.
- **Sensors:** SHT31-D / DHT22 (Ambient Temp/RH), Capacitive Soil Moisture v1.2 (10cm root-zone VWC %), Optical/Tipping Rain Gauge.
- **Firmware Stack:** C++ / Arduino Framework (`firmware/esp32_community_node.ino`) utilizing `ArduinoJson` and `PubSubClient` (MQTT).
- **Communication Protocol:** JSON payload over WiFi / 4G LTE-M / LoRaWAN to central Gram Panchayat MQTT broker.

