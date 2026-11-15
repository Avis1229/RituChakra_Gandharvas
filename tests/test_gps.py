"""
Unit test for modules/gps.py (HTML5 Browser GPS Geolocation wrapper).
"""

import pytest
from modules.gps import get_browser_gps

def test_gps_component_callable():
    """Verify get_browser_gps is defined and returns None in headless/non-interactive test environment."""
    result = get_browser_gps()
    # In headless pytest without a connected browser, it returns None safely
    assert result is None or isinstance(result, dict)

