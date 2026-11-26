# Gözİhale ilan filtreleme motoru

`collector/filtering.py`, kaynak adaptörlerinin getirdiği aday ilanları filtreleyen ilk ortak katmandır.

1. İlan başlığı, kurum ve açıklama bir arada değerlendirilir.
2. Oftalmoloji anahtar kelime gruplarıyla kategori belirlenir.
3. İlgisiz kayıtlar elenir.
4. İlgili kayıtlar kategori ve öncelik eşleşmeleri üzerinden puanlanır.
5. Sonraki aşamada kayıtlar normalize edilip mükerrer kontrolüne ve veri tabanı kayıt sürecine aktarılabilir.

Bu modül kaynak sitelerden veri çekmez; kaynak adaptörü ve gerçek ilan verisi gerektirir. Puan, klinik veya ihale uygunluğu garantisi değil, ön eleme sinyalidir.
