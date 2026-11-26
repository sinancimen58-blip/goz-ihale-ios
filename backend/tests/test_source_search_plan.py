from app.collector.source_search_plan import build_source_query_plan

def test_plan_includes_key_terms():
    terms={row["term"] for row in build_source_query_plan()}
    assert "OCT" in terms
    assert "optik biyometri" in terms
    assert "fako" in terms
    assert "YAG lazer" in terms

def test_all_plan_items_require_verification():
    plan=build_source_query_plan()
    assert plan
    assert all(row["verification"]=="original_notice_required" for row in plan)
