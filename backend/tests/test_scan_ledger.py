import sqlite3
from types import SimpleNamespace
from app.collector import scan_ledger

def test_ledger_migrates_retry_metric_and_persists_it(tmp_path,monkeypatch):
    path=tmp_path/"scan.db"
    monkeypatch.setattr(scan_ledger,"DB_PATH",str(path))
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE scan_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source_key TEXT NOT NULL,
            source_name TEXT NOT NULL, source_url TEXT NOT NULL,
            status TEXT NOT NULL, message TEXT, notices_found INTEGER NOT NULL DEFAULT 0,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP, finished_at TEXT)""")
    scan_ledger.initialize()
    source=SimpleNamespace(key="ekap",name="EKAP",url="https://example.org")
    row=scan_ledger.record_run(source,"success","test",0,{"retry_count":2})
    assert row["retry_count"]==2
    assert "retry_count" in {r[1] for r in sqlite3.connect(path).execute("PRAGMA table_info(scan_runs)")}

def test_safe_source_url_redacts_common_credential_variants_and_preserves_safe_parts():
    url="https://user:pass@example.org:8443/feed?client_secret=abc&x-api-key=def&auth_token=ghi&keyword=OCT#private"
    safe=scan_ledger.safe_source_url(url)
    assert safe=="https://example.org:8443/feed?client_secret=%5Bredacted%5D&x-api-key=%5Bredacted%5D&auth_token=%5Bredacted%5D&keyword=OCT"


def test_safe_source_url_handles_ipv6_and_key_variants():
    safe=scan_ledger.safe_source_url("https://[2001:4860:4860::8888]/feed?access-token=abc&search=OCT")
    assert safe=="https://[2001:4860:4860::8888]/feed?access-token=%5Bredacted%5D&search=OCT"
