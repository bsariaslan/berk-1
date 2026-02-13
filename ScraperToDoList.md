# Scraper Implementation Plan

## Context
Uygulama şu an Supabase'e bağlı, seed data ile çalışıyor. Gerçek kampanya verilerini banka sitelerinden çekmek için Python scraper sistemi kurulacak. Scraper dizini mevcut ama içi boş (sadece eski SQLite schema var).

## Dosya Yapısı

```
scraper/
├── .env                    # Supabase credentials
├── requirements.txt        # Python bağımlılıkları
├── main.py                 # Ana orchestrator (CLI: --banks akbank garanti ...)
├── config.py               # Banka URL'leri, kart keyword mapping
├── supabase_client.py      # Supabase okuma/yazma işlemleri
├── base_scraper.py         # Abstract base class (browser, rate limit, hata yönetimi)
├── normalizer.py           # Türkçe metin → yapısal veri dönüşümü
└── banks/
    ├── __init__.py
    ├── akbank.py            # Axess, Wings
    ├── garanti.py           # Bonus, Shop&Fly
    ├── yapikredi.py         # World, Play
    ├── isbank.py            # Maximum
    └── finansbank.py        # CardFinans
```

## Mimari Özet

```
main.py → [5 banka scraper] → normalizer.py → supabase_client.py → Supabase DB
              ↓
         base_scraper.py (Playwright browser, rate limiting)
```

- Her scraper `BaseScraper`'ı extend eder, sadece `extract_campaigns()` implement eder
- Playwright ile JS-heavy sayfalar render edilir
- BeautifulSoup ile HTML parse edilir
- `normalizer.py` Türkçe metinden discount_type/rate/min_spend/tarih çıkarır
- Dedup: `(card_id, title)` eşleşmesi ile upsert

## Uygulama Adımları

### Adım 1: Altyapı dosyaları
- `scraper/.env` — Supabase URL + Service Role Key (migrate.js'den alınacak)
- `scraper/requirements.txt` — playwright, beautifulsoup4, supabase, python-dotenv, lxml
- `pip install -r requirements.txt && playwright install chromium`

### Adım 2: config.py
- Banka/Kart özel web siteleri hedeflenecek (Daha temiz veri için):
  - **Akbank**: `axess.com.tr` (Axess & Wings)
  - **Garanti**: `bonus.com.tr` (Bonus & Shop&Fly)
  - **Yapı Kredi**: `worldcard.com.tr`
  - **İş Bankası**: `maximum.com.tr`
  - **QNB**: `cardfinans.com.tr`
- Her site için `needs_playwright`, `wait_selector`, `request_delay` ayarları

### Adım 3: normalizer.py (Türkçe metin parser)
- `parse_discount()`: "%15 indirim" → (percentage, 0.15), "100 TL indirim" → (fixed, 100)
- `parse_min_spend()`: "500 TL ve üzeri" → 500
- `parse_dates()`: "1 Şubat - 31 Mart 2026" → (2026-02-01, 2026-03-31)
- `generate_merchant_pattern()`: "Trendyol'da" → "trendyol"

### Adım 4: supabase_client.py
- `get_cards_for_bank(bank_slug)` — Banka kartlarını DB'den çek (slug → id map)
- `upsert_campaigns(campaigns)` — Dedup ile insert/update
- `deactivate_expired_campaigns(card_ids)` — Süresi dolan kampanyaları is_active=false yap

### Adım 5: base_scraper.py
- Playwright browser setup/teardown
- `navigate()` ile rate-limited sayfa yükleme
- `run()` template method: browser aç → card_map çek → extract → normalize → upsert → kapat
- Hata toplama (kısmi başarı desteklenir)

### Adım 6: Banka scraperları (birer birer)
1. **akbank.py** — İlk pilot uygulama, selector'lar canlı siteden test edilir
2. **garanti.py** — Bonus/Shop&Fly ayrımı
3. **yapikredi.py** — World/Play grid layout
4. **isbank.py** — Tek kart (Maximum), en basit
5. **finansbank.py** — CardFinans, muhtemel XHR/API call intercept

Her scraper için: siteyi incele → selector bul → implement et → test et

### Adım 7: main.py orchestrator
- CLI argümanları: `--banks akbank garanti` (opsiyonel filtre)
- Tüm scraperları sırayla çalıştır, özet rapor yazdır
- Hata varsa exit code 1

### Adım 8: DB schema güncelleme
- `ALTER TABLE campaigns ADD CONSTRAINT unique_card_title UNIQUE (card_id, title)` — Dedup için
- Eski seed data temizliği (is_active=false veya DELETE)

## Kritik Dosyalar
- `scraper/base_scraper.py` — Tüm scraperların temel sınıfı
- `scraper/normalizer.py` — Türkçe metin → yapısal veri
- `scraper/supabase_client.py` — DB işlemleri
- `scraper/banks/akbank.py` — Referans implementasyon
- `migrate.js:6` — Supabase Service Role Key
- `supabase_schema.sql` — Campaigns tablo yapısı
- `frontend/lib/engine.js` — Fuzzy matching (scraper'ın ürettiği merchant_pattern ile uyumlu olmalı)

## Doğrulama
1. `python scraper/main.py --banks akbank` → Akbank kampanyaları Supabase'e yazılır
2. Supabase Dashboard'da campaigns tablosunu kontrol et
3. Frontend'de `/api/compare` ile gerçek kampanya verisiyle karşılaştırma test et
4. `python scraper/main.py` → 5 banka tamamlanır, özet rapor hatasız
