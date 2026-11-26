"""Extract procurement-method and payment clues with evidence and confidence."""
import re

METHOD_PATTERNS = [
    (r"\\b21\\s*/\\s*[bcf]\\b", "Pazarlık usulü (21. madde alt b/c/f)", 0.92),
    (r"\\b22\\s*/\\s*[abcd]\\b|doğrudan temin", "Doğrudan temin", 0.92),
    (r"açık\\s+ihale\\s+usul", "Açık ihale usulü", 0.90),
    (r"\\b(\\d{1,2})\\s*\\.\\s*madde\\b", "Kanun maddesi metinde belirtilmiş", 0.55),
]
PAYMENT_PATTERNS = [
    r"(?:ödeme|ödemeler)[^\\n.;]{0,100}?(?:\\d{1,3}\\s*(?:gün|iş günü|takvim günü)|hakediş|avans)[^\\n.;]{0,80}",
    r"(?:\\d{1,3}\\s*(?:gün|iş günü|takvim günü))[^\\n.;]{0,100}?(?:ödeme|hakediş|fatura)[^\\n.;]{0,80}",
    r"(?:fatura|teslim)[^\\n.;]{0,100}?(?:\\d{1,3}\\s*(?:gün|iş günü|takvim günü))[^\\n.;]{0,80}",
]

def extract_terms(text: str):
    raw=text or ""
    method=None
    for pattern,label,confidence in METHOD_PATTERNS:
        match=re.search(pattern,raw,re.IGNORECASE)
        if match:
            method={"value":label,"evidence":match.group(0),"confidence":confidence}
            break
    payment=None
    for pattern in PAYMENT_PATTERNS:
        match=re.search(pattern,raw,re.IGNORECASE)
        if match:
            evidence=re.sub(r"\\s+"," ",match.group(0)).strip()
            payment={"value":evidence,"evidence":evidence,"confidence":0.62}
            break
    return {"procurement_method":method,"payment_terms":payment,"note":"Metin eşleştirmeleri ön tespit niteliğindedir. Dokümanın bağlamı ve tam metni insan tarafından doğrulanmalıdır."}

