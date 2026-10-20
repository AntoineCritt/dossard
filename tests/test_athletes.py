from datetime import date
from pathlib import Path


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
    athlete = make_athlete("Durand", club="AC Rivebelle")

    response = client.get(f"/athletes/{athlete['id']}")

    assert response.status_code == 200
    assert response.json() == athlete


def test_get_athlete_unknown_returns_404(client):
    response = client.get("/athletes/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_get_athlete_invalid_id_returns_422(client):
    response = client.get("/athletes/abc")

    assert response.status_code == 422


CSV_EXEMPLE = Path(__file__).parents[1] / "scripts" / "legacy" / "licencies_exemple.csv"
CSV_HEADERS = {"Content-Type": "text/csv"}


def test_import_athletes_creates_skips_and_reports_errors(client):
    response = client.post(
        "/athletes/import", content=CSV_EXEMPLE.read_bytes(), headers=CSV_HEADERS
    )

    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 17
    assert body["skipped"] == 1
    assert [e["line"] for e in body["errors"]] == [15, 16]
    assert len(client.get("/athletes").json()) == 17


def test_import_athletes_twice_skips_everything_valid(client):
    content = CSV_EXEMPLE.read_bytes()
    first = client.post("/athletes/import", content=content, headers=CSV_HEADERS).json()

    response = client.post("/athletes/import", content=content, headers=CSV_HEADERS)

    body = response.json()
    assert (body["created"], body["skipped"]) == (0, 18)
    assert body["errors"] == first["errors"]
    assert [e["line"] for e in body["errors"]] == [15, 16]


def test_import_athletes_missing_columns_returns_400(client):
    response = client.post("/athletes/import", content=b"nom;prenom\nA;B\n", headers=CSV_HEADERS)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_csv"
