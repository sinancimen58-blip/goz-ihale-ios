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

from types import SimpleNamespace
from app.collector import runner


def test_run_source_counts_ingestion_outcomes(monkeypatch):
    source = SimpleNamespace(key="ekap", name="EKAP", url="https://example.org")
    adapter = SimpleNamespace(collect=lambda: ["candidate-a", "candidate-b", "candidate-c"])
    monkeypatch.setattr(runner, "list_sources", lambda: [source])
    monkeypatch.setattr(runner, "enabled_keys", lambda: {"ekap"})
    monkeypatch.setattr(runner, "configured_adapters", lambda: {"ekap": adapter})
    monkeypatch.setattr(runner, "screen_many", lambda candidates: [
        {"title": str(c), "source_url": None} for c in candidates
    ])
    outcomes = iter([
        {"action": "new", "alert": True},
        {"action": "updated", "alert": False},
        {"action": "unchanged", "alert": True},
    ])
    monkeypatch.setattr(runner, "ingest", lambda record: next(outcomes))
    captured = {}
    monkeypatch.setattr(runner, "record_run", lambda s, status, message, count, metrics=None, source_url=None:
        captured.update(status=status, message=message, count=count, metrics=metrics) or captured)

    result = runner.run_source("ekap")
    assert result["status"] == "success"
    assert captured["count"] == 3
    assert "new: 1" in captured["message"]
    assert "updated: 1" in captured["message"]
    assert "unchanged: 1" in captured["message"]
    assert "alert candidates: 2" in captured["message"]


def test_run_source_unknown_key(monkeypatch):
    monkeypatch.setattr(runner, "list_sources", lambda: [])
    captured = {}
    monkeypatch.setattr(runner, "record_run", lambda s, status, message, count:
        captured.update(status=status, message=message, count=count) or captured)
    result = runner.run_source("unknown")
    assert result["status"] == "unknown_source"
    assert result["notices_saved"] == 0

import pytest
from app.collector.rss_adapter import _validate_feed_url


def test_feed_url_requires_https():
    with pytest.raises(ValueError):
        _validate_feed_url("http://example.org/feed")


def test_feed_url_rejects_credentials():
    with pytest.raises(ValueError):
        _validate_feed_url("https://user:pass@example.org/feed")


def test_feed_url_rejects_localhost():
    with pytest.raises(ValueError):
        _validate_feed_url("https://localhost/feed")


def test_feed_url_rejects_localhost_suffix():
    with pytest.raises(ValueError):
        _validate_feed_url("https://test.localhost/feed")

def test_feed_url_rejects_fragment():
    with pytest.raises(ValueError):
        _validate_feed_url("https://example.org/feed#fragment")


def test_feed_url_rejects_too_long():
    with pytest.raises(ValueError):
        _validate_feed_url("https://example.org/" + "a" * 2050)


def test_feed_url_rejects_private_resolution(monkeypatch):
    import socket
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))
    ])
    with pytest.raises(ValueError, match="non-public"):
        _validate_feed_url("https://example.org/feed")


def test_parser_rejects_oversized_content():
    from app.collector.rss_adapter import MAX_FEED_BYTES
    with pytest.raises(ValueError, match="size limit"):
        parse_feed(b"x" * (MAX_FEED_BYTES + 1), "Test", "https://example.org")


def test_parser_caps_items():
    from app.collector.rss_adapter import MAX_ITEMS
    xml = ("<rss><channel>" + "".join(
        f"<item><title>Notice {i}</title></item>" for i in range(MAX_ITEMS + 1)
    ) + "</channel></rss>").encode()
    assert len(parse_feed(xml, "Test", "https://example.org")) == MAX_ITEMS

from app.collector.keywords import classify_text


def test_classifier_recognizes_expanded_terms():
    assert "Yarık lamba" in classify_text("Slit lamp cihazı alımı")
    assert "Biyometri" in classify_text("optik biyometri ve aks uzunluğu ölçümü")
    assert "A-scan / B-scan" in classify_text("B scan ultrasonik cihaz")
    assert "Fako sarf" in classify_text("phaco cassette consumables")


