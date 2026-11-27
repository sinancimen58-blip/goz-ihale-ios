"""Expanded ophthalmology procurement vocabulary with conservative phrase matching."""
import re
import unicodedata

KEYWORD_GROUPS = {
    "OCT": ["oct", "oct-a", "optik koherens tomografi", "optical coherence tomography", "retina duo", "glauvas", "spectral domain oct", "swept source oct"],
    "Fako": ["fako", "phaco", "fakoemülsifikasyon", "phacoemulsification", "phaco cihaz"],
    "Fako sarf": ["fako sarf", "phaco consumable", "fako ucu", "fako uç", "fako kaset", "phaco cassette", "phaco tip", "phaco pack"],
    "Biyometri": ["optik biyometri", "optical biometry", "iol master", "al-scan", "aks uzunluğu", "axial length", "biometri", "biyometri cihazı"],
    "Pakimetri": ["pakimetri", "pachymetry", "pachymeter", "kornea kalınlık ölçümü", "corneal thickness"],
    "IOL / Göz içi lens": ["iol", "göz içi lens", "intraoküler lens", "intraocular lens", "intraocular lenses", "göz içi mercek", "lens implant", "iç göz lens"],
    "Topografi": ["topografi", "kornea haritası", "corneal topography", "korneal topografi", "kornea tomografi", "pentacam", "scheimpflug"],
    "YAG / SLT": ["yag lazer", "slt lazer", "slt", "yag laser", "green laser", "532 nm laser"],
    "Fundus": ["fundus kamera", "fundus camera", "retinal kamera", "retinal imaging", "göz dibi kamera"],
    "Mikroskop": ["oftalmik mikroskop", "operasyon mikroskobu", "ophthalmic microscope", "cerrahi mikroskop"],
    "Tonometri": ["tonometre", "tonometry", "göz tansiyonu ölçüm", "non contact tonometer", "applanasyon tonometre", "tonometer"],
    "Görme alanı": ["perimetre", "görme alanı", "visual field", "automated perimeter"],
    "Refraksiyon": ["refraktometre", "keratometre", "autorefractor", "refractometer", "refraktokeratometre"],
    "Lensmetre": ["lensmetre", "lens meter", "lensmeter", "focimeter"],
    "Mikroperimetri": ["mikroperimetri", "microperimetry", "micro perimeter"],
    "Yarık lamba": ["yarık lamba", "slit lamp", "biomicroscope", "biomikroskop"],
    "Aberrometre": ["aberometre", "aberrometer", "wavefront"],
    "Muayene ünitesi": ["oftalmik muayene ünitesi", "ophthalmic examination unit", "göz muayene ünitesi", "göz poliklinik sistemi"],
    "A-scan / B-scan": ["a scan", "a-scan", "b scan", "b-scan", "ultrasonik biyometri", "ocular ultrasound"],
    "Glokom cihazları": ["glokom", "glaucoma", "glokom analiz", "glaucoma analyzer", "oct glokom", "optik disk", "rnfl", "ganglion cell analysis", "göz tansiyonu"],
    "Göz cerrahisi sarf": ["oftalmik sarf", "göz cerrahisi sarf", "intraoküler", "göz cerrahi sarf malzeme", "vitrektomi sarf", "vitrectomy consumables", "retina cerrahisi sarf", "katarakt cerrahi sarf"],
}

def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").casefold()
    text = re.sub(r"[^\w]+", " ", text, flags=re.UNICODE)
    return " " + re.sub(r"\s+", " ", text).strip() + " "

def _contains(normalized: str, term: str) -> bool:
    term_norm = _normalize(term)
    return term_norm in normalized

ALL_KEYWORDS = sorted({term for terms in KEYWORD_GROUPS.values() for term in terms})

def classify_text(text: str) -> list[str]:
    normalized = _normalize(text)
    return [category for category, terms in KEYWORD_GROUPS.items() if any(_contains(normalized, term) for term in terms)]

def is_relevant(text: str) -> bool:
    return bool(classify_text(text))
