/*
 * =====================================================================================
 * RituChakra: Field Shift — Full Community IoT Node Hardware Simulator
 * NASA Space Apps Challenge 2026 | Team Gandharvas
 * 
 * COMPLETE HARDWARE SUITE SIMULATED IN WOKWI:
 * 1. Bosch BME280 (I2C):
 *    - Barometric Atmospheric Pressure (hPa)
 *    - Ambient Air Temperature (°C)
 *    - Relative Humidity (%)
 * 2. Capacitive Soil Moisture Sensor v1.2:
 *    - Root-Zone Volumetric Water Content (0% to 100% VWC) via Potentiometer on GPIO 34
 * 3. Optical Tipping Bucket Rain Gauge:
 *    - Pushbutton interrupt on GPIO 14 (0.2mm per tip)
 * 4. SSD1306 128x64 OLED Display (I2C):
 *    - Live visual field telemetry dashboard & Phase 1 "Bird Effect" Storm Alerts
 * 5. Wokwi Virtual WiFi & REST Server:
 *    - Connects to "Wokwi-GUEST" and serves live JSON telemetry on http://<IP>/data
 * =====================================================================================
 */

#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// --- Pin Definitions ---
#define SOIL_POT_PIN     34    // GPIO 34 (ADC1)
#define RAIN_PIN         14    // GPIO 14 (Interrupt for rain gauge)
#define SCREEN_WIDTH    128
#define SCREEN_HEIGHT    64
#define OLED_RESET       -1

// Node Configuration
const char* NODE_ID = "COMM_NODE_MH_042";
const char* REGION  = "Vidarbha_Krishi_Kendra";

Adafruit_BME280 bme;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
WebServer server(80);

volatile unsigned long rainTips = 0;
float currentTemp = 28.5;
float currentHumidity = 62.0;
float currentPressure = 1012.8;
float currentSoilMoisture = 35.0;
float deltaP3h = -0.3;
float dewPoint = 20.5;
float dewPointDepression = 8.0;
bool birdEffectAlert = false;
unsigned long lastUpdate = 0;

void IRAM_ATTR onRainTip() {
  rainTips++;
}

float calcDewPoint(float temp, float rh) {
  float a = 17.27;
  float b = 237.7;
  float alpha = ((a * temp) / (b + temp)) + log(rh / 100.0);
  return (b * alpha) / (a - alpha);
}

void updateOLED() {
  display.clearDisplay();
  
  // Header
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("RITUCHAKRA IoT NODE");
  display.drawLine(0, 9, 127, 9, SSD1306_WHITE);

  // Row 1: Temp & Humidity
  display.setCursor(0, 13);
  display.print("Temp: ");
  display.print(currentTemp, 1);
  display.print("C  RH: ");
  display.print(currentHumidity, 0);
  display.println("%");

  // Row 2: Barometric Pressure
  display.setCursor(0, 24);
  display.print("Baro: ");
  display.print(currentPressure, 1);
  display.print(" hPa");

  // Row 3: Soil Moisture & Rain
  display.setCursor(0, 35);
  display.print("Soil: ");
  display.print(currentSoilMoisture, 0);
  display.print("%  Rain: ");
  display.print(rainTips * 0.2, 1);
  display.println("mm");

  // Row 4: Bird Effect Storm Alert Banner
  display.drawLine(0, 47, 127, 47, SSD1306_WHITE);
  display.setCursor(0, 52);
  if (birdEffectAlert) {
    display.print("! STORM WARNING !");
  } else {
    display.print("Atmosphere: STABLE");
  }

  display.display();
}

