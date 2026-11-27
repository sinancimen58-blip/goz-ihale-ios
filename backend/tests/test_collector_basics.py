from app.collector.rss_adapter import parse_feed
from app.collector.filtering import screen_candidate
from app.collector.models import NoticeCandidate
from app.collector.normalize import fingerprint_notice, material_change

def test_parse_rss_items():
    xml=b'<rss><channel><item><title>OCT cihaz alimi</title><link>https://example.org/1</link><description>Optik OCT</description></item></channel></rss>'
    result=parse_feed(xml,"Test","https://example.org/feed")
    assert len(result)==1
    assert result[0].title=="OCT cihaz alimi"
    assert result[0].source_url=="https://example.org/1"

def test_parse_atom_entry():
    xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Tonometre</title><link href="https://example.org/a"/></entry></feed>'
    result=parse_feed(xml,"Test","https://example.org/feed")
    assert len(result)==1
    assert result[0].source_url=="https://example.org/a"

def test_irrelevant_notice_filtered():
    candidate=NoticeCandidate("Yol yapim","Belediye","Test","https://example.org")
    assert screen_candidate(candidate) is None

def test_relevant_notice_enriched():
    candidate=NoticeCandidate("OCT cihazı alımı","Hastane","Test","https://example.org")
    result=screen_candidate(candidate)
    assert result and "OCT" in result["category"]

def test_fingerprint_stable_normalized():
    assert fingerprint_notice("OCT alımı","Hastane") == fingerprint_notice(" oct ALIMI "," hastane ")

def test_material_change_detects_deadline():
    assert "deadline" in material_change({"deadline":"2026-12-01"},{"deadline":"2026-12-02"})
