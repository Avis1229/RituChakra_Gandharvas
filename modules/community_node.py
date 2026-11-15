"""
Community Node Module (Team Gandharvas USP)
Models the Village/Panchayat-level AWS (ESP32/Raspberry Pi Community Node) with BME280 sensor
and ESA Sentinel-1 SAR cloud-penetrating radar validation.
Implements:
  - Phase 1: "Bird Effect" Proactive Storm Early Warning via ΔP/Δt and Dew Point Depression
  - Phase 2: Post-Event Sentinel-1 SAR Waterlogging & Disruption Protocol
  - Phase 3: In-Situ Calibration & Spatial Downscaling for NASA Satellite Grids
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

class CommunityNodeEngine:
    def __init__(self, node_id: str = "COMM_NODE_MH_042", radius_km: float = 10.0, is_custom_node: bool = False):
        self.node_id = node_id
        self.radius_km = radius_km
        self.is_custom_node = is_custom_node
        self.location_name = "Custom Field Node" if is_custom_node else "Gram Panchayat Krishi Kendra Node"
        self.status = "ONLINE (Active MQTT/HTTP Stream)"
        self.custom_telemetry = None

    def set_custom_telemetry(self, temp: float = 28.0, humidity: float = 60.0, pressure: float = 1012.0, 
                             soil_moisture: float = 25.0, rain_mm: float = 0.0, soil_temp: float = None, 
                             node_id: str = None, delta_p_3h: float = None, bird_effect_alert: bool = None, **kwargs):
        """Sets custom real-hardware readings from user's physical ESP32 or custom sensor."""
        self.custom_telemetry = {
            "temp": float(temp),
            "soil_temp": float(soil_temp if soil_temp is not None else temp),
            "humidity": float(humidity),
            "pressure": float(pressure),
            "soil_moisture": float(soil_moisture),
            "rain_mm": float(rain_mm),
            "delta_p_3h": float(delta_p_3h) if delta_p_3h is not None else None,
            "bird_effect_alert": bool(bird_effect_alert) if bird_effect_alert is not None else None,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if node_id:
            self.node_id = str(node_id)

    def fetch_from_http_endpoint(self, endpoint_url: str):
        """Attempts to poll live JSON telemetry from user's physical ESP32 or custom server."""
        try:
            import requests
            res = requests.get(endpoint_url.strip(), timeout=3)
            if res.status_code == 200:
                data = res.json()
                temp = float(data.get("temp", data.get("temperature", 28.0)))
                hum = float(data.get("humidity", data.get("rh", 60.0)))
                pres = float(data.get("pressure", data.get("baro", 1012.0)))
                sm = float(data.get("soil_moisture", data.get("moisture", 25.0)))
                st = float(data.get("soil_temp", data.get("soil_temperature", temp)))
                rain = float(data.get("rain", data.get("precipitation", 0.0)))
                node_id = data.get("node_id", None)
                delta_p = data.get("delta_p_3h", None)
                bird_alert = data.get("bird_effect_alert", None)
                
                telemetry = {
                    "temp": temp,
                    "soil_temp": st,
                    "humidity": hum,
                    "pressure": pres,
                    "soil_moisture": sm,
                    "rain_mm": rain
                }
                if node_id:
                    telemetry["node_id"] = str(node_id)
                if delta_p is not None:
                    telemetry["delta_p_3h"] = float(delta_p)
                if bird_alert is not None:
                    telemetry["bird_effect_alert"] = bool(bird_alert)
                    
                self.set_custom_telemetry(**telemetry)
                return telemetry
        except Exception:
            pass
        return None
        
    def generate_ground_truth_telemetry(self, satellite_temp: float, satellite_precip: float, 
                                        base_soil_moisture: float = 24.5, days: int = 30, seed: int = None) -> pd.DataFrame:
        """
        Simulate 30 days of high-frequency local BME280 + Sentinel-1 SAR telemetry.
        Ground sensors capture micro-topography, barometric pressure anomalies, and canopy effects.
        """
        if seed is not None:
            np.random.seed(seed)
        else:
            # Deterministic, unique seed per node to ensure location-specific variance
            node_seed = sum(ord(c) for c in self.node_id) * 31 + int(satellite_temp * 10)
            np.random.seed(node_seed % 100000)
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in reversed(range(days))]
        
        records = []
        temp_bias = 0.8  # Ground is slightly warmer during dry spell due to bare soil albedo
        precip_bias_multiplier = 1.15 # Convective storms cause localized spikes
        
        current_sm = base_soil_moisture
        base_pressure = 1012.5 # Mean sea-level / field station barometric baseline (hPa)
        
        for i, dt in enumerate(dates):
            # Satellite nominal reading with small variance
            sat_t = satellite_temp + np.sin(i / 5.0) * 2.0 + np.random.normal(0, 0.4)
            
            # Convective rainfall events (simulate storm events on day 10 and day 24)
            is_storm_day = (i == 10 or i == 24)
            has_rain = is_storm_day or (i % 7 == 3)
            sat_p = (np.random.exponential(24.0 if is_storm_day else 8.0) if has_rain else 0.0)
            
            # Ground truth ESP32 BME280 readings
            ground_t = sat_t + temp_bias + np.random.normal(0, 0.6)
            ground_p = sat_p * precip_bias_multiplier + (np.random.normal(2.5, 0.8) if has_rain else 0.0)
            ground_p = max(0.0, ground_p)
            
            # BME280 Barometric Pressure Dynamics:
            # Diurnal atmospheric tide ±1.5 hPa; storm events cause sudden pressure plunges of -3.5 to -5.0 hPa
            pressure_dip = -4.2 if is_storm_day else (np.random.normal(0, 0.4))
            baro_pressure = base_pressure + np.cos(i / 3.0) * 1.8 + pressure_dip
            
            # Rate of change of pressure (ΔP/Δt over 3 hours)
            delta_p_3h = -3.8 if is_storm_day else round(np.random.normal(0.1, 0.5), 2)
            
            # Relative Humidity & Dew Point calculation (BME280)
            # Before a convective storm, high humidity influx pushes RH to 80-95%
            base_rh = 86.0 if is_storm_day else 62.0
            rh_pct = min(96.0, max(38.0, base_rh + (ground_p * 0.4) - (ground_t - 25.0) * 0.6 + np.random.normal(0, 1.5)))
            # Magnus approximation for Dew Point
            dew_point = ground_t - ((100.0 - rh_pct) / 5.0)
            dew_point_depression = max(0.2, ground_t - dew_point)
            
            # PHASE 1: "BIRD EFFECT" PROACTIVE EARLY WARNING
            # Sudden barometric pressure plunge (ΔP/Δt <= -2.0 hPa/3hr) combined with low dew point depression (moisture saturation)
            bird_effect_alert = bool(delta_p_3h <= -2.0 and dew_point_depression <= 4.5)
            
            # Ground soil moisture dynamic (Capacitive sensor 0-100% VWC)
            evap = 0.35 + (ground_t / 35.0) * 0.4
            current_sm = max(10.0, min(52.0, current_sm + (ground_p * 0.65) - evap + np.random.normal(0, 0.3)))
            
            # Satellite SMAP proxy (9km resolution tends to smooth spatial extremes)
            smap_sm = current_sm * 0.88 + 3.0 + np.random.normal(0, 1.2)
            
            # Calibrated Values (Sensor Fusion: α = 0.75 in-situ weight)
            calibrated_t = 0.75 * ground_t + 0.25 * sat_t
            calibrated_sm = 0.75 * current_sm + 0.25 * smap_sm
            
            # PHASE 2: ESA SENTINEL-1 SAR RADAR BACKSCATTER (CLOUDS PENETRATION)
            # Normal agricultural vegetation backscatter: -14 to -16 dB
            # Standing water / waterlogging specular reflection: drops sharply to <= -19.5 dB
            is_post_storm_flooded = is_storm_day or (i in [11, 12, 25])
            sar_backscatter = -21.2 if is_post_storm_flooded else round(-14.2 + np.random.normal(0, 0.6), 1)
            waterlogging_detected = bool(sar_backscatter <= -19.0 and current_sm > 44.0)
            
            records.append({
                "Date": dt.strftime("%Y-%m-%d"),
                "Satellite_T2M_C": round(sat_t, 2),
                "Ground_ESP32_Temp_C": round(ground_t, 2),
                "Calibrated_Temp_C": round(calibrated_t, 2),
                
                "Satellite_Precip_mm": round(sat_p, 2),
                "Ground_ESP32_Rain_mm": round(ground_p, 2),
                
                "NASA_SMAP_Moisture_pct": round(smap_sm, 1),
                "Ground_ESP32_SoilMoisture_pct": round(current_sm, 1),
                "Calibrated_SoilMoisture_pct": round(calibrated_sm, 1),
                
                # BME280 Atmospheric Metrics
                "BME280_Pressure_hPa": round(baro_pressure, 2),
                "Pressure_Delta_3h_hPa": round(delta_p_3h, 2),
                "BME280_Humidity_pct": round(rh_pct, 1),
                "Dew_Point_C": round(dew_point, 2),
                "Dew_Point_Depression_C": round(dew_point_depression, 2),
                "Bird_Effect_Storm_Alert": bird_effect_alert,
                
                # Sentinel-1 SAR Radar Metrics
                "Sentinel1_SAR_Backscatter_dB": round(sar_backscatter, 1),
                "Sentinel1_Waterlogging": waterlogging_detected,
                
                "Node_Battery_V": round(3.95 - (i * 0.003) + np.random.normal(0, 0.02), 2),
                "Signal_RSSI_dBm": int(-68 + np.random.normal(0, 2))
            })

        # Inject real physical hardware telemetry if connected
        if self.custom_telemetry and len(records) > 0:
            last = records[-1]
            last["Ground_ESP32_Temp_C"] = round(float(self.custom_telemetry["temp"]), 2)
            last["BME280_Humidity_pct"] = round(float(self.custom_telemetry["humidity"]), 1)
            last["BME280_Pressure_hPa"] = round(float(self.custom_telemetry["pressure"]), 2)
            last["Ground_ESP32_SoilMoisture_pct"] = round(float(self.custom_telemetry["soil_moisture"]), 1)
            last["Ground_ESP32_Rain_mm"] = round(float(self.custom_telemetry.get("rain_mm", 0.0)), 2)
            last["Calibrated_Temp_C"] = round(0.75 * last["Ground_ESP32_Temp_C"] + 0.25 * last["Satellite_T2M_C"], 2)
            last["Calibrated_SoilMoisture_pct"] = round(0.75 * last["Ground_ESP32_SoilMoisture_pct"] + 0.25 * last["NASA_SMAP_Moisture_pct"], 1)
            dew = last["Ground_ESP32_Temp_C"] - ((100.0 - last["BME280_Humidity_pct"]) / 5.0)
            last["Dew_Point_C"] = round(dew, 2)
            last["Dew_Point_Depression_C"] = round(max(0.2, last["Ground_ESP32_Temp_C"] - dew), 2)
            
            # Inject Pressure Delta & Bird Effect Storm Alert
            if self.custom_telemetry.get("delta_p_3h") is not None:
                last["Pressure_Delta_3h_hPa"] = round(float(self.custom_telemetry["delta_p_3h"]), 2)
            elif len(records) >= 2:
                last["Pressure_Delta_3h_hPa"] = round(last["BME280_Pressure_hPa"] - records[-2]["BME280_Pressure_hPa"], 2)
                
            if self.custom_telemetry.get("bird_effect_alert") is not None:
                last["Bird_Effect_Storm_Alert"] = bool(self.custom_telemetry["bird_effect_alert"])
            else:
                last["Bird_Effect_Storm_Alert"] = bool(last["Pressure_Delta_3h_hPa"] <= -1.5 and last["Dew_Point_Depression_C"] <= 5.5)
            
        return pd.DataFrame(records)

    def calculate_calibration_metrics(self, df_telemetry: pd.DataFrame) -> dict:
        """
        Calculate quantitative calibration accuracy, BME280 pressure trends, and Sentinel-1 SAR waterlogging status.
        """
        raw_temp_error = np.abs(df_telemetry["Satellite_T2M_C"] - df_telemetry["Ground_ESP32_Temp_C"]).mean()
        calibrated_temp_error = np.abs(df_telemetry["Calibrated_Temp_C"] - df_telemetry["Ground_ESP32_Temp_C"]).mean()
        
        raw_sm_error = np.abs(df_telemetry["NASA_SMAP_Moisture_pct"] - df_telemetry["Ground_ESP32_SoilMoisture_pct"]).mean()
        calibrated_sm_error = np.abs(df_telemetry["Calibrated_SoilMoisture_pct"] - df_telemetry["Ground_ESP32_SoilMoisture_pct"]).mean()
        
        temp_improvement_pct = ((raw_temp_error - calibrated_temp_error) / max(0.001, raw_temp_error)) * 100.0
        sm_improvement_pct = ((raw_sm_error - calibrated_sm_error) / max(0.001, raw_sm_error)) * 100.0
        
        latest_row = df_telemetry.iloc[-1]
        storm_alerts_count = int(df_telemetry["Bird_Effect_Storm_Alert"].sum())
        waterlogged_days_count = int(df_telemetry["Sentinel1_Waterlogging"].sum())
        
        # Disruption protocol is active if recent waterlogging detected
        disruption_active = bool(waterlogged_days_count > 0 or latest_row["Sentinel1_Waterlogging"])
        
        return {
            "node_id": self.node_id,
            "coverage_radius_km": self.radius_km,
            "raw_temp_mae": round(raw_temp_error, 2),
            "calibrated_temp_mae": round(calibrated_temp_error, 2),
            "temp_accuracy_gain_pct": round(temp_improvement_pct, 1),
            "raw_soil_moisture_mae": round(raw_sm_error, 2),
            "calibrated_soil_moisture_mae": round(calibrated_sm_error, 2),
            "sm_accuracy_gain_pct": round(sm_improvement_pct, 1),
            
            # Phase 1 & 2 Metrics
            "latest_pressure_hPa": float(latest_row["BME280_Pressure_hPa"]),
            "latest_delta_p_3h": float(latest_row["Pressure_Delta_3h_hPa"]),
            "latest_dew_point_depression": float(latest_row["Dew_Point_Depression_C"]),
            "bird_effect_storm_alert": bool(latest_row["Bird_Effect_Storm_Alert"]),
            "storm_alerts_30d": storm_alerts_count,
            
            "latest_sar_backscatter_db": float(latest_row["Sentinel1_SAR_Backscatter_dB"]),
            "sar_waterlogging_detected": bool(latest_row["Sentinel1_Waterlogging"]),
            "waterlogged_days_30d": waterlogged_days_count,
            "disruption_protocol_active": disruption_active,
            
            "active_sensors": [
                "BME280 Atmospheric Sensor (Barometric Pressure, Temp, RH via I2C)",
                "Capacitive Corrosion-Resistant Soil VWC Probe (10cm Root-Zone)",
                "Tipping Bucket Rain Gauge (0.2mm resolution)",
                "ESA Sentinel-1 SAR C-band Cloud-Penetrating Radar Pipeline"
            ],
            "calibration_formula": "Calibrated_Value = α · Ground_Node_Obs + (1 - α) · NASA_Grid_Pixel (α = 0.75)"
        }


