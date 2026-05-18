import argparse
import sqlite3
from datetime import date, timedelta
from pathlib import Path

try:
    from .migrate import DEFAULT_DB_PATH, run_migrations
except ImportError:
    from migrate import DEFAULT_DB_PATH, run_migrations

TEAMS = [
    {"id": 1, "country": "Italy", "sport_category": "Winter Sports"},
    {"id": 2, "country": "Canada", "sport_category": "Ice Sports"},
]

ATHLETES = [
    {"id": 1, "team_id": 1, "name": "Luca Bianchi", "sport": "Skiing", "discipline": "Downhill", "weight": 82.4, "height": 1.84},
    {"id": 2, "team_id": 1, "name": "Sofia Romano", "sport": "Skiing", "discipline": "Slalom", "weight": 64.8, "height": 1.70},
    {"id": 3, "team_id": 1, "name": "Marco Gentile", "sport": "Biathlon", "discipline": "Sprint", "weight": 75.3, "height": 1.79},
    {"id": 4, "team_id": 1, "name": "Giulia Ferri", "sport": "Snowboarding", "discipline": "Halfpipe", "weight": 59.1, "height": 1.66},
    {"id": 5, "team_id": 1, "name": "Elena Costa", "sport": "Speed Skating", "discipline": "1500m", "weight": 61.5, "height": 1.68},
    {"id": 6, "team_id": 2, "name": "Noah Carter", "sport": "Ice Hockey", "discipline": "Forward", "weight": 87.2, "height": 1.88},
    {"id": 7, "team_id": 2, "name": "Emma Brooks", "sport": "Figure Skating", "discipline": "Singles", "weight": 55.2, "height": 1.63},
    {"id": 8, "team_id": 2, "name": "Liam Turner", "sport": "Curling", "discipline": "Lead", "weight": 79.6, "height": 1.82},
    {"id": 9, "team_id": 2, "name": "Olivia Price", "sport": "Short Track", "discipline": "1000m", "weight": 58.7, "height": 1.65},
    {"id": 10, "team_id": 2, "name": "Ava Hudson", "sport": "Luge", "discipline": "Singles", "weight": 62.3, "height": 1.69},
]

JETLAG_STATES = ["none", "mild", "moderate"]


def _build_audit_logs() -> list[dict]:
    start_date = date(2025, 1, 1)
    logs: list[dict] = []
    log_id = 1
    for athlete in ATHLETES:
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            logs.append(
                {
                    "id": log_id,
                    "athlete_id": athlete["id"],
                    "date": current_date.isoformat(),
                    "sleep_hours": round(6.5 + ((athlete["id"] + day_offset) % 4) * 0.5, 1),
                    "rpe_score": ((athlete["id"] + day_offset) % 10) + 1,
                    "stress_level": ((athlete["id"] + day_offset * 2) % 10) + 1,
                    "fatigue_score": ((athlete["id"] * 2 + day_offset) % 10) + 1,
                    "nutrition_compliant": 1 if (athlete["id"] + day_offset) % 3 != 0 else 0,
                    "jetlag_status": JETLAG_STATES[(athlete["id"] + day_offset) % len(JETLAG_STATES)],
                }
            )
            log_id += 1
    return logs


def seed_database(db_path: Path = DEFAULT_DB_PATH) -> None:
    run_migrations(db_path)
    logs = _build_audit_logs()

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executemany(
            """
            INSERT OR IGNORE INTO teams(id, country, sport_category)
            VALUES (:id, :country, :sport_category)
            """,
            TEAMS,
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO athletes(id, team_id, name, sport, discipline, weight, height)
            VALUES (:id, :team_id, :name, :sport, :discipline, :weight, :height)
            """,
            ATHLETES,
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO audit_logs(
                id, athlete_id, date, sleep_hours, rpe_score, stress_level,
                fatigue_score, nutrition_compliant, jetlag_status
            )
            VALUES (
                :id, :athlete_id, :date, :sleep_hours, :rpe_score, :stress_level,
                :fatigue_score, :nutrition_compliant, :jetlag_status
            )
            """,
            logs,
        )
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Olympic audit database.")
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help="SQLite database file path.",
    )
    args = parser.parse_args()
    db_path = Path(args.db)

    seed_database(db_path)
    print(f"Seed complete for database: {db_path}")


if __name__ == "__main__":
    main()
