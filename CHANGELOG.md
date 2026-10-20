# Changelog

## Non publié

- Ajout de `POST /athletes/import` : import en masse d'athlètes depuis un CSV (200).
- Supprime le script `scripts/legacy/import_licencies.py`, remplacé par l'endpoint d'import.
- Ajout de `GET /athletes/{athlete_id}` : détail d'un athlète (200, 404).
