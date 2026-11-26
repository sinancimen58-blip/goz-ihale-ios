# Gözİhale API testleri

Bu testler demo API'sinin temel davranışlarını doğrulamak içindir. Canlı ihale toplama test edilmez.

## Çalıştırma

Backend klasöründe:

```bash
pip install -r requirements.txt
pytest -q
```

Testler ayrı bir geçici SQLite dosyası kullanır.

## Kontroller

- Sağlık uç noktası ve canlı veri olmadığı bilgisinin açıkça sunulması
- Demo kayıtların listelenmesi ve kategori filtresi
- Metin araması
- Olmayan kayıt için 404
- Yeni kayıt ekleme ve aynı ID ile tekrar ekleme durumunda 409

Test kodu GitHub'a eklendi; henüz gerçek bir CI ortamında yürütülüp doğrulanmamıştır.
