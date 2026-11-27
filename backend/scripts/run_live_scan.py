#!/usr/bin/env python3
"""Run configured source scans against the local, loopback-only API."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json, sys, time

BACKEND_DIR=Path(__file__).resolve().parents[1]
SOURCE_KEYS=("khgm_central_notices","dmo")

def read_env(path):
    values={}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key,value=line.split("=",1)
        values[key.strip()]=value.strip()
    return values

def request_json(url,token=None,method="GET",timeout=30):
    headers={"Accept":"application/json"}
    if token:
        headers["X-Goz-Ihale-Token"]=token
    request=Request(url,headers=headers,method=method)
    with urlopen(request,timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    env=read_env(BACKEND_DIR/".env")
    token=env.get("GOZ_IHALE_API_WRITE_TOKEN")
    if not token:
        print("Missing GOZ_IHALE_API_WRITE_TOKEN in backend/.env",file=sys.stderr)
        return 2
    port=env.get("GOZ_IHALE_PORT","8000")
    base=f"http://127.0.0.1:{port}"
    health=None
    for attempt in range(10):
        try:
            health=request_json(base+"/api/health")
            if health.get("status")=="ok":
                break
        except (HTTPError,URLError,TimeoutError):
            if attempt==9:
                raise
            time.sleep(2)
    if not health or health.get("status")!="ok":
        print("API health check failed.",file=sys.stderr)
        return 2
    outcomes=[]
    for key in SOURCE_KEYS:
        result=request_json(base+"/api/run-source/"+key,token=token,method="POST")
        outcomes.append(result)
        print(f"{key}: {result.get('status')} | fetched={result.get('fetched_count',0)} | relevant={result.get('relevant_count',0)} | new={result.get('new_count',0)} | updated={result.get('updated_count',0)}")
        if result.get("status") not in {"success","success_empty"}:
            print(f"Source run failed: {key}",file=sys.stderr)
            return 1
    summary=request_json(base+"/api/scan-summary")
    print(f"Scan ledger: {summary.get('sources_with_runs',0)} sources with runs; {summary.get('latest_status_counts',{})}")
    return 0

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (HTTPError,URLError,TimeoutError) as exc:
        print(f"API request failed: {type(exc).__name__}",file=sys.stderr)
        raise SystemExit(2)
