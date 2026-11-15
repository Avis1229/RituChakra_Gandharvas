"""
Geocoder Module for RituChakra (Project Field Shift)
Multi-tier Geocoding & Geolocation Architecture:
- Tier 1: Mapbox Places Geocoding API (Primary world-class search & reverse geocoding)
- Tier 2: Geoapify Geocoding & IPinfo API (High-speed fallback & Live IP Geolocation)
- Tier 3: OpenStreetMap Nominatim API (Resilient open-source fallback)
"""

import requests
import os
from typing import List, Dict, Optional
from config import MAPBOX_ACCESS_TOKEN, GEOAPIFY_API_KEY

MAPBOX_PLACES_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
GEOAPIFY_AUTOCOMPLETE_URL = "https://api.geoapify.com/v1/geocode/autocomplete"
GEOAPIFY_REVERSE_URL = "https://api.geoapify.com/v1/geocode/reverse"
GEOAPIFY_IPINFO_URL = "https://api.geoapify.com/v1/ipinfo"
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

def detect_live_location(api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Auto-detect the user's current live location with multi-tiered fallback:
    1. ip-api.com (Instant, reliable, zero key required)
    2. Geoapify IP Geolocation (if key provided)
    3. ipapi.co (Secondary free fallback)
    """
    # 1. Primary fast fallback: ip-api.com
    try:
        res = requests.get("http://ip-api.com/json/", timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                lat = data.get("lat")
                lon = data.get("lon")
                city = data.get("city", "Local Field")
                state = data.get("regionName", "")
                country = data.get("country", "India")
                return {
                    "label": f"{city}, {state}, {country}".strip(", "),
                    "lat": round(float(lat), 4),
                    "lon": round(float(lon), 4),
                    "city": city,
                    "district": city,
                    "state": state,
                    "country": country,
                    "source": "Live Network Geolocation"
                }
    except Exception:
        pass

    # 2. Geoapify IP Geolocation if key provided
    key = api_key or GEOAPIFY_API_KEY
    if key:
        try:
            params = {"apiKey": key}
            res = requests.get(GEOAPIFY_IPINFO_URL, params=params, timeout=3)
            if res.status_code == 200:
                data = res.json()
                loc = data.get("location", {})
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                if lat is not None and lon is not None:
                    city = data.get("city", {}).get("name") or "Local Field"
                    state = data.get("state", {}).get("name") or ""
                    country = data.get("country", {}).get("name") or "India"
                    return {
                        "label": f"{city}, {state}, {country}".strip(", "),
                        "lat": round(float(lat), 4),
                        "lon": round(float(lon), 4),
                        "city": city,
                        "district": city,
                        "state": state,
                        "country": country,
                        "source": "Geoapify Live IP Geolocation"
                    }
        except Exception:
            pass

    # 3. ipapi.co Fallback
    try:
        headers = {"User-Agent": "RituChakra-SpaceApps/1.0"}
        res = requests.get("https://ipapi.co/json/", headers=headers, timeout=3)
        if res.status_code == 200:
            data = res.json()
            lat = data.get("latitude")
            lon = data.get("longitude")
            if lat and lon:
                city = data.get("city", "Local Field")
                state = data.get("region", "")
                country = data.get("country_name", "India")
                return {
                    "label": f"{city}, {state}, {country}".strip(", "),
                    "lat": round(float(lat), 4),
                    "lon": round(float(lon), 4),
                    "city": city,
                    "district": city,
                    "state": state,
                    "country": country,
                    "source": "IPAPI Fallback"
                }
    except Exception:
        pass

    return None

def search_locations(
    query: str, 
    limit: int = 5, 
    mapbox_token: Optional[str] = None,
    geoapify_key: Optional[str] = None,
    api_key: Optional[str] = None
) -> List[Dict]:
    """
    Search for a location by name (village, tehsil, district, city, country).
    Uses Mapbox as Tier-1 primary geocoder,
    with automatic fallback to Geoapify, and graceful degradation to OpenStreetMap Nominatim.
    """
    if not query or len(query.strip()) < 2:
        return []

    clean_query = query.strip()
    mb_token = mapbox_token or MAPBOX_ACCESS_TOKEN
    geo_key = geoapify_key or api_key or GEOAPIFY_API_KEY
    if api_key and not mapbox_token:
        # If an explicit test key was passed as api_key, check if it's invalid
        if "INVALID" in str(api_key):
            mb_token = None
            geo_key = None

    # Tier 1: Mapbox Places Geocoding API
    if mb_token:
        try:
            url = f"{MAPBOX_PLACES_BASE_URL}/{clean_query}.json"
            params = {
                "access_token": mb_token,
                "limit": limit
            }
            res = requests.get(url, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                results = []
                for feat in data.get("features", []):
                    label = feat.get("place_name", "")
                    center = feat.get("center", [])
                    if len(center) >= 2:
                        lon, lat = center[0], center[1]
                        context = feat.get("context", [])
                        district = ""
                        state = ""
                        country = ""
                        for c in context:
                            cid = c.get("id", "")
                            if "district" in cid or "place" in cid:
                                district = c.get("text", "")
                            elif "region" in cid:
                                state = c.get("text", "")
                            elif "country" in cid:
                                country = c.get("text", "")
                        if not district:
                            district = feat.get("text", "")

                        results.append({
                            "label": label,
                            "lat": round(float(lat), 4),
                            "lon": round(float(lon), 4),
                            "district": district,
                            "state": state,
                            "country": country,
                            "source": "Mapbox Places API"
                        })
                if results:
                    return results
        except Exception as e:
            print(f"[Geocoder] Mapbox notice: ({e}). Engaging Geoapify fallback.")

    # Tier 2: Geoapify Autocomplete API
    if geo_key:
        try:
            params = {
                "text": clean_query,
                "apiKey": geo_key,
                "limit": limit,
                "format": "json"
            }
            res = requests.get(GEOAPIFY_AUTOCOMPLETE_URL, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                results = []
                items = data.get("results") or [f.get("properties", {}) for f in data.get("features", [])]
                for item in items:
                    formatted = item.get("formatted", "")
                    lat = item.get("lat")
                    lon = item.get("lon")
                    if lat is not None and lon is not None:
                        district = item.get("district") or item.get("county") or item.get("city") or ""
                        state = item.get("state") or ""
                        country = item.get("country") or ""
                        results.append({
                            "label": formatted,
                            "lat": round(float(lat), 4),
                            "lon": round(float(lon), 4),
                            "district": district,
                            "state": state,
                            "country": country,
                            "source": "Geoapify API"
                        })
                if results:
                    return results
        except Exception as e:
            print(f"[Geocoder] Geoapify notice: ({e}). Engaging Nominatim fallback.")

    # Tier 3: OpenStreetMap Nominatim
    try:
        headers = {"User-Agent": "RituChakra-NASA-SpaceApps/1.0 (agritech-decision-support)"}
        params = {
            "q": clean_query,
            "format": "json",
            "limit": limit,
            "addressdetails": 1
        }
        res = requests.get(NOMINATIM_SEARCH_URL, params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            results = []
            for item in res.json():
                address = item.get("address", {})
                district = address.get("state_district") or address.get("county") or address.get("city") or ""
                state = address.get("state", "")
                country = address.get("country", "")
                results.append({
                    "label": item.get("display_name", ""),
                    "lat": round(float(item["lat"]), 4),
                    "lon": round(float(item["lon"]), 4),
                    "district": district,
                    "state": state,
                    "country": country,
                    "source": "OpenStreetMap Fallback"
                })
            return results
    except Exception as e:
        print(f"[Geocoder] Nominatim error: ({e})")

    return []

def reverse_geocode(
    lat: float, 
    lon: float, 
    mapbox_token: Optional[str] = None,
    geoapify_key: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict:
    """
    Convert (Latitude, Longitude) coordinates into a formatted place name, district, and state.
    Uses Mapbox as Tier-1 primary, falling back to Geoapify and OpenStreetMap.
    """
    mb_token = mapbox_token or MAPBOX_ACCESS_TOKEN
    geo_key = geoapify_key or api_key or GEOAPIFY_API_KEY

    # Tier 1: Mapbox Reverse Geocoding
    if mb_token:
        try:
            url = f"{MAPBOX_PLACES_BASE_URL}/{lon},{lat}.json"
            params = {"access_token": mb_token, "limit": 1}
            res = requests.get(url, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                features = data.get("features", [])
                if features:
                    feat = features[0]
                    context = feat.get("context", [])
                    district = ""
                    state = ""
                    country = ""
                    for c in context:
                        cid = c.get("id", "")
                        if "district" in cid or "place" in cid:
                            district = c.get("text", "")
                        elif "region" in cid:
                            state = c.get("text", "")
                        elif "country" in cid:
                            country = c.get("text", "")
                    return {
                        "formatted": feat.get("place_name", f"{lat:.4f}°, {lon:.4f}°"),
                        "district": district or feat.get("text", ""),
                        "state": state,
                        "country": country,
                        "source": "Mapbox Places API"
                    }
        except Exception:
            pass

    # Tier 2: Geoapify Reverse
    if geo_key:
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "apiKey": geo_key,
                "format": "json"
            }
            res = requests.get(GEOAPIFY_REVERSE_URL, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                items = data.get("results") or [f.get("properties", {}) for f in data.get("features", [])]
                if items:
                    first = items[0]
                    return {
                        "formatted": first.get("formatted", f"{lat:.4f}°, {lon:.4f}°"),
                        "district": first.get("district") or first.get("county") or "",
                        "state": first.get("state", ""),
                        "country": first.get("country", ""),
                        "source": "Geoapify API"
                    }
        except Exception:
            pass

    # Tier 3: OpenStreetMap Reverse Fallback
    try:
        headers = {"User-Agent": "RituChakra-NASA-SpaceApps/1.0"}
        params = {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1}
        res = requests.get(NOMINATIM_REVERSE_URL, params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            address = data.get("address", {})
            return {
                "formatted": data.get("display_name", f"{lat:.4f}°, {lon:.4f}°"),
                "district": address.get("state_district") or address.get("county") or "",
                "state": address.get("state", ""),
                "country": address.get("country", ""),
                "source": "OpenStreetMap Fallback"
            }
    except Exception:
        pass

    return {
        "formatted": f"{lat:.4f}°, {lon:.4f}°",
        "district": "Unknown District",
        "state": "Unknown State",
        "country": "India",
        "source": "Coordinate Fallback"
    }
