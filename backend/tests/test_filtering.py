from datetime import date
from app.collector.models import NoticeCandidate
from app.collector.filtering import screen_candidate, screen_many

def test_candidate_is_categorized_and_scored():
    candidate = NoticeCandidate(
        title="OCT-A retina imaging device procurement",
        institution="University Hospital", source_name="Publisher",
        source_url="https://example.invalid/notice", deadline=date(2026,12,10),
        description="Optical coherence tomography device"
    )
    result = screen_candidate(candidate)
    assert result is not None
    assert result["categories"]
    assert result["relevance_score"] > 0
    assert result["deadline"] == "2026-12-10"

def test_unrelated_candidate_is_excluded():
    candidate = NoticeCandidate(
        title="Office stationery", institution="Municipality",
        source_name="Publisher", source_url="https://example.invalid/notice"
    )
    assert screen_candidate(candidate) is None

def test_batch_screening():
    relevant = NoticeCandidate(
        title="Tonometre alımı", institution="Hospital",
        source_name="Publisher", source_url="https://example.invalid/1"
    )
    unrelated = NoticeCandidate(
        title="Furniture purchase", institution="Hospital",
        source_name="Publisher", source_url="https://example.invalid/2"
    )
    assert len(screen_many([relevant, unrelated])) == 1
