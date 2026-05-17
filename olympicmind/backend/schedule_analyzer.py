"""
Olympic Schedule Analyzer for OlympicMind
Provides event schedule awareness and proactive departure warnings.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# 2026 Milan Winter Olympics - Key Events Schedule
OLYMPIC_EVENTS = [
    # February 6-7 Opening
    {"sport": "Opening Ceremony", "venue": "San Siro Stadium", "date": "2026-02-06", "time": "20:00", "duration_mins": 180, "expected_crowd": 95},
    
    # Alpine Skiing - Cortina
    {"sport": "Alpine Skiing - Downhill Men", "venue": "Cortina Venue", "date": "2026-02-08", "time": "11:00", "duration_mins": 120, "expected_crowd": 85},
    {"sport": "Alpine Skiing - Downhill Women", "venue": "Cortina Venue", "date": "2026-02-09", "time": "11:00", "duration_mins": 120, "expected_crowd": 80},
    
    # Ice Hockey - Milan
    {"sport": "Ice Hockey Men - Group A", "venue": "Forum Assago", "date": "2026-02-10", "time": "15:00", "duration_mins": 150, "expected_crowd": 90},
    {"sport": "Ice Hockey Men - Group B", "venue": "Forum Assago", "date": "2026-02-11", "time": "19:00", "duration_mins": 150, "expected_crowd": 88},
    {"sport": "Ice Hockey Women - Final", "venue": "Forum Assago", "date": "2026-02-17", "time": "18:00", "duration_mins": 150, "expected_crowd": 92},
    {"sport": "Ice Hockey Men - Final", "venue": "Forum Assago", "date": "2026-02-22", "time": "20:00", "duration_mins": 150, "expected_crowd": 98},
    
    # Figure Skating - Milan
    {"sport": "Figure Skating - Short Program", "venue": "Palazzo del Ghiaccio", "date": "2026-02-12", "time": "14:00", "duration_mins": 180, "expected_crowd": 88},
    {"sport": "Figure Skating - Free Skate", "venue": "Palazzo del Ghiaccio", "date": "2026-02-14", "time": "16:00", "duration_mins": 180, "expected_crowd": 92},
    {"sport": "Figure Skating - Ice Dance", "venue": "Palazzo del Ghiaccio", "date": "2026-02-16", "time": "15:00", "duration_mins": 150, "expected_crowd": 85},
    
    # Speed Skating
    {"sport": "Speed Skating 500m", "venue": "Oval Lingotto", "date": "2026-02-13", "time": "10:00", "duration_mins": 120, "expected_crowd": 75},
    {"sport": "Speed Skating 1000m", "venue": "Oval Lingotto", "date": "2026-02-15", "time": "13:00", "duration_mins": 120, "expected_crowd": 78},
    
    # Biathlon
    {"sport": "Biathlon Sprint Men", "venue": "Anterselva Venue", "date": "2026-02-13", "time": "14:30", "duration_mins": 90, "expected_crowd": 70},
    {"sport": "Biathlon Sprint Women", "venue": "Anterselva Venue", "date": "2026-02-14", "time": "14:30", "duration_mins": 90, "expected_crowd": 72},
    
    # Ski Jumping
    {"sport": "Ski Jumping Men Normal Hill", "venue": "Predazzo Venue", "date": "2026-02-08", "time": "16:00", "duration_mins": 120, "expected_crowd": 80},
    {"sport": "Ski Jumping Men Large Hill", "venue": "Predazzo Venue", "date": "2026-02-15", "time": "16:00", "duration_mins": 120, "expected_crowd": 82},
    
    # Closing
    {"sport": "Closing Ceremony", "venue": "San Siro Stadium", "date": "2026-02-22", "time": "20:00", "duration_mins": 180, "expected_crowd": 96},
]


def _parse_event_times(event: Dict[str, Any]):
    """Parse event start and end datetime."""
    start_dt = datetime.strptime(f"{event['date']} {event['time']}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(minutes=event["duration_mins"])
    return start_dt, end_dt


def get_upcoming_events(hours_ahead: int = 3) -> List[Dict[str, Any]]:
    """
    Returns events happening in the next X hours.
    
    Args:
        hours_ahead: How many hours ahead to look (default 3)
    
    Returns:
        List of upcoming events with time details
    """
    now = datetime.now()
    cutoff = now + timedelta(hours=hours_ahead)
    upcoming = []

    for event in OLYMPIC_EVENTS:
        start_dt, end_dt = _parse_event_times(event)

        # Event starting soon or currently ongoing
        if now <= start_dt <= cutoff or (start_dt <= now <= end_dt):
            mins_until_start = int((start_dt - now).total_seconds() / 60)
            mins_until_end = int((end_dt - now).total_seconds() / 60)

            upcoming.append({
                **event,
                "starts_in_mins": max(0, mins_until_start),
                "ends_in_mins": max(0, mins_until_end),
                "status": "ONGOING" if start_dt <= now <= end_dt else "UPCOMING",
            })

    upcoming.sort(key=lambda x: x["starts_in_mins"])
    return upcoming


def get_departure_recommendation(venue_name: str) -> Dict[str, Any]:
    """
    Check if any event is ending soon at a venue and warn athletes to leave early.
    
    Args:
        venue_name: Name of the venue to check
    
    Returns:
        Dict with warning level and recommendation message
    """
    now = datetime.now()
    warnings = []

    for event in OLYMPIC_EVENTS:
        if venue_name.lower() not in event["venue"].lower():
            continue

        start_dt, end_dt = _parse_event_times(event)
        mins_until_end = int((end_dt - now).total_seconds() / 60)
        mins_until_start = int((start_dt - now).total_seconds() / 60)

        # Event ending in 30-60 mins — HIGH urgency
        if 0 < mins_until_end <= 30:
            warnings.append({
                "urgency": "CRITICAL",
                "event": event["sport"],
                "message": f"🚨 CRITICAL: '{event['sport']}' ends in {mins_until_end} mins! Roads will be severely congested. Leave IMMEDIATELY.",
                "expected_crowd_surge": event["expected_crowd"],
            })

        elif 30 < mins_until_end <= 60:
            warnings.append({
                "urgency": "HIGH",
                "event": event["sport"],
                "message": f"⚠️ HIGH ALERT: '{event['sport']}' ends in {mins_until_end} mins. Leave now to avoid post-event crowds.",
                "expected_crowd_surge": event["expected_crowd"],
            })

        # Event starting soon — people arriving
        elif 0 < mins_until_start <= 45:
            warnings.append({
                "urgency": "MEDIUM",
                "event": event["sport"],
                "message": f"⚡ HEADS UP: '{event['sport']}' starts in {mins_until_start} mins. Crowds arriving — expect delays near {event['venue']}.",
                "expected_crowd_surge": event["expected_crowd"],
            })

    if not warnings:
        return {
            "urgency": "LOW",
            "message": f"No major events ending soon near {venue_name}. Roads should be clear.",
            "warnings": [],
        }

    # Return highest urgency warning
    urgency_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    warnings.sort(key=lambda x: urgency_order.get(x["urgency"], 3))

    return {
        "urgency": warnings[0]["urgency"],
        "message": warnings[0]["message"],
        "warnings": warnings,
    }


def get_risk_score(venue_name: str, crowd_level: int) -> Dict[str, Any]:
    """
    Combines event schedule + live crowd level to return a 0-100 risk score.
    
    Args:
        venue_name: Name of venue
        crowd_level: Current crowd level 0-100 from TomTom traffic data
    
    Returns:
        Dict with risk_score (0-100) and recommendation string
    """
    departure_info = get_departure_recommendation(venue_name)
    urgency = departure_info.get("urgency", "LOW")

    # Event urgency weight
    urgency_weights = {"CRITICAL": 40, "HIGH": 25, "MEDIUM": 15, "LOW": 0}
    event_score = urgency_weights.get(urgency, 0)

    # Crowd level weight (60% of total score)
    crowd_score = int(crowd_level * 0.6)

    # Final risk score capped at 100
    risk_score = min(100, crowd_score + event_score)

    # Recommendation based on risk
    if risk_score >= 80:
        recommendation = "🚨 EXTREME RISK: Avoid this area entirely. Take completely alternate routes."
        level = "EXTREME"
    elif risk_score >= 60:
        recommendation = "⚠️ HIGH RISK: Significant delays expected. Leave 45+ mins early or use public transport."
        level = "HIGH"
    elif risk_score >= 40:
        recommendation = "⚡ MODERATE RISK: Some delays possible. Allow extra 20-30 mins travel time."
        level = "MODERATE"
    elif risk_score >= 20:
        recommendation = "✅ LOW RISK: Light congestion. Normal travel times with minor delays."
        level = "LOW"
    else:
        recommendation = "✅ CLEAR: Roads are clear. Good time to travel."
        level = "CLEAR"

    return {
        "venue": venue_name,
        "risk_score": risk_score,
        "risk_level": level,
        "crowd_contribution": crowd_score,
        "event_contribution": event_score,
        "recommendation": recommendation,
        "departure_warning": departure_info.get("message", ""),
    }


def get_all_venue_risks(crowd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get risk scores for all venues using live crowd data.
    
    Args:
        crowd_data: Live crowd data dict from crowd_monitor
    
    Returns:
        List of risk assessments for all venues, sorted by risk score
    """
    results = []
    for venue in crowd_data.get("venues", []):
        risk = get_risk_score(venue["name"], venue.get("crowd_level", 0))
        results.append(risk)

    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results