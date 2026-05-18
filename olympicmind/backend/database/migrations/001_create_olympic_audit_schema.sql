CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    country TEXT NOT NULL,
    sport_category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS athletes (
    id INTEGER PRIMARY KEY,
    team_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sport TEXT NOT NULL,
    discipline TEXT NOT NULL,
    weight REAL NOT NULL CHECK (weight > 0),
    height REAL NOT NULL CHECK (height > 0),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY,
    athlete_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    sleep_hours REAL NOT NULL CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    rpe_score INTEGER NOT NULL CHECK (rpe_score BETWEEN 1 AND 10),
    stress_level INTEGER NOT NULL CHECK (stress_level BETWEEN 1 AND 10),
    fatigue_score INTEGER NOT NULL CHECK (fatigue_score BETWEEN 1 AND 10),
    nutrition_compliant INTEGER NOT NULL CHECK (nutrition_compliant IN (0, 1)),
    jetlag_status TEXT NOT NULL,
    FOREIGN KEY (athlete_id) REFERENCES athletes(id) ON DELETE CASCADE,
    UNIQUE (athlete_id, date)
);

CREATE INDEX IF NOT EXISTS idx_athletes_team_id ON athletes(team_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_athlete_id ON audit_logs(athlete_id);
