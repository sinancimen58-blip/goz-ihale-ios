"""API tests using an isolated SQLite database."""
import os
import tempfile

# Set DB and write token before importing application module.
os.environ["GOZ_IHALE_API_WRITE_TOKEN"] = "test-write-token"
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["GOZ_IHALE_DB"] = _tmp.name

from fastapi.testclient import TestClient
from app.main import app, init_db

init_db()
client = TestClient(app)

def test_health_is_explicitly_not_live():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["live_data"] is False

def test_demo_records_and_category_filter():
    response = client.get("/api/tenders")
    assert response.status_code == 200
    assert len(response.json()) >= 2
    filtered = client.get("/api/tenders", params={"category": "OCT"})
    assert filtered.status_code == 200
    assert all("OCT" in row["category"] or "OCT" in row["title"] for row in filtered.json())

def test_search_filter():
    response = client.get("/api/tenders", params={"q": "Demo Üniversite"})
    assert response.status_code == 200
    assert any("Üniversite" in row["institution"] for row in response.json())

def test_get_missing_notice_returns_404():
    response = client.get("/api/tenders/not-found")
    assert response.status_code == 404

def test_create_and_duplicate_notice():
    payload = {
        "id": "test-unique-1", "title": "Test OCT alımı", "institution": "Test Hastanesi",
        "city": "Sivas", "category": "OCT", "deadline": "2026-12-31",
        "source_name": "Test", "source_url": None, "summary": "Test kaydı", "status": "new"
    }
    created = client.post("/api/tenders", json=payload, headers={"X-Goz-Ihale-Token": "test-write-token"})
    assert created.status_code == 200
    assert created.json()["id"] == payload["id"]
    duplicate = client.post("/api/tenders", json=payload, headers={"X-Goz-Ihale-Token": "test-write-token"})
    assert duplicate.status_code == 409
