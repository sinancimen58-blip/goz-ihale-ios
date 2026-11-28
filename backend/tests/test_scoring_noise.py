from app.collector.scoring import relevance_score

def test_ophthalmology_procurement_relevant():
    result=relevance_score("OCT cihazı satın alma ihalesi")
    assert result["is_relevant"]
    assert "OCT" in result["categories"]

def test_appointment_noise_suppressed():
    result=relevance_score("Göz polikliniği hasta randevu sistemi ve OCT ölçümü")
    assert not result["is_relevant"]
    assert result["score"] == 0

def test_personnel_noise_suppressed():
    result=relevance_score("Oftalmoloji uzman personel alımı iş başvurusu")
    assert not result["is_relevant"]


def test_multi_category_notice_scores_higher_than_single_category():
    single = relevance_score("OCT cihazı satın alma")
    multi = relevance_score("OCT ve optik biyometri cihazı satın alma")
    assert single["is_relevant"] and multi["is_relevant"]
    assert len(multi["categories"]) > len(single["categories"])
    assert multi["score"] > single["score"]


def test_deadline_and_amendment_terms_raise_priority_score():
    base = relevance_score("Tonometre cihazı satın alma")
    urgent = relevance_score("Tonometre cihazı satın alma son teklif tarihi zeyilname")
    assert urgent["score"] >= base["score"]
    assert urgent["priority_terms"]


def test_noise_phrases_do_not_override_procurement_categories_silently():
    rejected = relevance_score("OCT cihazı poliklinik randevu sistemi")
    assert not rejected["is_relevant"]
    assert rejected["noise_terms"]


def test_score_is_bounded():
    result = relevance_score("OCT fako tonometre optik biyometri YAG SLT topografi fundus mikroskop ihale zeyilname")
    assert 0 <= result["score"] <= 100


def test_specific_device_matches_raise_score_and_are_grouped():
    broad = relevance_score("Göz poliklinik sistemi alımı")
    specific = relevance_score("OCT cihazı alımı")
    aliases = relevance_score("OCT-A OCT retina duo alımı")
    assert broad["is_relevant"] and specific["is_relevant"]
    assert specific["score"] > broad["score"]
    assert aliases["specificity_matches"].count("OCT") == 1
