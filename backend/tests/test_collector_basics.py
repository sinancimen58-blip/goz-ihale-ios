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
    monkeypatch.setattr(runner, "record_run", lambda s, status, message, count:
        captured.update(status=status, message=message, count=count) or captured)

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
