# Product Definition: Field Shift

## 1. Vision & Core Value Proposition
**Field Shift** is a climate-smart agricultural decision-support platform engineered by **Team Gandharvas** for the **NASA Space Apps Challenge 2026** ("Adapting Farms with NASA Data"). It empowers smallholder farmers to adapt to accelerating temperature anomalies, erratic monsoons, and groundwater depletion by recommending science-backed, 3-tier crop rotation strategies.

## 2. The Core Innovation: Village Community Node Model
- **The "Jhunjhuna" Problem:** Traditional agritech solutions burdened smallholder farmers with purchasing, solar-powering, and maintaining fragile IoT probes on individual 1–3 acre plots.
- **Gandharvas Solution:** A single, rugged ESP32-based Automatic Weather Station (AWS) is deployed at the Gram Panchayat / Krishi Vigyan Kendra level, serving a 5–10 km radius.
- **Sensor Fusion & Downscaling:** The node captures hyper-local microclimate ground truth (ambient temperature, humidity, rainfall tipping gauge, root-zone capacitive moisture) to calibrate and downscale coarse 9×9 km NASA satellite observations (NASA POWER, SMAP L3), reducing Mean Absolute Error by >65%.

## 3. The 3-Strategy Rotation Framework
1. **Strategy 1: Optimized Baseline**
   - Retains the farmer's current primary crop (Cotton, Rice, Wheat, Soybean, Maize).
   - Recommends climate-adjusted sowing windows (shifting dates by 10–14 days based on monsoon delay) and deficit irrigation schedules.
2. **Strategy 2: Soil Builder (Regenerative Legume)**
   - Introduces nitrogen-fixing legumes (Chickpea, Moong, Pigeon Pea, Cowpea).
   - Biologically restores +45 to +85 kg N/ha into depleted soils, reduces next-season synthetic urea costs by 40–50%, and cuts water consumption by 50–65%.
3. **Strategy 3: Climate Resilient & Cash (Hardy Super-Cereals / Oilseeds)**
   - Deploys drought- and extreme heat-resilient cash crops (Pearl Millet / Bajra, Sorghum / Jowar, Finger Millet / Ragi, Mustard).
   - Maintains photosynthetic stability up to 42°C, achieves 60–70% water savings, and taps into growing commercial MSP, superfood, and bio-ethanol markets.

## 4. Hardware Constraints & Computational Architecture
- **Target Hardware:** Intel i5 12th Gen, 16GB RAM, NVIDIA RTX 2050 (4GB VRAM).
- **Tabular Space AI Principle:** Avoids system lockups by rejecting local processing of multi-gigabyte raw satellite TIFF rasters; uses lightweight tabular REST APIs (NASA POWER) and sub-millisecond Scikit-Learn Random Forest inference (<50MB RAM).

## 5. User Personas & Target Audience
- **Smallholder Farmers:** Access actionable, simple recommendations via a clean Streamlit web app without hardware overhead.
- **Agricultural Extension Officers / KVK Agronomists:** Review downscaled local climate shifts and export printable advisory reports.
- **Gram Panchayat / Community Admins:** Monitor the live telemetry and calibration health of the village AWS node.
