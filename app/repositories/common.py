from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from typing import Any

from app.errors import NotFoundError


def fetch_or_404(
    conn: sqlite3.Connection, sql: str, params: Sequence[Any], message: str
) -> sqlite3.Row:
    """Exécute une requête qui doit renvoyer une ligne, sinon lève NotFoundError(message).

    Exemple : fetch_or_404(conn, "SELECT * FROM events WHERE id = ?", (event_id,),
    f"Épreuve {event_id} introuvable").
    """
    row = conn.execute(sql, params).fetchone()
    if row is None:
        raise NotFoundError(message)
    return row
