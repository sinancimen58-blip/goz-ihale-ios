from datetime import date
from app.collector.deadlines import parse_deadline, days_remaining, urgency_label

def test_iso_datetime_deadline_parsing():
    assert parse_deadline("2027-02-04T15:00:00") == date(2027,2,4)

def test_urgency_windows():
    today=date(2027,2,1)
    assert days_remaining("2027-02-01",today)==0
    assert urgency_label("2027-02-01",today)=="Bugün"
    assert urgency_label("2027-02-04",today)=="Kritik: 3 gün"
    assert urgency_label("2027-02-10",today)=="Acil: 7 gün"
    assert urgency_label("2027-02-20",today)=="Normal"

def test_invalid_and_past_dates():
    assert days_remaining("unknown",date(2027,2,1)) is None
    assert urgency_label("2027-01-31",date(2027,2,1))=="Süresi geçmiş"
