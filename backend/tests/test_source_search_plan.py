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
\n\ndef test_query_plan_targets_added_procurement_entities():\n    plan=build_source_query_plan()\n    targets={target for row in plan for target in row["source_targets"]}\n    assert {"USHAŞ", "Türk Kızılay", "TİKA", "KHGM Merkezi Satın Alma", "İl Sağlık Müdürlükleri"} <= targets\n