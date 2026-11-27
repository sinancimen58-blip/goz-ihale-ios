"""Institution-targeted search plan for ophthalmology procurement discovery.
Targets are search entities, not live scraping claims. EKAP is the primary verification source;
institution pages are secondary discovery sources once their URLs are confirmed.
"""
UNIVERSITY_HOSPITAL_TARGETS = [
"Ankara Üniversitesi Hastaneleri","Hacettepe Üniversitesi Hastaneleri","Gazi Üniversitesi Hastaneleri",
"İstanbul Üniversitesi-Cerrahpaşa Hastaneleri","İstanbul Üniversitesi İstanbul Tıp Fakültesi",
"Marmara Üniversitesi Hastaneleri","Ege Üniversitesi Hastaneleri","Dokuz Eylül Üniversitesi Hastaneleri",
"Akdeniz Üniversitesi Hastaneleri","Çukurova Üniversitesi Hastaneleri","Mersin Üniversitesi Hastaneleri",
"Erciyes Üniversitesi Hastaneleri","Selçuk Üniversitesi Hastaneleri","Necmettin Erbakan Üniversitesi Hastaneleri",
"Konya Teknik Üniversitesi","Süleyman Demirel Üniversitesi Hastaneleri","Pamukkale Üniversitesi Hastaneleri",
"Eskişehir Osmangazi Üniversitesi Hastaneleri","Bursa Uludağ Üniversitesi Hastaneleri",
"Atatürk Üniversitesi Hastaneleri","Karadeniz Teknik Üniversitesi Hastaneleri","Ondokuz Mayıs Üniversitesi Hastaneleri",
"Fırat Üniversitesi Hastaneleri","Dicle Üniversitesi Hastaneleri","Gaziantep Üniversitesi Hastaneleri",
"İnönü Üniversitesi Hastaneleri","Kocaeli Üniversitesi Hastaneleri","Sakarya Üniversitesi Hastaneleri",
"Trakya Üniversitesi Hastaneleri","Başkent Üniversitesi Hastaneleri","Koç Üniversitesi Hastaneleri",
"Acıbadem Üniversitesi Hastaneleri","Yeditepe Üniversitesi Hastaneleri","Bezmialem Vakıf Üniversitesi Hastaneleri",
"Anadolu Üniversitesi sağlık birimleri","Sivas Cumhuriyet Üniversitesi Hastaneleri",
"Ordu Üniversitesi Hastaneleri","Rize Recep Tayyip Erdoğan Üniversitesi Hastaneleri",
"Hatay Mustafa Kemal Üniversitesi Hastaneleri","Aydın Adnan Menderes Üniversitesi Hastaneleri",
"Balıkesir Üniversitesi Hastaneleri","Manisa Celal Bayar Üniversitesi Hastaneleri",
"Muğla Sıtkı Koçman Üniversitesi Hastaneleri","Kahramanmaraş Sütçü İmam Üniversitesi Hastaneleri",
"Van Yüzüncü Yıl Üniversitesi Hastaneleri","Bolu Abant İzzet Baysal Üniversitesi Hastaneleri",
"Zonguldak Bülent Ecevit Üniversitesi Hastaneleri","Kırıkkale Üniversitesi Hastaneleri",
"Afyonkarahisar Sağlık Bilimleri Üniversitesi Hastaneleri","İzmir Katip Çelebi Üniversitesi Hastaneleri",
"Erzurum Teknik Üniversitesi sağlık birimleri","Yıldırım Beyazıt Üniversitesi sağlık birimleri",
]
CITY_HOSPITAL_TARGETS = [
"Ankara Bilkent Şehir Hastanesi","Ankara Etlik Şehir Hastanesi","İstanbul Başakşehir Çam ve Sakura Şehir Hastanesi",
"İstanbul Kartal Dr. Lütfi Kırdar Şehir Hastanesi","İstanbul Prof. Dr. Süleyman Yalçın Şehir Hastanesi",
"Adana Şehir Hastanesi","Mersin Şehir Hastanesi","Kayseri Şehir Hastanesi","Konya Şehir Hastanesi",
"Eskişehir Şehir Hastanesi","Bursa Şehir Hastanesi","Antalya Şehir Hastanesi","İzmir Şehir Hastanesi",
"Gaziantep Şehir Hastanesi","Elazığ Fethi Sekin Şehir Hastanesi","Erzurum Şehir Hastanesi",
"Malatya Şehir Hastanesi","Samsun Şehir Hastanesi","Trabzon Kanuni Eğitim ve Araştırma Hastanesi",
"Tekirdağ Şehir Hastanesi","Kocaeli Şehir Hastanesi","Yozgat Şehir Hastanesi","Manisa Şehir Hastanesi",
"Balıkesir Atatürk Şehir Hastanesi","Sakarya Eğitim ve Araştırma Hastanesi",
]
OPHTHALMOLOGY_TERMS = [
"OCT","OCT-A","optik koherens tomografi","fako","fakoemülsifikasyon","fako cihazı","fako sarf",
"optik biyometri","biyometri","kornea topografisi","YAG lazer","SLT lazer","fundus kamera",
"oftalmik mikroskop","yarık lamba","pakimetri","göz içi lens","tonometre","görme alanı",
"perimetre","refraktometre","keratometre","lensmetre","mikroperimetri","aberometre",
"oftalmik muayene ünitesi","oftalmik sarf","göz cerrahisi sarf","glokom analiz","retina cerrahisi sarf",
"vitrektomi sarf","cihaz bakım","kalibrasyon","yedek parça"
]
DISCOVERY_SOURCES = ["EKAP","ilan.gov.tr","DMO","Resmî Gazete","KİK","institution_official_pages"]

def build_institution_search_plan(institutions=None):
    targets=institutions or (UNIVERSITY_HOSPITAL_TARGETS + CITY_HOSPITAL_TARGETS)
    return [
        {"institution":institution,"source_targets":DISCOVERY_SOURCES,
         "queries":[f'"{institution}" "{term}"' for term in OPHTHALMOLOGY_TERMS],
         "verification":"verify_original_source_and_notice","live_search_enabled":False}
        for institution in targets
    ]
