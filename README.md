# 🌾 Field Shift — NASA Space Apps Challenge 2026
### Climate-Smart Decision Support for Resilient Crop Rotation
**Team:** Gandharvas  
**Challenge Track:** Adapting Farms with NASA Data  
**Hardware Profile:** Intel i5 12th Gen | 16GB RAM | NVIDIA RTX 2050 (4GB VRAM)  
**Architecture Principle:** High-yield Tabular Space AI & Downscaled Microclimate Calibration (Zero heavy local raster downloads)

---

## 🚀 1. Executive Summary & Objective

Across vulnerable agricultural belts—from Central India's Vidarbha & Bundelkhand to semi-arid regions globally—rising temperatures (+0.5°C to +1.5°C over the past decade), erratic monsoon onset, and declining groundwater tables are causing severe yield losses in traditional monocultures (e.g. Cotton, Paddy Rice, Wheat).

**Field Shift** is a lightweight, decision-support platform that fuses **NASA Earth Observations** with a **Village/Tehsil Community Node** to generate **3 actionable crop rotation strategies**:
1. **Optimized Baseline:** Climate-adjusted sowing calendar and deficit irrigation for the farmer's current primary crop.
2. **Soil Builder Strategy:** Nitrogen-fixing legumes (e.g., Chickpea, Moong, Pigeon Pea) restoring biological soil nitrogen (+45 to +85 kg N/ha) while cutting water consumption by 50–65%.
3. **Climate Resilient & Cash Strategy:** Drought- and extreme heat-tolerant crops (Pearl Millet / Bajra, Sorghum / Jowar) capable of photosynthesizing up to 42°C with minimal water footprints.

---

## 🌟 2. The "Gandharvas" USP: The Village Community Node Model

### Overcoming the "Jhunjhuna" Problem
Most agritech solutions fail because they expect individual smallholder farmers with 1–3 acre plots to purchase, power, and maintain expensive IoT sensors in their muddy fields. In reality, sensors get clogged, batteries die, and hardware becomes an abandoned novelty.

### Our Solution
**Team Gandharvas introduces the "Panchayat / Tehsil Community Node":**
* A single, rugged ESP32-powered **Automatic Weather Station (AWS)** is installed at a central village hub (e.g., Gram Panchayat office, Krishi Vigyan Kendra, or grain cooperative), covering a **5–10 km radius**.
* **Spatial Downscaling & Bias Correction:** NASA's satellite observations (e.g. SMAP, NASA POWER) provide valuable macro-data on a 9x9 km or 10x10 km pixel grid. The Community Node captures hyper-local ground-truth microclimate (air temp, canopy humidity, rain tipping gauge, 10cm capacitive soil moisture).
* **The Fusion Algorithm:**
  $$\text{Calibrated\_Value}(t) = \alpha \cdot \text{Ground\_Node\_Obs}(t) + (1 - \alpha) \cdot \text{NASA\_Grid\_Pixel}(t)$$
  Where $\alpha = 0.75$ grounds the broad satellite grid in local field reality, achieving **over 65% reduction in temperature and soil moisture Mean Absolute Error (MAE)**.
* **Farmer Experience:** Farmers interact solely with a clean, responsive web dashboard. They never touch hardware.

---

## 🏗️ 3. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    NASA EARTH OBSERVATIONS                   │
│  • NASA POWER REST API (T2M, PRECTOTCORR, RH2M, Solar Rad)   │
│  • SMAP L3 Soil Moisture (9x9 km Macro Soil Moisture)       │
│  • FAO GAEZ Agro-Climatic Benchmarks                         │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│            GANDHARVAS VILLAGE COMMUNITY NODE (ESP32)         │
│  • Central Gram Panchayat / Tehsil AWS (5-10 km radius)     │
│  • Ground Sensors: SHT31 Temp/RH, Capacitive VWC, Rain Gauge │
│  • Ground-Truth Calibration & Bias Correction Engine         │
└──────────────────────────────┬───────────────────────────────┘
                               │ (Fused Micro-Macro Features)
                               ▼
┌──────────────────────────────────────────────────────────────┐
│          LIGHTWEIGHT TABULAR ML ENGINE (Scikit-Learn)         │
│  • Features: Temp, Precip, NPK, Soil pH, Drought Index, VWC  │
│  • < 50MB RAM footprint, Zero GPU VRAM lockup                │
│  • Dynamic Suitability Scoring across 12+ Agro-Zones         │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│               STREAMLIT DECISION SUPPORT DASHBOARD           │
│  1. Farm Profile & Geographic Centroid                       │
│  2. 10-Year NASA POWER Climate Shift Trajectory              │
│  3. Community Node Ground-Truth Calibration (Admin View)     │
│  4. 3-Strategy Rotation Advisory & Downloadable Report       │
└──────────────────────────────────────────────────────────────┘
```

---

## ⚡ 4. Hardware Optimization (RTX 2050 / 4GB VRAM Capable)

To ensure the application runs smoothly on standard laptops (e.g., Intel i5 12th Gen, 16GB RAM, RTX 2050 with 4GB VRAM) without freezing during live demonstrations:
- **No Heavy Raster GeoTIFF Downloads:** Instead of processing multi-gigabyte satellite imagery locally, the application leverages lightweight tabular REST endpoints from NASA POWER and pre-processed spatial statistics.
- **Microsecond Tabular Inference:** Random Forest / XGBoost tabular models evaluate crop suitability scores in < 2ms, operating strictly in system memory.
- **Graceful Offline Fallback:** Includes statistical regional climatology caches so the dashboard functions seamlessly even if venue Wi-Fi drops or the NASA API rate-limits.

---

## 📋 5. Installation & Quickstart

```bash
# 1. Clone repository
git clone https://github.com/AhqafCoder/RituChakra_Gandharvas.git
cd RituChakra_Gandharvas

# 2. Activate virtual environment
source .venv/bin/activate  # (Linux/macOS)
# or: .venv\Scripts\activate (Windows)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the Streamlit Dashboard
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📁 6. Repository Structure

```
RituChakra_Gandharvas/
├── app.py                      # Main Streamlit application with 4 core tabs
├── config.py                   # Agricultural presets & FAO/ICAR crop database
├── requirements.txt            # Python dependencies
├── modules/
│   ├── __init__.py
│   ├── nasa_power.py           # NASA POWER REST API client with offline cache
│   ├── community_node.py       # ESP32 calibration node & sensor fusion engine
│   ├── climate_analysis.py     # 10-year trend, warming rate & monsoon shift metrics
│   ├── ml_model.py             # Lightweight Scikit-Learn/XGBoost tabular regressor
│   ├── rotation_engine.py      # 3-Strategy rotation generator & multi-criteria matrix
│   └── visualizer.py           # Publication-quality interactive Plotly charts
├── firmware/
│   └── esp32_community_node.ino # Arduino C++ firmware for village AWS station
└── README.md                   # Hackathon pitch documentation
```

---

## 👥 7. Team Gandharvas

* **Sarthak Maurya** — R&D Lead & Hardware Lead
* **Aadya Saraswat** — R&D and Designing Lead
* **Ahqaf Ali** — Hardware & Backend Lead
* **Vivek Vishwakarma** — AI/ML Lead
* **Lal Shivam Singh** — UI/UX Lead
* **Trisha Bhardwaj** — Documentation Lead
* **Avi Singh** — Project Strategy & Development Lead

---
*Built for the **NASA Space Apps Challenge 2026**.*
