import json
from app.collector import sqlite_repository as repo

def setup(tmp_path, monkeypatch):
    monkeypatch.setattr(repo, "DB_PATH", str(tmp_path / "ingest.sqlite"))
    repo.initialize()

def sample():
    return {
        "title":"OCT cihazı alımı", "institution":"Test Üniversitesi",
        "notice_id":"K-100", "source_name":"Test kaynak",
        "source_url":"https://example.invalid/100", "category":"OCT",
        "deadline":"2026-12-20", "status":"new", "relevance_score":90,
        "specification":"64 kesit", "summary":"Test notice"
    }

def test_persist_new_then_unchanged(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    first=repo.ingest(sample())
    second=repo.ingest(sample())
    assert first["action"] == "new" and first["alert"]
    assert second["action"] == "unchanged" and not second["alert"]
    assert len(repo.list_notices()) == 1
    assert len(repo.list_events()) == 1

def test_material_update_creates_event(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    repo.ingest(sample())
    changed=sample(); changed["specification"]="Yeni şartname"
    result=repo.ingest(changed)
    assert result["action"] == "updated"
    assert "specification" in result["changed_fields"]
    assert result["alert"]
    assert len(repo.list_events()) == 2

def test_different_notice_id_is_distinct(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    repo.ingest(sample())
    other=sample(); other["notice_id"]="K-101"; other["title"]="Fako cihazı"
    assert repo.ingest(other)["action"] == "new"
    assert len(repo.list_notices()) == 2
