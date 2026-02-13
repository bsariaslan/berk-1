-- Kredi Kartı Kampanya Karşılaştırma Uygulaması
-- Supabase Seed Data

-- Bankalar verisi
INSERT INTO banks (name, slug, color, logo_url, website_url) VALUES
('Akbank', 'akbank', '#FF6600', '/logos/akbank.svg', 'https://www.akbank.com'),
('Garanti BBVA', 'garanti', '#00854A', '/logos/garanti.svg', 'https://www.garantibbva.com.tr'),
('Yapı Kredi', 'yapikredi', '#005EB8', '/logos/yapikredi.svg', 'https://www.yapikredi.com.tr'),
('İş Bankası', 'isbank', '#EA0029', '/logos/isbank.svg', 'https://www.isbank.com.tr'),
('QNB Finansbank', 'finansbank', '#702082', '/logos/finansbank.svg', 'https://www.qnbfinansbank.com');

-- Kartlar verisi
INSERT INTO cards (bank_id, name, slug, type) VALUES
-- Akbank kartları (bank_id = 1)
(1, 'Axess', 'akbank-axess', 'credit'),
(1, 'Wings', 'akbank-wings', 'credit'),

-- Garanti kartları (bank_id = 2)
(2, 'Bonus', 'garanti-bonus', 'credit'),
(2, 'Shop&Fly', 'garanti-shopfly', 'credit'),

-- Yapı Kredi kartları (bank_id = 3)
(3, 'World', 'yapikredi-world', 'credit'),
(3, 'Play', 'yapikredi-play', 'credit'),

-- İş Bankası kartları (bank_id = 4)
(4, 'Maximum', 'isbank-maximum', 'credit'),

-- Finansbank kartları (bank_id = 5)
(5, 'CardFinans', 'finansbank-cardfinans', 'credit');

-- Kampanyalar verisi
INSERT INTO campaigns (
    card_id, title, description, merchant_name, merchant_pattern,
    discount_type, discount_rate, max_discount, min_spend,
    start_date, end_date, conditions, source_url, is_active
) VALUES
-- Akbank Axess - Trendyol (card_id = 1)
(1, 'Trendyol''da %15 İndirim', 'Trendyol alışverişlerinizde Axess kartınızla %15 indirim kazanın.', 'Trendyol', 'trendyol', 'percentage', 0.15, 150, 500, '2026-02-01', '2026-03-31', 'Tek seferde geçerlidir. Kampanya sadece online alışverişlerde geçerlidir.', 'https://www.akbank.com/kampanyalar', TRUE),

-- Akbank Wings - Hepsiburada (card_id = 2)
(2, 'Hepsiburada''da 100 TL İndirim', 'Hepsiburada''da Wings kartınızla 1000 TL ve üzeri alışverişlerinizde 100 TL indirim.', 'Hepsiburada', 'hepsiburada', 'fixed', 100, 100, 1000, '2026-02-01', '2026-02-28', 'Ayda bir kez kullanılabilir.', 'https://www.akbank.com/kampanyalar', TRUE),

-- Garanti Bonus - Migros (card_id = 3)
(3, 'Migros''ta %10 BonusFlaş', 'Migros marketlerde Bonus kartınızla %10 BonusFlaş kazanın.', 'Migros', 'migros', 'percentage', 0.10, 75, 300, '2026-02-01', '2026-12-31', 'Haftada bir kez geçerlidir.', 'https://www.garantibbva.com.tr/kampanyalar', TRUE),

-- Garanti Shop&Fly - Trendyol (card_id = 4)
(4, 'Trendyol''da %20 İndirim', 'Trendyol alışverişlerinizde Shop&Fly kartınızla %20''ye varan indirim.', 'Trendyol', 'trendyol', 'percentage', 0.20, 200, 750, '2026-02-01', '2026-03-31', '3 taksit ve üzeri işlemlerde geçerlidir.', 'https://www.garantibbva.com.tr/kampanyalar', TRUE),

-- Yapı Kredi World - MediaMarkt (card_id = 5)
(5, 'MediaMarkt''ta 300 TL İndirim', 'MediaMarkt mağazalarında World kartınızla 2000 TL ve üzeri alışverişlerinizde 300 TL indirim.', 'MediaMarkt', 'mediamarkt', 'fixed', 300, 300, 2000, '2026-02-01', '2026-02-28', 'Sadece mağazalarda geçerlidir.', 'https://www.yapikredi.com.tr/kampanyalar', TRUE),

-- Yapı Kredi Play - Spotify (card_id = 6)
(6, 'Spotify Premium 6 Ay Hediye', 'Play kartınızla Spotify Premium üyeliğinizi 6 ay ücretsiz kullanın.', 'Spotify', 'spotify', 'percentage', 1.0, NULL, 0, '2026-01-01', '2026-12-31', 'Yeni üyelere özeldir. Kampanya süresi sonunda ücretlendirme başlar.', 'https://www.yapikredi.com.tr/kampanyalar', TRUE),

-- İş Bankası Maximum - Teknosa (card_id = 7)
(7, 'Teknosa''da %12 İndirim', 'Teknosa alışverişlerinizde Maximum kartınızla %12 indirim fırsatı.', 'Teknosa', 'teknosa', 'percentage', 0.12, 500, 1500, '2026-02-01', '2026-03-15', '6 taksit ve üzeri alışverişlerde geçerlidir.', 'https://www.isbank.com.tr/kampanyalar', TRUE),

-- Finansbank CardFinans - Hepsiburada (card_id = 8)
(8, 'Hepsiburada''da %8 İndirim', 'Hepsiburada''da CardFinans ile yapacağınız alışverişlerde %8 indirim.', 'Hepsiburada', 'hepsiburada', 'percentage', 0.08, 120, 600, '2026-02-01', '2026-02-28', 'Online alışverişlerde geçerlidir.', 'https://www.qnbfinansbank.com/kampanyalar', TRUE),

-- Bonus - Hepsiburada (çakışma durumu için test) (card_id = 3)
(3, 'Hepsiburada''da 150 TL Chip-Para', 'Hepsiburada alışverişlerinizde 1200 TL ve üzeri harcamalarınızda 150 TL Chip-Para kazanın.', 'Hepsiburada', 'hepsiburada', 'fixed', 150, 150, 1200, '2026-02-01', '2026-03-31', 'Chip-Para 30 gün içinde kullanılmalıdır.', 'https://www.garantibbva.com.tr/kampanyalar', TRUE);

-- Verification query
SELECT
    (SELECT COUNT(*) FROM banks) as banks_count,
    (SELECT COUNT(*) FROM cards) as cards_count,
    (SELECT COUNT(*) FROM campaigns) as campaigns_count;
