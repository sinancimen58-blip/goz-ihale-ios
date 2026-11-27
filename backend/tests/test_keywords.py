from app.collector.keywords import classify_text, is_relevant

def test_oct_classification():
    assert "OCT" in classify_text("Retina OCT cihazı satın alma")

def test_phaco_classification():
    assert "Fako" in classify_text("Phacoemulsification system")

def test_unrelated_text():
    assert not is_relevant("Office chair and desk procurement")


def test_eye_clinic_system_procurement_classifies_as_ophthalmic():
    assert "Muayene ünitesi" in classify_text("İhale İlanı: Göz Poliklinik Sistemi Alımı")
    assert is_relevant("İhale İlanı: Göz Poliklinik Sistemi Alımı")