def test_classifier_avoids_partial_word_false_positive():
    assert classify_text("tipografi kitap basımı") == []


def test_classifier_additional_procurement_terms():
    assert "Yarık lamba" in classify_text("Biomikroskop alımı")
    assert "Pakimetri" in classify_text("Pakimetri cihazı")
    assert "Pakimetri" in classify_text("Pachymetry equipment")
    assert "IOL / Göz içi lens" in classify_text("IOL ve intraocular lens")
    assert "Biyometri" in classify_text("Biometri cihazı")



def test_source_query_plan_contains_added_terms():
    from app.collector.source_search_plan import TERMS
    terms = {term.casefold() for term in TERMS}
    assert "biomikroskop" in terms
    assert "pakimetri" in terms
    assert "iol" in terms
    assert "göz içi lens" in terms


def test_classifier_glaucoma_and_surgery_consumables():
    from app.collector.keywords import classify_text
    assert "Glokom cihazları" in classify_text("RNFL glaucoma analysis device")
    assert "Göz cerrahisi sarf" in classify_text("Vitrektomi sarf malzemesi")

def test_source_plan_includes_glaucoma_and_retina_terms():
    from app.collector.source_search_plan import TERMS
    terms = {term.casefold() for term in TERMS}
    assert "glokom" in terms and "vitrektomi sarf" in terms


def test_scoring_detects_amendment_and_deadline_signals():
    from app.collector.scoring import relevance_score
    result = relevance_score("OCT cihazı ihalesi için zeyilname ve son başvuru tarihi")
    assert result["is_relevant"]
    assert "zeyilname" in result["priority_terms"]
    assert "son başvuru" in result["priority_terms"]
    assert result["score"] > 18

def test_priority_signal_alone_does_not_make_notice_relevant():
    from app.collector.scoring import relevance_score
    result = relevance_score("Acil yol bakım ihalesi")
    assert not result["is_relevant"]


def test_material_change_tracks_cancellation_and_amendment_fields():
    from app.collector.normalize import material_change
    old = {"status":"active", "specification":"OCT", "document_url":"https://x.test/a"}
    new = {"status":"cancelled", "specification":"OCT updated", "document_url":"https://x.test/b"}
    changed = material_change(old, new)
    assert "status" in changed and "specification" in changed and "document_url" in changed

def test_material_change_tracks_category_and_notice_identity():
    from app.collector.normalize import material_change
    changed = material_change({"category":"OCT", "notice_id":"1"}, {"category":"Fako", "notice_id":"2"})
    assert "category" in changed and "notice_id" in changed


def test_alerts_highlight_deadline_document_and_cancel_changes():
    from app.collector.alerts import decide_alert
    assert decide_alert("updated", ["document_url"]).priority == "high"
    assert decide_alert("updated", ["status"], text="iptal edilen ihale").priority == "high"
    assert decide_alert("updated", ["payment_terms"]).priority == "high"

def test_alerts_normalize_turkish_priority_terms():
    from app.collector.alerts import decide_alert
    assert decide_alert("updated", [], text="Zeyilname yayınlandı").priority == "high"

 
def test_notice_match_keys_has_title_institution_fallback():
    from app.collector.normalize import notice_match_keys
    keys = notice_match_keys({"title":"OCT alımı", "institution":"Hastane", "publication_date":"2026-11-27"})
    assert len(keys) == 2
    assert notice_match_keys({"title":"", "institution":"Hastane"}) == []


