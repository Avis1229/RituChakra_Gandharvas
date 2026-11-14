/*
 * =================================================================================
 * Project Field Shift (RituChakra) - NASA Space Apps Challenge 2026
 * Team: Gandharvas
 * 
 * Hardware: ESP32 Dev Module (Village Community Ground-Truth AWS Node)
 * Purpose: Ground-truth sensor node deployed at Gram Panchayat / Krishi Kendra
 *          Fuses with NASA POWER & SMAP 9x9 km satellite grids for microclimate calibration.
 *
 * Sensors:
 *  - DHT22 / SHT31: Ambient Air Temperature (°C) & Relative Humidity (%)
 *  - Capacitive Soil Moisture Sensor v1.2 (10cm Root-Zone VWC %)
 *  - Optical/Tipping Rain Gauge (Pulse Interrupt on GPIO 14)
 *  - BH1750 / Solar Pyranometer Photodiode (Solar Irradiance W/m^2)
 *
 * Protocol: Lightweight JSON payload over WiFi / 4G LTE-M / LoRaWAN to MQTT Broker
 * =================================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "DHT.h"

// --- Hardware Pin Definitions ---
#define DHTPIN 4
#define DHTTYPE DHT22
#define SOIL_PIN 34          // ADC1 Channel 6 (Capacitive Moisture Sensor)
#define RAIN_PIN 14          // Digital Interrupt for Tipping Bucket (0.2mm per tip)
#define BATTERY_PIN 35       // Voltage divider for 18650 Li-Ion monitoring

// Calibration constants for Capacitive Soil Moisture
const int AIR_VALUE = 3200;   // Sensor reading in completely dry air
const int WATER_VALUE = 1450; // Sensor reading submerged in water

// Node Identification
const char* NODE_ID = "COMM_NODE_MH_042";
const char* TEHSIL = "Amravati_GramPanchayat";

DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient mqttClient(espClient);

volatile unsigned long rainTipCount = 0;
unsigned long lastTelemetryMillis = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 60000; // Publish every 60s (or 10m in low-power)

void IRAM_ATTR onRainTip() {
  rainTipCount++;
}

float readBatteryVoltage() {
  int raw = analogRead(BATTERY_PIN);
  return (raw / 4095.0) * 2.0 * 3.3; // 1:1 voltage divider
}

float readSoilMoistureVWC() {
  int raw = analogRead(SOIL_PIN);
  raw = constrain(raw, WATER_VALUE, AIR_VALUE);
  // Map to volumetric water content percentage (0 to 100%)
  float vwc = map(raw, AIR_VALUE, WATER_VALUE, 0, 100);
  return vwc;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[RituChakra] Initializing Gandharvas Community IoT Node...");
  
  dht.begin();
  pinMode(RAIN_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(RAIN_PIN), onRainTip, FALLING);
  
  // WiFi / Connectivity placeholder (configured via WiFiManager or AP)
  Serial.println("[RituChakra] Sensors calibrated. Ready for telemetry stream.");
}

void loop() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - lastTelemetryMillis >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryMillis = currentMillis;
    
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float soilMoisture = readSoilMoistureVWC();
    float rainMm = rainTipCount * 0.2; // 0.2mm per tip
    rainTipCount = 0; // Reset for next interval
    float batteryV = readBatteryVoltage();
    
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("[ERROR] Failed to read from DHT sensor!");
      return;
    }
    
    // Construct Ground Truth Calibration JSON Payload
    StaticJsonDocument<256> doc;
    doc["node_id"] = NODE_ID;
    doc["location"] = TEHSIL;
    doc["temp_c"] = round(temperature * 100.0) / 100.0;
    doc["rh_pct"] = round(humidity * 10.0) / 10.0;
    doc["soil_vwc_pct"] = round(soilMoisture * 10.0) / 10.0;
    doc["rain_mm"] = round(rainMm * 10.0) / 10.0;
    doc["batt_v"] = round(batteryV * 100.0) / 100.0;
    doc["uptime_sec"] = millis() / 1000;
    
    String payload;
    serializeJson(doc, payload);
    
    Serial.print("[TELEMETRY -> MQTT/HTTP] ");
    Serial.println(payload);
    
    // In live deployment: mqttClient.publish("rituchakra/community_node/telemetry", payload.c_str());
  }
}
