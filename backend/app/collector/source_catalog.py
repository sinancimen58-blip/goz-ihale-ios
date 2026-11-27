"""Expanded catalogue of Turkish procurement discovery sources for Gözİhale.
Metadata only: this does not enable scraping. URLs are entry points; verify terms and actual endpoints before adapter implementation.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Source:
    key: str
    name: str
    url: str
    group: str
    official: bool = True
    notes: str = ""

SOURCES = [
 Source("ekap","EKAP","https://ekap.kik.gov.tr/","national"),
 Source("kik","Kamu İhale Kurumu","https://www.ihale.gov.tr/","national"),
 Source("dmo","Devlet Malzeme Ofisi","https://www.dmo.gov.tr/","national"),
 Source("ilan","ilan.gov.tr","https://www.ilan.gov.tr/","national"),
 Source("resmigazete","Resmî Gazete","https://www.resmigazete.gov.tr/","national"),
 Source("gtb","Ticaret Bakanlığı GTB e-İhale","https://www.turkiye.gov.tr/gtb-e-ihale","agency"),
 Source("mke","MKE e-İhale","https://www.turkiye.gov.tr/mke-eihale-8554","agency"),
 Source("vgm","Vakıflar Genel Müdürlüğü","https://www.vgm.gov.tr/ihaleler","agency"),
 Source("ted","TED Avrupa İhale Portalı","https://ted.europa.eu/","international"),
 Source("undp","UNDP Procurement","https://procurement-notices.undp.org/","international"),
 Source("ebrd","EBRD","https://www.ebrd.com/","international"),
 Source("worldbank","World Bank","https://www.worldbank.org/","international"),
 Source("iett","İETT İhale","https://iett.istanbul/tender/index","institution"),
 Source("pau_hospital_purchase","Pamukkale Üniversitesi Hastane Satın Alma","https://www.pau.edu.tr/ihale/tr","university_hospital",True,"Verified official hospital purchasing page; adapter URL and terms still need review."),
 Source("deu_hospital_purchase","Dokuz Eylül Üniversitesi Hastane Satın Alma","https://hastane2.deu.edu.tr/satin-alma/","university_hospital",True,"Verified official hospital purchasing page; adapter URL and terms still need review."),
]

# Institution pages are added dynamically as configured source URLs (e.g. hospitals,
# universities, provincial directorates, city hospitals and municipalities).
AGGREGATORS = [
 Source("ihaletara","İhaleTara","https://ihaletara.com/","aggregator",False,"Discovery aid only; verify at original publisher."),
 Source("ihale365","İhale365","https://ihale365.com/","aggregator",False,"Discovery aid only; verify at original publisher."),
]
