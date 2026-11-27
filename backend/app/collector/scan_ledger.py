"""Source scan ledger with per-run metrics and outcome visibility."""
import sqlite3, os, re
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

DB_PATH=os.getenv("GOZ_IHALE_SCAN_DB", str(Path(__file__).resolve().parents[2] / "scan_runs.db"))

# Match common credential spellings without masking ordinary search parameters such as "keyword".
_SENSITIVE_QUERY_KEYS={
    "token", "accesstoken", "refreshtoken", "authtoken", "authorization",
    "auth", "apikey", "xapikey", "key", "secret", "clientsecret",
    "secretkey", "privatekey", "password", "passwd", "signature", "sig",
    "credential", "credentials", "jwt", "bearer", "session", "sessionid",
    "sessiontoken", "cookie", "sid",
}

def _sensitive_query_key(key: str) -> bool:
    compact=re.sub(r"[^a-z0-9]","",key.casefold())
    return compact in _SENSITIVE_QUERY_KEYS or compact.endswith(("token","secret","apikey"))

def safe_source_url(url: str | None) -> str | None:
    """Redact query credentials, userinfo and fragments before storing an endpoint."""
    if not url:
        return url
    parsed=urlparse(url)
    query=[]
    for key,value in parse_qsl(parsed.query,keep_blank_values=True):
        query.append((key,"[redacted]" if _sensitive_query_key(key) else value))
    host=parsed.hostname or ""
    if ":" in host and not host.startswith("["):
        host=f"[{host}]"
    port=parsed.port
    netloc=host+(f":{port}" if port is not None else "")
    return urlunparse(parsed._replace(netloc=netloc,query=urlencode(query),fragment=""))

_METRIC_COLUMNS = {
    "fetched_count": "INTEGER NOT NULL DEFAULT 0",
    "relevant_count": "INTEGER NOT NULL DEFAULT 0",
    "new_count": "INTEGER NOT NULL DEFAULT 0",
    "updated_count": "INTEGER NOT NULL DEFAULT 0",
    "unchanged_count": "INTEGER NOT NULL DEFAULT 0",
    "alert_candidates": "INTEGER NOT NULL DEFAULT 0",
    "duration_ms": "INTEGER NOT NULL DEFAULT 0",
    "retry_count": "INTEGER NOT NULL DEFAULT 0",
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

def record_run(source, status="not_implemented", message="No permitted live adapter configured.", notices_found=0, metrics=None, source_url=None):
    initialize()
    metrics=metrics or {}
    with connection() as db:
        cur=db.execute("""INSERT INTO scan_runs
            (source_key,source_name,source_url,status,message,notices_found,finished_at,
             fetched_count,relevant_count,new_count,updated_count,unchanged_count,alert_candidates,duration_ms,retry_count)
            VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP,?,?,?,?,?,?,?,?)""",
            (source.key,source.name,safe_source_url(source_url or source.url),status,message,notices_found,
             int(metrics.get("fetched_count",0)),int(metrics.get("relevant_count",notices_found)),
             int(metrics.get("new_count",0)),int(metrics.get("updated_count",0)),
             int(metrics.get("unchanged_count",0)),int(metrics.get("alert_candidates",0)),
             int(metrics.get("duration_ms",0)),int(metrics.get("retry_count",0))))
        return dict(db.execute("SELECT * FROM scan_runs WHERE id=?",(cur.lastrowid,)).fetchone())

def list_runs(limit=100):
    initialize()
    with connection() as db:
        rows=db.execute("SELECT * FROM scan_runs ORDER BY id DESC LIMIT ?",(max(1,min(limit,500)),)).fetchall()
    return [dict(r) for r in rows]
