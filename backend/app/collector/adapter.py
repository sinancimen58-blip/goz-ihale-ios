from abc import ABC, abstractmethod
from .models import NoticeCandidate

class SourceAdapter(ABC):
    """Adapter contract. Implement only for sources and methods permitted by their terms."""
    source_name: str

    @abstractmethod
    def collect(self) -> list[NoticeCandidate]:
        """Return candidates; empty until a verified source implementation exists."""
        raise NotImplementedError
