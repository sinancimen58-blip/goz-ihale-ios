"""Tests for bounded retry behavior of read-only collection."""
from urllib.error import HTTPError
from app.collector import runner

class _SequenceAdapter:
    def __init__(self, sequence):
        self.sequence=list(sequence)
        self.calls=0
    def collect(self):
        self.calls+=1
        item=self.sequence.pop(0)
        if isinstance(item,Exception):
            raise item
        return item

def _http_error(code):
    return HTTPError("https://example.gov.tr/feed",code,"HTTP error",None,None)

def test_retries_transient_timeout_and_http_503(monkeypatch):
    delays=[]
    monkeypatch.setattr(runner.time,"sleep",delays.append)
    adapter=_SequenceAdapter([TimeoutError("timeout"),_http_error(503),["candidate"]])
    result,retries=runner.collect_with_retries(adapter)
    assert result==["candidate"]
    assert retries==2
    assert adapter.calls==3
    assert delays==list(runner.RETRY_DELAYS_SECONDS)

def test_non_retryable_error_is_not_retried(monkeypatch):
    delays=[]
    monkeypatch.setattr(runner.time,"sleep",delays.append)
    adapter=_SequenceAdapter([ValueError("invalid page"),["unused"]])
    try:
        runner.collect_with_retries(adapter)
    except ValueError as exc:
        assert exc.retry_count==0
    else:
        raise AssertionError("ValueError should be propagated")
    assert adapter.calls==1
    assert delays==[]

def test_retryable_error_exhaustion_reports_retry_count(monkeypatch):
    delays=[]
    monkeypatch.setattr(runner.time,"sleep",delays.append)
    adapter=_SequenceAdapter([TimeoutError("1"),TimeoutError("2"),TimeoutError("3")])
    try:
        runner.collect_with_retries(adapter)
    except TimeoutError as exc:
        assert exc.retry_count==2
    else:
        raise AssertionError("TimeoutError should be propagated after retry cap")
    assert adapter.calls==3
    assert delays==list(runner.RETRY_DELAYS_SECONDS)
