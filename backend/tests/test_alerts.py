from app.collector.alerts import decide_alert

def test_new_alert():
    d=decide_alert("new", score=80)
    assert d.send and d.priority == "high"

def test_low_score_new_notice_is_not_suppressed_but_marked_low():
    d=decide_alert("new", score=18)
    assert d.send and d.priority == "low"
    assert "düşük ilgililik" in d.reason

def test_mid_score_new_notice_is_normal_priority():
    d=decide_alert("new", score=35)
    assert d.send and d.priority == "normal"

def test_deadline_update_high():
    d=decide_alert("updated", ["deadline"])
    assert d.send and d.priority == "high"

def test_unchanged_no_alert():
    assert not decide_alert("unchanged").send

def test_alert_policy_does_not_send_for_unchanged_or_unknown():
    assert not decide_alert("unchanged").send
    assert not decide_alert("other").send
