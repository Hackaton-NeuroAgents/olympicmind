import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "")
BASE_TRAFFIC_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json"
BASE_ROUTING_URL = "https://api.tomtom.com/routing/1/calculateRoute"


def _api_key_or_raise() -> str:
    if not TOMTOM_API_KEY:
        raise RuntimeError("TOMTOM_API_KEY is not configured")
    return TOMTOM_API_KEY


def get_flow_segment(lat: float, lng: float) -> Dict[str, Any]:
    api_key = _api_key_or_raise()
    response = requests.get(
        BASE_TRAFFIC_URL,
        params={"point": f"{lat},{lng}", "key": api_key},
        timeout=8,
    )
    response.raise_for_status()
    return response.json().get("flowSegmentData", {})


def get_routes(origin_lat: float, origin_lng: float, destination_lat: float, destination_lng: float) -> List[Dict[str, Any]]:
    api_key = _api_key_or_raise()
    route_path = f"{origin_lat},{origin_lng}:{destination_lat},{destination_lng}/json"
    response = requests.get(
        f"{BASE_ROUTING_URL}/{route_path}",
        params={
            "key": api_key,
            "traffic": "true",
            "travelMode": "car",
            "routeType": "fastest",
            "maxAlternatives": 2,
            "alternativeType": "anyRoute",
            "instructionsType": "text",
            "language": "en-US",
        },
        timeout=12,
    )
    response.raise_for_status()
    return response.json().get("routes", [])