void readAllSensors() {
  // Read BME280
  float t = bme.readTemperature();
  float h = bme.readHumidity();
  float p = bme.readPressure() / 100.0F;

  if (!isnan(t) && t > -30.0 && t < 80.0) currentTemp = t;
  if (!isnan(h) && h >= 0.0 && h <= 100.0) currentHumidity = h;
  if (!isnan(p) && p > 800.0 && p < 1100.0) currentPressure = p;

  // Read Soil Moisture Potentiometer (0 - 4095 mapped to 5% - 85% VWC)
  int rawSoil = analogRead(SOIL_POT_PIN);
  currentSoilMoisture = map(rawSoil, 0, 4095, 5, 85);

  // Compute Dew Point & Depression
  dewPoint = calcDewPoint(currentTemp, currentHumidity);
  dewPointDepression = max(0.1F, currentTemp - dewPoint);

  // Compute delta P (If pressure dropped below 1009 hPa with high humidity)
  deltaP3h = (currentPressure - 1013.25);
  
  // Phase 1: Bird Effect Early Storm Warning
  birdEffectAlert = (deltaP3h <= -2.0F && dewPointDepression <= 4.5F);
}

// REST API for RituChakra Dashboard
void handleData() {
  readAllSensors();

  String json = "{";
  json += "\"node_id\":\"" + String(NODE_ID) + "\",";
  json += "\"region\":\"" + String(REGION) + "\",";
  json += "\"temp\":" + String(currentTemp, 1) + ",";
  json += "\"soil_temp\":" + String(currentTemp - 1.5, 1) + ",";
  json += "\"humidity\":" + String(currentHumidity, 1) + ",";
  json += "\"pressure\":" + String(currentPressure, 1) + ",";
  json += "\"delta_p_3h\":" + String(deltaP3h, 1) + ",";
  json += "\"dew_point_c\":" + String(dewPoint, 1) + ",";
  json += "\"bird_effect_alert\":" + String(birdEffectAlert ? "true" : "false") + ",";
  json += "\"soil_moisture\":" + String(currentSoilMoisture, 1) + ",";
  json += "\"rain\":" + String(rainTips * 0.2, 1) + ",";
  json += "\"uptime_sec\":" + String(millis() / 1000);
  json += "}";

  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n=======================================================");
  Serial.println("  RituChakra: Field Shift — Full Community IoT Node    ");
  Serial.println("  NASA Space Apps Challenge 2026 | Team Gandharvas     ");
  Serial.println("=======================================================\n");

  Wire.begin();

  // Initialize OLED Display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("[WARN] OLED display not found at 0x3C");
  } else {
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(10, 24);
    display.println("RituChakra Booting...");
    display.display();
  }

  // Initialize Bosch BME280
  if (!bme.begin(0x76) && !bme.begin(0x77)) {
    Serial.println("[ERROR] BME280 sensor not detected on I2C bus!");
  } else {
    Serial.println("[OK] Bosch BME280 (Pressure/Temp/Humidity) active.");
  }

  // Setup pins
  pinMode(SOIL_POT_PIN, INPUT);
  pinMode(RAIN_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(RAIN_PIN), onRainTip, FALLING);

  // Connect to Wokwi Virtual WiFi
  Serial.print("[WiFi] Connecting to virtual Wokwi-GUEST...");
  WiFi.begin("Wokwi-GUEST", "", 6);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 15) {
    delay(200);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" CONNECTED!");
    Serial.print("[WiFi] IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("[REST Webhook]: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/data");
  }

  server.on("/data", handleData);
  server.begin();
  Serial.println("[HTTP] Server ready.\n");
}

void loop() {
  server.handleClient();

  if (millis() - lastUpdate >= 1500) {
    lastUpdate = millis();
    readAllSensors();
    updateOLED();

    // Print JSON telemetry to Serial Monitor
    Serial.print("{\"node_id\":\"COMM_NODE_MH_042\",\"temp\":");
    Serial.print(currentTemp, 1);
    Serial.print(",\"humidity\":");
    Serial.print(currentHumidity, 1);
    Serial.print(",\"pressure\":");
    Serial.print(currentPressure, 1);
    Serial.print(",\"soil_moisture\":");
    Serial.print(currentSoilMoisture, 1);
    Serial.print(",\"rain_mm\":");
    Serial.print(rainTips * 0.2, 1);
    Serial.print(",\"bird_effect\":");
    Serial.print(birdEffectAlert ? "ALERT_STORM" : "NOMINAL");
    Serial.println("}");
  }

  delay(20);
}
