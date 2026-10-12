from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response

from app.db import Conn
from app.ranking import rank_results
from app.repositories import results
from app.schemas import ResultIn, ResultOut, ResultUnit

router = APIRouter(tags=["results"])


@router.put("/registrations/{registration_id}/result", response_model=ResultOut)
def record_result(registration_id: int, data: ResultIn, conn: Conn) -> ResultOut:
    return results.record_result(conn, registration_id, data.performance)


@router.get("/events/{eventId}/ranking")
def getRanking(eventId: int, conn: Conn) -> dict:
    event = results.find_event(conn, eventId)
    if not event:
        raise HTTPException(status_code=404, detail="Epreuve introuvable")
    data = rank_results(results.ranking_rows(conn, eventId), ResultUnit(event["unit"]))
    return {"data": [entry.model_dump() for entry in data], "count": len(data)}


@router.get("/competitions/{competition_id}/results.csv")
def exportCsv(competition_id: int, conn: Conn) -> Response:
    csv = results.export_csv(conn, competition_id)
    return Response(content=csv, media_type="text/csv")
