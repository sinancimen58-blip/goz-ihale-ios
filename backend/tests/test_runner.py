from app.collector.runner import run_source

def test_unknown_source_does_not_fetch():
    result=run_source("not-in-registry")
    assert result["status"]=="unknown_source"

def test_registry_source_without_adapter_does_not_fetch():
    result=run_source("ekap")
    assert result["status"] in {"disabled","adapter_missing"}
    assert result["notices_found"]==0
