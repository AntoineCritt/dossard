---
name: classement-html
description: Génère une page HTML du classement d'une épreuve (dossard, athlète, club, performance) à partir de l'API GET /events/{event_id}/ranking. À utiliser quand l'utilisateur veut un classement en page ou fichier HTML, à imprimer, partager ou consulter hors de l'API.
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/classement_html.py *)
---

# Classement HTML

Produit `classement-<event_id>.html` dans le répertoire courant, à partir du classement réel renvoyé par l'API (pas de HTML à écrire soi-même : le script s'en charge).

## Étapes

1. Si l'`event_id` n'est pas donné par l'utilisateur, le retrouver dans `data/dossard.db` (ou la base pointée par `DOSSARD_DB`), par exemple :
   ```bash
   sqlite3 data/dossard.db "SELECT id, name, unit FROM events WHERE name LIKE '%<mot-clé>%'"
   ```
   En cas d'ambiguïté (plusieurs épreuves correspondantes), demander à l'utilisateur de préciser.

2. Lancer le script depuis la racine du dépôt :
   ```bash
   python ${CLAUDE_SKILL_DIR}/scripts/classement_html.py <event_id>
   ```

3. Ne jamais écrire le HTML à la main : si le script échoue (épreuve introuvable, base absente, classement indisponible), lire le message d'erreur renvoyé et corriger l'`event_id` ou signaler le problème à l'utilisateur plutôt que de produire un classement soi-même.

4. Donner à l'utilisateur le chemin du fichier produit (affiché par le script, de la forme `classement-<event_id>.html : <n> athlètes classés`).
