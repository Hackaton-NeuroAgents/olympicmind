import json
import os
import logging

from tomtom_client import get_flow_segment

logger = logging.getLogger(__name__)

def get_crowd_data():
    file_path = os.path.join(os.path.dirname(__file__), "data", "crowd_data.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def simulate_crowd_change():
    # Uses live road traffic around each venue to infer pressure levels.
    data = get_crowd_data()

    for venue in data["venues"]:
        try:
            segment = get_flow_segment(venue["lat"], venue["lng"])
            free_flow_speed = float(segment.get("freeFlowSpeed", 0) or 0)
            current_speed = float(segment.get("currentSpeed", 0) or 0)
            road_closure = bool(segment.get("roadClosure", False))

            if road_closure:
                crowd_level = 100
            elif free_flow_speed > 0:
                congestion_pct = max(0.0, min(100.0, (1 - (current_speed / free_flow_speed)) * 100))
                crowd_level = int(round(congestion_pct))
            else:
                crowd_level = int(venue.get("crowd_level", 0))

            venue["crowd_level"] = crowd_level
            venue["traffic"] = {
                "current_speed_kmh": current_speed,
                "free_flow_speed_kmh": free_flow_speed,
                "current_travel_time_sec": segment.get("currentTravelTime"),
                "free_flow_travel_time_sec": segment.get("freeFlowTravelTime"),
                "road_closure": road_closure,
                "confidence": segment.get("confidence", 0),
            }
        except Exception:
            # Keep last known values if the traffic API is temporarily unavailable.
            logger.exception("Failed to refresh traffic for venue %s", venue.get("name", "unknown"))
            venue.setdefault("traffic", {})

        venue["current"] = int((venue.get("capacity", 0) * venue["crowd_level"]) / 100)

        if venue["crowd_level"] > 75:
            venue["status"] = "HIGH"
        elif venue["crowd_level"] > 45:
            venue["status"] = "MEDIUM"
        else:
            venue["status"] = "LOW"

    return data

def check_for_incidents(crowd_data):
    incidents = []
    for venue in crowd_data["venues"]:
        traffic = venue.get("traffic", {})
        if traffic.get("road_closure"):
            incidents.append({
                "venue": venue["name"],
                "level": venue["crowd_level"],
                "message": f"ALERT: Road closure near {venue['name']}.",
                "type": "BLOCKED",
            })
            continue

        if venue["crowd_level"] > 75:
            incidents.append({
                "venue": venue["name"],
                "level": venue["crowd_level"],
                "message": f"ALERT: Heavy congestion near {venue['name']}.",
                "type": "CONGESTED",
            })
    return incidents
