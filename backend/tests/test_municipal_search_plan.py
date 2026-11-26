from app.collector.municipal_search_plan import build_search_plan

def test_plan_for_all_municipalities():
    plans = build_search_plan()
    assert len(plans) == 30
    assert all("EKAP" in plan["source_scope"] for plan in plans)

def test_plan_for_one_municipality():
    plans = build_search_plan("Kayseri")
    assert len(plans) == 1
    assert plans[0]["municipality"] == "Kayseri"
    assert any("OCT" in query for query in plans[0]["search_queries"])

def test_unknown_city_plan_empty():
    assert build_search_plan("Not a city") == []

def test_queries_are_not_live_search_claims():
    assert all(plan["live_search_enabled"] is False for plan in build_search_plan())
