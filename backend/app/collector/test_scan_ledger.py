"""Tests for scan ledger endpoint provenance and URL redaction."""
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from app.collector import scan_ledger

def test_record_run_stores_actual_endpoint_and_redacts_sensitive_query(monkeypatch,tmp_path):
    monkeypatch.setattr(scan_ledger,"DB_PATH",str(tmp_path/"scan.db"))
    source=SimpleNamespace(key="example",name="Example",url="https://example.gov.tr/")
    actual="https://example.gov.tr/feed?token=secret-value&category=medical&api_key=hidden"
    row=scan_ledger.record_run(source,status="success",message="ok",notices_found=2,
                               metrics={"fetched_count":3},source_url=actual)
    assert row["source_url"].startswith("https://example.gov.tr/feed?")
    query=parse_qs(urlparse(row["source_url"]).query)
    assert query["token"]==["[redacted]"]
    assert query["api_key"]==["[redacted]"]
    assert query["category"]==["medical"]
    assert row["fetched_count"]==3

def test_record_run_defaults_to_registered_source_url(monkeypatch,tmp_path):
    monkeypatch.setattr(scan_ledger,"DB_PATH",str(tmp_path/"scan.db"))
    source=SimpleNamespace(key="example",name="Example",url="https://example.gov.tr/notices")
    row=scan_ledger.record_run(source,status="disabled")
    assert row["source_url"]==source.url
