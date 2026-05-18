import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

READINESS_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "readiness_audit_logs.json")

DEFAULT_READINESS_DATA = {
    "teams": [
        {"id": "TEAM-001", "name": "OlympicMind Demo Team", "members": ["ATH001", "ATH002", "ATH003"]}
    ],
    "audit_logs": {
        "ATH001": [
            {"date": "2026-05-18", "rpe": 6, "fatigue": 5, "stress": 4, "sleep": 8, "logistics": 9, "environment": 8},
            {"date": "2026-05-17", "rpe": 7, "fatigue": 6, "stress": 5, "sleep": 7, "logistics": 8, "environment": 8},
            {"date": "2026-05-16", "rpe": 5, "fatigue": 5, "stress": 3, "sleep": 8, "logistics": 9, "environment": 9},
        ],
        "ATH002": [
            {"date": "2026-05-18", "rpe": 8, "fatigue": 7, "stress": 6, "sleep": 6, "logistics": 7, "environment": 7},
            {"date": "2026-05-17", "rpe": 7, "fatigue": 7, "stress": 6, "sleep": 7, "logistics": 8, "environment": 7},
            {"date": "2026-05-16", "rpe": 8, "fatigue": 6, "stress": 5, "sleep": 7, "logistics": 8, "environment": 8},
        ],
        "ATH003": [
            {"date": "2026-05-18", "rpe": 5, "fatigue": 4, "stress": 4, "sleep": 9, "logistics": 9, "environment": 9},
            {"date": "2026-05-17", "rpe": 6, "fatigue": 5, "stress": 5, "sleep": 8, "logistics": 9, "environment": 8},
            {"date": "2026-05-16", "rpe": 5, "fatigue": 4, "stress": 3, "sleep": 9, "logistics": 9, "environment": 9},
        ],
    },
}


def load_readiness_data() -> Dict[str, Any]:
    if not os.path.exists(READINESS_DATA_FILE):
        return DEFAULT_READINESS_DATA

    try:
        with open(READINESS_DATA_FILE, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_READINESS_DATA


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def _normalize_0_to_100(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if 0 <= numeric <= 10:
        numeric = numeric * 10
    return max(0.0, min(100.0, numeric))


def _inverse_score(value: Any) -> float:
    return 100.0 - _normalize_0_to_100(value)


def _category_score(log: Dict[str, Any]) -> float:
    physical = (_inverse_score(log.get("rpe")) + _inverse_score(log.get("fatigue"))) / 2
    mental = (_inverse_score(log.get("stress")) + _normalize_0_to_100(log.get("sleep"))) / 2
    contextual = (_normalize_0_to_100(log.get("logistics")) + _normalize_0_to_100(log.get("environment"))) / 2
    return (physical * 0.4) + (mental * 0.4) + (contextual * 0.2)


def calculate_athlete_readiness_score(audit_logs: List[Dict[str, Any]]) -> float:
    if not audit_logs:
        return 0.0

    valid_logs = [log for log in audit_logs if isinstance(log, dict) and log.get("date")]
    if not valid_logs:
        return 0.0

    valid_logs.sort(key=lambda log: _parse_date(log["date"]), reverse=True)
    recent_logs = valid_logs[:3]
    average = sum(_category_score(log) for log in recent_logs) / len(recent_logs)
    return round(average, 2)


def calculate_team_readiness(team_members: List[str], audit_logs_by_athlete: Dict[str, List[Dict[str, Any]]]) -> Tuple[float, List[Dict[str, Any]]]:
    athlete_scores: List[Dict[str, Any]] = []
    for athlete_id in team_members:
        score = calculate_athlete_readiness_score(audit_logs_by_athlete.get(athlete_id, []))
        athlete_scores.append({"athlete_id": athlete_id, "readiness_score": score})

    if not athlete_scores:
        return 0.0, []

    team_score = round(sum(athlete["readiness_score"] for athlete in athlete_scores) / len(athlete_scores), 2)
    return team_score, athlete_scores


def get_team_readiness(team_id: str) -> Optional[Dict[str, Any]]:
    readiness_data = load_readiness_data()
    teams = readiness_data.get("teams", [])
    team = next((candidate for candidate in teams if candidate.get("id") == team_id), None)
    if not team:
        return None

    team_members = team.get("members", [])
    team_score, athlete_scores = calculate_team_readiness(team_members, readiness_data.get("audit_logs", {}))
    return {
        "team_id": team_id,
        "team_name": team.get("name", ""),
        "readiness_score": team_score,
        "athletes": athlete_scores,
        "member_count": len(team_members),
    }
