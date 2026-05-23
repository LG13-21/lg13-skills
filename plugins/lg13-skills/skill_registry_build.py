#!/usr/bin/env python3
"""skill_registry_build.py — Import manifest.json → skill_registry.db (SQLite).

Usage:
    python skill_registry_build.py [--manifest PATH] [--db PATH]
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

DEFAULT_MANIFEST = Path(__file__).parent / "manifest.json"
DEFAULT_DB = Path(__file__).parent / "skill_registry.db"

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS skills (
    name        TEXT PRIMARY KEY,
    category    TEXT NOT NULL,
    tokens      INTEGER,
    role        TEXT,
    triggers    TEXT,
    hot         INTEGER NOT NULL DEFAULT 0,
    strat_only  INTEGER NOT NULL DEFAULT 0
);
"""

def build(manifest_path: Path, db_path: Path) -> int:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_SQL)
    conn.execute("DELETE FROM skills")

    rows = []

    for s in data["hot"]["skills"]:
        rows.append((
            s["name"], "hot", s.get("tokens"), s.get("role"),
            None, 1, 0
        ))

    for s in data["hot_strat_only"]["skills"]:
        rows.append((
            s["name"], "hot_strat_only", s.get("tokens"), s.get("role"),
            None, 1, 1
        ))

    for s in data["cold"]["skills"]:
        rows.append((
            s["name"], "cold", s.get("tokens"), s.get("role"),
            json.dumps(s.get("triggers", []), ensure_ascii=False),
            0, 0
        ))

    conn.executemany(
        "INSERT OR REPLACE INTO skills(name,category,tokens,role,triggers,hot,strat_only) "
        "VALUES(?,?,?,?,?,?,?)",
        rows
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
    conn.close()
    print(f"skill_registry.db: {count} skills imported from {manifest_path.name}")
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = ap.parse_args()

    if not args.manifest.exists():
        print(f"ERROR: manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    build(args.manifest, args.db)


if __name__ == "__main__":
    main()
