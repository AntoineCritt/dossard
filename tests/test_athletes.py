from datetime import date
from pathlib import Path

FIXTURE_CSV = (
    Path(__file__).resolve().parent.parent / "scripts" / "legacy" / "licencies_exemple.csv"
)


def test_create_athlete_returns_201_with_category(client):
    birth_date = date(date.today().year - 30, 3, 2)

    response = client.post(
        "/athletes",
        json={
            "first_name": "Inès",
            "last_name": "Morel",
            "birth_date": birth_date.isoformat(),
            "sex": "F",
            "license_number": "DOS-000042",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["category"] == "SENIOR"
    assert body["club"] is None


def test_create_athlete_rejects_duplicate_license(client, make_athlete):
    athlete = make_athlete()

    response = client.post(
        "/athletes",
        json={
            "first_name": "Hugo",
            "last_name": "Lemaire",
            "birth_date": "1995-05-20",
            "sex": "M",
            "license_number": athlete["license_number"],
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_list_athletes_filters_by_club(client, make_athlete):
    make_athlete("Durand", club="AC Rivebelle")
    make_athlete("Petit", club="Stade Nordval")

    response = client.get("/athletes", params={"club": "AC Rivebelle"})

    assert response.status_code == 200
    assert [a["last_name"] for a in response.json()] == ["Durand"]


def test_get_athlete_returns_200(client, make_athlete):
    athlete = make_athlete("Durand")

    response = client.get(f"/athletes/{athlete['id']}")

    assert response.status_code == 200
    assert response.json()["last_name"] == "Durand"


def test_get_athlete_returns_404_when_missing(client):
    response = client.get("/athletes/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_import_athletes_creates_skips_and_reports_errors(client):
    content = FIXTURE_CSV.read_text(encoding="utf-8")
    headers = {"Content-Type": "text/csv"}

    response = client.post("/athletes/import", content=content, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 17
    assert body["skipped"] == 1
    assert [e["line"] for e in body["errors"]] == [15, 16]


def test_import_athletes_twice_skips_everything_already_imported(client):
    content = FIXTURE_CSV.read_text(encoding="utf-8")
    headers = {"Content-Type": "text/csv"}
    client.post("/athletes/import", content=content, headers=headers)

    response = client.post("/athletes/import", content=content, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 0
    assert body["skipped"] == 18
    assert [e["line"] for e in body["errors"]] == [15, 16]
