"""Rule-based procurement procedure and challenge-route hints (not legal advice)."""
import re

METHODS = [
    ("21/b", ["21/b", "pazarlık usulü 21 b", "doğal afet", "ivedi"], "4734 sayılı Kanun 21/b: pazarlık usulü (ivedilik/özel koşullar)", "İlan/ davet ve doküman şartlarını; başvuru süresini olayın tarihine ve güncel mevzuata göre ayrıca doğrulayın."),
    ("21/c", ["21/c", "pazarlık usulü 21 c"], "4734 sayılı Kanun 21/c: pazarlık usulü (öngörülemeyen özel durum)", "İlan/davet ve başvuru süresini güncel mevzuat ve ihale belgelerine göre doğrulayın."),
    ("21/f", ["21/f", "pazarlık usulü 21 f"], "4734 sayılı Kanun 21/f: pazarlık usulü (limit ve koşullara bağlı)", "İhale türü ve parasal limitin güncel halini doğrulayın; başvuru süreleri farklılaşabilir."),
    ("22", ["22/d", "doğrudan temin", "22/a", "22/b", "22/c"], "4734 sayılı Kanun 22: doğrudan temin", "Doğrudan teminde KİK şikâyet yolu genel olarak ihale usullerindeki gibi işletilmez; sözleşme, idari başvuru ve yargı seçeneklerini somut işlem bazında inceleyin."),
    ("Açık ihale", ["açık ihale", "açık usul"], "4734 sayılı Kanun: açık ihale usulü", "İdareye şikâyet ve ardından KİK'e itirazen şikâyet süreçleri gündeme gelebilir. Süre başlangıcı, başvuru ehliyeti, işlem türü ve sözleşme aşaması kontrol edilmelidir."),
    ("39/40", ["elektronik ihale", "e-ihale", "ekap"], "Elektronik ihale / EKAP üzerinden yürütülen süreç (usul ayrıca belirlenmeli)", "EKAP işlem kayıtları, tebliğ tarihi, doküman indirme/ilan tarihleri ve başvuru sürelerini kaydedin."),
]

def analyze_procurement_rules(text: str):
    raw = text or ""
    lower = raw.casefold()
    matches=[]
    for key, tokens, label, note in METHODS:
        if any(token.casefold() in lower for token in tokens):
            matches.append({"method_key":key,"label":label,"note":note})
    explicit=[]
    for pattern in [r"(?:şikayet|şikâyet|itirazen şikayet|itirazen şikâyet)[^\\n]{0,100}", r"(?:son başvuru|başvuru süresi|ihale tarihi|tebliğ tarihi)[^\\n]{0,100}"]:
        explicit += re.findall(pattern, raw, flags=re.IGNORECASE)
    return {
        "detected_methods":matches,
        "challenge_route": ["1) İhale dokümanı/işlem ve tarihleri belirle", "2) İlgili işlem için idareye şikâyet süresini güncel mevzuattan doğrula", "3) İdarenin karar/cevap veya cevap vermeme durumuna göre itirazen şikâyet süresini ve EKAP başvuru koşullarını doğrula", "4) Sözleşme imzalanma ve bekleme süresi durumunu kontrol et"],
        "time_limits": {"exact_days":None,"reason":"Süreler yöntem, işlem, tebliğ/ilan tarihi ve mevzuat değişikliklerine göre değişir; metinden otomatik kesin süre tayin edilmedi."},
        "document_clues":explicit,
        "checklist":["İhale usulü ve madde", "İlan/davet ve doküman tarihleri", "Şikâyete konu işlem ve öğrenme/tebliğ tarihi", "İdareye başvuru ve karar/cevap tarihi", "İtirazen şikâyet başvuru şartları ve süre", "Sözleşme imza/bekleme durumu", "Başvuru bedeli, şekli ve EKAP yükümlülükleri (güncel düzenleme)", "Şartname/zeyilname ve eşit muamele iddiası için kanıtlar"],
        "disclaimer":"Bilgilendirme ve kontrol listesi amaçlıdır; hukuki görüş değildir. Kesin süre ve başvuru yöntemi ihale özelinde, güncel mevzuat ve EKAP kayıtlarından teyit edilmelidir."
    }
