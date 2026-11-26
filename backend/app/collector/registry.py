"""Source registry model; live adapters are added separately and run only via permitted access."""
from dataclasses import dataclass

@dataclass(frozen=True)
class SourceDefinition:
    key: str
    name: str
    source_group: str
    url: str
    official: bool = True
    enabled: bool = False
    notes: str = ""

# Registry entries are planning metadata, not active crawlers or verified API endpoints.
SOURCES = [
    SourceDefinition("ekap", "EKAP", "national", "https://ekap.kik.gov.tr/", notes="Official public procurement platform"),
    SourceDefinition("dmo", "DMO", "national", "https://www.dmo.gov.tr/", notes="Catalogue and procurement notices"),
    SourceDefinition("ilan", "ilan.gov.tr", "national", "https://www.ilan.gov.tr/", notes="Public notice discovery"),
    SourceDefinition("resmigazete", "Resmî Gazete", "national", "https://www.resmigazete.gov.tr/", notes="Legal and institutional notices"),
    SourceDefinition("ted", "TED", "international", "https://ted.europa.eu/", notes="EU procurement notices; Turkey-relevant opportunities"),
    SourceDefinition("undp", "UNDP Procurement", "international", "https://procurement-notices.undp.org/", notes="International project procurement"),
    SourceDefinition("worldbank", "World Bank Procurement", "international", "https://www.worldbank.org/", notes="Project procurement discovery"),
    SourceDefinition("ebrd", "EBRD Procurement", "international", "https://www.ebrd.com/", notes="Project procurement discovery"),
]

def list_sources(group: str | None = None):
    return [s for s in SOURCES if group is None or s.source_group == group]
