from __future__ import annotations

from fastapi import APIRouter, Query, Request, status

from app.db import Conn
from app.repositories import athletes
from app.schemas import AthleteCreate, AthleteImportReport, AthleteOut

router = APIRouter(prefix="/athletes", tags=["athletes"])


@router.get("", response_model=list[AthleteOut])
def list_athletes(
    conn: Conn,
    club: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[AthleteOut]:
    return athletes.list_athletes(conn, club=club, limit=limit, offset=offset)


@router.post("", response_model=AthleteOut, status_code=status.HTTP_201_CREATED)
def create_athlete(data: AthleteCreate, conn: Conn) -> AthleteOut:
    return athletes.create_athlete(conn, data)


@router.post("/import", response_model=AthleteImportReport, status_code=status.HTTP_200_OK)
async def import_athletes(request: Request, conn: Conn) -> AthleteImportReport:
    body = await request.body()
    return athletes.import_athletes_csv(conn, body.decode("utf-8-sig"))


@router.get("/{athlete_id}", response_model=AthleteOut)
def get_athlete(athlete_id: int, conn: Conn) -> AthleteOut:
    return athletes.get_athlete(conn, athlete_id)
