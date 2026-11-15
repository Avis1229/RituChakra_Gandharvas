#!/usr/bin/env python3
"""
RituChakra: Mock Field Hardware Node Server
Simulates an ESP32 Community Node over HTTP for local testing and presentation demos.
Provides a REST endpoint at http://127.0.0.1:8000/data and an interactive control panel at http://127.0.0.1:8000/
"""

import json
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Global state for simulated node telemetry
SIM_NODE_STATE = {
    "node_id": "ESP32_FIELD_NODE_01",
    "location": "Vidarbha_Krishi_Kendra",
    "temp": 31.5,
    "soil_temp": 28.2,
    "humidity": 64.0,
    "pressure": 1008.4,
    "delta_p_3h": -2.2,
    "soil_moisture": 33.5,
    "rain": 1.4,
    "bird_effect_alert": True,
    "uptime_sec": 0
}

START_TIME = time.time()

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RituChakra — Virtual Field Hardware Node</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #0F172A;
      color: #F8FAFC;
      margin: 0;
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .panel {
      background: #1E293B;
      border: 1px solid #334155;
      border-radius: 6px;
      max-width: 540px;
      width: 100%;
      padding: 24px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    h1 {
      font-size: 1.3rem;
      margin-top: 0;
      color: #38BDF8;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .badge {
      display: inline-block;
      background: #059669;
      color: #FFF;
      font-size: 0.75rem;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .control-row {
      margin-bottom: 16px;
    }
    .control-label {
      display: flex;
      justify-content: space-between;
      font-size: 0.88rem;
      margin-bottom: 6px;
      color: #CBD5E1;
      font-weight: 600;
    }
    input[type=range] {
      width: 100%;
      accent-color: #38BDF8;
    }
    .val-display {
      color: #10B981;
      font-weight: 700;
    }
    .api-url-box {
      background: #0F172A;
      border: 1px solid #334155;
      border-radius: 4px;
      padding: 12px;
      margin-top: 20px;
      font-family: monospace;
      font-size: 0.88rem;
      color: #38BDF8;
      word-break: break-all;
    }
    .btn-storm {
      background: #DC2626;
      color: white;
      border: none;
      padding: 10px 16px;
      border-radius: 4px;
      font-weight: 700;
      cursor: pointer;
      width: 100%;
      margin-top: 12px;
      transition: background 0.2s;
    }
    .btn-storm:hover {
      background: #B91C1C;
    }
  </style>
</head>
<body>
  <div class="panel">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
      <h1>🌾 RituChakra Virtual Node</h1>
      <span class="badge">ONLINE (Port 8000)</span>
    </div>
    <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0;">
      Simulates ESP32 BME280 + Capacitive Soil Moisture telemetry. Adjust sliders below to stream live readings to your Streamlit dashboard.
    </p>

    <div class="control-row">
      <div class="control-label">
        <span>Air Temperature</span>
        <span class="val-display" id="disp_temp">31.5 °C</span>
      </div>
      <input type="range" id="rng_temp" min="15.0" max="48.0" step="0.5" value="31.5" oninput="updateVal('temp', this.value, '°C')">
    </div>

    <div class="control-row">
      <div class="control-label">
        <span>Relative Humidity</span>
        <span class="val-display" id="disp_humidity">64 %</span>
      </div>
      <input type="range" id="rng_hum" min="20.0" max="98.0" step="1.0" value="64.0" oninput="updateVal('humidity', this.value, '%')">
    </div>

    <div class="control-row">
      <div class="control-label">
        <span>Soil Moisture (VWC)</span>
        <span class="val-display" id="disp_soil_moisture">33.5 %</span>
      </div>
      <input type="range" id="rng_soil" min="5.0" max="75.0" step="0.5" value="33.5" oninput="updateVal('soil_moisture', this.value, '%')">
    </div>

    <div class="control-row">
      <div class="control-label">
        <span>Barometric Pressure</span>
        <span class="val-display" id="disp_pressure">1008.4 hPa</span>
      </div>
      <input type="range" id="rng_press" min="980.0" max="1025.0" step="0.5" value="1008.4" oninput="updateVal('pressure', this.value, 'hPa')">
    </div>

    <button class="btn-storm" onclick="triggerStorm()">⚡ Simulate Sudden Convective Storm (Bird Effect)</button>

    <div class="api-url-box">
      <b>Streamlit Webhook URL:</b><br>
      http://127.0.0.1:8000/data
    </div>
  </div>

  <script>
    function updateVal(key, val, unit) {
      document.getElementById('disp_' + key).innerText = val + ' ' + unit;
      fetch('/update?' + key + '=' + encodeURIComponent(val));
    }
    function triggerStorm() {
      fetch('/update?pressure=996.5&humidity=94.0&temp=24.5&soil_moisture=52.0&rain=18.5&bird_effect_alert=true')
        .then(() => location.reload());
    }
  </script>
</body>
</html>
"""

class NodeRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/data":
            # Return live JSON telemetry
            SIM_NODE_STATE["uptime_sec"] = int(time.time() - START_TIME)
            data_bytes = json.dumps(SIM_NODE_STATE).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data_bytes)))
            self.end_headers()
            self.wfile.write(data_bytes)
            
        elif parsed.path == "/update":
            # Update parameters from query params
            params = parse_qs(parsed.query)
            for k, v in params.items():
                if k in SIM_NODE_STATE and v:
                    try:
                        val = float(v[0])
                        SIM_NODE_STATE[k] = val
                    except ValueError:
                        if v[0].lower() in ["true", "false"]:
                            SIM_NODE_STATE[k] = (v[0].lower() == "true")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            
        else:
            # Serve Interactive Control Panel
            page_bytes = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page_bytes)))
            self.end_headers()
            self.wfile.write(page_bytes)

def run_server(port=8000):
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, NodeRequestHandler)
    print(f"RituChakra Mock Node Server running on http://127.0.0.1:{port}/")
    print(f"Telemetry Webhook: http://127.0.0.1:{port}/data")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server(8000)

