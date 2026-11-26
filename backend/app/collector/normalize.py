"""Normalize notice records and generate stable deduplication fingerprints."""
from __future__ import annotations
import hashlib
import re
import unicodedata
from dataclasses import asdict
from typing import Any


def normalize_text(value: str | None) -> str:
    value = value or ""
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"\s+", " ", value).strip()
    return value


def fingerprint_notice(title: str, institution: str, publication_date: str | None = None, notice_id: str | None = None) -> str:
    """Prefer publisher notice ID; otherwise fingerprint title/institution/date."""
    if notice_id and normalize_text(notice_id):
        seed = "id:" + normalize_text(notice_id)
    else:
        seed = "|".join((normalize_text(title), normalize_text(institution), normalize_text(publication_date)))
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def material_change(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    """Return fields whose changes should trigger an update alert."""
    tracked = ("title", "deadline", "status", "quantity", "specification", "estimated_price", "document_url")
    changed=[]
    for field in tracked:
        a=normalize_text(str(old.get(field) or ""))
        b=normalize_text(str(new.get(field) or ""))
        if a != b:
            changed.append(field)
    return changed
