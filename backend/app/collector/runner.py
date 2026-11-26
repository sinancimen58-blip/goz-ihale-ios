"""Controlled source runner. No adapter means no network request is made."""
from .registry import list_sources
from .scan_ledger import record_run
from .filtering import screen_many
from .sqlite_repository import ingest
from .models import NoticeCandidate

ADAPTERS = {}  # source_key -> verified SourceAdapter instance; populate only after review.

def run_source(source_key: str):
    sources={s.key:s for s in list_sources()}
    source=sources.get(source_key)
    if source is None:
        return {"source_key":source_key,"status":"unknown_source","notices_saved":0}
    adapter=ADAPTERS.get(source_key)
    if not source.enabled or adapter is None:
        status="disabled" if not source.enabled else "adapter_missing"
        message="Source is disabled." if not source.enabled else "No verified adapter is registered; no request was made."
        return record_run(source,status,message,0)
    try:
        candidates=adapter.collect()
        screened=screen_many(candidates)
        saved=[]
        for record in screened:
            record["source_name"]=source.name
            record["source_url"]=record.get("source_url") or source.url
            saved.append(ingest(record))
        return record_run(source,"success",f"Candidates: {len(candidates)}; relevant: {len(screened)}",len(screened))
    except Exception as exc:
        # Store concise error text; never include credentials or request headers.
        return record_run(source,"error",f"{type(exc).__name__}: {str(exc)[:300]}",0)

def run_enabled_sources():
    return [run_source(s.key) for s in list_sources() if s.enabled]
