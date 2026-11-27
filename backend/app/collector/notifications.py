"""Optional Telegram delivery for a durable, deduplicated alert outbox."""
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from .sqlite_repository import list_pending_alerts, mark_alert_delivery, notification_counts

def telegram_configured() -> bool:
    return bool(os.getenv("GOZ_IHALE_TELEGRAM_BOT_TOKEN") and os.getenv("GOZ_IHALE_TELEGRAM_CHAT_ID"))

def format_notice(record: dict, priority: str, reason: str) -> str:
    lines=["Gözİhale bildirimi",f"Öncelik: {priority.upper()}",reason,
           str(record.get("title") or "Başlık belirtilmemiş"),
           f"Kurum: {record.get('institution') or '-'}",
           f"Kategori: {record.get('category') or '-'}",
           f"Son tarih: {record.get('deadline') or 'Belirtilmemiş'}",
           f"İlgililik puanı: {record.get('relevance_score') or 0}"]
    url=record.get("source_url") or record.get("document_url")
    if url and str(url).startswith("https://"):
        lines.append(f"Resmî kaynak: {url}")
    summary=record.get("summary")
    if summary:
        lines.append("Özet: "+str(summary)[:500])
    return "\n".join(lines)[:3800]

def send_telegram(message: str) -> dict:
    token=os.getenv("GOZ_IHALE_TELEGRAM_BOT_TOKEN","")
    chat_id=os.getenv("GOZ_IHALE_TELEGRAM_CHAT_ID","")
    if not token or not chat_id:
        return {"success":False,"error":"Telegram not configured"}
    endpoint=f"https://api.telegram.org/bot{token}/sendMessage"
    payload=json.dumps({"chat_id":chat_id,"text":message},ensure_ascii=False).encode("utf-8")
    request=Request(endpoint,data=payload,headers={"Content-Type":"application/json"},method="POST")
    try:
        with urlopen(request,timeout=10) as response:
            result=json.loads(response.read().decode("utf-8"))
        if result.get("ok") is True:
            return {"success":True}
        return {"success":False,"error":"Telegram API rejected the message"}
    except HTTPError as exc:
        return {"success":False,"error":f"Telegram HTTP error {exc.code}"}
    except (URLError,TimeoutError,OSError,ValueError):
        return {"success":False,"error":"Telegram transport or response error"}

def dispatch_pending_telegram(limit: int = 100) -> dict:
    if not telegram_configured():
        counts=notification_counts()
        return {"configured":False,"sent":0,"failed":0,"pending":counts["pending"],"message":"Telegram credentials are not configured; outbox is retained."}
    sent=0
    failed=0
    for item in list_pending_alerts(limit):
        message=format_notice(item.get("payload") or {},item.get("priority","normal"),item.get("reason",""))
        result=send_telegram(message)
        mark_alert_delivery(item["alert_key"],result.get("success",False),result.get("error"))
        if result.get("success"):
            sent+=1
        else:
            failed+=1
    counts=notification_counts()
    return {"configured":True,"sent":sent,"failed":failed,"pending":counts["pending"],"permanently_failed":counts["failed"]}
