-- Kredi Kartı Kampanya Karşılaştırma Uygulaması
-- Supabase PostgreSQL Schema

-- Bankalar tablosu
CREATE TABLE banks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    color TEXT NOT NULL,
    logo_url TEXT,
    website_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Kartlar tablosu
CREATE TABLE cards (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bank_id BIGINT NOT NULL REFERENCES banks(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Kampanyalar tablosu
CREATE TABLE campaigns (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    card_id BIGINT NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    merchant_name TEXT NOT NULL,
    merchant_pattern TEXT NOT NULL,
    discount_type TEXT NOT NULL CHECK(discount_type IN ('percentage', 'fixed')),
    discount_rate DOUBLE PRECISION NOT NULL,
    max_discount DOUBLE PRECISION,
    min_spend DOUBLE PRECISION DEFAULT 0,
    start_date DATE,
    end_date DATE,
    conditions TEXT,
    source_url TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- İndeksler (performans için)
CREATE INDEX idx_cards_bank_id ON cards(bank_id);
CREATE INDEX idx_campaigns_card_id ON campaigns(card_id);
CREATE INDEX idx_campaigns_active ON campaigns(is_active);
CREATE INDEX idx_campaigns_merchant ON campaigns(merchant_pattern);

-- Row Level Security (RLS) Politikaları
ALTER TABLE banks ENABLE ROW LEVEL SECURITY;
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;

-- Public read access (SELECT) - Herkes okuyabilir
CREATE POLICY "Public read access for banks" ON banks FOR SELECT USING (true);
CREATE POLICY "Public read access for cards" ON cards FOR SELECT USING (true);
CREATE POLICY "Public read access for campaigns" ON campaigns FOR SELECT USING (true);

-- Authenticated write access (INSERT/UPDATE) - Sadece service role key ile yazılabilir
-- Not: Supabase'de service_role bypass eder RLS'i, bu yüzden scraper için ek policy gerekmez
