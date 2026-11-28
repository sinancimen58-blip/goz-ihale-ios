"""Alert policy helper for persistent outbox delivery."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AlertDecision:
    send: bool
    reason: str
    priority: str = "normal"

HIGH_PRIORITY_TERMS = ("zeyilname", "iptal", "tarih değiş", "son başvuru", "son teklif")

def decide_alert(action: str, changed_fields: list[str] | None = None, text: str = "", score: int = 0) -> AlertDecision:
    if action == "new":
        if score >= 75:
            return AlertDecision(True, "Yeni yüksek önem seviyeli ilan", "high")
        if score < 25:
            # Keep low-confidence candidates visible; don't silently drop procurement leads.
            return AlertDecision(True, "Yeni düşük ilgililik seviyeli ilan", "low")
        return AlertDecision(True, "Yeni ilan", "normal")
    if action == "updated":
        haystack=(text or "").casefold()
        if any(term in haystack for term in HIGH_PRIORITY_TERMS) or any(f in (changed_fields or []) for f in ("deadline", "status", "specification", "payment_terms", "document_url")):
            return AlertDecision(True, "Önemli ilan değişikliği", "high")
        return AlertDecision(True, "İlan güncellemesi", "normal")
    return AlertDecision(False, "Yeni veya önemli değişiklik yok", "normal")
