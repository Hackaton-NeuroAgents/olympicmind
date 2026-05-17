"""
Weather Client for OlympicMind
Fetches real-time weather data for Milan and Olympic venues.
Uses OpenWeatherMap free API.
"""

import os
import requests
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"

# Olympic venue coordinates for weather checks
VENUE_COORDS = {
    "Milano San Siro Stadium":      {"lat": 45.4781, "lon": 9.1240},
    "Santagiulia Ice Arena":        {"lat": 45.4384, "lon": 9.2084},
    "Rho Ice Hockey Arena":         {"lat": 45.5170, "lon": 9.0830},
    "Milano Ice Skating Arena":     {"lat": 45.4654, "lon": 9.1859},
    "Milano Speed Skating Stadium": {"lat": 45.4505, "lon": 9.1725},
    "Cortina Sliding Center":       {"lat": 46.5362, "lon": 12.1356},
    "Cortina Curling Stadium":      {"lat": 46.5400, "lon": 12.1390},
    "Tofane Skiing Centre":         {"lat": 46.5500, "lon": 12.1200},
    "Stelvio Ski Centre (Bormio)":  {"lat": 46.4667, "lon": 10.3667},
    "Predazzo Ski Jumping":         {"lat": 46.3167, "lon": 11.6000},
    "Tesero Cross-Country":         {"lat": 46.2833, "lon": 11.5833},
    "Antholz Biathlon Arena":       {"lat": 46.7500, "lon": 12.0167},
    "Livigno Snow Park":            {"lat": 46.5372, "lon": 10.1360},
    "Verona Olympic Arena":         {"lat": 45.4386, "lon": 10.9928},
}


def _risk_from_weather(weather: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate travel risk based on weather conditions."""
    condition = weather.get("main", "").lower()
    description = weather.get("description", "").lower()
    wind_speed = weather.get("wind_speed_ms", 0)
    visibility_km = weather.get("visibility_km", 10)
    temp_c = weather.get("temp_c", 5)

    risk_score = 0
    warnings = []

    # Snow/ice conditions
    if "snow" in condition or "snow" in description:
        risk_score += 40
        warnings.append("❄️ Snow — icy roads, reduce speed")
    elif "sleet" in description or "freezing" in description:
        risk_score += 35
        warnings.append("🌨️ Sleet/Freezing rain — dangerous roads")

    # Rain
    if "rain" in condition or "drizzle" in condition:
        risk_score += 20
        warnings.append("🌧️ Rain — wet roads, allow extra time")

    # Fog/low visibility
    if visibility_km < 1:
        risk_score += 30
        warnings.append("🌫️ Dense fog — extremely low visibility")
    elif visibility_km < 5:
        risk_score += 15
        warnings.append("🌫️ Fog — low visibility, drive carefully")

    # Strong winds
    if wind_speed > 15:
        risk_score += 20
        warnings.append(f"💨 Strong winds {wind_speed:.0f} m/s — mountain roads dangerous")
    elif wind_speed > 10:
        risk_score += 10
        warnings.append(f"💨 Moderate winds {wind_speed:.0f} m/s")

    # Extreme cold (black ice risk)
    if temp_c < -5:
        risk_score += 15
        warnings.append(f"🥶 Extreme cold {temp_c:.0f}°C — black ice risk")
    elif temp_c < 0:
        risk_score += 8
        warnings.append(f"🌡️ Below freezing {temp_c:.0f}°C — ice possible")

    risk_score = min(100, risk_score)

    if risk_score >= 60:
        level = "HIGH"
    elif risk_score >= 30:
        level = "MODERATE"
    elif risk_score > 0:
        level = "LOW"
    else:
        level = "CLEAR"

    return {
        "weather_risk_score": risk_score,
        "weather_risk_level": level,
        "warnings": warnings,
    }


def get_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Fetch current weather for given coordinates."""
    if not OPENWEATHER_API_KEY:
        # Return simulated data if no API key
        return {
            "temp_c": 2.0,
            "feels_like_c": -1.0,
            "main": "Snow",
            "description": "light snow",
            "humidity": 85,
            "wind_speed_ms": 8.0,
            "visibility_km": 5.0,
            "simulated": True,
        }

    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "temp_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "main": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed_ms": data["wind"]["speed"],
            "visibility_km": data.get("visibility", 10000) / 1000,
            "simulated": False,
        }
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        return None


def get_venue_weather(venue_name: str) -> Dict[str, Any]:
    """Get weather and travel risk for a specific venue."""
    coords = VENUE_COORDS.get(venue_name)
    if not coords:
        return {
            "venue": venue_name,
            "error": "Venue coordinates not found",
            "weather_risk_score": 0,
            "weather_risk_level": "UNKNOWN",
        }

    weather = get_weather(coords["lat"], coords["lon"])
    if not weather:
        return {
            "venue": venue_name,
            "error": "Weather data unavailable",
            "weather_risk_score": 0,
            "weather_risk_level": "UNKNOWN",
        }

    risk = _risk_from_weather(weather)

    return {
        "venue": venue_name,
        "weather": weather,
        **risk,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def get_all_venue_weather() -> list:
    """Get weather risk for all Olympic venues."""
    results = []
    for venue_name in VENUE_COORDS:
        result = get_venue_weather(venue_name)
        results.append(result)
    results.sort(key=lambda x: x.get("weather_risk_score", 0), reverse=True)
    return results