from app.collector.institution_targets import (
    UNIVERSITY_HOSPITAL_TARGETS, CITY_HOSPITAL_TARGETS, OPHTHALMOLOGY_TERMS,
    build_institution_search_plan
)

def test_institution_targets_cover_priority_groups():
    assert any("Üniversitesi" in x for x in UNIVERSITY_HOSPITAL_TARGETS)
    assert any("Şehir Hastanesi" in x for x in CITY_HOSPITAL_TARGETS)
    assert "OCT" in OPHTHALMOLOGY_TERMS
    assert "fako" in OPHTHALMOLOGY_TERMS

def test_plan_requires_original_verification_and_not_live_claim():
    plan=build_institution_search_plan(["Test Üniversitesi Hastanesi"])
    assert plan[0]["institution"] == "Test Üniversitesi Hastanesi"
    assert plan[0]["verification"] == "verify_original_source_and_notice"
    assert plan[0]["live_search_enabled"] is False
    assert len(plan[0]["queries"]) > 10
