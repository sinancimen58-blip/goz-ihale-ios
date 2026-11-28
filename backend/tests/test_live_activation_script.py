from pathlib import Path


def test_live_activation_installs_schedule_before_first_scan():
    script = Path(__file__).resolve().parents[1] / "scripts" / "enable_live_collection.sh"
    text = script.read_text(encoding="utf-8")
    cron_setup = text.index("/etc/cron.d/gozihale-collection")
    initial_scan = text.index("python3 scripts/run_live_scan.py")
    assert cron_setup < initial_scan


def test_live_scan_retains_pending_alerts_when_telegram_is_not_configured(monkeypatch):
    from scripts.run_live_scan import dispatch_if_configured
    calls=[]
    monkeypatch.setattr("scripts.run_live_scan.request_json",lambda *args,**kwargs:calls.append((args,kwargs)))
    result=dispatch_if_configured("http://127.0.0.1:8000","token",{"telegram_configured":False,"outbox":{"pending":3}})
    assert result["pending"]==3
    assert result["configured"] is False
    assert calls==[]


def test_live_scan_dispatches_outbox_when_telegram_is_configured(monkeypatch):
    from scripts.run_live_scan import dispatch_if_configured
    calls=[]
    monkeypatch.setattr("scripts.run_live_scan.request_json",lambda *args,**kwargs:calls.append((args,kwargs)) or {"configured":True,"sent":2,"failed":0,"pending":0})
    result=dispatch_if_configured("http://127.0.0.1:8000","token",{"telegram_configured":True,"outbox":{"pending":2}})
    assert result["sent"]==2
    assert calls[0][0][0]=="http://127.0.0.1:8000/api/dispatch-alerts"
    assert calls[0][1]["method"]=="POST"
