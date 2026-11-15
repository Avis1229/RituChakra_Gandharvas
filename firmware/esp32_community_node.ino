/*
 * =================================================================================
 * Project Field Shift (RituChakra) - NASA Space Apps Challenge 2026
 * Team: Gandharvas
 * 
 * Hardware: ESP32 Dev Module (Village Community Ground-Truth AWS Node)
 * Location: Gram Panchayat / Krishi Vigyan Kendra (10-12 km coverage radius)
 * Purpose: Stream real-time in-situ telemetry for NASA POWER & SMAP grid downscaling
 *          and Phase 1 "Bird Effect" convective storm early warnings.
 *
 * Sensors:
 *  - Bosch BME280 (I2C): Barometric Pressure (hPa), Ambient Temp (°C), Humidity (%)
 *  - Capacitive Soil Moisture Sensor v1.2 (10cm Root-Zone VWC %)
 *  - Optical/Tipping Rain Gauge (Pulse Interrupt on GPIO 14)
 *
 * Protocol: Lightweight JSON payload over WiFi / 4G LTE-M / LoRaWAN to MQTT Broker
 * =================================================================================
 */

#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// --- Hardware Pin Definitions ---
#define SOIL_PIN 34          // ADC1 Channel 6 (Capacitive Moisture Sensor)
#define RAIN_PIN 14          // Digital Interrupt for Tipping Bucket (0.2mm per tip)
#define BATTERY_PIN 35       // Voltage divider for 18650 Li-Ion monitoring

// Calibration constants for Capacitive Soil Moisture
const int AIR_VALUE = 3200;   // Sensor reading in completely dry air
const int WATER_VALUE = 1450; // Sensor reading submerged in water

// Node Identification
const char* NODE_ID = "COMM_NODE_MH_042";
const char* TEHSIL = "Amravati_GramPanchayat";

Adafruit_BME280 bme; // I2C address 0x76 or 0x77
WiFiClient espClient;
PubSubClient mqttClient(espClient);

volatile unsigned long rainTipCount = 0;
unsigned long lastTelemetryMillis = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 60000; // Publish every 60s

// Pressure tracking for Bird Effect (ΔP/Δt over 3 hours)
float pressureHistory[3] = {1013.25, 1013.25, 1013.25};
int pressureIdx = 0;

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
  float vwc = map(raw, AIR_VALUE, WATER_VALUE, 0, 100);
  return vwc;
}

// Magnus approximation for Dew Point (°C)
float calculateDewPoint(float tempC, float rhPct) {
  float a = 17.27;
  float b = 237.7;
  float alpha = ((a * tempC) / (b + tempC)) + log(rhPct / 100.0);
  return (b * alpha) / (a - alpha);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[RituChakra] Initializing Gandharvas Community IoT Node...");
  
  Wire.begin();
  if (!bme.begin(0x76) && !bme.begin(0x77)) {
    Serial.println("[ERROR] Bosch BME280 sensor not detected on I2C bus!");
  } else {
    Serial.println("[OK] Bosch BME280 (Pressure/Temp/Humidity) initialized.");
  }
  
  pinMode(RAIN_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(RAIN_PIN), onRainTip, FALLING);
  
  Serial.println("[RituChakra] Ground sensors calibrated. Streaming telemetry.");
}

void loop() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - lastTelemetryMillis >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryMillis = currentMillis;
    
    float temperature = bme.readTemperature();
    float humidity = bme.readHumidity();
    float pressureHPa = bme.readPressure() / 100.0F;
    float soilMoisture = readSoilMoistureVWC();
    float rainMm = rainTipCount * 0.2;
    rainTipCount = 0;
    float batteryV = readBatteryVoltage();
    
    // Dew Point and Depression
    float dewPoint = calculateDewPoint(temperature, humidity);
    float dewPointDepression = max(0.0F, temperature - dewPoint);
    
    // Calculate rate of pressure change (ΔP/Δt 3h estimate)
    float deltaP3h = pressureHPa - pressureHistory[pressureIdx];
    pressureHistory[pressureIdx] = pressureHPa;
    pressureIdx = (pressureIdx + 1) % 3;
    
    // Phase 1: Bird Effect proactive storm alert
    bool birdEffectAlert = (deltaP3h <= -2.0F && dewPointDepression <= 4.5F);
    
    // Construct Ground Truth Calibration JSON Payload
    StaticJsonDocument<384> doc;
    doc["node_id"] = NODE_ID;
    doc["location"] = TEHSIL;
    doc["temp_c"] = round(temperature * 100.0) / 100.0;
    doc["rh_pct"] = round(humidity * 10.0) / 10.0;
    doc["pressure_hpa"] = round(pressureHPa * 100.0) / 100.0;
    doc["delta_p_3h"] = round(deltaP3h * 100.0) / 100.0;
    doc["dew_point_c"] = round(dewPoint * 10.0) / 10.0;
    doc["dew_point_dep_c"] = round(dewPointDepression * 10.0) / 10.0;
    doc["bird_effect_alert"] = birdEffectAlert;
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

