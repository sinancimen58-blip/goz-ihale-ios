from dataclasses import dataclass
from datetime import date

@dataclass
class NoticeCandidate:
    title: str
    institution: str
    source_name: str
    source_url: str
    city: str | None = None
    deadline: date | None = None
    description: str | None = None

    @property
    def searchable_text(self) -> str:
        return " ".join(filter(None, [self.title, self.institution, self.description]))
