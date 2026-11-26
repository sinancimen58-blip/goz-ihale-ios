"""Heuristic specification review: flags phrases for human review, not legal conclusions."""
import re

RULES = [
    ("brand_model", "Marka/model adı veya belirli ürün ailesi", [r"\\bmarka\\b", r"\\bmodel\\b", r"(?:NIDEK|ZEISS|Alcon|Topcon|Leica|Heidelberg|CSO)"], "Marka/model adı geçen ifadelerde eşdeğer ürün kabulü, gerekçe ve teknik kriterlerin kontrol edilmesi önerilir."),
    ("equivalence", "Eşdeğerlik ve alternatif ürün", [r"eşdeğer", r"muadil", r"alternatif"], "Eşdeğer ürün değerlendirmesi için kriterlerin açık, ölçülebilir ve tutarlı olup olmadığını kontrol edin."),
    ("exclusive_feature", "Belirli yazılım/özellik/aksesuar bağımlılığı", [r"yalnızca", r"sadece", r"özel yazılım", r"lisans dongle", r"proprietary"], "Tek bir üreticiye özgü olabilecek özellik veya aksesuarın gerekçesi ve işlevsel ihtiyacı incelenmeli."),
    ("measurement", "Ölçülebilir teknik kriter", [r"\\bmm\\b", r"\\bµm\\b", r"\\bmicron\\b", r"\\bMHz\\b", r"\\bGHz\\b", r"\\bscan\\b", r"tarama"], "Ölçü, hız, çözünürlük ve performans eşikleri; klinik ihtiyaçla ilişkisi ve doğrulanabilirliği kontrol edilmeli."),
    ("certificate", "Belge/sertifika/standart şartı", [r"ISO\\s*\\d+", r"CE", r"sertifika", r"belge"], "Belge/standart şartının kapsamı, geçerliliği ve mevzuata uygun şekilde tarif edilmesi incelenmeli."),
    ("delivery_service", "Teslim, kurulum, eğitim veya servis", [r"kurulum", r"eğitim", r"servis", r"yedek parça", r"bakım"], "Teslim, kurulum, eğitim ve servis koşullarının süre, kapsam ve kabul ölçütleri açık mı kontrol edin."),
]

def analyze_specification(text: str):
    raw=text or ""
    flags=[]
    for key,label,patterns,note in RULES:
        hits=[]
        for pattern in patterns:
            for m in re.finditer(pattern,raw,re.IGNORECASE):
                hits.append(m.group(0))
        if hits:
            flags.append({"key":key,"label":label,"matched_terms":list(dict.fromkeys(hits[:12])),"review_note":note})
    return {"flags":flags,"flag_count":len(flags),"assessment":"Bu otomatik tarama hukuki uygunsuzluk tespit etmez; inceleme için dikkat noktalarını işaretler.","checklist":["Kriterler klinik/teknik ihtiyaca dayanıyor mu?","Kriterler ölçülebilir ve doğrulanabilir mi?","Eşdeğer ürünler için açık değerlendirme ölçütleri var mı?","Marka/model veya özel aksesuar bağımlılığı gerekçeli mi?","Belge ve sertifika koşulları güncel mevzuatla uyumlu mu?","Teslim, eğitim, servis ve kabul şartları açık mı?","Tüm maddeler birlikte rekabeti gereksiz sınırlıyor olabilir mi?"],"disclaimer":"Bilgilendirme amaçlı ön taramadır; kesin hukuki değerlendirme değildir. İhale dokümanının bütünü ve güncel mevzuat uzman tarafından incelenmelidir."}
