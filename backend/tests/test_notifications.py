from app.collector import notifications

def test_format_notice_contains_source_and_priority():
    message=notifications.format_notice({"title":"OCT cihazı","institution":"Test Hastane","deadline":"2026-12-01","relevance_score":88,"source_url":"https://example.gov/notice","summary":"Özet"}, "high", "Yeni ilan")
    assert "OCT cihazı" in message
    assert "HIGH" in message
    assert "https://example.gov/notice" in message

def test_missing_telegram_credentials_keeps_outbox(monkeypatch):
    monkeypatch.delenv("GOZ_IHALE_TELEGRAM_BOT_TOKEN",raising=False)
    monkeypatch.delenv("GOZ_IHALE_TELEGRAM_CHAT_ID",raising=False)
    monkeypatch.setattr(notifications,"notification_counts",lambda:{"pending":2,"sent":0,"failed":0})
    result=notifications.dispatch_pending_telegram()
    assert result["configured"] is False
    assert result["pending"]==2

def test_dispatch_marks_success_and_failure(monkeypatch):
    monkeypatch.setenv("GOZ_IHALE_TELEGRAM_BOT_TOKEN","fake-token")
    monkeypatch.setenv("GOZ_IHALE_TELEGRAM_CHAT_ID","fake-chat")
    pending=[{"alert_key":"a","payload":{"title":"FIRST_NOTICE"},"priority":"high","reason":"new"},{"alert_key":"b","payload":{"title":"SECOND_NOTICE"},"priority":"normal","reason":"new"}]
    marked=[]
    monkeypatch.setattr(notifications,"claim_pending_alerts",lambda limit:pending)
    monkeypatch.setattr(notifications,"send_telegram",lambda message:{"success":"FIRST_NOTICE" in message})
    monkeypatch.setattr(notifications,"mark_alert_delivery",lambda key,success,error:marked.append((key,success)))
    monkeypatch.setattr(notifications,"notification_counts",lambda:{"pending":0,"sent":1,"failed":1})
    result=notifications.dispatch_pending_telegram()
    assert result["sent"]==1 and result["failed"]==1
    assert marked==[("a",True),("b",False)]
