from app.collector.municipal_targets import METROPOLITAN_MUNICIPALITIES, TARGETS, MUNICIPAL_HEALTH_SEARCH_TERMS

def test_all_30_metropolitan_municipalities_present():
    assert len(METROPOLITAN_MUNICIPALITIES) == 30
    assert len(TARGETS) == 30
    assert "Kayseri" in METROPOLITAN_MUNICIPALITIES
    assert "İstanbul" in METROPOLITAN_MUNICIPALITIES

def test_search_terms_include_ophthalmology():
    terms = {term.casefold() for term in MUNICIPAL_HEALTH_SEARCH_TERMS}
    assert {"oct", "fako", "tonometre", "optik biyometri", "göz"} <= terms

def test_targets_require_source_verification():
    assert all(target["verification_required"] for target in TARGETS)
