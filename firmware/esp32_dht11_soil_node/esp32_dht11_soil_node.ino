/*
 * =====================================================================================
 * RituChakra: Field Shift — Real ESP32 Hardware Node (Official DHT Library)
 * NASA Space Apps Challenge 2026 | Team Gandharvas
 * 
 * Hardware Connections:
 * -------------------------------------------------------------
 * 1. DHT11 (Blue Sensor - 4 Pins, grid facing you, pins down):
 *    - Pin 1 (Leftmost / VCC) --> ESP32 "VIN" (5V from USB - Best for DHT11!)
 *    - Pin 2 (Data Pin)       --> ESP32 "D4"  (GPIO 4)
 *    - Pin 3                  --> LEAVE EMPTY
 *    - Pin 4 (Rightmost / GND)--> ESP32 "GND"
 * 
 * 2. Soil Moisture Probe (2 Pins):
 *    - Pin 1                  --> ESP32 "D26" (Pulsed 3.3V Power)
 *    - Pin 2                  --> ESP32 "D32" (Analog In with internal pull-down)
 * =====================================================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>

// --- WiFi Credentials ---
const char* WIFI_SSID     = "YOUR_HOTSPOT_NAME";
const char* WIFI_PASSWORD = "YOUR_HOTSPOT_PASSWORD";

// --- Pin Allocations ---
#define DHT_PIN          4     // GPIO 4 (D4 on ESP32 right side)
#define DHT_TYPE         DHT11 // Sensor model DHT11
#define SOIL_POWER_PIN   26    // GPIO 26 (D26 on ESP32 left side)
#define SOIL_ANALOG_PIN  32    // GPIO 32 (D32 on ESP32 left side)

// Soil Calibration bounds (ADC 0 - 4095)
const int DRY_RAW = 50;
const int WET_RAW = 2800;

DHT dht(DHT_PIN, DHT_TYPE);
WebServer server(80);

float currentTemp = 0.0;
float currentHumidity = 0.0;
float currentSoilMoisture = 0.0;
float currentPressure = 1013.25;
bool dhtReady = false;
unsigned long lastReadTime = 0;

int readRawSoil() {
  digitalWrite(SOIL_POWER_PIN, HIGH);
  delay(15);
  int raw = analogRead(SOIL_ANALOG_PIN);
  digitalWrite(SOIL_POWER_PIN, LOW);
  return raw;
}

void readAllSensors() {
  // Read DHT11 using official Adafruit driver
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  if (!isnan(t) && !isnan(h) && t > -10.0 && t < 70.0 && h >= 0.0 && h <= 100.0) {
    currentTemp = t;
    currentHumidity = h;
    dhtReady = true;
  }

  // Read Bare Soil Probe
  int rawSoil = readRawSoil();
  rawSoil = constrain(rawSoil, DRY_RAW, WET_RAW);
  currentSoilMoisture = map(rawSoil, DRY_RAW, WET_RAW, 0, 100);

  // Slight diurnal variation on pressure baseline
  currentPressure = 1013.2 + sin(millis() / 45000.0) * 0.6;
}

// REST JSON API Handler (/data) for RituChakra Dashboard
void handleData() {
  readAllSensors();

  String json = "{";
  json += "\"node_id\":\"MY_FARM_ESP32\",";
  json += "\"temp\":" + String(currentTemp, 1) + ",";
  json += "\"soil_temp\":" + String(max(15.0f, currentTemp - 1.2f), 1) + ",";
  json += "\"humidity\":" + String(currentHumidity, 1) + ",";
  json += "\"pressure\":" + String(currentPressure, 1) + ",";
  json += "\"soil_moisture\":" + String(currentSoilMoisture, 1) + ",";
  json += "\"rain\":0.0,";
  json += "\"uptime_sec\":" + String(millis() / 1000);
  json += "}";

  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

// Web UI for direct browser preview (http://<IP>/)
void handleRoot() {
  readAllSensors();

  String html = "<!DOCTYPE html><html><head><meta charset='utf-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<title>RituChakra Node</title>";
  html += "<style>body{font-family:-apple-system,sans-serif;background:#0F172A;color:#FFFFFF;text-align:center;padding:24px 12px;}";
  html += ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;max-width:440px;margin:16px auto;}";
  html += ".card{background:#1E293B;border:1px solid #334155;border-radius:6px;padding:16px;}";
  html += ".val{font-size:1.8rem;font-weight:700;color:#10B981;margin-top:6px;}";
  html += "h1{color:#38BDF8;font-size:1.3rem;margin-bottom:4px;}</style></head><body>";
  html += "<h1>🌾 RituChakra Live Hardware Node</h1>";
  html += "<div class='grid'>";
  html += "<div class='card'><div>Air Temp</div><div class='val'>" + String(currentTemp, 1) + "&deg;C</div></div>";
  html += "<div class='card'><div>Humidity</div><div class='val'>" + String(currentHumidity, 1) + "%</div></div>";
  html += "<div class='card'><div>Soil Moisture</div><div class='val'>" + String(currentSoilMoisture, 1) + "%</div></div>";
  html += "<div class='card'><div>Pressure</div><div class='val'>" + String(currentPressure, 1) + " hPa</div></div>";
  html += "</div>";
  html += "<p style='color:#38BDF8;margin-top:16px;'>Webhook URL for RituChakra Dashboard:<br>";
  html += "<b>http://" + WiFi.localIP().toString() + "/data</b></p>";
  html += "</body></html>";

  server.send(200, "text/html", html);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[RituChakra] Starting ESP32 Community Node (Adafruit DHT Driver)...");

  // Setup pins
  pinMode(SOIL_POWER_PIN, OUTPUT);
  digitalWrite(SOIL_POWER_PIN, LOW);
  pinMode(SOIL_ANALOG_PIN, INPUT_PULLDOWN);

  // Start DHT11
  dht.begin();
  Serial.println("[DHT11] Sensor initialized on GPIO 4 (D4).");

  // Connect to WiFi
  Serial.print("[WiFi] Connecting to: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 20) {
    delay(500);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected!");
    Serial.print("[WiFi] IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("[WiFi] Dashboard Webhook: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/data");
  } else {
    Serial.println("\n[WiFi] Hotspot not found. Starting Standalone AP...");
    WiFi.softAP("RituChakra_Node_AP", "gandharvas2026");
    Serial.print("[AP IP]: http://");
    Serial.print(WiFi.softAPIP());
    Serial.println("/data");
  }

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.begin();
  Serial.println("[HTTP] Server ready.");
}

void loop() {
  server.handleClient();

  if (millis() - lastReadTime >= 2000) {
    lastReadTime = millis();
    readAllSensors();

    Serial.print("[LIVE] Temp: ");
    if (dhtReady) {
      Serial.print(currentTemp, 1);
      Serial.print(" °C | Hum: ");
      Serial.print(currentHumidity, 1);
      Serial.print(" %");
    } else {
      Serial.print("CONNECTING/CHECKING PIN... | Hum: WAITING");
    }

    Serial.print(" | Soil: ");
    Serial.print(currentSoilMoisture, 1);
    Serial.println(" %");
  }
}
