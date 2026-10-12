from __future__ import annotations

from fastapi import APIRouter, status

from app.db import Conn
from app.repositories import registrations
from app.schemas import RegistrationCreate, RegistrationOut, RegistrationUpdate

router = APIRouter(tags=["registrations"])


@router.post(
    "/events/{event_id}/registrations",
    response_model=RegistrationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_registration(event_id: int, data: RegistrationCreate, conn: Conn) -> RegistrationOut:
    return registrations.create_registration(conn, event_id, data.athlete_id)


@router.patch("/registrations/{registration_id}", response_model=RegistrationOut)
def update_registration(
    registration_id: int, data: RegistrationUpdate, conn: Conn
) -> RegistrationOut:
    return registrations.update_registration_status(conn, registration_id, data.status)