def test_ingestion_cross_source_duplicate_identity(monkeypatch, tmp_path):
    from app.collector import sqlite_repository as repo
    monkeypatch.setattr(repo, 'DB_PATH', str(tmp_path / 'ingestion.sqlite'))
    first = {'title':'OCT cihazı alımı','institution':'Örnek Hastane','publication_date':'2026-11-27','source_name':'Kaynak A','source_url':'https://a.test'}
    second = dict(first, source_name='Kaynak B', source_url='https://b.test', deadline='2026-12-15')
    one = repo.ingest(first)
    two = repo.ingest(second)
    assert one['action'] == 'new'
    assert two['action'] == 'updated'
    notices = repo.list_notices()
    assert len(notices) == 1
    assert notices[0]['deadline'] == '2026-12-15'
    events = repo.list_events(fingerprint=one['fingerprint'])
    assert len(events) == 2


def test_duplicate_identity_does_not_merge_different_dates(monkeypatch, tmp_path):
    from app.collector import sqlite_repository as repo
    monkeypatch.setattr(repo, 'DB_PATH', str(tmp_path / 'identity.sqlite'))
    first = {'title':'OCT cihazı alımı','institution':'Örnek Hastane','publication_date':'2026-11-27','source_name':'Kaynak A'}
    second = dict(first, publication_date='2026-12-02', source_name='Kaynak B')
    a = repo.ingest(first)
    b = repo.ingest(second)
    assert a['fingerprint'] != b['fingerprint']
    assert len(repo.list_notices()) == 2


def test_ingest_classifies_deadline_and_cancellation_events(monkeypatch, tmp_path):
    from app.collector import sqlite_repository as repo
    monkeypatch.setattr(repo, 'DB_PATH', str(tmp_path / 'events.sqlite'))
    base = {'title':'OCT cihazı alımı','institution':'Örnek Hastane','publication_date':'2026-11-27','source_name':'Kaynak','status':'active'}
    first=repo.ingest(base)
    cancelled=dict(base,status='cancelled',summary='İhale iptal edildi')
    repo.ingest(cancelled)
    events=repo.list_events(fingerprint=first['fingerprint'])
    assert events[0]['event_type']=='cancellation'


def test_ingest_classifies_deadline_extension(monkeypatch, tmp_path):
    from app.collector import sqlite_repository as repo
    monkeypatch.setattr(repo, 'DB_PATH', str(tmp_path / 'extension.sqlite'))
    base = {'title':'OCT cihazı alımı','institution':'Örnek Hastane','publication_date':'2026-11-27','source_name':'Kaynak','deadline':'2026-12-10'}
    first=repo.ingest(base)
    extended=dict(base,deadline='2026-12-20')
    repo.ingest(extended)
    events=repo.list_events(fingerprint=first['fingerprint'])
    assert events[0]['event_type']=='deadline_extension'


def test_alert_candidate_deduplicates_repeated_identical_change(monkeypatch, tmp_path):
    from app.collector import sqlite_repository as repo
    monkeypatch.setattr(repo, 'DB_PATH', str(tmp_path / 'alerts.sqlite'))
    base = {'title':'OCT cihazı alımı','institution':'Örnek Hastane','publication_date':'2026-11-27','source_name':'Kaynak','deadline':'2026-12-10'}
    repo.ingest(base)
    extended=dict(base,deadline='2026-12-20')
    first=repo.ingest(extended)
    assert first['alert']
    repo.ingest(base)
    repeated=repo.ingest(extended)
    assert not repeated['alert']
    assert 'bastırıldı' in repeated['alert_reason']


def test_event_payload_contains_old_new_and_changed_fields(monkeypatch, tmp_path):
    import json
    from app.collector import sqlite_repository as repo
    monkeypatch.setattr(repo, 'DB_PATH', str(tmp_path / 'event_payload.sqlite'))
    base={'title':'OCT cihazı alımı','institution':'Örnek Hastane','publication_date':'2026-11-27','source_name':'Kaynak','deadline':'2026-12-10'}
    first=repo.ingest(base)
    repo.ingest(dict(base,deadline='2026-12-20'))
    event=repo.list_events(fingerprint=first['fingerprint'])[0]
    payload=json.loads(event['payload_json'])
    assert payload['old']['deadline']=='2026-12-10'
    assert payload['new']['deadline']=='2026-12-20'
    assert 'deadline' in payload['changed_fields']
