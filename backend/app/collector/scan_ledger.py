"""Source scan ledger with per-run metrics and outcome visibility."""
import sqlite3, os
from pathlib import Path
DB_PATH=os.getenv("GOZ_IHALE_SCAN_DB", str(Path(__file__).resolve().parents[2] / "scan_runs.db"))

_METRIC_COLUMNS = {
    "fetched_count": "INTEGER NOT NULL DEFAULT 0",
    "relevant_count": "INTEGER NOT NULL DEFAULT 0",
    "new_count": "INTEGER NOT NULL DEFAULT 0",
    "updated_count": "INTEGER NOT NULL DEFAULT 0",
    "unchanged_count": "INTEGER NOT NULL DEFAULT 0",
    "alert_candidates": "INTEGER NOT NULL DEFAULT 0",
    "duration_ms": "INTEGER NOT NULL DEFAULT 0",
}

def connection():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def initialize():
    with connection() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS scan_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source_key TEXT NOT NULL,
            source_name TEXT NOT NULL, source_url TEXT NOT NULL,
            status TEXT NOT NULL, message TEXT, notices_found INTEGER NOT NULL DEFAULT 0,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP, finished_at TEXT)""")
        existing={row[1] for row in db.execute("PRAGMA table_info(scan_runs)").fetchall()}
        for name, definition in _METRIC_COLUMNS.items():
            if name not in existing:
                db.execute(f"ALTER TABLE scan_runs ADD COLUMN {name} {definition}")

def record_run(source, status="not_implemented", message="No permitted live adapter configured.", notices_found=0, metrics=None):
    initialize()
    metrics=metrics or {}
    with connection() as db:
        cur=db.execute("""INSERT INTO scan_runs
            (source_key,source_name,source_url,status,message,notices_found,finished_at,
             fetched_count,relevant_count,new_count,updated_count,unchanged_count,alert_candidates,duration_ms)
            VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP,?,?,?,?,?,?,?)""",
            (source.key,source.name,source.url,status,message,notices_found,
             int(metrics.get("fetched_count",0)),int(metrics.get("relevant_count",notices_found)),
             int(metrics.get("new_count",0)),int(metrics.get("updated_count",0)),
             int(metrics.get("unchanged_count",0)),int(metrics.get("alert_candidates",0)),
             int(metrics.get("duration_ms",0))))
        return dict(db.execute("SELECT * FROM scan_runs WHERE id=?",(cur.lastrowid,)).fetchone())

def list_runs(limit=100):
    initialize()
    with connection() as db:
        rows=db.execute("SELECT * FROM scan_runs ORDER BY id DESC LIMIT ?",(max(1,min(limit,500)),)).fetchall()
    return [dict(r) for r in rows]
