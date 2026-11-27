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
    SourceDefinition("khgm_central_notices", "KHGM Merkezi Satın Alma İhale Duyuruları", "agency", "https://khgm.saglik.gov.tr/TR-119527/ihale-duyurulari.html", notes="Dedicated central purchasing notice page; adapter review pending"),
    SourceDefinition("khgm_supply", "KHGM Tedarik Yöntemleri ve Satın Alma Daire Başkanlığı", "agency", "https://khgmsatinalmadb.saglik.gov.tr/", notes="Separate procurement portal and central medical device purchase notices; adapter review pending"),
    SourceDefinition("deu_hospital_purchase", "Dokuz Eylül Üniversitesi Hastane Satın Alma", "university_hospital", "https://hastane2.deu.edu.tr/satin-alma/", notes="Official hospital procurement listing; adapter readiness to be verified"),
    SourceDefinition("pau_hospital_purchase", "Pamukkale Üniversitesi Hastane Satın Alma", "university_hospital", "https://www.pau.edu.tr/ihale/tr", notes="Official hospital procurement listing; adapter readiness to be verified"),
    SourceDefinition("ushas", "USHAŞ Tedarik Yönetim Sistemi", "agency", "https://www.ushas.gov.tr/tedarik-yonetim-sistemi/", notes="Supplier portal and online procurement; adapter/authentication review pending"),
    SourceDefinition("kizilay", "Türk Kızılay İhale İlanları", "institution", "https://www.kizilay.org.tr/IhaleIlanlari", notes="Direct supplier portal may be required; not governed by public procurement law"),
    SourceDefinition("kizilay_logistics", "Kızılay Lojistik İhale Duyuruları", "institution", "https://kizilaylojistik.com.tr/ihale-duyurulari", notes="Separate logistics purchasing announcements"),
    SourceDefinition("tika", "TİKA", "agency", "https://tika.gov.tr/basin-odasi/duyurular/", notes="Duyurular and overseas project procurement; investigate specific tender page/office notices"),
    SourceDefinition("presidency_support", "Cumhurbaşkanlığı Destek Hizmetleri", "agency", "https://www.tccb.gov.tr/", notes="Presidential procurement/support-services announcements; page and tender endpoint verification pending"),
    SourceDefinition("tdt", "Türk Devletleri Teşkilatı", "international", "https://turkicstates.org/", notes="Secretariat procurement/project notices; endpoint verification pending"),
    SourceDefinition("turksoy", "TÜRKSOY", "international", "https://turksoy.org/", notes="Related organization of TDT; procurement notices endpoint review pending"),
    SourceDefinition("turkpa", "TÜRKPA", "international", "https://turkpa.org/", notes="Related parliamentary organization; procurement endpoint review pending"),
    SourceDefinition("turkic_academy", "Türk Akademisi", "international", "https://turkicacademy.org/", notes="TDT-related organization; procurement endpoint review pending"),
    SourceDefinition("turkic_fund", "Türk Yatırım Fonu", "international", "https://turkicfund.org/", notes="TDT-related financing organization; project procurement monitoring pending"),
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
