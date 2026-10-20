# Changelog

## Non publié

- Ajoute `POST /athletes/import` : import d'un CSV fédéral (`text/csv`, `;`, dates `jj/mm/aaaa`) avec compte-rendu `created` / `skipped` / `errors`. Remplace `scripts/legacy/import_licencies.py`, supprimé.
- Ajoute `GET /athletes/{athlete_id}` : détail d'un athlète (404 si introuvable).
