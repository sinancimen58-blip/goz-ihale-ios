"""Municipal discovery query builder (metadata-only; no network requests)."""
from .municipal_targets import METROPOLITAN_MUNICIPALITIES, MUNICIPAL_HEALTH_SEARCH_TERMS

def build_search_plan(municipality: str | None = None):
    cities = METROPOLITAN_MUNICIPALITIES
    if municipality:
        cities = [city for city in cities if city.casefold() == municipality.casefold()]
    return [
        {
            "municipality": city,
            "institution_query": f"{city} Büyükşehir Belediyesi",
            "source_scope": ["EKAP", "official_municipal_procurement"],
            "search_queries": [
                f'{city} Büyükşehir Belediyesi "{term}"' for term in MUNICIPAL_HEALTH_SEARCH_TERMS
            ],
            "verification": "Verify each candidate at the original publisher before treating it as a notice.",
            "live_search_enabled": False,
        }
        for city in cities
    ]
