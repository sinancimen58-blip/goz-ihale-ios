from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import Tender
from .collector.scoring import relevance_score
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
