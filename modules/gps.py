"""
GPS Geolocation Component Wrapper for Streamlit.
Integrates HTML5 Browser Geolocation with Streamlit custom component interface.
Provides real-time device hardware GPS coordinates with zero IP-lookup error.
"""

import os
import streamlit.components.v1 as components
from typing import Optional, Dict

_COMPONENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "components", "gps_locator"))

_gps_component = components.declare_component("gps_locator", path=_COMPONENT_DIR)

def get_browser_gps(key: str = "browser_gps_locator") -> Optional[Dict]:
    """
    Renders the HTML5 GPS locator component in the browser.
    Returns:
        dict: {"latitude": float, "longitude": float, "accuracy": int, "timestamp": int} or None
    """
    return _gps_component(key=key)
