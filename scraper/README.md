# Kredi Kartı Kampanya Scraper

Türk bankalarının kredi kartı kampanyalarını otomatik olarak toplayan Python scraper sistemi.

## Desteklenen Bankalar

1. **Akbank** (Axess, Wings) - axess.com.tr
2. **Garanti BBVA** (Bonus, Shop&Fly) - bonus.com.tr
3. **Yapı Kredi** (World, Play) - worldcard.com.tr
4. **İş Bankası** (Maximum) - maximum.com.tr
5. **QNB Finansbank** (CardFinans) - cardfinans.com.tr

## Kurulum

### 1. Virtual Environment Oluştur

```bash
cd scraper
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# veya
venv\Scripts\activate  # Windows
```

### 2. Bağımlılıkları Kur

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Supabase Constraint Ekle

Supabase Dashboard → SQL Editor'da aşağıdaki SQL'i çalıştır:

```sql
ALTER TABLE campaigns
ADD CONSTRAINT unique_card_campaign
UNIQUE (card_id, title);
```

veya:

```bash
# add_unique_constraint.sql dosyasını Supabase Dashboard'a kopyala-yapıştır
```

## Kullanım

### Tüm Bankaları Scrape Et

```bash
python main.py
```

### Belirli Bankaları Scrape Et

```bash
# Sadece Akbank
python main.py --banks akbank

# Akbank ve Garanti
python main.py --banks akbank garanti

# 3 banka
python main.py --banks akbank garanti yapikredi
```

## Çıktı Örneği

```
================================================================================
Starting scrape run for 5 banks: ['akbank', 'garanti', 'yapikredi', 'isbank', 'finansbank']
================================================================================

================================================================================
Running AKBANK scraper...
================================================================================
2026-02-13 15:30:01 [scraper.akbank] INFO: Starting scraper for Akbank
2026-02-13 15:30:02 [scraper.akbank] INFO: Setting up Playwright browser...
2026-02-13 15:30:05 [scraper.akbank] INFO: Found 12 potential campaign elements
2026-02-13 15:30:08 [scraper.akbank] INFO: Extracted 12 raw campaigns
2026-02-13 15:30:09 [scraper.supabase] INFO: Saved 12/12 campaigns for akbank
2026-02-13 15:30:10 [scraper.akbank] INFO: Completed: {'bank': 'Akbank', 'scraped': 12, 'saved': 12, 'errors': 0, 'elapsed_seconds': 9.2}

================================================================================
SCRAPE RUN SUMMARY
================================================================================
  Akbank               | scraped:  12 | saved:  12 |   9.2s | ✓ OK
  Garanti BBVA         | scraped:  18 | saved:  18 |  11.5s | ✓ OK
  Yapı Kredi           | scraped:  15 | saved:  15 |  10.1s | ✓ OK
  İş Bankası           | scraped:   8 | saved:   8 |   7.3s | ✓ OK
  QNB Finansbank       | scraped:  10 | saved:  10 |   8.9s | ✓ OK
  ────────────────────────────────────────────────────────────────────────────
  TOTAL                | scraped:  63 | saved:  63 | errors: 0
================================================================================
✓ All scrapers completed successfully!
```

## Log Dosyaları

Her çalıştırmada otomatik log dosyası oluşturulur:

```
scraper_20260213_153001.log
```

## Mimari

```
main.py
  └─> [5 banka scraper]
       ├─> base_scraper.py (Playwright browser, rate limiting)
       ├─> normalizer.py (Türkçe metin parser)
       └─> supabase_client.py (DB işlemleri)
```

### Dosya Yapısı

```
scraper/
├── .env                    # Supabase credentials
├── requirements.txt        # Python bağımlılıkları
├── main.py                 # Ana orchestrator
├── config.py               # Banka URL'leri, kart mapping
├── supabase_client.py      # DB okuma/yazma + dedup
├── base_scraper.py         # Abstract base class
├── normalizer.py           # Türkçe metin → yapısal veri
├── banks/
│   ├── __init__.py
│   ├── akbank.py           # Axess, Wings
│   ├── garanti.py          # Bonus, Shop&Fly
│   ├── yapikredi.py        # World, Play
│   ├── isbank.py           # Maximum
│   └── finansbank.py       # CardFinans
└── venv/                   # Virtual environment
```

## Normalizer Örnekleri

Türkçe metinden yapısal veriye dönüşüm:

| Girdi | Çıktı |
|-------|-------|
| "%15 indirim" | `discount_type: "percentage", discount_rate: 0.15` |
| "100 TL indirim" | `discount_type: "fixed", discount_rate: 100.0` |
| "500 TL ve üzeri" | `min_spend: 500.0` |
| "1 Şubat - 31 Mart 2026" | `start_date: "2026-02-01", end_date: "2026-03-31"` |
| "Trendyol'da" | `merchant_pattern: "trendyol"` |

## Dedup Mekanizması

**2 katmanlı koruma:**
1. **DB seviyesi**: UNIQUE constraint ile `(card_id, title)` tekrar eklenemez
2. **Kod seviyesi**: `upsert_campaigns()` mevcut kampanyayı kontrol eder — varsa günceller, yoksa yeni ekler

## Hata Yönetimi

- **Kısmi başarı desteklenir**: 3/5 banka başarılıysa veri yine de kaydedilir
- **Rate limiting**: İstekler arası 3 saniye gecikme
- **Timeout**: 30 saniye navigation, 15 saniye selector
- **Logging**: Her banka için ayrı log, hata detayları

## Cron Job (Opsiyonel)

Günlük otomatik çalıştırma için crontab:

```bash
# Her gün saat 02:00'da çalıştır
0 2 * * * cd /Users/melisyilmaz/berk/1/scraper && source venv/bin/activate && python main.py >> cron.log 2>&1
```

## Sorun Giderme

### "Module not found" hatası

```bash
source venv/bin/activate  # Virtual environment'ı aktive et
pip install -r requirements.txt
```

### "Playwright browser not found"

```bash
playwright install chromium
```

### Supabase bağlantı hatası

`.env` dosyasındaki credential'ları kontrol et:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

### Selector bulunamıyor

CSS selector'lar banka sitelerinin HTML yapısına göre ayarlanmıştır. Siteler değişirse `config.py` ve ilgili banka scraper'ı güncellenmelidir.

## Geliştirme

### Yeni Banka Eklemek

1. `config.py`'a banka config ekle
2. `banks/yenibanka.py` oluştur, `BaseScraper`'ı extend et
3. `extract_campaigns()` methodunu implement et
4. `banks/__init__.py`'a import ekle
5. `main.py` SCRAPERS dict'ine ekle

### Test

```bash
# Tek banka test
python main.py --banks akbank

# Supabase'deki kampanyaları kontrol et
# https://supabase.com/dashboard/project/lmygwmivhbswqnuvsuht/editor
```
