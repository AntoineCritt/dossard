from collections.abc import Iterator
from datetime import date, timedelta
from itertools import count
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.db import init_db
from app.main import app

STATUS_CHAIN = ["draft", "open", "closed", "finished"]


@pytest.fixture
def db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Une base SQLite neuve par test, jamais data/dossard.db."""
    path = tmp_path / "dossard.db"
    monkeypatch.setenv("DOSSARD_DB", str(path))
    return path


@pytest.fixture
def client(db_path: Path) -> Iterator[TestClient]:
    init_db(db_path)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def make_competition(client: TestClient):
    """Fabrique : crée une compétition via l'API puis la fait avancer jusqu'au statut demandé."""

    def _make(name: str = "Meeting test", date: date | None = None, status: str = "draft") -> dict:
        competition_date = date or _today() + timedelta(days=30)
        response = client.post(
            "/competitions", json={"name": name, "date": competition_date.isoformat()}
        )
        assert response.status_code == 201
        competition = response.json()
        for next_status in STATUS_CHAIN[1 : STATUS_CHAIN.index(status) + 1]:
            response = client.patch(
                f"/competitions/{competition['id']}", json={"status": next_status}
            )
            assert response.status_code == 200
            competition = response.json()
        return competition

    return _make


@pytest.fixture
def make_event(client: TestClient):
    def _make(
        competition_id: int, name: str = "100 m", unit: str = "time_s", category: str | None = None
    ) -> dict:
        response = client.post(
            f"/competitions/{competition_id}/events",
            json={"name": name, "unit": unit, "category": category},
        )
        assert response.status_code == 201
        return response.json()

    return _make


@pytest.fixture
def make_athlete(client: TestClient):
    """Fabrique : athlète senior (30 ans), certificat valide un an, licence unique."""
    licenses = count(1)

    def _make(
        last_name: str = "Martin",
        birth_date: date | None = None,
        sex: str = "F",
        club: str | None = None,
        certificate_valid_until: date | None = None,
    ) -> dict:
        today = _today()
        birth_date = birth_date or date(today.year - 30, 6, 15)
        certificate = certificate_valid_until or today + timedelta(days=365)
        response = client.post(
            "/athletes",
            json={
                "first_name": "Camille",
                "last_name": last_name,
                "birth_date": birth_date.isoformat(),
                "sex": sex,
                "club": club,
                "license_number": f"DOS-{next(licenses):06d}",
                "medical_certificate_valid_until": certificate.isoformat(),
            },
        )
        assert response.status_code == 201
        return response.json()

    return _make


@pytest.fixture
def make_registration(client: TestClient):
    def _make(event_id: int, athlete_id: int, confirm: bool = True) -> dict:
        response = client.post(f"/events/{event_id}/registrations", json={"athlete_id": athlete_id})
        assert response.status_code == 201
        registration = response.json()
        if confirm:
            response = client.patch(
                f"/registrations/{registration['id']}", json={"status": "confirmed"}
            )
            assert response.status_code == 200
            registration = response.json()
        return registration

    return _make


def _today() -> date:
    return date.today()
