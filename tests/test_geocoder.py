"""
Unit tests for modules/geocoder.py
Validates Geoapify location search, reverse geocoding, and OpenStreetMap fallback.
"""

import pytest
from modules.geocoder import search_locations, reverse_geocode, detect_live_location

def test_search_locations_geoapify_success():
    """Verify live search resolves an Indian district correctly via Mapbox / Geoapify."""
    results = search_locations("Amravati", limit=3)
    assert len(results) > 0
    first = results[0]
    assert "lat" in first
    assert "lon" in first
    assert isinstance(first["lat"], float)
    assert isinstance(first["lon"], float)
    assert 18.0 <= first["lat"] <= 23.0
    assert 75.0 <= first["lon"] <= 80.0
    assert "source" in first

def test_search_locations_mapbox_explicit():
    """Verify Mapbox Places API returns clean district and state attributes."""
    from config import MAPBOX_ACCESS_TOKEN
    results = search_locations("Bathinda", limit=2, mapbox_token=MAPBOX_ACCESS_TOKEN)
    assert len(results) > 0
    first = results[0]
    assert "Punjab" in first.get("state", "") or "India" in first.get("country", "")
    if MAPBOX_ACCESS_TOKEN:
        assert "Mapbox" in first.get("source", "")
    else:
        assert "OpenStreetMap" in first.get("source", "") or "Fallback" in first.get("source", "")


def test_search_locations_empty_query():
    """Verify empty or single character query returns empty list safely."""
    assert search_locations("") == []
    assert search_locations("a") == []

def test_reverse_geocode_bounds():
    """Verify coordinates reverse geocode into structured location dictionary."""
    result = reverse_geocode(lat=20.9320, lon=77.7523)
    assert "formatted" in result
    assert "district" in result
    assert "state" in result
    assert "India" in result["country"] or "Maharashtra" in result["state"]

def test_nominatim_fallback_when_key_invalid():
    """Verify graceful fallback to OpenStreetMap when an invalid key is supplied."""
    results = search_locations("Ludhiana", limit=2, api_key="INVALID_KEY_TEST_FALLBACK")
    assert len(results) > 0
    first = results[0]
    assert "lat" in first
    assert "lon" in first
    assert 29.0 <= first["lat"] <= 32.0

def test_detect_live_location():
    """Verify live location detection returns valid coordinates within global bounds."""
    loc = detect_live_location()
    if loc is not None:
        assert "lat" in loc
        assert "lon" in loc
        assert "label" in loc
        assert -90.0 <= loc["lat"] <= 90.0
        assert -180.0 <= loc["lon"] <= 180.0


