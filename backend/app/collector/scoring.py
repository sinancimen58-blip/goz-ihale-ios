from .keywords import classify_text

PRIORITY_TERMS = ["doğrudan temin", "acil", "ivedi", "son teklif", "teklif tarihi"]

def relevance_score(text: str) -> dict:
    categories = classify_text(text)
    normalized = text.casefold()
    score = min(100, len(categories) * 18)
    priority_matches = [term for term in PRIORITY_TERMS if term in normalized]
    score = min(100, score + min(10, len(priority_matches) * 2))
    return {"score": score, "categories": categories, "priority_terms": priority_matches, "is_relevant": bool(categories)}
