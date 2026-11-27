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
