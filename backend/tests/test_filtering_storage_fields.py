from datetime import date
from app.collector.models import NoticeCandidate
from app.collector.filtering import screen_candidate

def test_screened_record_includes_storage_fields():
    candidate=NoticeCandidate(title="OCT cihazı alımı",institution="Üniversite Hastanesi",source_name="Feed",source_url="https://example.org",deadline=date(2027,1,1),description="Optik koherens tomografi")
    result=screen_candidate(candidate)
    assert result is not None
    assert result["category"]
    assert "categories" in result
    assert result["publication_date"] is None
    assert result["deadline"]=="2027-01-01"
