"""Controlled source runner. Only explicitly configured feed adapters run."""
import os
from .registry import list_sources
from .scan_ledger import record_run
from .filtering import screen_many
from .sqlite_repository import ingest
from .rss_adapter import RSSFeedAdapter

def configured_adapters():
    adapters={}
    for source in list_sources():
        env_key="GOZ_IHALE_FEED_"+source.key.upper().replace("-","_")
        feed_url=os.getenv(env_key)
        if feed_url and source.enabled:
            try:
                adapters[source.key]=RSSFeedAdapter(source.name,feed_url)
            except ValueError:
                continue
    return adapters

ADAPTERS = configured_adapters()

def run_source(source_key: str):
    sources={s.key:s for s in list_sources()}
    source=sources.get(source_key)
    if source is None:
        return {"source_key":source_key,"status":"unknown_source","notices_saved":0}
    adapter=ADAPTERS.get(source_key)
    if not source.enabled or adapter is None:
        status="disabled" if not source.enabled else "adapter_missing"
        message="Source disabled." if not source.enabled else "No configured adapter; no request was made."
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
        return record_run(source,"error",f"{type(exc).__name__}: {str(exc)[:300]}",0)

def run_enabled_sources():
    return [run_source(s.key) for s in list_sources() if s.enabled and s.key in ADAPTERS]
