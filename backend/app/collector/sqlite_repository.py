"""SQLite-backed notice ingestion repository with fingerprint deduplication."""
from __future__ import annotations
import json, sqlite3, os
from pathlib import Path
from typing import Any
from .normalize import fingerprint_notice, material_change, notice_match_keys
from .alerts import decide_alert

DB_PATH=os.getenv("GOZ_IHALE_INGEST_DB", str(Path(__file__).resolve().parents[2] / "ingestion.db"))

def connection():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

def initialize():
    with connection() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS collected_notices (
            fingerprint TEXT PRIMARY KEY, notice_id TEXT, title TEXT NOT NULL,
            institution TEXT NOT NULL, city TEXT, publication_date TEXT, deadline TEXT,
            category TEXT, quantity TEXT, specification TEXT, estimated_price TEXT, document_url TEXT,
            source_name TEXT NOT NULL, source_url TEXT, summary TEXT, procurement_method TEXT, payment_terms TEXT,
            status TEXT NOT NULL DEFAULT 'new', relevance_score INTEGER DEFAULT 0,
            payload_json TEXT NOT NULL, first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
            last_seen TEXT DEFAULT CURRENT_TIMESTAMP)""")
        existing={row[1] for row in db.execute("PRAGMA table_info(collected_notices)").fetchall()}
        for field in ("procurement_method", "payment_terms"):
            if field not in existing:
                db.execute(f"ALTER TABLE collected_notices ADD COLUMN {field} TEXT")
        db.execute("""CREATE TABLE IF NOT EXISTS notice_identity_keys (identity_key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL)""")
        db.execute("""CREATE TABLE IF NOT EXISTS collected_notice_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT NOT NULL,
            event_type TEXT NOT NULL, changed_fields TEXT, payload_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

def ingest(record: dict[str, Any]) -> dict[str, Any]:
    initialize()
    fingerprint=fingerprint_notice(record.get("title",""),record.get("institution",""),record.get("publication_date"),record.get("notice_id"))
    payload=json.dumps(record,ensure_ascii=False,default=str)
    identity_keys=notice_match_keys(record)
    with connection() as db:
        oldrow=db.execute("SELECT * FROM collected_notices WHERE fingerprint=?",(fingerprint,)).fetchone()
        if oldrow is None and not record.get("notice_id") and identity_keys:
            marks=",".join("?" for _ in identity_keys)
            match=db.execute("SELECT fingerprint FROM notice_identity_keys WHERE identity_key IN ("+marks+") LIMIT 1",identity_keys).fetchone()
            if match:
                fingerprint=match["fingerprint"]
                oldrow=db.execute("SELECT * FROM collected_notices WHERE fingerprint=?",(fingerprint,)).fetchone()
        old=dict(oldrow) if oldrow else None
        if old is None:
            action="new"; changed=[]
        else:
            changed=material_change(old,record)
            action="updated" if changed else "unchanged"
        columns=("notice_id","title","institution","city","publication_date","deadline","category","quantity","specification","estimated_price","document_url","source_name","source_url","summary","procurement_method","payment_terms","status","relevance_score")
        values=[record.get(c) for c in columns]
        if old is None:
            db.execute("""INSERT INTO collected_notices (fingerprint,notice_id,title,institution,city,publication_date,deadline,category,quantity,specification,estimated_price,document_url,source_name,source_url,summary,procurement_method,payment_terms,status,relevance_score,payload_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",[fingerprint,*values,payload])
        else:
            db.execute("""UPDATE collected_notices SET notice_id=?,title=?,institution=?,city=?,publication_date=?,deadline=?,category=?,quantity=?,specification=?,estimated_price=?,document_url=?,source_name=?,source_url=?,summary=?,procurement_method=?,payment_terms=?,status=?,relevance_score=?,payload_json=?,last_seen=CURRENT_TIMESTAMP WHERE fingerprint=?""",[*values,payload,fingerprint])
        for identity_key in identity_keys:
            db.execute("INSERT OR IGNORE INTO notice_identity_keys(identity_key,fingerprint) VALUES (?,?)",(identity_key,fingerprint))
        if action != "unchanged":
            db.execute("INSERT INTO collected_notice_events (fingerprint,event_type,changed_fields,payload_json) VALUES (?,?,?,?)",(fingerprint,action,json.dumps(changed,ensure_ascii=False),payload))
    alert=decide_alert(action,changed,text=str(record),score=int(record.get("relevance_score",0)))
    return {"fingerprint":fingerprint,"action":action,"changed_fields":changed,"alert":alert.send,"alert_reason":alert.reason,"priority":alert.priority}

def list_notices(limit: int=100):
    initialize()
    with connection() as db:
        rows=db.execute("SELECT * FROM collected_notices ORDER BY deadline IS NULL, deadline, last_seen DESC LIMIT ?",(max(1,min(limit,500)),)).fetchall()
    return [dict(row) for row in rows]

def list_events(limit: int=100, fingerprint: str | None = None):
    initialize()
    with connection() as db:
        limit=max(1,min(limit,500))
        if fingerprint:
            rows=db.execute("SELECT * FROM collected_notice_events WHERE fingerprint=? ORDER BY created_at DESC,id DESC LIMIT ?",(fingerprint,limit)).fetchall()
        else:
            rows=db.execute("SELECT * FROM collected_notice_events ORDER BY created_at DESC,id DESC LIMIT ?",(limit,)).fetchall()
    return [dict(row) for row in rows]
