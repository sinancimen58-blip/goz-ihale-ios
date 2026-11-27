from app.collector.alerts import decide_alert

def test_new_alert():
    assert decide_alert("new", score=80).send

def test_deadline_update_high():
    d=decide_alert("updated", ["deadline"])
    assert d.send and d.priority == "high"

def test_unchanged_no_alert():
    assert not decide_alert("unchanged").send

def test_alert_policy_does_not_send_for_unchanged_or_unknown():
    assert not decide_alert("unchanged").send
    assert not decide_alert("other").send
