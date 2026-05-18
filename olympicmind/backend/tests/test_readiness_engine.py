import unittest

from readiness_engine import calculate_athlete_readiness_score, calculate_team_readiness


class ReadinessEngineTests(unittest.TestCase):
    def test_athlete_score_uses_latest_three_days(self):
        logs = [
            {"date": "2026-05-18", "rpe": 5, "fatigue": 5, "stress": 5, "sleep": 8, "logistics": 8, "environment": 8},
            {"date": "2026-05-17", "rpe": 5, "fatigue": 5, "stress": 5, "sleep": 8, "logistics": 8, "environment": 8},
            {"date": "2026-05-16", "rpe": 5, "fatigue": 5, "stress": 5, "sleep": 8, "logistics": 8, "environment": 8},
            {"date": "2026-05-15", "rpe": 10, "fatigue": 10, "stress": 10, "sleep": 1, "logistics": 1, "environment": 1},
        ]
        score = calculate_athlete_readiness_score(logs)
        self.assertEqual(score, 62.0)

    def test_team_score_is_average_of_member_scores(self):
        audit_logs = {
            "A1": [
                {"date": "2026-05-18", "rpe": 5, "fatigue": 5, "stress": 5, "sleep": 8, "logistics": 8, "environment": 8},
            ],
            "A2": [
                {"date": "2026-05-18", "rpe": 8, "fatigue": 8, "stress": 7, "sleep": 6, "logistics": 7, "environment": 7},
            ],
        }
        team_score, athlete_scores = calculate_team_readiness(["A1", "A2"], audit_logs)
        self.assertEqual(len(athlete_scores), 2)
        self.assertEqual(athlete_scores[0]["readiness_score"], 62.0)
        self.assertEqual(athlete_scores[1]["readiness_score"], 40.0)
        self.assertEqual(team_score, 51.0)

    def test_athlete_score_averages_varying_days(self):
        logs = [
            {"date": "2026-05-18", "rpe": 5, "fatigue": 5, "stress": 5, "sleep": 8, "logistics": 8, "environment": 8},
            {"date": "2026-05-17", "rpe": 8, "fatigue": 8, "stress": 7, "sleep": 6, "logistics": 7, "environment": 7},
            {"date": "2026-05-16", "rpe": 9, "fatigue": 9, "stress": 9, "sleep": 5, "logistics": 5, "environment": 5},
        ]
        score = calculate_athlete_readiness_score(logs)
        self.assertEqual(score, 42.67)
if __name__ == "__main__":
    unittest.main()
