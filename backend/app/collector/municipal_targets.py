"""Targets for municipal health and medical procurement monitoring.
Names are based on the 30 metropolitan municipalities; URLs are not inferred here.
"""
METROPOLITAN_MUNICIPALITIES = [
  "Adana",
  "Ankara",
  "Antalya",
  "Aydın",
  "Balıkesir",
  "Bursa",
  "Denizli",
  "Diyarbakır",
  "Erzurum",
  "Eskişehir",
  "Gaziantep",
  "Hatay",
  "İstanbul",
  "İzmir",
  "Kahramanmaraş",
  "Kayseri",
  "Kocaeli",
  "Konya",
  "Malatya",
  "Manisa",
  "Mardin",
  "Mersin",
  "Muğla",
  "Ordu",
  "Sakarya",
  "Samsun",
  "Şanlıurfa",
  "Tekirdağ",
  "Trabzon",
  "Van"
]

MUNICIPAL_HEALTH_SEARCH_TERMS = [
    "hastane", "sağlık işleri", "sağlık dairesi", "medikal", "oftalmoloji",
    "göz", "OCT", "optik biyometri", "fako", "tonometre", "mikroskop",
    "YAG lazer", "SLT", "görme alanı", "fundus", "topografi",
    "cihaz bakım", "kalibrasyon", "yedek parça", "sarf malzeme",
]

TARGETS = [{
    "municipality": city,
    "institution": f"{city} Büyükşehir Belediyesi",
    "discovery_source": "EKAP + municipality official procurement pages",
    "search_terms": MUNICIPAL_HEALTH_SEARCH_TERMS,
    "verification_required": True,
} for city in METROPOLITAN_MUNICIPALITIES]
