"""Deadline parsing and urgency labels for tender triage."""
from datetime import datetime, date, timezone

def parse_deadline(value):
    if not value: return None
    raw=str(value).strip()
    try:
        return datetime.fromisoformat(raw.replace("Z","+00:00")).date()
    except ValueError:
        try: return date.fromisoformat(raw[:10])
        except ValueError: return None

def days_remaining(value, today=None):
    deadline=parse_deadline(value)
    if deadline is None: return None
    current=today or date.today()
    return (deadline-current).days

def urgency_label(value, today=None):
    days=days_remaining(value,today)
    if days is None: return "Tarih belirsiz"
    if days < 0: return "Süresi geçmiş"
    if days == 0: return "Bugün"
    if days <= 3: return "Kritik: 3 gün"
    if days <= 7: return "Acil: 7 gün"
    if days <= 14: return "Yaklaşıyor"
    return "Normal"
