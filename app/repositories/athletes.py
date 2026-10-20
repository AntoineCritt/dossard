from __future__ import annotations

import csv
import io
import sqlite3
from datetime import date

from pydantic import ValidationError

from app.categories import age_category
from app.errors import ConflictError
from app.repositories.common import fetch_or_404
from app.schemas import AthleteCreate, AthleteImportError, AthleteImportReport, AthleteOut


def _to_athlete(row: sqlite3.Row) -> AthleteOut:
    birth_date = date.fromisoformat(row["birth_date"])
    certificate = row["medical_certificate_valid_until"]
    return AthleteOut(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        birth_date=birth_date,
        sex=row["sex"],
        club=row["club"],
        license_number=row["license_number"],
        medical_certificate_valid_until=date.fromisoformat(certificate) if certificate else None,
        category=age_category(birth_date),
    )


def list_athletes(
    conn: sqlite3.Connection,
    club: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AthleteOut]:
    sql = "SELECT * FROM athletes"
    params: list[str | int] = []
    if club is not None:
        sql += " WHERE club = ?"
        params.append(club)
    sql += " ORDER BY last_name, first_name, id LIMIT ? OFFSET ?"
    params.append(limit)
    params.append(offset)
    return [_to_athlete(row) for row in conn.execute(sql, params)]


def get_athlete(conn: sqlite3.Connection, athlete_id: int) -> AthleteOut:
    row = fetch_or_404(
        conn,
        "SELECT * FROM athletes WHERE id = ?",
        (athlete_id,),
        f"Athlète {athlete_id} introuvable",
    )
    return _to_athlete(row)


def create_athlete(conn: sqlite3.Connection, data: AthleteCreate) -> AthleteOut:
    existing = conn.execute(
        "SELECT id FROM athletes WHERE license_number = ?", (data.license_number,)
    ).fetchone()
    if existing is not None:
        raise ConflictError(f"Licence {data.license_number} déjà enregistrée")

    certificate = data.medical_certificate_valid_until
    cursor = conn.execute(
        "INSERT INTO athletes (first_name, last_name, birth_date, sex, club, license_number,"
        " medical_certificate_valid_until) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data.first_name,
            data.last_name,
            data.birth_date.isoformat(),
            data.sex.value,
            data.club,
            data.license_number,
            certificate.isoformat() if certificate else None,
        ),
    )
    row = conn.execute("SELECT * FROM athletes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _to_athlete(row)


def import_athletes_csv(conn: sqlite3.Connection, content: str) -> AthleteImportReport:
    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    created = 0
    skipped = 0
    errors: list[AthleteImportError] = []
    for line_number, row in enumerate(reader, start=2):
        try:
            data = _row_to_athlete_create(row)
        except (ValueError, ValidationError) as exc:
            errors.append(AthleteImportError(line=line_number, message=_format_row_error(exc)))
            continue
        try:
            create_athlete(conn, data)
            created += 1
        except ConflictError:
            skipped += 1
    return AthleteImportReport(created=created, skipped=skipped, errors=errors)


def _parse_french_date(value: str | None, label: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        day_str, month_str, year_str = value.split("/")
        return date(int(year_str), int(month_str), int(day_str))
    except (ValueError, IndexError) as exc:
        raise ValueError(f"{label} invalide : « {value} »") from exc


def _row_to_athlete_create(row: dict[str, str | None]) -> AthleteCreate:
    birth_date = _parse_french_date(row.get("date_naissance"), "Date de naissance")
    if birth_date is None:
        raise ValueError("Date de naissance manquante")
    certificate = _parse_french_date(row.get("certificat_valide_jusqu"), "Certificat médical")
    return AthleteCreate(
        first_name=(row.get("prenom") or "").strip(),
        last_name=(row.get("nom") or "").strip(),
        birth_date=birth_date,
        sex=(row.get("sexe") or "").strip(),
        club=(row.get("club") or "").strip() or None,
        license_number=(row.get("licence") or "").strip(),
        medical_certificate_valid_until=certificate,
    )


def _format_row_error(exc: ValueError | ValidationError) -> str:
    if isinstance(exc, ValidationError):
        first = exc.errors()[0]
        field = ".".join(str(part) for part in first["loc"])
        return f"Champ « {field} » invalide : {first['msg']}"
    return str(exc)
