from app.collector.normalize import fingerprint_notice, material_change
from app.collector.pipeline import NoticeStore

def test_notice_id_fingerprint_stable():
    assert fingerprint_notice("x", "h", notice_id="ABC-1") == fingerprint_notice("y", "z", notice_id="abc-1")

def test_fallback_fingerprint():
    assert fingerprint_notice(" OCT Alımı ", "Hastane", "2026-01-01") == fingerprint_notice("oct alımı", "hastane", "2026-01-01")

def test_material_changes_only_tracked_fields():
    assert material_change({"deadline":"1","notes":"a"}, {"deadline":"2","notes":"b"}) == ["deadline"]

def test_ingest_new_then_unchanged_then_update():
    store=NoticeStore()
    item={"title":"OCT alımı", "institution":"Hastane", "notice_id":"123", "deadline":"2026-12-01"}
    assert store.ingest(item).action == "new"
    assert store.ingest(item).action == "unchanged"
    changed=dict(item, deadline="2026-12-05")
    result=store.ingest(changed)
    assert result.action == "updated" and result.changed_fields == ["deadline"]
