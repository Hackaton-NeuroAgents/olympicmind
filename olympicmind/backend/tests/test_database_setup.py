import sqlite3
import tempfile
import unittest
from pathlib import Path

from database.migrate import run_migrations
from database.seed import seed_database


class DatabaseSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_olympic_audit.db"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_migrations_create_expected_schema_and_relationships(self) -> None:
        applied = run_migrations(self.db_path)
        self.assertIn("001_create_olympic_audit_schema.sql", applied)

        with sqlite3.connect(self.db_path) as conn:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            self.assertTrue(
                {"teams", "athletes", "audit_logs", "schema_migrations"}.issubset(tables)
            )

            athlete_fks = conn.execute("PRAGMA foreign_key_list(athletes)").fetchall()
            self.assertTrue(any(fk[2] == "teams" for fk in athlete_fks))

            log_fks = conn.execute("PRAGMA foreign_key_list(audit_logs)").fetchall()
            self.assertTrue(any(fk[2] == "athletes" for fk in log_fks))

    def test_seed_inserts_required_dummy_data_volume(self) -> None:
        seed_database(self.db_path)

        with sqlite3.connect(self.db_path) as conn:
            team_count = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
            athlete_count = conn.execute("SELECT COUNT(*) FROM athletes").fetchone()[0]
            log_count = conn.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
            min_logs_per_athlete = conn.execute(
                "SELECT MIN(log_count) FROM (SELECT COUNT(*) AS log_count FROM audit_logs GROUP BY athlete_id)"
            ).fetchone()[0]

        self.assertEqual(team_count, 2)
        self.assertEqual(athlete_count, 10)
        self.assertEqual(log_count, 70)
        self.assertEqual(min_logs_per_athlete, 7)


if __name__ == "__main__":
    unittest.main()
