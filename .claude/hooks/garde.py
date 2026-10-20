#!/usr/bin/env python3
"""Hook PreToolUse : bloque les commandes destructrices (rm -rf, git push --force, DROP TABLE/VIEW)."""

import json
import re
import sys

DANGEROUS_TOOLS = ("Bash", "PowerShell")


def split_statements(command):
    return re.split(r"&&|\|\||[;&|\n]", command)


def tokenize(statement):
    return statement.split()


def strip_quotes(token):
    return token.strip("\"'")


def find_command_index(tokens, name):
    for i, token in enumerate(tokens):
        candidate = strip_quotes(token)
        base = re.split(r"[\\/]", candidate)[-1]
        if base.lower() == name:
            return i
    return None


def is_rm_rf(statement):
    tokens = tokenize(statement)
    rm_idx = find_command_index(tokens, "rm")
    if rm_idx is None:
        return False

    has_r = False
    has_f = False
    for token in tokens[rm_idx + 1 :]:
        value = strip_quotes(token)
        if value.startswith("--"):
            if value in ("--recursive",):
                has_r = True
            if value in ("--force",):
                has_f = True
        elif value.startswith("-") and len(value) > 1:
            letters = value[1:]
            if "r" in letters or "R" in letters:
                has_r = True
            if "f" in letters:
                has_f = True

    return has_r and has_f


POWERSHELL_REMOVE_ALIASES = {"remove-item", "ri", "rm", "rd", "rmdir", "del", "erase"}


def is_powershell_remove_force(statement):
    tokens = tokenize(statement)
    idx = None
    for i, token in enumerate(tokens):
        candidate = strip_quotes(token).lower()
        base = re.split(r"[\\/]", candidate)[-1]
        if base in POWERSHELL_REMOVE_ALIASES:
            idx = i
            break
    if idx is None:
        return False

    has_recurse = False
    has_force = False
    for token in tokens[idx + 1 :]:
        value = strip_quotes(token)
        if not value.startswith("-"):
            continue
        flag = value[1:].split(":", 1)[0].lower()
        if flag and len(flag) >= 3 and "recurse".startswith(flag):
            has_recurse = True
        if flag and len(flag) >= 2 and "force".startswith(flag):
            has_force = True

    return has_recurse and has_force


def is_git_push_force(statement):
    tokens = [strip_quotes(t) for t in tokenize(statement)]
    git_idx = find_command_index([t for t in tokens], "git")
    if git_idx is None or "push" not in tokens[git_idx:]:
        return False

    for token in tokens[git_idx:]:
        if token in ("--force", "-f") or token.startswith("--force="):
            return True
        if re.match(r"^-[a-zA-Z]*f[a-zA-Z]*$", token) and not token.startswith("--"):
            return True

    return False


def is_drop_table_or_view(statement):
    return bool(re.search(r"\bdrop\s+(table|view)\b", statement, re.IGNORECASE))


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw.lstrip("﻿"))
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = payload.get("tool_name")
    if tool_name not in DANGEROUS_TOOLS:
        sys.exit(0)

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    for statement in split_statements(command):
        if is_rm_rf(statement):
            print(
                "Bloqué par le hook garde.py : commande de suppression récursive forcée (rm -rf) détectée",
                file=sys.stderr,
            )
            sys.exit(2)
        if is_powershell_remove_force(statement):
            print(
                "Bloqué par le hook garde.py : suppression récursive forcée PowerShell "
                "(Remove-Item -Recurse -Force ou équivalent) détectée",
                file=sys.stderr,
            )
            sys.exit(2)
        if is_git_push_force(statement):
            print(
                "Bloqué par le hook garde.py : git push --force détecté",
                file=sys.stderr,
            )
            sys.exit(2)
        if is_drop_table_or_view(statement):
            print(
                "Bloqué par le hook garde.py : instruction DROP TABLE/VIEW détectée",
                file=sys.stderr,
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
