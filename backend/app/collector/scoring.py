"""Conservative relevance scoring with explicit noise suppression and device specificity."""
from .keywords import classify_text, _normalize

PRIORITY_TERMS = [
    "doğrudan temin", "acil", "ivedi", "son teklif", "teklif tarihi",
    "son başvuru", "ihale tarihi", "deadline", "süre uzatımı", "zeyilname",
    "ek doküman", "doküman değişikliği", "iptal", "cancelled", "cancellation",
]
# Distinct equipment groups prevent several aliases for one device from inflating the score.
SPECIFICITY_GROUPS = {
    "OCT": ["oct", "oct-a", "optik koherens tomografi", "retina duo", "glauvas"],
    "Fako": ["fako", "phaco", "fakoemülsifikasyon", "phacoemulsification"],
    "Fako sarf": ["fako ucu", "fako uç", "fako kaset", "phaco cassette", "phaco tip", "phaco pack", "fako sarf"],
    "Optik biyometri": ["optik biyometri", "iol master", "al-scan", "aks uzunluğu", "optical biometry"],
    "Tonometri": ["tonometre", "tonometry", "non contact tonometer", "applanasyon tonometre"],
    "YAG / SLT": ["yag lazer", "slt lazer", "green laser", "532 nm laser"],
    "Fundus": ["fundus kamera", "fundus camera", "retinal camera", "göz dibi kamera"],
    "Mikroskop": ["oftalmik mikroskop", "operasyon mikroskobu", "ophthalmic microscope", "cerrahi mikroskop"],
    "Görme alanı": ["perimetre", "görme alanı", "visual field", "automated perimeter"],
    "Topografi": ["topografi", "kornea tomografi", "pentacam", "scheimpflug"],
    "Refraksiyon": ["refraktometre", "keratometre", "autorefractor", "refractometer", "refraktokeratometre"],
    "Lensmetre": ["lensmetre", "lens meter", "lensmeter", "focimeter"],
    "Yarık lamba": ["yarık lamba", "slit lamp", "biomicroscope", "biomikroskop"],
    "Mikroperimetri": ["mikroperimetri", "microperimetry", "micro perimeter"],
    "Aberrometre": ["aberometre", "aberrometer", "wavefront"],
    "Ultrason": ["a-scan", "b-scan", "ultrasonik biyometri", "ocular ultrasound"],
    "Retina cerrahisi": ["vitrektomi sarf", "vitrectomy consumables", "retina cerrahisi sarf"],
}
# Exclude obvious non-procurement clinical, educational and employment content.
NOISE_PHRASES = [
    "hasta randevu", "randevu sistemi", "hasta kabul", "poliklinik randevu",
    "personel alımı", "iş başvurusu", "kariyer ilan", "uzmanlık eğitimi",
    "asistan eğitimi", "kongre program", "bilimsel toplantı", "makale",
]

def relevance_score(text: str) -> dict:
    normalized = _normalize(text)
    categories = classify_text(text)
    noise_matches = [term for term in NOISE_PHRASES if _normalize(term) in normalized]
    priority_matches = [term for term in PRIORITY_TERMS if _normalize(term) in normalized]
    specificity_matches = [
        group for group, aliases in SPECIFICITY_GROUPS.items()
        if any(_normalize(alias) in normalized for alias in aliases)
    ]
    # Category coverage is the base score; explicit device matches improve confidence
    # without suppressing broad, potentially valid procurement notices.
    score = min(100, len(categories) * 18)
    score = min(100, score + min(30, len(specificity_matches) * 5))
    score = min(100, score + min(20, len(priority_matches) * 3))
    # Obvious non-purchasing notices are rejected even if medical keywords occur.
    relevant = bool(categories) and not noise_matches
    if noise_matches:
        score = 0
    return {
        "score": score, "categories": categories, "priority_terms": priority_matches,
        "specificity_matches": specificity_matches,
        "is_relevant": relevant, "noise_terms": noise_matches,
    }
