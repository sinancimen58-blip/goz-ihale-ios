from datetime import date
from app.collector.deadlines import days_remaining, urgency_label


def test_priority_notice_deadline_enrichment_contract():
    deadline = "2027-02-04"
    today = date(2027, 2, 1)
    assert days_remaining(deadline, today) == 3
    assert urgency_label(deadline, today) == "Kritik: 3 gün"
