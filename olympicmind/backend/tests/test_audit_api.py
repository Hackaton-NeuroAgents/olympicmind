import json
import os
import tempfile
import unittest

from fastapi.testclient import TestClient

import athlete_profiles
from main import app


class AuditApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        athlete_profiles.DATA_DIR = cls.temp_dir.name
        athlete_profiles.ATHLETES_FILE = os.path.join(cls.temp_dir.name, "athletes.json")
        athlete_profiles.AUDIT_LOGS_FILE = os.path.join(cls.temp_dir.name, "audit_logs.json")
        with open(athlete_profiles.ATHLETES_FILE, "w") as f:
            json.dump(
                [
                    {
                        "id": "ATH001",
                        "name": "Sofia Belmonte",
                        "country": "ITA",
                        "sport": "Alpine Skiing",
                        "events": [],
                    }
                ],
                f,
            )
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def setUp(self):
        with open(athlete_profiles.AUDIT_LOGS_FILE, "w") as f:
            json.dump([], f)

    def test_post_audit_and_get_history_sorted_desc(self):
        older = self.client.post(
            "/api/v1/audit",
            json={
                "athlete_id": "ATH001",
                "date": "2026-02-01",
                "scores": {"sleep": 7, "recovery": 8},
                "notes": "Good day",
            },
        )
        self.assertEqual(older.status_code, 200)

        newer = self.client.post(
            "/api/v1/audit",
            json={
                "athlete_id": "ATH001",
                "date": "2026-02-03",
                "scores": {"sleep": 9, "recovery": 9},
            },
        )
        self.assertEqual(newer.status_code, 200)

        history = self.client.get("/api/v1/athletes/ATH001/history")
        self.assertEqual(history.status_code, 200)
        body = history.json()
        self.assertEqual(body["count"], 2)
        self.assertEqual(body["history"][0]["date"], "2026-02-03")
        self.assertEqual(body["history"][1]["date"], "2026-02-01")

    def test_post_audit_with_invalid_score_returns_400(self):
        response = self.client.post(
            "/api/v1/audit",
            json={
                "athlete_id": "ATH001",
                "date": "2026-02-01",
                "scores": {"sleep": 11},
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("between 1 and 10", response.json()["detail"])

    def test_post_audit_for_missing_athlete_returns_404(self):
        response = self.client.post(
            "/api/v1/audit",
            json={
                "athlete_id": "ATH999",
                "date": "2026-02-01",
                "scores": {"sleep": 8},
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"])

    def test_get_history_for_missing_athlete_returns_404(self):
        response = self.client.get("/api/v1/athletes/ATH999/history")
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
