"""SQLite-backed notice ingestion repository with fingerprint deduplication."""
from __future__ import annotations
import json, sqlite3, os, hashlib
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
        db.execute("""CREATE TABLE IF NOT EXISTS notice_source_observations (fingerprint TEXT NOT NULL, source_name TEXT NOT NULL, source_url TEXT, observed_payload TEXT, last_seen TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(fingerprint,source_name,source_url))""")
        db.execute("""CREATE TABLE IF NOT EXISTS collected_notice_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, fingerprint TEXT NOT NULL,
            event_type TEXT NOT NULL, changed_fields TEXT, payload_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        db.execute("""CREATE TABLE IF NOT EXISTS alert_deduplication (
            alert_key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, event_type TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        db.execute("""CREATE TABLE IF NOT EXISTS alert_outbox (
            alert_key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, payload_json TEXT NOT NULL,
            priority TEXT NOT NULL, reason TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT, next_attempt_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, sent_at TEXT, claimed_at TEXT)""")
        existing_alert_columns={row[1] for row in db.execute("PRAGMA table_info(alert_outbox)").fetchall()}
        if "next_attempt_at" not in existing_alert_columns:
            db.execute("ALTER TABLE alert_outbox ADD COLUMN next_attempt_at TEXT")
        if "claimed_at" not in existing_alert_columns:
            db.execute("ALTER TABLE alert_outbox ADD COLUMN claimed_at TEXT")

def ingest(record: dict[str, Any]) -> dict[str, Any]:
    initialize()
    fingerprint=fingerprint_notice(record.get("title",""),record.get("institution",""),record.get("publication_date"),record.get("notice_id"))
    payload=json.dumps(record,ensure_ascii=False,default=str)
    identity_keys=notice_match_keys(record)
    with connection() as db:
        oldrow=db.execute("SELECT * FROM collected_notices WHERE fingerprint=?",(fingerprint,)).fetchone()
        if oldrow is None and not record.get("notice_id") and record.get("publication_date") and identity_keys:
            # Match only date-specific key to avoid merging separate procurement rounds.
            dated_key=identity_keys[0]
            match=db.execute("SELECT fingerprint FROM notice_identity_keys WHERE identity_key=?",(dated_key,)).fetchone()
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
        values=[(record.get(c) if record.get(c) not in (None, "") else ("new" if c == "status" and old is None else None)) if old is None else (record.get(c) if record.get(c) not in (None, "") else old.get(c)) for c in columns]
        if old is None:
            db.execute("""INSERT INTO collected_notices (fingerprint,notice_id,title,institution,city,publication_date,deadline,category,quantity,specification,estimated_price,document_url,source_name,source_url,summary,procurement_method,payment_terms,status,relevance_score,payload_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",[fingerprint,*values,payload])
        else:
            db.execute("""UPDATE collected_notices SET notice_id=?,title=?,institution=?,city=?,publication_date=?,deadline=?,category=?,quantity=?,specification=?,estimated_price=?,document_url=?,source_name=?,source_url=?,summary=?,procurement_method=?,payment_terms=?,status=?,relevance_score=?,payload_json=?,last_seen=CURRENT_TIMESTAMP WHERE fingerprint=?""",[*values,payload,fingerprint])
        observation=json.dumps(record,ensure_ascii=False,default=str)
        db.execute("INSERT INTO notice_source_observations(fingerprint,source_name,source_url,observed_payload,last_seen) VALUES (?,?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(fingerprint,source_name,source_url) DO UPDATE SET observed_payload=excluded.observed_payload,last_seen=CURRENT_TIMESTAMP",(fingerprint,record.get("source_name") or "unknown",record.get("source_url") or "",observation))
        for identity_key in identity_keys:
            db.execute("INSERT OR IGNORE INTO notice_identity_keys(identity_key,fingerprint) VALUES (?,?)",(identity_key,fingerprint))
        if action != "unchanged":
            event_type=action
            if action == "updated":
                status_text=str(record.get("status") or "").casefold()
                haystack=" ".join(str(record.get(k) or "") for k in ("title","summary","status","specification")).casefold()
                if any(term in status_text or term in haystack for term in ("iptal","cancel","cancelled")):
                    event_type="cancellation"
                elif any(term in haystack for term in ("zeyilname","amendment","ek doküman")):
                    event_type="amendment"
                elif "deadline" in changed:
                    old_deadline=str(old.get("deadline") or "")
                    new_deadline=str(record.get("deadline") or "")
                    # ISO-like values compare chronologically; otherwise keep generic.
                    event_type="deadline_extension" if old_deadline and new_deadline and new_deadline > old_deadline else "deadline_change"
                elif "specification" in changed:
                    event_type="specification_change"
                elif "document_url" in changed:
                    event_type="document_change"
                elif "status" in changed:
                    event_type="status_change"
            event_payload={"new":record,"old":old or {},"changed_fields":changed}
            db.execute("INSERT INTO collected_notice_events (fingerprint,event_type,changed_fields,payload_json) VALUES (?,?,?,?)",(fingerprint,event_type,json.dumps(changed,ensure_ascii=False),json.dumps(event_payload,ensure_ascii=False,default=str)))
    alert=decide_alert(action,changed,text=str(record),score=int(record.get("relevance_score",0)))
    alert_sent=alert.send
    alert_reason=alert.reason
    alert_key=None
    if alert.send:
        event_type_for_alert=event_type if action != "unchanged" else action
        changed_values={field:record.get(field) for field in changed}
        key_material=json.dumps({"fingerprint":fingerprint,"event_type":event_type_for_alert,"changed":changed_values},sort_keys=True,ensure_ascii=False,default=str)
        alert_key=hashlib.sha256(key_material.encode("utf-8")).hexdigest()
        with connection() as db:
            prior=db.execute("SELECT alert_key FROM alert_deduplication WHERE alert_key=?",(alert_key,)).fetchone()
            if prior:
                alert_sent=False
                alert_reason="Aynı olay için bildirim daha önce oluşturuldu; tekrar bastırıldı"
            else:
                db.execute("INSERT INTO alert_deduplication(alert_key,fingerprint,event_type) VALUES (?,?,?)",(alert_key,fingerprint,event_type_for_alert))
                db.execute("INSERT INTO alert_outbox(alert_key,fingerprint,payload_json,priority,reason) VALUES (?,?,?,?,?)",
                           (alert_key,fingerprint,payload,alert.priority,alert.reason))
    return {"fingerprint":fingerprint,"action":action,"changed_fields":changed,"alert":alert_sent,"alert_reason":alert_reason,"priority":alert.priority,"alert_key":alert_key}

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


def list_source_observations(fingerprint: str | None = None, limit: int = 100):
    initialize()
    limit=max(1,min(limit,500))
    with connection() as db:
        if fingerprint:
            rows=db.execute("SELECT * FROM notice_source_observations WHERE fingerprint=? ORDER BY last_seen DESC LIMIT ?",(fingerprint,limit)).fetchall()
        else:
            rows=db.execute("SELECT * FROM notice_source_observations ORDER BY last_seen DESC LIMIT ?",(limit,)).fetchall()
    return [dict(row) for row in rows]


def source_disagreements(fingerprint: str):
    """Summarize differing observed values across sources for selected notice fields."""
    fields=("deadline","status","quantity","specification","document_url","estimated_price","procurement_method","payment_terms")
    observations=list_source_observations(fingerprint=fingerprint,limit=500)
    parsed=[]
    for obs in observations:
        try:
            payload=json.loads(obs.get("observed_payload") or "{}")
        except (TypeError, ValueError):
            payload={}
        parsed.append({"source_name":obs.get("source_name"),"source_url":obs.get("source_url"),"last_seen":obs.get("last_seen"),"payload":payload})
    disagreements=[]
    for field in fields:
        values={}
        for obs in parsed:
            value=obs["payload"].get(field)
            if value is not None and str(value).strip():
                values.setdefault(str(value).strip(),[]).append({"source_name":obs["source_name"],"source_url":obs["source_url"],"last_seen":obs["last_seen"]})
        if len(values)>1:
            disagreements.append({"field":field,"values":[{"value":value,"sources":sources} for value,sources in values.items()]})
    return {"fingerprint":fingerprint,"observation_count":len(parsed),"disagreements":disagreements}

def _decode_alert_rows(rows):
    result=[]
    for row in rows:
        item=dict(row)
        try:
            item["payload"]=json.loads(item.pop("payload_json"))
        except (TypeError,ValueError):
            item["payload"]={}
        result.append(item)
    return result


def list_pending_alerts(limit: int = 100):
    initialize()
    with connection() as db:
        rows=db.execute("SELECT alert_key,fingerprint,payload_json,priority,reason,attempts,next_attempt_at FROM alert_outbox WHERE status='pending' AND attempts<8 AND (next_attempt_at IS NULL OR next_attempt_at<=CURRENT_TIMESTAMP) ORDER BY created_at,alert_key LIMIT ?",(max(1,min(limit,500)),)).fetchall()
    return _decode_alert_rows(rows)


def claim_pending_alerts(limit: int = 100):
    """Atomically lease due alerts so parallel dispatchers cannot send the same row.

    A crashed dispatcher leaves a lease for at most ten minutes; stale leases are
    returned to pending before the next claim operation.
    """
    initialize()
    with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE alert_outbox SET status='pending',claimed_at=NULL WHERE status='sending' AND claimed_at<=datetime('now','-10 minutes')")
        rows=db.execute("SELECT alert_key,fingerprint,payload_json,priority,reason,attempts,next_attempt_at FROM alert_outbox WHERE status='pending' AND attempts<8 AND (next_attempt_at IS NULL OR next_attempt_at<=CURRENT_TIMESTAMP) ORDER BY created_at,alert_key LIMIT ?",(max(1,min(limit,500)),)).fetchall()
        keys=[row["alert_key"] for row in rows]
        for key in keys:
            db.execute("UPDATE alert_outbox SET status='sending',claimed_at=CURRENT_TIMESTAMP WHERE alert_key=? AND status='pending'",(key,))
        claimed=db.execute("SELECT alert_key,fingerprint,payload_json,priority,reason,attempts,next_attempt_at FROM alert_outbox WHERE status='sending' AND alert_key IN (" + ",".join("?" for _ in keys) + ") ORDER BY created_at,alert_key",keys).fetchall() if keys else []
    return _decode_alert_rows(claimed)


def retry_delay_seconds(attempts: int) -> int:
    """Bounded exponential delay: 1 minute initially, capped at 1 hour."""
    return min(3600, 60 * (2 ** max(0, int(attempts))))

def mark_alert_delivery(alert_key: str, success: bool, error: str | None = None):
    initialize()
    safe_error=(str(error or "Delivery failed")[:300] if not success else None)
    with connection() as db:
        if success:
            db.execute("UPDATE alert_outbox SET status='sent',attempts=attempts+1,last_error=NULL,next_attempt_at=NULL,claimed_at=NULL,sent_at=CURRENT_TIMESTAMP WHERE alert_key=? AND status IN ('pending','sending')",(alert_key,))
        else:
            row=db.execute("SELECT attempts FROM alert_outbox WHERE alert_key=? AND status IN ('pending','sending')",(alert_key,)).fetchone()
            if row is None:
                return
            attempts=int(row["attempts"])
            delay=retry_delay_seconds(attempts)
            db.execute("UPDATE alert_outbox SET attempts=attempts+1,last_error=?,next_attempt_at=datetime('now', '+' || ? || ' seconds'),claimed_at=NULL,status=CASE WHEN attempts+1>=8 THEN 'failed' ELSE 'pending' END WHERE alert_key=? AND status IN ('pending','sending')",(safe_error,delay,alert_key))

def notification_counts():
    initialize()
    with connection() as db:
        rows=db.execute("SELECT status,COUNT(*) AS count FROM alert_outbox GROUP BY status").fetchall()
    counts={"pending":0,"sending":0,"sent":0,"failed":0}
    for row in rows:
        counts[row["status"]]=int(row["count"])
    return counts
