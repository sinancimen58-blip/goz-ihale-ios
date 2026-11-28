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


def test_payment_and_method_persist_and_trigger_update(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    notice=sample(); notice["procurement_method"]="Açık ihale"; notice["payment_terms"]="90 gün"
    repo.ingest(notice)
    row=repo.list_notices()[0]
    assert row["procurement_method"] == "Açık ihale"
    assert row["payment_terms"] == "90 gün"
    updated=sample(); updated["procurement_method"]="21/b"; updated["payment_terms"]="120 gün"
    result=repo.ingest(updated)
    assert result["action"] == "updated"
    assert "procurement_method" in result["changed_fields"]
    assert "payment_terms" in result["changed_fields"]

def test_alert_outbox_persists_and_deduplicates(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    first=repo.ingest(sample())
    second=repo.ingest(sample())
    pending=repo.list_pending_alerts()
    assert first["alert"] and not second["alert"]
    assert len(pending)==1
    assert pending[0]["payload"]["title"]=="OCT cihazı alımı"
    repo.mark_alert_delivery(pending[0]["alert_key"],True)
    assert repo.notification_counts()["sent"]==1
    assert repo.list_pending_alerts()==[]

def test_outbox_failure_retries_then_stops(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    repo.ingest(sample())
    item=repo.list_pending_alerts()[0]
    for _ in range(8):
        repo.mark_alert_delivery(item["alert_key"],False,"test failure")
    assert repo.list_pending_alerts()==[]
    assert repo.notification_counts()["failed"]==1


def test_outbox_failure_schedules_backoff_and_excludes_not_due_alert(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    repo.ingest(sample())
    item=repo.list_pending_alerts()[0]
    repo.mark_alert_delivery(item["alert_key"],False,"temporary failure")
    assert repo.list_pending_alerts()==[]
    with repo.connection() as db:
        db.execute("UPDATE alert_outbox SET next_attempt_at=datetime('now', '-1 minute') WHERE alert_key=?",(item["alert_key"],))
    assert len(repo.list_pending_alerts())==1
    assert repo.retry_delay_seconds(0)==60
    assert repo.retry_delay_seconds(5)==1920
    assert repo.retry_delay_seconds(8)==3600


def test_outbox_claim_is_atomic_and_stale_lease_recovers(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    repo.ingest(sample())
    first=repo.claim_pending_alerts()
    assert len(first)==1
    assert first[0]["payload"]["title"]=="OCT cihazı alımı"
    assert repo.claim_pending_alerts()==[]
    with repo.connection() as db:
        db.execute("UPDATE alert_outbox SET claimed_at=datetime('now', '-11 minutes') WHERE alert_key=?",(first[0]["alert_key"],))
    recovered=repo.claim_pending_alerts()
    assert len(recovered)==1
    assert recovered[0]["alert_key"]==first[0]["alert_key"]
    repo.mark_alert_delivery(recovered[0]["alert_key"],True)
    assert repo.notification_counts()["sent"]==1
    assert repo.notification_counts()["sending"]==0
