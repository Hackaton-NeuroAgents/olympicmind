import argparse
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "migrations"
DEFAULT_DB_PATH = BASE_DIR.parent / "data" / "olympic_audit.db"


def run_migrations(db_path: Path = DEFAULT_DB_PATH) -> list[str]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        applied = {
            row[0]
            for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
        }
        applied_now: list[str] = []

        for migration_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = migration_file.name
            if version in applied:
                continue

            conn.executescript(migration_file.read_text(encoding="utf-8"))
            conn.execute(
                "INSERT INTO schema_migrations(version) VALUES (?)",
                (version,),
            )
            applied_now.append(version)

        conn.commit()
    return applied_now


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply Olympic audit DB migrations.")
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help="SQLite database file path.",
    )
    args = parser.parse_args()
    db_path = Path(args.db)

    applied_now = run_migrations(db_path)
    if applied_now:
        print(f"Applied {len(applied_now)} migration(s): {', '.join(applied_now)}")
    else:
        print("No new migrations to apply.")


if __name__ == "__main__":
    main()
