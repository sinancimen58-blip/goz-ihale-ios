# Gözİhale — Ingestion and deduplication foundation

This iteration establishes the normalized record fingerprint and change detection logic, plus a lightweight in-memory ingestion contract and source registry.

## Pipeline
1. Adapter emits a normalized record with source, publisher, title, institution, notice ID, publication date, original URL, deadline, status and details.
2. Fingerprint prefers a publisher notice ID; absent an ID it uses normalized title + institution + publication date.
3. Repeated records are classified as unchanged; tracked changes (deadline, status, quantity, specifications, price, document URL and title) are classified as updates.
4. Later persistence will store source provenance and event history in PostgreSQL. This prototype is in-memory only.

## Status
- Foundation implemented, not connected to live sources.
- Source registry is metadata only; URLs are discovery entry points, not verified scraping/API endpoints.
- Alerting and persistence are future work.
