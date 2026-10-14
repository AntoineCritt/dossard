"""Récepteur local des hooks HTTP de Claude Code : affiche chaque événement reçu.

    python scripts/recepteur_hooks.py          # écoute sur http://127.0.0.1:8765
    python scripts/recepteur_hooks.py 9000     # autre port

Arrêt : Ctrl+C. N'écoute que sur la machine locale.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class Recepteur(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        taille = int(self.headers.get("Content-Length", 0))
        try:
            evenement = json.loads(self.rfile.read(taille) or b"{}")
        except json.JSONDecodeError:
            evenement = {}
        nom = evenement.get("hook_event_name", "?")
        detail = evenement.get("message") or evenement.get("last_assistant_message") or ""
        heure = datetime.now().strftime("%H:%M:%S")
        print(f"{heure} [{nom}] {str(detail)[:100]}", flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, format: str, *args: object) -> None:
        """Silence le journal par défaut de http.server."""


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Récepteur des hooks sur http://127.0.0.1:{port} (Ctrl+C pour arrêter)", flush=True)
    try:
        HTTPServer(("127.0.0.1", port), Recepteur).serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
