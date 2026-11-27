from urllib.error import HTTPError
from app.collector import runner
from app.collector.runner import run_source

def test_unknown_source_does_not_fetch():
    result=run_source("not-in-registry")
    assert result["status"]=="unknown_source"

def test_registry_source_without_adapter_does_not_fetch():
    result=run_source("ekap")
    assert result["status"] in {"disabled","adapter_missing_or_invalid"}
    assert result["notices_found"]==0

def _patch_run(monkeypatch,adapter,recorded):
    monkeypatch.setenv("GOZ_IHALE_ENABLED_SOURCE_KEYS","ekap")
    monkeypatch.setattr(runner,"configured_adapters",lambda:{"ekap":adapter})
    monkeypatch.setattr(runner,"screen_many",lambda candidates: [])
    monkeypatch.setattr(runner,"record_run",lambda source,status,message,notices_found,metrics=None:
                        recorded.update(status=status,message=message,metrics=metrics) or recorded)
    monkeypatch.setattr(runner.time,"sleep",lambda delay: None)

def test_collect_retries_transient_errors_and_records_retry_count(monkeypatch):
    recorded={}
    class Adapter:
        calls=0
        def collect(self):
            self.calls+=1
            if self.calls==1:
                raise TimeoutError("temporary timeout")
            if self.calls==2:
                raise HTTPError("https://example.invalid/feed",503,"Unavailable",None,None)
            return []
    adapter=Adapter()
    _patch_run(monkeypatch,adapter,recorded)
    result=run_source("ekap")
    assert result["status"]=="success_empty"
    assert adapter.calls==3
    assert result["metrics"]["retry_count"]==2
    assert "retries: 2" in result["message"]

def test_nontransient_error_is_not_retried(monkeypatch):
    recorded={}
    class Adapter:
        calls=0
        def collect(self):
            self.calls+=1
            raise HTTPError("https://example.invalid/feed",403,"Forbidden",None,None)
    adapter=Adapter()
    _patch_run(monkeypatch,adapter,recorded)
    result=run_source("ekap")
    assert result["status"]=="error"
    assert adapter.calls==1
    assert result["metrics"]["retry_count"]==0

def test_retry_exhaustion_records_attempt_count(monkeypatch):
    recorded={}
    class Adapter:
        calls=0
        def collect(self):
            self.calls+=1
            raise TimeoutError("temporary timeout")
    adapter=Adapter()
    _patch_run(monkeypatch,adapter,recorded)
    result=run_source("ekap")
    assert result["status"]=="error"
    assert adapter.calls==3
    assert result["metrics"]["retry_count"]==2
