"""
Athlete Profile System for OlympicMind
Tracks athlete schedules and gives personalized departure recommendations.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ATHLETES_FILE = os.path.join(DATA_DIR, "athletes.json")
AUDIT_LOGS_FILE = os.path.join(DATA_DIR, "audit_logs.json")

# Default athletes for demo
DEFAULT_ATHLETES = [
    {
        "id": "ATH001",
        "name": "Sofia Belmonte",
        "country": "ITA",
        "sport": "Alpine Skiing",
        "phone": "",
        "events": [
            {"venue": "Tofane Skiing Centre", "date": "2026-02-08", "time": "11:00", "role": "competitor"},
            {"venue": "Tofane Skiing Centre", "date": "2026-02-10", "time": "14:00", "role": "competitor"},
        ],
        "hotel": "Hotel Cristallo Cortina",
        "hotel_coords": {"lat": 46.5400, "lon": 12.1390},
    },
    {
        "id": "ATH002",
        "name": "Marco Rossi",
        "country": "ITA",
        "sport": "Ice Hockey",
        "phone": "",
        "events": [
            {"venue": "Rho Ice Hockey Arena", "date": "2026-02-10", "time": "15:00", "role": "competitor"},
            {"venue": "Rho Ice Hockey Arena", "date": "2026-02-11", "time": "19:00", "role": "competitor"},
            {"venue": "Rho Ice Hockey Arena", "date": "2026-02-22", "time": "20:00", "role": "competitor"},
        ],
        "hotel": "Hotel Sheraton Milan",
        "hotel_coords": {"lat": 45.4654, "lon": 9.1859},
    },
    {
        "id": "ATH003",
        "name": "Elena Voronova",
        "country": "RUS",
        "sport": "Figure Skating",
        "phone": "",
        "events": [
            {"venue": "Palazzo del Ghiaccio", "date": "2026-02-12", "time": "14:00", "role": "competitor"},
            {"venue": "Palazzo del Ghiaccio", "date": "2026-02-14", "time": "16:00", "role": "competitor"},
        ],
        "hotel": "Hotel Principe di Savoia",
        "hotel_coords": {"lat": 45.4761, "lon": 9.1974},
    },
]


def _load_athletes() -> List[Dict[str, Any]]:
    """Load athletes from JSON file or return defaults."""
    try:
        if os.path.exists(ATHLETES_FILE):
            with open(ATHLETES_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load athletes file: {e}")
    return DEFAULT_ATHLETES


def _save_athletes(athletes: List[Dict[str, Any]]):
    """Save athletes to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ATHLETES_FILE, "w") as f:
        json.dump(athletes, f, indent=2)


