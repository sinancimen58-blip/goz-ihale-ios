"""Screen, categorize and score procurement notice candidates."""
from .scoring import relevance_score

def screen_candidate(candidate) -> dict | None:
    """Enrich a candidate with fields expected by persistent storage."""
    text = candidate.searchable_text
    result = relevance_score(text)
    if not result["is_relevant"]:
        return None
    categories = result["categories"]
    deadline = getattr(candidate, "deadline", None)
    return {
        "title": candidate.title.strip(),
        "institution": candidate.institution.strip(),
        "source_name": candidate.source_name.strip(),
        "source_url": getattr(candidate, "source_url", None),
        "city": getattr(candidate, "city", None),
        "publication_date": getattr(candidate, "publication_date", None),
        "deadline": deadline.isoformat() if deadline else None,
        "summary": getattr(candidate, "description", None),
        "category": ", ".join(categories) if categories else "Diğer",
        "categories": categories,
        "relevance_score": result["score"],
        "priority_terms": result["priority_terms"],
        "status": "new",
    }

def screen_many(candidates) -> list[dict]:
    """Screen iterable candidates, excluding unrelated notices."""
    screened=[]
    for candidate in candidates:
        record=screen_candidate(candidate)
        if record is not None:
            screened.append(record)
    return screened
