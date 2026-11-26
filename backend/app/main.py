from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import Tender
from .collector.scoring import relevance_score
from .collector.deadlines import days_remaining, urgency_label
from .collector.sqlite_repository import list_notices as list_collected_notices, list_events as list_ingestion_events, ingest as ingest_collected_notice
import sqlite3, os
from pathlib import Path

app = FastAPI(title="GozIhale API", version="0.2.0", description="Ophthalmology procurement intelligence API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
DB_PATH=os.getenv("GOZ_IHALE_DB", str(Path(__file__).resolve().parent.parent / "gozihale.db"))

SAMPLE_TENDERS = [
    {"id":"demo-001","title":"OCT cihazı alımı (örnek)","institution":"Demo Üniversite Hastanesi","city":"Ankara","category":"OCT","deadline":None,"source_name":"Demo","source_url":None,"summary":"Demo kayıt; gerçek ilan değildir.","status":"demo"},
    {"id":"demo-002","title":"Fako cihazı ve sarf (örnek)","institution":"Demo Şehir Hastanesi","city":"İstanbul","category":"Fako","deadline":None,"source_name":"Demo","source_url":None,"summary":"Demo kayıt; gerçek ilan değildir.","status":"demo"},
]

def connect():
    conn=sqlite3.connect(DB_PATH); conn.row_factory=sqlite3.Row; return conn

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tenders (
        id TEXT PRIMARY KEY, title TEXT NOT NULL, institution TEXT NOT NULL, city TEXT,
        category TEXT NOT NULL, deadline TEXT, source_name TEXT NOT NULL, source_url TEXT,
        summary TEXT, status TEXT NOT NULL DEFAULT 'new')""")
        for item in SAMPLE_TENDERS:
            c.execute("INSERT OR IGNORE INTO tenders VALUES (?,?,?,?,?,?,?,?,?,?)",tuple(item.values()))

@app.on_event("startup")
def startup(): init_db()

@app.get("/", tags=["health"])
def health(): return {"name":"GozIhale API","status":"development","live_data":False,"storage":"SQLite prototype"}

@app.get("/api/tenders", response_model=list[Tender], tags=["tenders"])
def list_tenders(q: str|None=None, category: str|None=None, city: str|None=None):
    sql="SELECT * FROM tenders WHERE 1=1"; args=[]
    if q: sql += " AND (title LIKE ? OR institution LIKE ? OR category LIKE ? OR summary LIKE ?)"; args += [f"%{q}%"]*4
    if category: sql += " AND category LIKE ?"; args.append(category)
    if city: sql += " AND city LIKE ?"; args.append(city)
    sql += " ORDER BY deadline IS NULL, deadline"
    with connect() as c: rows=c.execute(sql,args).fetchall()
    return [dict(r) for r in rows]

@app.get("/api/tenders/{tender_id}", response_model=Tender, tags=["tenders"])
def get_tender(tender_id: str):
    with connect() as c: row=c.execute("SELECT * FROM tenders WHERE id=?",(tender_id,)).fetchone()
    if not row: raise HTTPException(404,"Tender not found")
    return dict(row)

@app.post("/api/tenders", response_model=Tender, tags=["tenders"])
def add_tender(tender: Tender):
    with connect() as c:
        try: c.execute("INSERT INTO tenders VALUES (?,?,?,?,?,?,?,?,?,?)",tuple(tender.model_dump().values()))
        except sqlite3.IntegrityError: raise HTTPException(409,"Tender ID already exists")
    return tender

@app.get("/api/categories", tags=["tenders"])
def categories(): return ["OCT / OCT-A", "Fako cihazı", "Fako sarf", "Optik biyometri", "Topografi", "YAG / SLT", "Fundus kamera", "Göz mikroskobu", "Tonometre", "Görme alanı", "Refraktometre", "Lensmetre", "Mikroperimetri", "Diğer"]

@app.get("/api/analyze", tags=["intelligence"])
def analyze_notice(text: str): return relevance_score(text)


@app.get("/api/collected-notices", tags=["collection"])
def collected_notices(limit: int = 100):
    """List notices in the separate persistent ingestion prototype."""
    return list_collected_notices(limit)

@app.get("/api/collection-events", tags=["collection"])
def collection_events(limit: int = 100):
    """List new/updated notice ingestion events."""
    return list_ingestion_events(limit)

@app.post("/api/collect/record", tags=["collection"])
def record_collected_notice(payload: dict):
    """Persist an already collected/enriched candidate. This does not fetch websites."""
    if not payload.get("title") or not payload.get("institution") or not payload.get("source_name"):
        raise HTTPException(400, "title, institution and source_name are required")
    return ingest_collected_notice(payload)

from .collector.registry import list_sources
from .collector.scan_ledger import record_run, list_runs as list_scan_runs

@app.get("/api/sources", tags=["collection"])
def sources():
    """Configured source catalog; entries are not active scrapers."""
    return [{"key":s.key,"name":s.name,"group":s.source_group,"url":s.url,"official":s.official,"enabled":s.key in enabled_keys(),"notes":s.notes} for s in list_sources()]

@app.get("/api/scan-runs", tags=["collection"])
def scan_runs(limit: int = 100):
    return list_scan_runs(limit)

@app.post("/api/scan-catalog", tags=["collection"])
def scan_catalog():
    """Audit catalog entries and record adapter readiness; deliberately does not fetch sites."""
    result=[]
    for source in list_sources():
        status="disabled" if source.key not in enabled_keys() else "configured_check"
        message="Source not enabled; no request made." if source.key not in enabled_keys() else "Enabled source; adapter readiness checked separately."
        result.append(record_run(source,status,message,0))
    return {"live_collection":False,"message":"Catalog audit only; websites were not contacted.","runs":result}

from .collector.runner import run_source, enabled_keys

@app.post("/api/run-source/{source_key}", tags=["collection"])
def run_one_source(source_key: str):
    """Run a registered adapter if enabled and available; otherwise safely log readiness."""
    result=run_source(source_key)
    if result.get("status")=="unknown_source":
        raise HTTPException(404,"Unknown source key")
    return result


from .collector.municipal_targets import TARGETS as MUNICIPAL_TARGETS, MUNICIPAL_HEALTH_SEARCH_TERMS

@app.get("/api/municipal-targets", tags=["collection"])
def municipal_targets():
    """Return all metropolitan municipality targets for health-related procurement discovery."""
    return {"count": len(MUNICIPAL_TARGETS), "search_terms": MUNICIPAL_HEALTH_SEARCH_TERMS, "targets": MUNICIPAL_TARGETS}


from .collector.municipal_search_plan import build_search_plan

@app.get("/api/municipal-search-plan", tags=["collection"])
def municipal_search_plan(municipality: str | None = None):
    """Generate official-source discovery query plans; does not perform live searches."""
    plans = build_search_plan(municipality)
    if municipality and not plans:
        raise HTTPException(404, "Metropolitan municipality not found")
    return {"count": len(plans), "plans": plans}


from .collector.source_search_plan import build_source_query_plan

@app.get('/api/source-search-plan', tags=['collection'])
def source_search_plan():
    """Return source/keyword matrix for manual or future automated searches."""
    plan=build_source_query_plan()
    return {'count':len(plan),'plans':plan,'live_search':False}

@app.get("/api/priority-notices", tags=["collection"])
def priority_notices(limit: int = 50):
    """Convenience shortlist ordered by relevance and deadline presence."""
    rows=list_collected_notices(limit)
    rows.sort(key=lambda row: (
        -int(row.get("relevance_score") or 0),
        row.get("deadline") is None,
        row.get("deadline") or "9999-12-31",
        row.get("last_seen") or ""
    ))
    today_rows=[]
    for row in rows[:max(1,min(limit,200))]:
        enriched=dict(row)
        enriched["days_remaining"]=days_remaining(enriched.get("deadline"))
        enriched["urgency"]=urgency_label(enriched.get("deadline"))
        today_rows.append(enriched)
    return today_rows
