from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import Tender
from .collector.scoring import relevance_score

app = FastAPI(title="GozIhale API", version="0.1.0", description="Ophthalmology procurement intelligence API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SAMPLE_TENDERS = [
    Tender(id="demo-001", title="OCT cihazı alımı (örnek)", institution="Demo Üniversite Hastanesi", city="Ankara", category="OCT", deadline=None, source_name="Demo", source_url=None, summary="Demo kayıt; gerçek ilan değildir.", status="demo"),
    Tender(id="demo-002", title="Fako cihazı ve sarf (örnek)", institution="Demo Şehir Hastanesi", city="İstanbul", category="Fako", deadline=None, source_name="Demo", source_url=None, summary="Demo kayıt; gerçek ilan değildir.", status="demo"),
]

@app.get("/", tags=["health"])
def health():
    return {"name": "GozIhale API", "status": "development", "live_data": False}

@app.get("/api/tenders", response_model=list[Tender], tags=["tenders"])
def list_tenders(q: str | None = None, category: str | None = None, city: str | None = None):
    results = SAMPLE_TENDERS
    if q:
        results = [t for t in results if q.lower() in (t.title + " " + t.institution + " " + t.category).lower()]
    if category:
        results = [t for t in results if t.category.lower() == category.lower()]
    if city:
        results = [t for t in results if t.city.lower() == city.lower()]
    return results

@app.get("/api/categories", tags=["tenders"])
def categories():
    return ["OCT / OCT-A", "Fako cihazı", "Fako sarf", "Optik biyometri", "Topografi", "YAG / SLT", "Fundus kamera", "Göz mikroskobu", "Tonometre", "Görme alanı", "Refraktometre", "Lensmetre", "Mikroperimetri", "Diğer"]

@app.get("/api/analyze", tags=["intelligence"])
def analyze_notice(text: str):
    """Analyze pasted notice text; does not fetch external pages."""
    return relevance_score(text)
