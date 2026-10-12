"""Peuple data/dossard.db avec des données 100 % synthétiques, à graine fixe.

    python scripts/seed.py              # refuse si la base contient déjà des données
    python scripts/seed.py --reset      # supprime la base, recrée le schéma, peuple
    python scripts/seed.py --year 2026  # saison de référence (défaut : année courante)

Toutes les dates sont relatives à --year : avec la même année, la base est identique.
"""

from __future__ import annotations

import argparse
import random
import sqlite3
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from app.categories import age_category
from app.db import connect, get_db_path, init_db

FIRST_NAMES = {
    "F": "Camille Inès Léa Manon Chloé Jade Louise Zoé Clara Lina Emma Nora Alice Rose Maëlys"
    " Sarah Lou Anaïs Agathe Salomé".split(),
    "M": "Hugo Lucas Nathan Théo Louis Adam Noah Jules Malo Sacha Gabriel Arthur Ethan Tom Yanis"
    " Paul Robin Axel Elias Victor".split(),
}
LAST_NAMES = (
    "Martin Bernard Morel Roux Fournier Girard Bonnet Dupuis Lambert Fontaine Rousseau Vincent"
    " Muller Lefort Faure Andrieu Mercier Blanchard Guerin Boyer Garnier Chevalier Perrin Morin"
    " Lemaire Renaud Barbier Arnaud Picard Gauthier Roche Marchal Colin Brunet Leclerc Aubert"
    " Masson Perrot Huet Carpentier".split()
)
CLUBS = [
    "AC Rivebelle",
    "Stade Nordval",
    "Entente Val-de-Brume, section piste",
    "US Montclair-sur-Aube",
    "Athlé Pays de Corbières-Hautes",
    "CA Lisière",
    "Olympique Ferrandeau",
    "Racing Club des Trois Lacs",
    "AS Port-Sablon",
    "Union Athlétique de Brévannes",
    "Jeunesse Sportive Granval",
    "Foulées de Saint-Aurèle",
]


@dataclass
class EventSpec:
    name: str
    unit: str
    category: str | None
    low: float
    high: float
    tie: bool = False


@dataclass
class CompetitionSpec:
    name: str
    venue: str
    day: date
    status: str
    events: list[EventSpec]


def competitions_for(year: int) -> list[CompetitionSpec]:
    """Cinq compétitions : chaque statut, plus une compétition ouverte sur la saison suivante."""
    return [
        CompetitionSpec(
            "Meeting d'automne",
            "Stade des Peupliers, Rivebelle",
            date(year - 1, 10, 11),
            "finished",
            [
                EventSpec("100 m", "time_s", None, 10.6, 14.8, tie=True),
                EventSpec("Saut en longueur", "distance_m", None, 4.2, 7.6, tie=True),
                EventSpec("800 m", "time_s", "SENIOR", 112, 165),
                EventSpec("Lancer du poids", "distance_m", None, 7.5, 18.5),
            ],
        ),
        CompetitionSpec(
            "Championnat départemental",
            "Stade municipal de Nordval",
            date(year, 6, 14),
            "closed",
            [
                EventSpec("200 m", "time_s", None, 21.8, 30.5, tie=True),
                EventSpec("Saut en hauteur", "distance_m", None, 1.20, 2.15, tie=True),
                EventSpec("1 500 m", "time_s", "U18", 245, 340),
                EventSpec("Triathlon", "points", "U16", 600, 2400),
            ],
        ),
        CompetitionSpec(
            "Meeting des Trois Lacs",
            "Complexe sportif des Trois Lacs",
            date(year, 11, 22),
            "open",
            [
                EventSpec("60 m", "time_s", None, 6.8, 9.2),
                EventSpec("Saut en longueur", "distance_m", None, 4.2, 7.6),
                EventSpec("400 m", "time_s", "MASTER", 55, 85),
                EventSpec("Lancer du disque", "distance_m", None, 20, 55),
            ],
        ),
        CompetitionSpec(
            "Meeting en salle de janvier",
            "Halle Jean-Fernier, Port-Sablon",
            date(year + 1, 1, 24),
            "open",
            [
                EventSpec("60 m", "time_s", "U20", 6.8, 8.6),
                EventSpec("60 m haies", "time_s", None, 7.9, 10.5),
                EventSpec("Saut à la perche", "distance_m", None, 2.5, 5.4),
                EventSpec("Triple saut", "distance_m", None, 10.5, 15.8),
            ],
        ),
        CompetitionSpec(
            "Rencontre de printemps",
            "Stade de Granval",
            date(year + 1, 4, 18),
            "draft",
            [
                EventSpec("100 m", "time_s", None, 10.6, 14.8),
                EventSpec("400 m", "time_s", None, 47, 70),
                EventSpec("Lancer du javelot", "distance_m", None, 25, 70),
                EventSpec("Pentathlon", "points", None, 1800, 4200),
            ],
        ),
    ]


