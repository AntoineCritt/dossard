# Changelog

## Non publié

- Ajoute la pagination `?limit=` (1–100, défaut 50) et `?offset=` (≥ 0, défaut 0) à `GET /athletes`, appliquée après le filtre `club` ; valeurs hors bornes rejetées en 422.
- Ajoute `POST /athletes/import` : import d'un CSV fédéral (`text/csv`, `;`, dates `jj/mm/aaaa`) avec compte-rendu `created` / `skipped` / `errors`. Remplace `scripts/legacy/import_licencies.py`, supprimé.
- Ajoute `GET /athletes/{athlete_id}` : détail d'un athlète (404 si introuvable).
