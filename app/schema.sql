CREATE TABLE IF NOT EXISTS competitions (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    venue       TEXT,
    date        TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'draft',
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id              INTEGER PRIMARY KEY,
    competition_id  INTEGER NOT NULL REFERENCES competitions(id),
    name            TEXT    NOT NULL,
    unit            TEXT    NOT NULL,
    category        TEXT
);

CREATE TABLE IF NOT EXISTS athletes (
    id                               INTEGER PRIMARY KEY,
    first_name                       TEXT NOT NULL,
    last_name                        TEXT NOT NULL,
    birth_date                       TEXT NOT NULL,
    sex                              TEXT NOT NULL,
    club                             TEXT,
    license_number                   TEXT NOT NULL UNIQUE,
    medical_certificate_valid_until  TEXT
);

CREATE TABLE IF NOT EXISTS registrations (
    id          INTEGER PRIMARY KEY,
    event_id    INTEGER NOT NULL REFERENCES events(id),
    athlete_id  INTEGER NOT NULL REFERENCES athletes(id),
    bib         INTEGER NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'pending',
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    registration_id  INTEGER PRIMARY KEY REFERENCES registrations(id),
    performance      REAL NOT NULL,
    recorded_at      TEXT NOT NULL
);

CREATE VIEW IF NOT EXISTS v_public_athletes AS
  SELECT id, first_name, last_name, club,
         CAST(strftime('%Y', birth_date) AS INTEGER) AS birth_year
  FROM athletes;

CREATE VIEW IF NOT EXISTS v_public_results AS
  SELECT c.name AS competition, c.date AS competition_date, e.name AS event, e.unit,
         r.bib, a.last_name, a.first_name, a.club, res.performance
  FROM results res
  JOIN registrations r ON r.id = res.registration_id
  JOIN events e        ON e.id = r.event_id
  JOIN competitions c  ON c.id = e.competition_id
  JOIN athletes a      ON a.id = r.athlete_id
  WHERE r.status = 'confirmed';
