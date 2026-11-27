"""Source registry model; all entries remain disabled until adapters are reviewed."""
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

# Planning and runner registry. Metadata only: no network access occurs from this list.
SOURCES = [
    SourceDefinition("ekap", "EKAP", "national", "https://ekap.kik.gov.tr/", notes="Official public procurement platform"),
    SourceDefinition("kik", "Kamu İhale Kurumu", "national", "https://www.ihale.gov.tr/", notes="KİK official information portal"),
    SourceDefinition("dmo", "Devlet Malzeme Ofisi", "national", "https://www.dmo.gov.tr/", notes="Catalogue and procurement notices"),
    SourceDefinition("khgm_central", "Sağlık Bakanlığı Kamu Hastaneleri Genel Müdürlüğü", "agency", "https://khgm.saglik.gov.tr/", notes="Central procurement and hospital purchasing announcements; endpoint review pending"),
    SourceDefinition("ilan", "ilan.gov.tr", "national", "https://www.ilan.gov.tr/", notes="Public notice discovery"),
    SourceDefinition("resmigazete", "Resmî Gazete", "national", "https://www.resmigazete.gov.tr/", notes="Legal and institutional notices"),
    SourceDefinition("gtb", "Ticaret Bakanlığı GTB e-İhale", "agency", "https://www.turkiye.gov.tr/gtb-e-ihale", notes="Access/terms review required"),
    SourceDefinition("mke", "MKE e-İhale", "agency", "https://www.turkiye.gov.tr/mke-eihale-8554", notes="Access/terms review required"),
    SourceDefinition("vgm", "Vakıflar Genel Müdürlüğü", "agency", "https://www.vgm.gov.tr/ihaleler", notes="Institutional procurement notices"),
    SourceDefinition("iett", "İETT İhale", "institution", "https://iett.istanbul/tender/index", notes="Institutional notices"),
    SourceDefinition("izmir_esrefpasa", "İzmir Büyükşehir Belediyesi Eşrefpaşa Hastanesi", "municipal_hospital", "https://www.izmir.bel.tr/", notes="Hospital and İzmir BB procurement notices; official portal entry point, URLs to verify"),
    SourceDefinition("ankara_municipal_health", "Ankara Büyükşehir Belediyesi sağlık hizmetleri", "municipal_hospital", "https://www.ankara.bel.tr/", notes="Health-service procurement discovery; confirm hospital unit and official procurement URLs"),
    SourceDefinition("municipal_health_procurement", "Büyükşehir belediyeleri sağlık/medikal alımları", "municipal_hospital", "https://www.ekap.kik.gov.tr/", notes="Search municipal procurement and hospital-related medical supplies across metropolitan municipalities; EKAP source of record"),
    SourceDefinition("ted", "TED", "international", "https://ted.europa.eu/", notes="EU procurement notices; Turkey-relevant opportunities"),
    SourceDefinition("undp", "UNDP Procurement", "international", "https://procurement-notices.undp.org/", notes="International project procurement"),
    SourceDefinition("worldbank", "World Bank Procurement", "international", "https://www.worldbank.org/", notes="Project procurement discovery"),
    SourceDefinition("ebrd", "EBRD Procurement", "international", "https://www.ebrd.com/", notes="Project procurement discovery"),
    SourceDefinition("ihaletara", "İhaleTara", "aggregator", "https://ihaletara.com/", official=False, notes="Discovery aid only; verify at original publisher"),
    SourceDefinition("ihale365", "İhale365", "aggregator", "https://ihale365.com/", official=False, notes="Discovery aid only; verify at original publisher"),
]

def list_sources(group: str | None = None):
    return [s for s in SOURCES if group is None or s.source_group == group]

def get_source(key: str):
    return next((source for source in SOURCES if source.key == key), None)
