"""Source scan run ledger (scaffold; no network collection yet)."""
import sqlite3, os
from pathlib import Path
DB_PATH=os.getenv("GOZ_IHALE_SCAN_DB", str(Path(__file__).resolve().parents[2] / "scan_runs.db"))

def connection():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def initialize():
    with connection() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS scan_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source_key TEXT NOT NULL,
            source_name TEXT NOT NULL, source_url TEXT NOT NULL,
            status TEXT NOT NULL, message TEXT, notices_found INTEGER NOT NULL DEFAULT 0,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP, finished_at TEXT)""")

def record_run(source, status="not_implemented", message="No permitted live adapter configured.", notices_found=0):
    initialize()
    with connection() as db:
        cur=db.execute("INSERT INTO scan_runs (source_key,source_name,source_url,status,message,notices_found,finished_at) VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
            (source.key,source.name,source.url,status,message,notices_found))
        return dict(db.execute("SELECT * FROM scan_runs WHERE id=?",(cur.lastrowid,)).fetchone())

def list_runs(limit=100):
    initialize()
    with connection() as db:
        rows=db.execute("SELECT * FROM scan_runs ORDER BY id DESC LIMIT ?",(max(1,min(limit,500)),)).fetchall()
    return [dict(r) for r in rows]
