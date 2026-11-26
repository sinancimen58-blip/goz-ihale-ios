"""Simple in-memory ingestion pipeline contract. Persistence will replace this store later."""
from dataclasses import dataclass, field
from typing import Any
from .normalize import fingerprint_notice, material_change

@dataclass
class IngestionResult:
    fingerprint: str
    action: str  # new, unchanged, updated
    changed_fields: list[str] = field(default_factory=list)

class NoticeStore:
    def __init__(self):
        self.records: dict[str, dict[str, Any]] = {}

    def ingest(self, record: dict[str, Any]) -> IngestionResult:
        key = fingerprint_notice(record.get("title", ""), record.get("institution", ""), record.get("publication_date"), record.get("notice_id"))
        old = self.records.get(key)
        if old is None:
            self.records[key] = dict(record)
            return IngestionResult(key, "new")
        changed = material_change(old, record)
        if changed:
            self.records[key] = dict(record)
            return IngestionResult(key, "updated", changed)
        # Refresh non-alert metadata, while keeping a material-change alert suppressed.
        self.records[key] = dict(record)
        return IngestionResult(key, "unchanged")
