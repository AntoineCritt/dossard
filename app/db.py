from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated

from fastapi import Depends

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = Path(__file__).with_name("schema.sql")


def get_db_path() -> Path:
    """Chemin de la base : variable DOSSARD_DB, sinon data/dossard.db à la racine du dépôt."""
    env = os.environ.get("DOSSARD_DB")
    return Path(env) if env else ROOT / "data" / "dossard.db"


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: Path) -> None:
    """Crée les tables et les vues si elles n'existent pas (opération idempotente)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    try:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


def get_conn() -> Iterator[sqlite3.Connection]:
    """Une connexion par requête : commit si tout va bien, rollback sinon, toujours fermée."""
    conn = connect(get_db_path())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


Conn = Annotated[sqlite3.Connection, Depends(get_conn)]
