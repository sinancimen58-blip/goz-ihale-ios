"""Conservative relevance scoring and urgency signal extraction."""
from .keywords import classify_text, _normalize

PRIORITY_TERMS = [
    "doğrudan temin", "acil", "ivedi", "son teklif", "teklif tarihi",
    "son başvuru", "ihale tarihi", "deadline", "süre uzatımı", "zeyilname",
    "ek doküman", "doküman değişikliği", "iptal", "cancelled", "cancellation",
]


def relevance_score(text: str) -> dict:
    categories = classify_text(text)
    normalized = _normalize(text)
    priority_matches = [term for term in PRIORITY_TERMS if _normalize(term) in normalized]
    score = min(100, len(categories) * 18)
    # Deadline/amendment signals increase attention but never determine relevance alone.
    score = min(100, score + min(20, len(priority_matches) * 3))
    return {"score": score, "categories": categories, "priority_terms": priority_matches, "is_relevant": bool(categories)}
