"""Controlled source runner. Explicit source allowlist and verified feed URLs required."""
import os, time
from .registry import list_sources
from .scan_ledger import record_run
from .filtering import screen_many
from .sqlite_repository import ingest
from .rss_adapter import RSSFeedAdapter
from .official_html_adapter import OfficialHTMLAdapter
from urllib.parse import urlparse

def enabled_keys():
    raw=os.getenv("GOZ_IHALE_ENABLED_SOURCE_KEYS","")
    return {key.strip() for key in raw.split(",") if key.strip()}

def configured_adapters():
    adapters={}
    enabled=enabled_keys()
    html_keys={key.strip() for key in os.getenv("GOZ_IHALE_HTML_SOURCE_KEYS","").split(",") if key.strip()}
    for source in list_sources():
        if source.key not in enabled:
            continue
        env_key="GOZ_IHALE_FEED_"+source.key.upper().replace("-","_")
        feed_url=os.getenv(env_key)
        if feed_url:
            try:
                adapters[source.key]=RSSFeedAdapter(source.name,feed_url)
            except ValueError:
                pass
        if source.key in html_keys:
            page_url=os.getenv("GOZ_IHALE_HTML_PAGE_"+source.key.upper().replace("-","_"))
            registered_host=urlparse(source.url).hostname
            if page_url and registered_host:
                try:
                    adapters[source.key]=OfficialHTMLAdapter(source.name,page_url,registered_host)
                except ValueError:
                    continue
    return adapters

def run_source(source_key: str):
    sources={s.key:s for s in list_sources()}
    source=sources.get(source_key)
    if source is None:
        return {"source_key":source_key,"status":"unknown_source","notices_saved":0}
    enabled=enabled_keys()
    adapter=configured_adapters().get(source_key)
    if source_key not in enabled or adapter is None:
        status="disabled" if source_key not in enabled else "adapter_missing_or_invalid"
        message="Source not explicitly enabled." if source_key not in enabled else "Enabled but feed URL missing or invalid; no request made."
        return record_run(source,status,message,0)
    started=time.perf_counter()
    try:
        candidates=adapter.collect()
        screened=screen_many(candidates)
        actions={"new":0,"updated":0,"unchanged":0}
        alert_count=0
        for record in screened:
            record["source_name"]=source.name
            record["source_url"]=record.get("source_url") or source.url
            result=ingest(record)
            action=result.get("action","unchanged")
            actions[action]=actions.get(action,0)+1
            if result.get("alert"):
                alert_count+=1
        duration_ms=int((time.perf_counter()-started)*1000)
        message=(f"Fetched: {len(candidates)}; relevant: {len(screened)}; "
                 f"new: {actions['new']}; updated: {actions['updated']}; "
                 f"unchanged: {actions['unchanged']}; alert candidates: {alert_count}; "
                 f"duration: {duration_ms} ms")
        metrics={"fetched_count":len(candidates),"relevant_count":len(screened),
                 "new_count":actions["new"],"updated_count":actions["updated"],
                 "unchanged_count":actions["unchanged"],"alert_candidates":alert_count,
                 "duration_ms":duration_ms}
        status="success_empty" if len(candidates)==0 else "success"
        return record_run(source,status,message,len(screened),metrics)
    except Exception as exc:
        duration_ms=int((time.perf_counter()-started)*1000)
        return record_run(source,"error",f"Collection failed ({type(exc).__name__}); details withheld to avoid leaking configuration or URLs.",0,{"duration_ms":duration_ms})

def run_enabled_sources():
    enabled=enabled_keys()
    return [run_source(s.key) for s in list_sources() if s.key in enabled]