def make_athletes(rng: random.Random, year: int) -> list[dict]:
    """300 athlètes : 10 nés en year - 17 (U18 cette saison, U20 la suivante), les autres répartis.

    Certificats : environ 10 % expirés (fin de saison précédente), 5 % absents, le reste
    valide jusqu'à la saison suivante au moins.
    """
    licenses = rng.sample(range(100000, 900000), 300)
    athletes = []
    for index in range(300):
        sex = "F" if index % 2 == 0 else "M"
        if index < 10:
            birth_year = year - 17
        else:
            birth_year = year - rng.choice([13, 14, 15, 16, 18, 19] * 3 + list(range(20, 61)))
        birth_date = date(birth_year, rng.randint(1, 12), rng.randint(1, 28))
        draw = rng.random()
        if index < 10 or draw >= 0.15:
            certificate = date(year + 1, 3, 1) + timedelta(days=rng.randint(0, 364))
        elif draw < 0.10:
            certificate = date(year - 1, 11, 1) + timedelta(days=rng.randint(0, 60))
        else:
            certificate = None
        athletes.append(
            {
                "first_name": rng.choice(FIRST_NAMES[sex]),
                "last_name": rng.choice(LAST_NAMES),
                "birth_date": birth_date,
                "sex": sex,
                "club": CLUBS[index % len(CLUBS)],
                "license_number": f"DOS-{licenses[index]:06d}",
                "medical_certificate_valid_until": certificate,
            }
        )
    return athletes


def at(day: date, hour: int) -> str:
    return datetime.combine(day, time(hour), tzinfo=UTC).isoformat()


def performance(rng: random.Random, event: EventSpec) -> float:
    value = rng.uniform(event.low, event.high)
    return float(round(value)) if event.unit == "points" else round(value, 2)


def seed(conn: sqlite3.Connection, year: int) -> dict[str, int]:
    rng = random.Random(2026)
    athletes = make_athletes(rng, year)
    athlete_ids = []
    for athlete in athletes:
        cursor = conn.execute(
            "INSERT INTO athletes (first_name, last_name, birth_date, sex, club, license_number,"
            " medical_certificate_valid_until) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                athlete["first_name"],
                athlete["last_name"],
                athlete["birth_date"].isoformat(),
                athlete["sex"],
                athlete["club"],
                athlete["license_number"],
                certificate.isoformat()
                if (certificate := athlete["medical_certificate_valid_until"])
                else None,
            ),
        )
        athlete_ids.append(cursor.lastrowid)

    counts = {"competitions": 0, "events": 0, "registrations": 0, "results": 0}
    for spec in competitions_for(year):
        cursor = conn.execute(
            "INSERT INTO competitions (name, venue, date, status, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                spec.name,
                spec.venue,
                spec.day.isoformat(),
                spec.status,
                at(spec.day - timedelta(days=90), 9),
            ),
        )
        competition_id = cursor.lastrowid
        counts["competitions"] += 1
        bib = 0
        for event in spec.events:
            cursor = conn.execute(
                "INSERT INTO events (competition_id, name, unit, category) VALUES (?, ?, ?, ?)",
                (competition_id, event.name, event.unit, event.category),
            )
            event_id = cursor.lastrowid
            counts["events"] += 1
            if spec.status == "draft":
                continue

            entries = []
            for athlete, athlete_id in zip(athletes, athlete_ids, strict=True):
                certificate = athlete["medical_certificate_valid_until"]
                if certificate is None or certificate < spec.day:
                    continue
                category = age_category(athlete["birth_date"], on=spec.day)
                if event.category is not None and category != event.category:
                    continue
                if event.category == "U20" and athlete["birth_date"].year == year - 17:
                    continue  # laissés libres pour s'inscrire pendant les TP
                if rng.random() < (0.8 if event.category else 0.3):
                    entries.append(athlete_id)

            finished = spec.status in ("closed", "finished")
            scored = []
            for athlete_id in entries:
                bib += 1
                draw = rng.random()
                if draw < 0.05:
                    status = "cancelled"
                elif draw < (0.08 if finished else 0.40):
                    status = "pending"
                else:
                    status = "confirmed"
                cursor = conn.execute(
                    "INSERT INTO registrations (event_id, athlete_id, bib, status, created_at)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (
                        event_id,
                        athlete_id,
                        bib,
                        status,
                        at(spec.day - timedelta(days=rng.randint(7, 60)), 12),
                    ),
                )
                counts["registrations"] += 1
                if finished and status == "confirmed" and rng.random() < 0.97:
                    scored.append(cursor.lastrowid)

            # Performances distinctes : les seuls ex aequo sont ceux posés ci-dessous.
            performances: list[float] = []
            while len(performances) < len(scored):
                value = performance(rng, event)
                if value not in performances:
                    performances.append(value)
            if event.tie and len(performances) >= 4:
                # Ex aequo sur la 2e place : la 3e performance devient égale à la 2e.
                best_first = sorted(performances, reverse=event.unit != "time_s")
                second, third = best_first[1], best_first[2]
                performances[performances.index(third)] = second
            for registration_id, value in zip(scored, performances, strict=True):
                conn.execute(
                    "INSERT INTO results (registration_id, performance, recorded_at)"
                    " VALUES (?, ?, ?)",
                    (registration_id, value, at(spec.day, 18)),
                )
                counts["results"] += 1
    counts["athletes"] = len(athletes)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Données d'exemple synthétiques pour dossard.")
    parser.add_argument("--reset", action="store_true", help="supprime la base avant de peupler")
    parser.add_argument("--year", type=int, default=date.today().year, help="saison de référence")
    args = parser.parse_args()

    path = get_db_path()
    if args.reset:
        path.unlink(missing_ok=True)
    init_db(path)
    conn = connect(path)
    try:
        if conn.execute("SELECT COUNT(*) FROM athletes").fetchone()[0]:
            print(f"La base {path} contient déjà des données. Relancez avec --reset.")
            return 1
        counts = seed(conn, args.year)
        conn.commit()
    finally:
        conn.close()
    print(
        f"{counts['competitions']} compétitions, {counts['events']} épreuves, "
        f"{counts['athletes']} athlètes, {counts['registrations']} inscriptions, "
        f"{counts['results']} résultats ({path.name}, saison {args.year})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
