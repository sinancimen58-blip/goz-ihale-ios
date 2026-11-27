"""Conservative relevance scoring with explicit noise suppression."""
from .keywords import classify_text, _normalize

PRIORITY_TERMS = [
    "doğrudan temin", "acil", "ivedi", "son teklif", "teklif tarihi",
    "son başvuru", "ihale tarihi", "deadline", "süre uzatımı", "zeyilname",
    "ek doküman", "doküman değişikliği", "iptal", "cancelled", "cancellation",
]
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
    score = min(100, len(categories) * 18)
    score = min(100, score + min(20, len(priority_matches) * 3))
    # Obvious non-purchasing notices are rejected even if medical keywords occur.
    relevant = bool(categories) and not noise_matches
    if noise_matches:
        score = 0
    return {
        "score": score, "categories": categories, "priority_terms": priority_matches,
        "is_relevant": relevant, "noise_terms": noise_matches,
    }
