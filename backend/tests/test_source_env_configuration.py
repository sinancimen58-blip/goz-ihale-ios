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



def test_html_adapter_uses_registered_url_when_page_override_is_missing(monkeypatch):
    from app.collector import runner
    monkeypatch.setenv("GOZ_IHALE_ENABLED_SOURCE_KEYS", "khgm_central_notices")
    monkeypatch.setenv("GOZ_IHALE_HTML_SOURCE_KEYS", "khgm_central_notices")
    monkeypatch.delenv("GOZ_IHALE_HTML_PAGE_KHGM_CENTRAL_NOTICES", raising=False)
    captured = {}

    class FakeAdapter:
        def __init__(self, name, page_url, registered_host):
            captured.update(name=name, page_url=page_url, registered_host=registered_host)

    monkeypatch.setattr(runner, "OfficialHTMLAdapter", FakeAdapter)
    adapters = runner.configured_adapters()
    assert "khgm_central_notices" in adapters
    assert captured["page_url"] == "https://khgm.saglik.gov.tr/TR-119527/ihale-duyurulari.html"
    assert captured["registered_host"] == "khgm.saglik.gov.tr"
