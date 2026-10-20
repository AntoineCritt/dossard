# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Dossard : API FastAPI + SQLite de gestion de compétitions sportives (compétitions, épreuves, athlètes, inscriptions, résultats). C'est le dépôt fil rouge d'une formation Claude Code de deux jours — chaque module le fait évoluer (nouveaux endpoints, skills, hooks, CI, serveur MCP, sous-agents). Attendez-vous à des instructions de modules de formation en plus des demandes de l'utilisateur.

## Commandes

```bash
pip install -e ".[dev]"             # installation (Python 3.12+, venv déjà présent dans .venv)
pytest                              # tous les tests
pytest tests/test_registrations.py  # un seul fichier de test
pytest -k nom_du_test               # un seul test par nom
ruff check . && ruff format .       # lint + formatage
python scripts/seed.py --reset      # rebâtit data/dossard.db avec des données synthétiques
uvicorn app.main:app --reload       # serveur sur http://localhost:8000 (doc interactive : /docs)
```

Les tests n'utilisent jamais `data/dossard.db` : `tests/conftest.py` fournit une base SQLite temporaire par test via la variable d'environnement `DOSSARD_DB`.

## Architecture

Flux d'une requête : `routers/` (validation Pydantic, pas de SQL) → `repositories/` (SQL + règles métier, lèvent `ApiError`/`NotFoundError`/`ConflictError`) → `app/db.py` (une connexion SQLite par requête, commit si succès, rollback sinon). Le handler global dans `app/main.py` sérialise toute `ApiError` en `{"error": {"code", "message"}}`. Un module métier par entité, même nom dans `repositories/` et `routers/` (ex. `repositories/registrations.py` ↔ `routers/registrations.py`).

`app/schema.sql` est la seule source de vérité du schéma, appliqué de façon idempotente par `init_db()` au démarrage (pas de migrations). Deux vues (`v_public_athletes`, `v_public_results`) exposent volontairement moins de colonnes que les tables : c'est ce que lit le serveur MCP en lecture seule (`scripts/mcp_dossard.py`), jamais les tables brutes.

Règles métier (détaillées avec leurs codes d'erreur dans `docs/api.md`, **à tenir à jour à chaque évolution de l'API** — règle du projet) :
- inscription uniquement sur une compétition `open` ; une inscription non annulée par athlète et par épreuve
- catégorie de l'épreuve (si définie) = catégorie d'âge de l'athlète pour la saison de la compétition (`app/categories.py`, âge atteint au 31/12)
- certificat médical obligatoire et valide à la date de la compétition
- dossard = max des dossards de la compétition + 1, jamais réattribué même après annulation
- résultat enregistrable seulement sur une inscription `confirmed` d'une compétition `closed`
- classement (`app/ranking.py`) : temps croissants, distances/points décroissants ; seules les inscriptions `confirmed` avec résultat y figurent

Transitions d'état : compétition `draft → open → closed → finished` ; inscription `pending → confirmed|cancelled`, `confirmed → cancelled`. Toute autre transition renvoie 409 `invalid_transition`.

`app/routers/results.py` s'écarte délibérément des conventions du reste du code (nommage camelCase, `HTTPException` au lieu de `ApiError`, réponse enveloppée `{"data", "count"}` au lieu d'une liste nue) : ne pas copier ce style ailleurs sans qu'un exercice de formation ne le demande explicitement.

`scripts/legacy/` contient un ancien import CSV volontairement non idiomatique, cible d'un exercice de refactoring.

## Règles du projet

- Lancer `pytest` : tous les tests doivent passer avant tout commit.
- Lancer `ruff check . && ruff format .` après toute modification de code Python.
- Faire passer toute erreur métier par `app/errors.py` (`ApiError`, `NotFoundError`, `ConflictError`) ; ne jamais lever `HTTPException` directement (`app/routers/results.py` est l'exception historique connue, pas un modèle à suivre).
- Réutiliser les fixtures de `tests/conftest.py` (`client`, `make_competition`, `make_event`, `make_athlete`, `make_registration`) plutôt que d'en recréer.
- Mettre un fichier de test par router.
- Tester systématiquement les cas d'erreur de chaque endpoint (404, 409, 422), pas seulement le cas nominal.
- Pour toute route ajoutée ou modifiée, ajouter une ligne dans `docs/api.md`.
- Pour toute route ajoutée ou modifiée, ajouter une entrée en tête de `CHANGELOG.md`, section « Non publié » (créer ce fichier s'il n'existe pas encore).
- Ne jamais modifier ni supprimer un fichier de `scripts/legacy/` sans demande explicite (la lecture est libre).
- Ne jamais ajouter de nouvelle dépendance sans demander.
- Ne jamais lire ni afficher .env : il contient des secrets.
