from typing import Any, Dict, List, Optional

from tomtom_client import get_routes


def _find_venue(name: str, venues: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    lowered = name.lower().strip()
    for venue in venues:
        if venue.get("name", "").lower().strip() == lowered:
            return venue
    return None


def _extract_steps(route: Dict[str, Any]) -> List[str]:
    steps: List[str] = []
    guidance = route.get("guidance", {})
    for instruction in guidance.get("instructions", []):
        message = instruction.get("message")
        if message:
            steps.append(message)
        if len(steps) >= 6:
            break
    return steps


def _extract_problem_roads(route: Dict[str, Any]) -> List[str]:
    roads = []
    for section in route.get("sections", []):
        if section.get("sectionType") != "TRAFFIC":
            continue
        if section.get("simpleCategory") in {"JAMMED", "ROAD_CLOSED", "CLOSED", "STOP_AND_GO", "SLOW"}:
            section_name = section.get("name") or section.get("street")
            if section_name:
                roads.append(section_name)
    # Deduplicate while preserving order.
    return list(dict.fromkeys(roads))


def _route_status(route: Dict[str, Any]) -> str:
    summary = route.get("summary", {})
    travel_time = int(summary.get("travelTimeInSeconds", 1) or 1)
    delay = int(summary.get("trafficDelayInSeconds", 0) or 0)
    ratio = delay / travel_time

    for section in route.get("sections", []):
        if section.get("sectionType") == "TRAFFIC" and section.get("simpleCategory") in {"ROAD_CLOSED", "CLOSED"}:
            return "BLOCKED"

    if delay >= 600 or ratio >= 0.2:
        return "CONGESTED"
    return "CLEAR"


def _to_route_payload(index: int, route: Dict[str, Any]) -> Dict[str, Any]:
    summary = route.get("summary", {})
    status = _route_status(route)
    travel_min = round((summary.get("travelTimeInSeconds", 0) or 0) / 60)
    delay_min = round((summary.get("trafficDelayInSeconds", 0) or 0) / 60)

    return {
        "name": f"TomTom Route {index + 1}",
        "time": f"{travel_min} mins",
        "delay": f"+{delay_min} mins" if delay_min > 0 else "+0 mins",
        "distance_km": round((summary.get("lengthInMeters", 0) or 0) / 1000, 1),
        "status": status,
        "avoid": _extract_problem_roads(route),
        "steps": _extract_steps(route),
    }


def get_best_route(origin: str, destination: str, crowd_data: Dict[str, Any]) -> Dict[str, Any]:
    venues = crowd_data.get("venues", [])
    origin_venue = _find_venue(origin, venues)
    destination_venue = _find_venue(destination, venues)

    if not origin_venue or not destination_venue:
        return {
            "recommended": None,
            "reason": "Origin or destination not found in venue list.",
            "routes": {},
            "blocked_routes": [],
            "congested_routes": [],
        }

    try:
        raw_routes = get_routes(
            origin_venue["lat"],
            origin_venue["lng"],
            destination_venue["lat"],
            destination_venue["lng"],
        )
    except Exception as exc:
        return {
            "recommended": None,
            "reason": "TomTom routing unavailable. Please retry in a few moments.",
            "routes": {},
            "blocked_routes": [],
            "congested_routes": [],
        }

    routes: Dict[str, Dict[str, Any]] = {}
    blocked_routes: List[str] = []
    congested_routes: List[str] = []

    for idx, route in enumerate(raw_routes[:3]):
        key = f"route_{idx + 1}"
        payload = _to_route_payload(idx, route)
        routes[key] = payload
        if payload["status"] == "BLOCKED":
            blocked_routes.append(key)
        elif payload["status"] == "CONGESTED":
            congested_routes.append(key)

    recommended = None
    for key, route in routes.items():
        if route["status"] == "CLEAR":
            recommended = key
            break
    if not recommended and routes:
        recommended = min(
            routes.keys(),
            key=lambda k: int(routes[k]["delay"].replace("+", "").replace(" mins", "") or "0"),
        )

    if blocked_routes:
        reason = "Blocked segments detected on some routes. Suggested an alternative path."
    elif congested_routes:
        reason = "Heavy traffic detected. Suggested the least congested option."
    else:
        reason = "Traffic is stable. Suggested the fastest clear route."

    return {
        "recommended": recommended,
        "reason": reason,
        "routes": routes,
        "blocked_routes": blocked_routes,
        "congested_routes": congested_routes,
    }
