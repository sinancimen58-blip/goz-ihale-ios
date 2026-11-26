# SQLite ilan kayıt sistemi

`collector/sqlite_repository.py` ilanları kalıcı olarak saklayan ve fingerprint ile tekrarları ayıklayan ilk gerçek kayıt katmanıdır.

- Yeni ilan: kayıt + olay kaydı oluşturur.
- Değişmemiş ilan: tekrar bildirime konu olmaz, son görülme bilgisi yenilenir.
- Maddi değişiklik: günceller ve olay kaydı oluşturur.
- İlanlar ve olaylar ayrı tablolar halinde saklanır.
- Listeleme sınırı 500 kayıtla sınırlandırılmıştır.

Bu katman kaynaklardan veri çekmez. Kaynak adaptörleri bu kayıt katmanına veri beslemelidir.
