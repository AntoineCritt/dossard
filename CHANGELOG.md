# Changelog

## Non publié

- Corrige `GET /competitions/{competition_id}/results.csv` : le CSV était construit par concaténation manuelle et se décalait d'une colonne quand un club contenait une virgule ; génération via le module `csv` (échappement correct des champs).
- Harmonise `app/routers/results.py` avec les conventions du projet : erreurs via `NotFoundError` (plus de `HTTPException`), noms en snake_case (`get_ranking`/`event_id`, `export_csv`), réponse de `GET /events/{event_id}/ranking` en liste nue (`response_model=list[RankingEntry]`, plus d'enveloppe `{"data", "count"}`), `summary=` en français sur chaque route.
- Ajout de la pagination à `GET /athletes` : paramètres `limit` (1-100, défaut 50) et `offset` (défaut 0).
- Ajout de `POST /athletes/import` : import en masse d'athlètes depuis un CSV (200).
- Supprime le script `scripts/legacy/import_licencies.py`, remplacé par l'endpoint d'import.
- Ajout de `GET /athletes/{athlete_id}` : détail d'un athlète (200, 404).
