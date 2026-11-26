import os
from app.collector.runner import enabled_keys, run_source

def test_source_enablement_requires_explicit_allowlist(monkeypatch):
    monkeypatch.delenv("GOZ_IHALE_ENABLED_SOURCE_KEYS", raising=False)
    assert enabled_keys() == set()
    result = run_source("ekap")
    assert result["status"] == "disabled"

def test_enabled_source_without_feed_is_not_contacted(monkeypatch):
    monkeypatch.setenv("GOZ_IHALE_ENABLED_SOURCE_KEYS", "ekap")
    monkeypatch.delenv("GOZ_IHALE_FEED_EKAP", raising=False)
    result = run_source("ekap")
    assert result["status"] == "adapter_missing_or_invalid"
    assert result["notices_found"] == 0
