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

def test_detailed_health_endpoint_reports_storage_without_claiming_live_collection():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["api_version"]
    assert payload["storage_checks"] == {
        "primary_db": "ok",
        "ingestion_db": "ok",
        "scan_ledger_db": "ok",
    }
    assert 0 <= payload["collected_notice_count_capped_at_500"] <= 500
    assert isinstance(payload["live_collection_configured"], bool)
    assert isinstance(payload["latest_source_status_counts"], dict)
    assert "latest_scan" in payload


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


def test_write_endpoint_requires_token():
    payload = {"id":"test-auth-1","title":"Test","institution":"Test","city":"Sivas","category":"OCT","deadline":None,"source_name":"Test","source_url":None,"summary":None,"status":"new"}
    response = client.post("/api/tenders", json=payload)
    assert response.status_code == 401


def test_legal_analysis_endpoint():
    response=client.get("/api/legal-analyze", params={"text":"4734 açık ihale usulü"})
    assert response.status_code == 200
    assert response.json()["detected_methods"]
    assert response.json()["time_limits"]["exact_days"] is None
    assert "extracted_terms" in response.json()


def test_specification_review_api():
    response=client.get("/api/specification-review", params={"text":"ZEISS marka, eşdeğer ürün, kurulum"})
    assert response.status_code == 200
    assert response.json()["flag_count"] >= 2


def test_source_catalog_api_is_safe_and_read_only():
    response = client.get("/api/sources")
    assert response.status_code == 200
    rows = response.json()
    assert rows
    assert all("feed_configured" in row and "html_configured" in row and "page_configured" in row and "adapter_ready" in row for row in rows)


def test_scan_catalog_requires_token_and_does_not_claim_live_collection():
    denied = client.post("/api/scan-catalog")
    assert denied.status_code == 401
    allowed = client.post("/api/scan-catalog", headers={"X-Goz-Ihale-Token": "test-write-token"})
    assert allowed.status_code == 200
    payload = allowed.json()
    assert payload["live_collection"] is False
    assert "websites were not contacted" in payload["message"]


def test_scan_summary_endpoint_reports_catalog_state():
    response = client.get("/api/scan-summary")
    assert response.status_code == 200
    payload = response.json()
    assert "sources_with_runs" in payload
    assert "latest_status_counts" in payload
    assert "live_collection_configured" in payload
