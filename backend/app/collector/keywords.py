"""Ophthalmology procurement keyword catalog used for relevance screening."""

KEYWORD_GROUPS = {
    "OCT": ["oct", "oct-a", "optik koherens tomografi", "retina duo", "glauvas"],
    "Fako": ["fako", "phaco", "fakoemülsifikasyon", "phacoemulsification"],
    "Fako sarf": ["fako sarf", "phaco consumable", "fako uç", "kaset", "tip"],
    "Biyometri": ["optik biyometri", "optical biometry", "iol master", "al-scan"],
    "Topografi": ["topografi", "tomografi", "kornea haritası", "corneal topography"],
    "YAG / SLT": ["yag lazer", "sl t", "slt", "yag laser", "green laser"],
    "Fundus": ["fundus kamera", "fundus camera", "retinal kamera"],
    "Mikroskop": ["oftalmik mikroskop", "operasyon mikroskobu", "ophthalmic microscope"],
    "Tonometri": ["tonometre", "tonometry", "göz tansiyonu"],
    "Görme alanı": ["perimetre", "görme alanı", "visual field"],
    "Refraksiyon": ["refraktometre", "keratometre", "autorefractor", "refractometer"],
    "Lensmetre": ["lensmetre", "lens meter", "lensmeter"],
    "Mikroperimetri": ["mikroperimetri", "microperimetry"],
}

ALL_KEYWORDS = sorted({term for terms in KEYWORD_GROUPS.values() for term in terms})

def classify_text(text: str) -> list[str]:
    normalized = text.casefold()
    return [category for category, terms in KEYWORD_GROUPS.items() if any(term.casefold() in normalized for term in terms)]


def is_relevant(text: str) -> bool:
    return bool(classify_text(text))