def _load_audit_logs() -> List[Dict[str, Any]]:
    """Load audit logs from JSON file."""
    try:
        if os.path.exists(AUDIT_LOGS_FILE):
            with open(AUDIT_LOGS_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load audit logs file: {e}")
    return []


def _save_audit_logs(audit_logs: List[Dict[str, Any]]):
    """Save audit logs to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(AUDIT_LOGS_FILE, "w") as f:
        json.dump(audit_logs, f, indent=2)


def get_all_athletes() -> List[Dict[str, Any]]:
    """Get all registered athletes."""
    return _load_athletes()


def get_athlete(athlete_id: str) -> Optional[Dict[str, Any]]:
    """Get athlete by ID."""
    athletes = _load_athletes()
    return next((a for a in athletes if a["id"] == athlete_id), None)


def add_athlete(athlete: Dict[str, Any]) -> Dict[str, Any]:
    """Add new athlete to system."""
    athletes = _load_athletes()
    # Check if ID already exists
    if any(a["id"] == athlete["id"] for a in athletes):
        raise ValueError(f"Athlete ID {athlete['id']} already exists")
    athletes.append(athlete)
    _save_athletes(athletes)
    return athlete


def get_athlete_next_event(athlete_id: str) -> Optional[Dict[str, Any]]:
    """Get the next upcoming event for an athlete."""
    athlete = get_athlete(athlete_id)
    if not athlete:
        return None

    now = datetime.now()
    upcoming = []

    for event in athlete.get("events", []):
        event_dt = datetime.strptime(f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M")
        if event_dt > now:
            mins_until = int((event_dt - now).total_seconds() / 60)
            upcoming.append({**event, "mins_until": mins_until, "event_dt": event_dt})

    if not upcoming:
        return None

    upcoming.sort(key=lambda x: x["mins_until"])
    return upcoming[0]


def get_departure_advice(athlete_id: str) -> Dict[str, Any]:
    """
    Give personalized departure advice for an athlete's next event.
    Considers: time until event, venue risk, weather conditions.
    """
    athlete = get_athlete(athlete_id)
    if not athlete:
        return {"error": f"Athlete {athlete_id} not found"}

    next_event = get_athlete_next_event(athlete_id)
    if not next_event:
        return {
            "athlete": athlete["name"],
            "message": "No upcoming events scheduled.",
            "urgency": "NONE",
        }

    mins_until = next_event["mins_until"]
    venue = next_event["venue"]
    hours_until = mins_until / 60

    # Recommended buffer time (travel + warm up + security)
    buffer_mins = 90

    # Departure urgency
    if mins_until <= buffer_mins:
        urgency = "CRITICAL"
        message = f"🚨 LEAVE NOW! '{next_event['sport'] if 'sport' in next_event else venue}' starts in {mins_until} mins. You needed to leave {buffer_mins - mins_until} mins ago!"
    elif mins_until <= buffer_mins + 30:
        urgency = "HIGH"
        message = f"⚠️ Leave in the next 15-30 mins for {venue}. Event starts in {mins_until} mins — allow {buffer_mins} mins for travel + check-in."
    elif mins_until <= buffer_mins + 90:
        urgency = "MEDIUM"
        depart_in = mins_until - buffer_mins
        message = f"⚡ Plan to leave in {depart_in} mins for {venue}. Event starts in {mins_until} mins."
    else:
        depart_in = mins_until - buffer_mins
        message = f"✅ You have time. Leave in ~{depart_in} mins for {venue}. Event starts in {int(hours_until)}h {mins_until % 60}m."
        urgency = "LOW"

    return {
        "athlete_id": athlete_id,
        "athlete": athlete["name"],
        "country": athlete["country"],
        "sport": athlete["sport"],
        "next_event": {
            "venue": venue,
            "date": next_event["date"],
            "time": next_event["time"],
            "mins_until": mins_until,
        },
        "urgency": urgency,
        "message": message,
        "recommended_departure_in_mins": max(0, mins_until - buffer_mins),
        "hotel": athlete.get("hotel", "Unknown"),
    }


def get_all_departure_alerts() -> List[Dict[str, Any]]:
    """Get departure alerts for ALL athletes with upcoming events."""
    athletes = _load_athletes()
    alerts = []

    for athlete in athletes:
        advice = get_departure_advice(athlete["id"])
        if advice.get("urgency") in ("CRITICAL", "HIGH", "MEDIUM"):
            alerts.append(advice)

    urgency_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    alerts.sort(key=lambda x: urgency_order.get(x.get("urgency", "LOW"), 3))
    return alerts


def add_audit_log(audit: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and persist a daily athlete audit log."""
    athlete_id = str(audit.get("athlete_id", "")).strip()
    date = str(audit.get("date", "")).strip()
    scores = audit.get("scores")
    notes = audit.get("notes", "")

    if not athlete_id:
        raise ValueError("athlete_id is required")
    if not get_athlete(athlete_id):
        raise LookupError(f"Athlete {athlete_id} not found")

    if not date:
        raise ValueError("date is required")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("date must be in YYYY-MM-DD format")

    if not isinstance(scores, dict) or not scores:
        raise ValueError("scores must be a non-empty object")

    normalized_scores: Dict[str, int] = {}
    for metric, score in scores.items():
        metric_name = str(metric).strip()
        if not metric_name:
            raise ValueError("score metric names must be non-empty")
        if not isinstance(score, int) or isinstance(score, bool):
            raise ValueError(f"score '{metric_name}' must be an integer between 1 and 10")
        if score < 1 or score > 10:
            raise ValueError(f"score '{metric_name}' must be between 1 and 10")
        normalized_scores[metric_name] = score

    if notes is None:
        notes = ""
    if not isinstance(notes, str):
        raise ValueError("notes must be a string")

    audit_log = {
        "athlete_id": athlete_id,
        "date": date,
        "scores": normalized_scores,
        "notes": notes,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    audit_logs = _load_audit_logs()
    audit_logs.append(audit_log)
    _save_audit_logs(audit_logs)
    return audit_log


def get_athlete_audit_history(athlete_id: str) -> List[Dict[str, Any]]:
    """Return all audit logs for an athlete sorted by most recent first."""
    if not get_athlete(athlete_id):
        raise LookupError(f"Athlete {athlete_id} not found")

    audit_logs = _load_audit_logs()
    history = [log for log in audit_logs if log.get("athlete_id") == athlete_id]
    history.sort(
        key=lambda log: (str(log.get("date", "")), str(log.get("created_at", ""))),
        reverse=True,
    )
    return history
