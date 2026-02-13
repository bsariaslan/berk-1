# Scraper Implementation Plan — Hazırlık Değerlendirmesi

## Durum Özeti

| Bileşen | Durum | Hazırlık |
|---------|-------|----------|
| Supabase (URL, key, schema) | Tamamlandı | 100% |
| Comparison Engine (fuzzy match) | Tamamlandı | 100% |
| API Routes (/api/banks, /api/compare) | Tamamlandı | 100% |
| Seed Data (5 banka, 8 kart, 9 kampanya) | Tamamlandı | 100% |
| Python 3.9.6 | Mevcut | 100% |
| **Scraper Kodu** | **Hiç yok** | **0%** |

**Genel Hazırlık: ~60%** — Altyapı tamam, scraper kodu sıfırdan yazılacak.

## Hazır Olan Bileşenler

1. **Supabase Schema** (`supabase_schema.sql`) — campaigns tablosu tüm gerekli alanları içeriyor (merchant_pattern, discount_type, discount_rate, max_discount, min_spend, start/end_date, is_active)
2. **Fuzzy Matching** (`frontend/lib/engine.js`) — `toLowerCase().includes()` ile çift yönlü eşleşme; scraper'ın ürettiği `merchant_pattern` ile uyumlu
3. **API Routes** — Compare endpoint Supabase nested query ile çalışıyor, scraper verisini doğrudan kullanabilir
4. **Credentials** — Service Role Key `migrate.js:6`'da mevcut, anon key `frontend/.env.local`'de

## Eksikler ve Öneriler

### Implementasyon Öncesi Yapılması Gerekenler

1. **DB UNIQUE Constraint Ekle** (Supabase SQL Editor'da)
   ```sql
   ALTER TABLE campaigns ADD CONSTRAINT unique_card_title UNIQUE (card_id, title);
   ```
   Neden: Dedup mekanizması olmadan scraper her çalıştığında duplike kampanya ekler.
   **İki katmanlı dedup koruması:**
   - **DB seviyesi**: UNIQUE constraint ile aynı (card_id, title) tekrar eklenemez
   - **Kod seviyesi**: `upsert_campaigns()` mevcut kampanyayı kontrol eder — varsa günceller, yoksa yeni ekler

2. **Eski seed data temizliği** — Gerçek veriler geldiğinde test verileri karışmasın:
   ```sql
   DELETE FROM campaigns; -- veya is_active = false yapılabilir
   ```

3. **`scraper/schema.sql` kaldırılabilir** — SQLite schema'sı artık kullanılmıyor, kafa karıştırıcı.

### Scraper Uygulama Sırası (8 Adım)

| Adım | Dosya | Açıklama | Bağımlılık |
|------|-------|----------|------------|
| 1 | `.env` + `requirements.txt` | Credentials ve bağımlılıklar | Yok |
| 2 | `config.py` | Banka URL'leri, kart mapping | Yok |
| 3 | `normalizer.py` | Türkçe metin parser | Yok |
| 4 | `supabase_client.py` | DB okuma/yazma + dedup | Adım 1 |
| 5 | `base_scraper.py` | Abstract base class | Adım 3, 4 |
| 6 | `banks/akbank.py` (pilot) | İlk scraper — unique selector'lar | Adım 5 |
| 6b-e | Diğer 4 banka | Her biri unique HTML yapısına göre | Adım 6 |
| 7 | `main.py` | CLI orchestrator | Adım 6 |

### Her Banka Scraper'ı Unique Olacak

| Banka | Hedef Site | Zorluk | Unique Özellik |
|-------|-----------|--------|----------------|
| Akbank | axess.com.tr | Orta | Axess/Wings kart ayrımı, kampanya kartları |
| Garanti | bonus.com.tr | Orta | Bonus/Shop&Fly tab ayrımı |
| Yapı Kredi | worldcard.com.tr | Orta | World/Play grid layout |
| İş Bankası | maximum.com.tr | Kolay | Tek kart (Maximum), en basit |
| QNB | cardfinans.com.tr | Zor | Muhtemel XHR/API call intercept |

**Ortak olan (base_scraper.py):** Playwright browser, rate limiting, hata yönetimi, run() akışı
**Her bankaya özel olan:** CSS selector'lar, sayfa navigasyonu, kampanya ayrıştırma, kart eşleştirme

### Teknik Öneriler

1. **Banka ana siteleri yerine kart-özel siteleri hedefle** — Daha temiz HTML, daha az JS
2. **Rate limiting** — İstekler arası 2-5 saniye gecikme, user-agent ayarla
3. **Kısmi başarı desteği** — 3/5 banka başarılıysa yine de veri kaydet
4. **Logging** — Her banka için ayrı log, hata detayları

## Dosya Yapısı

```
scraper/
├── .env                    # SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY
├── requirements.txt        # playwright, beautifulsoup4, supabase, python-dotenv, lxml
├── main.py                 # Orchestrator (--banks akbank garanti)
├── config.py               # URL'ler, kart mapping, selector'lar
├── supabase_client.py      # get_cards_for_bank(), upsert_campaigns(), dedup
├── base_scraper.py         # BaseScraper ABC (browser, rate limit, run template)
├── normalizer.py           # parse_discount(), parse_dates(), parse_min_spend()
└── banks/
    ├── __init__.py
    ├── akbank.py            # Unique: Axess/Wings ayrımı
    ├── garanti.py           # Unique: Bonus/Shop&Fly tab
    ├── yapikredi.py         # Unique: World/Play grid
    ├── isbank.py            # Unique: Tek kart Maximum
    └── finansbank.py        # Unique: XHR intercept
```

## Kritik Dosyalar (Mevcut)
- `supabase_schema.sql` — Campaigns tablo yapısı referansı
- `migrate.js:6` — Supabase Service Role Key
- `frontend/lib/engine.js` — Fuzzy match mantığı (merchant_pattern uyumu)
- `frontend/app/api/compare/route.js` — Kampanya query yapısı

## Doğrulama
1. `python scraper/main.py --banks akbank` → Akbank kampanyaları Supabase'e yazılır
2. Supabase Dashboard → campaigns tablosunda gerçek veriler görünür
3. Frontend `/api/compare` → gerçek kampanya verisiyle test
4. `python scraper/main.py` → 5 banka tamamlanır, özet rapor hatasız
