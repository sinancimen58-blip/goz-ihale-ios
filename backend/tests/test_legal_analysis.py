from app.collector.legal_analysis import analyze_procurement_rules


def test_detects_open_tender_and_includes_cautious_deadline_note():
    result=analyze_procurement_rules("4734 açık ihale usulü")
    assert any("açık ihale" in item["label"].lower() for item in result["detected_methods"])
    assert result["time_limits"]["exact_days"] is None
    assert "hukuki görüş değildir" in result["disclaimer"]


def test_detects_direct_procurement():
    result=analyze_procurement_rules("22/d doğrudan temin")
    assert any(item["method_key"] == "22" for item in result["detected_methods"])


def test_unknown_method_returns_checklist():
    result=analyze_procurement_rules("İhale metni")
    assert result["detected_methods"] == []
    assert len(result["checklist"]) >= 5


def test_extracts_method_and_payment_with_evidence():
    from app.collector.term_extraction import extract_terms
    text="Açık ihale usulü. Fatura tesliminden sonra 90 gün içinde ödeme yapılacaktır."
    result=extract_terms(text)
    assert result["procurement_method"] is not None
    assert result["payment_terms"] is not None
    assert "90 gün" in result["payment_terms"]["evidence"]
    assert result["payment_terms"]["confidence"] < 1


def test_specification_review_flags_brand_and_equivalence():
    from app.collector.specification_review import analyze_specification
    result=analyze_specification("ZEISS model ve eşdeğer ürün; kurulum ve servis şartı")
    keys={flag["key"] for flag in result["flags"]}
    assert "brand_model" in keys
    assert "equivalence" in keys
    assert "delivery_service" in keys
    assert result["disclaimer"]
