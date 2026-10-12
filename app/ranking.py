from __future__ import annotations

import sqlite3

from app.schemas import RankingEntry, ResultUnit


def rank_results(rows: list[sqlite3.Row], unit: ResultUnit) -> list[RankingEntry]:
    """Classe les performances : temps croissants, distances et points décroissants."""
    best_first = sorted(rows, key=lambda row: row["performance"], reverse=unit != ResultUnit.TIME_S)
    return [
        RankingEntry(
            rank=index + 1,
            bib=row["bib"],
            athlete_id=row["athlete_id"],
            last_name=row["last_name"],
            first_name=row["first_name"],
            club=row["club"],
            performance=row["performance"],
        )
        for index, row in enumerate(best_first)
    ]
