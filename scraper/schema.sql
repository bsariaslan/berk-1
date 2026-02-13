-- Kredi Kartı Kampanya Karşılaştırma Uygulaması
-- SQLite Database Schema

-- Bankalar tablosu
CREATE TABLE IF NOT EXISTS banks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    color TEXT NOT NULL,
    logo_url TEXT,
    website_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Kartlar tablosu
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    type TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES banks(id) ON DELETE CASCADE
);

-- Kampanyalar tablosu
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    merchant_name TEXT NOT NULL,
    merchant_pattern TEXT NOT NULL,
    discount_type TEXT NOT NULL CHECK(discount_type IN ('percentage', 'fixed')),
    discount_rate REAL NOT NULL,
    max_discount REAL,
    min_spend REAL DEFAULT 0,
    start_date DATE,
    end_date DATE,
    conditions TEXT,
    source_url TEXT,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);

-- İndeksler (performans için)
CREATE INDEX IF NOT EXISTS idx_cards_bank_id ON cards(bank_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_card_id ON campaigns(card_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_active ON campaigns(is_active);
CREATE INDEX IF NOT EXISTS idx_campaigns_merchant ON campaigns(merchant_pattern);
