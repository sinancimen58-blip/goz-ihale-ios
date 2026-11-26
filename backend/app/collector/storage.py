"""Persistence-neutral storage interface and PostgreSQL schema draft."""
from typing import Protocol, Any

class NoticeRepository(Protocol):
    def upsert_notice(self, notice: dict[str, Any]) -> Any: ...
    def record_event(self, fingerprint: str, event_type: str, payload: dict[str, Any]) -> Any: ...
    def list_notices(self, limit: int = 100) -> Any: ...

POSTGRES_SCHEMA = r"""
CREATE TABLE IF NOT EXISTS sources (
 id BIGSERIAL PRIMARY KEY, source_key TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
 url TEXT NOT NULL, source_group TEXT NOT NULL, official BOOLEAN NOT NULL DEFAULT TRUE,
 enabled BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS notices (
 id BIGSERIAL PRIMARY KEY, fingerprint TEXT UNIQUE NOT NULL, notice_id TEXT,
 title TEXT NOT NULL, institution TEXT, city TEXT, category TEXT, publication_date DATE,
 deadline TIMESTAMPTZ, status TEXT, original_url TEXT, specification_text TEXT,
 estimated_price NUMERIC, currency TEXT, relevance_score INTEGER DEFAULT 0,
 first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(), last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 source_key TEXT, raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS notice_sources (
 notice_id BIGINT REFERENCES notices(id) ON DELETE CASCADE,
 source_id BIGINT REFERENCES sources(id), source_url TEXT NOT NULL, seen_at TIMESTAMPTZ DEFAULT now(),
 PRIMARY KEY(notice_id, source_id, source_url)
);
CREATE TABLE IF NOT EXISTS notice_events (
 id BIGSERIAL PRIMARY KEY, notice_id BIGINT REFERENCES notices(id) ON DELETE CASCADE,
 event_type TEXT NOT NULL, event_at TIMESTAMPTZ NOT NULL DEFAULT now(), payload JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS notices_deadline_idx ON notices(deadline);
CREATE INDEX IF NOT EXISTS notices_category_idx ON notices(category);
CREATE INDEX IF NOT EXISTS notices_city_idx ON notices(city);
CREATE INDEX IF NOT EXISTS notice_events_notice_idx ON notice_events(notice_id, event_at DESC);
"""
