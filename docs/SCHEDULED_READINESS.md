# Scheduled readiness audit

GitHub Actions `source-readiness.yml` hafta içi UTC 06:15 ve 14:15 saatlerinde (Türkiye'de yaklaşık 09:15 ve 17:15; mevsimsel UTC offset değişimine dikkat) ve manuel tetiklemeyle çalışır.

Bu iş akışı yalnızca Python ortamını hazırlayıp kaynak katalog durumunu yazdırır. Web sitelerini taramaz, ilan çekmez ve canlı veri oluşturmaz. Gerçek taramaya geçmek için resmi kaynak URL/feed doğrulaması, adaptör aktivasyonu ve güvenli ağ erişim kuralları gerekir.
