const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const DB_PATH = path.join(__dirname, '..', 'data', 'campaigns.db');
const SCHEMA_PATH = path.join(__dirname, '..', 'scraper', 'schema.sql');

console.log('🌱 Starting database seeding...\n');

// Veritabanını oluştur
const db = new Database(DB_PATH);

// Şemayı yükle
const schema = fs.readFileSync(SCHEMA_PATH, 'utf-8');
db.exec(schema);
console.log('✅ Database schema created\n');

// Bankalar verisi
const banks = [
  {
    name: 'Akbank',
    slug: 'akbank',
    color: '#FF6600',
    logo_url: '/logos/akbank.svg',
    website_url: 'https://www.akbank.com'
  },
  {
    name: 'Garanti BBVA',
    slug: 'garanti',
    color: '#00854A',
    logo_url: '/logos/garanti.svg',
    website_url: 'https://www.garantibbva.com.tr'
  },
  {
    name: 'Yapı Kredi',
    slug: 'yapikredi',
    color: '#005EB8',
    logo_url: '/logos/yapikredi.svg',
    website_url: 'https://www.yapikredi.com.tr'
  },
  {
    name: 'İş Bankası',
    slug: 'isbank',
    color: '#EA0029',
    logo_url: '/logos/isbank.svg',
    website_url: 'https://www.isbank.com.tr'
  },
  {
    name: 'QNB Finansbank',
    slug: 'finansbank',
    color: '#702082',
    logo_url: '/logos/finansbank.svg',
    website_url: 'https://www.qnbfinansbank.com'
  }
];

// Bankaları ekle
const insertBank = db.prepare(`
  INSERT INTO banks (name, slug, color, logo_url, website_url)
  VALUES (@name, @slug, @color, @logo_url, @website_url)
`);

const bankIds = {};
for (const bank of banks) {
  const result = insertBank.run(bank);
  bankIds[bank.slug] = result.lastInsertRowid;
  console.log(`✅ Added bank: ${bank.name}`);
}

console.log('\n');

// Kartlar verisi
const cards = [
  // Akbank kartları
  { bank: 'akbank', name: 'Axess', slug: 'akbank-axess', type: 'credit' },
  { bank: 'akbank', name: 'Wings', slug: 'akbank-wings', type: 'credit' },

  // Garanti kartları
  { bank: 'garanti', name: 'Bonus', slug: 'garanti-bonus', type: 'credit' },
  { bank: 'garanti', name: 'Shop&Fly', slug: 'garanti-shopfly', type: 'credit' },

  // Yapı Kredi kartları
  { bank: 'yapikredi', name: 'World', slug: 'yapikredi-world', type: 'credit' },
  { bank: 'yapikredi', name: 'Play', slug: 'yapikredi-play', type: 'credit' },

  // İş Bankası kartları
  { bank: 'isbank', name: 'Maximum', slug: 'isbank-maximum', type: 'credit' },

  // Finansbank kartları
  { bank: 'finansbank', name: 'CardFinans', slug: 'finansbank-cardfinans', type: 'credit' }
];

const insertCard = db.prepare(`
  INSERT INTO cards (bank_id, name, slug, type)
  VALUES (@bank_id, @name, @slug, @type)
`);

const cardIds = {};
for (const card of cards) {
  const result = insertCard.run({
    bank_id: bankIds[card.bank],
    name: card.name,
    slug: card.slug,
    type: card.type
  });
  cardIds[card.slug] = result.lastInsertRowid;
  console.log(`✅ Added card: ${card.name}`);
}

console.log('\n');

// Sample kampanya verisi (MVP test için)
const campaigns = [
  // Akbank Axess - Trendyol
  {
    card: 'akbank-axess',
    title: 'Trendyol\'da %15 İndirim',
    description: 'Trendyol alışverişlerinizde Axess kartınızla %15 indirim kazanın.',
    merchant_name: 'Trendyol',
    merchant_pattern: 'trendyol',
    discount_type: 'percentage',
    discount_rate: 0.15,
    max_discount: 150,
    min_spend: 500,
    start_date: '2026-02-01',
    end_date: '2026-03-31',
    conditions: 'Tek seferde geçerlidir. Kampanya sadece online alışverişlerde geçerlidir.',
    source_url: 'https://www.akbank.com/kampanyalar',
    is_active: 1
  },

  // Akbank Wings - Hepsiburada
  {
    card: 'akbank-wings',
    title: 'Hepsiburada\'da 100 TL İndirim',
    description: 'Hepsiburada\'da Wings kartınızla 1000 TL ve üzeri alışverişlerinizde 100 TL indirim.',
    merchant_name: 'Hepsiburada',
    merchant_pattern: 'hepsiburada',
    discount_type: 'fixed',
    discount_rate: 100,
    max_discount: 100,
    min_spend: 1000,
    start_date: '2026-02-01',
    end_date: '2026-02-28',
    conditions: 'Ayda bir kez kullanılabilir.',
    source_url: 'https://www.akbank.com/kampanyalar',
    is_active: 1
  },

  // Garanti Bonus - Migros
  {
    card: 'garanti-bonus',
    title: 'Migros\'ta %10 BonusFlaş',
    description: 'Migros marketlerde Bonus kartınızla %10 BonusFlaş kazanın.',
    merchant_name: 'Migros',
    merchant_pattern: 'migros',
    discount_type: 'percentage',
    discount_rate: 0.10,
    max_discount: 75,
    min_spend: 300,
    start_date: '2026-02-01',
    end_date: '2026-12-31',
    conditions: 'Haftada bir kez geçerlidir.',
    source_url: 'https://www.garantibbva.com.tr/kampanyalar',
    is_active: 1
  },

  // Garanti Shop&Fly - Trendyol
  {
    card: 'garanti-shopfly',
    title: 'Trendyol\'da %20 İndirim',
    description: 'Trendyol alışverişlerinizde Shop&Fly kartınızla %20\'ye varan indirim.',
    merchant_name: 'Trendyol',
    merchant_pattern: 'trendyol',
    discount_type: 'percentage',
    discount_rate: 0.20,
    max_discount: 200,
    min_spend: 750,
    start_date: '2026-02-01',
    end_date: '2026-03-31',
    conditions: '3 taksit ve üzeri işlemlerde geçerlidir.',
    source_url: 'https://www.garantibbva.com.tr/kampanyalar',
    is_active: 1
  },

  // Yapı Kredi World - MediaMarkt
  {
    card: 'yapikredi-world',
    title: 'MediaMarkt\'ta 300 TL İndirim',
    description: 'MediaMarkt mağazalarında World kartınızla 2000 TL ve üzeri alışverişlerinizde 300 TL indirim.',
    merchant_name: 'MediaMarkt',
    merchant_pattern: 'mediamarkt',
    discount_type: 'fixed',
    discount_rate: 300,
    max_discount: 300,
    min_spend: 2000,
    start_date: '2026-02-01',
    end_date: '2026-02-28',
    conditions: 'Sadece mağazalarda geçerlidir.',
    source_url: 'https://www.yapikredi.com.tr/kampanyalar',
    is_active: 1
  },

  // Yapı Kredi Play - Spotify
  {
    card: 'yapikredi-play',
    title: 'Spotify Premium 6 Ay Hediye',
    description: 'Play kartınızla Spotify Premium üyeliğinizi 6 ay ücretsiz kullanın.',
    merchant_name: 'Spotify',
    merchant_pattern: 'spotify',
    discount_type: 'percentage',
    discount_rate: 1.0,
    max_discount: null,
    min_spend: 0,
    start_date: '2026-01-01',
    end_date: '2026-12-31',
    conditions: 'Yeni üyelere özeldir. Kampanya süresi sonunda ücretlendirme başlar.',
    source_url: 'https://www.yapikredi.com.tr/kampanyalar',
    is_active: 1
  },

  // İş Bankası Maximum - Teknosa
  {
    card: 'isbank-maximum',
    title: 'Teknosa\'da %12 İndirim',
    description: 'Teknosa alışverişlerinizde Maximum kartınızla %12 indirim fırsatı.',
    merchant_name: 'Teknosa',
    merchant_pattern: 'teknosa',
    discount_type: 'percentage',
    discount_rate: 0.12,
    max_discount: 500,
    min_spend: 1500,
    start_date: '2026-02-01',
    end_date: '2026-03-15',
    conditions: '6 taksit ve üzeri alışverişlerde geçerlidir.',
    source_url: 'https://www.isbank.com.tr/kampanyalar',
    is_active: 1
  },

  // Finansbank CardFinans - Hepsiburada
  {
    card: 'finansbank-cardfinans',
    title: 'Hepsiburada\'da %8 İndirim',
    description: 'Hepsiburada\'da CardFinans ile yapacağınız alışverişlerde %8 indirim.',
    merchant_name: 'Hepsiburada',
    merchant_pattern: 'hepsiburada',
    discount_type: 'percentage',
    discount_rate: 0.08,
    max_discount: 120,
    min_spend: 600,
    start_date: '2026-02-01',
    end_date: '2026-02-28',
    conditions: 'Online alışverişlerde geçerlidir.',
    source_url: 'https://www.qnbfinansbank.com/kampanyalar',
    is_active: 1
  },

  // Bonus - Hepsiburada (çakışma durumu için test)
  {
    card: 'garanti-bonus',
    title: 'Hepsiburada\'da 150 TL Chip-Para',
    description: 'Hepsiburada alışverişlerinizde 1200 TL ve üzeri harcamalarınızda 150 TL Chip-Para kazanın.',
    merchant_name: 'Hepsiburada',
    merchant_pattern: 'hepsiburada',
    discount_type: 'fixed',
    discount_rate: 150,
    max_discount: 150,
    min_spend: 1200,
    start_date: '2026-02-01',
    end_date: '2026-03-31',
    conditions: 'Chip-Para 30 gün içinde kullanılmalıdır.',
    source_url: 'https://www.garantibbva.com.tr/kampanyalar',
    is_active: 1
  }
];

const insertCampaign = db.prepare(`
  INSERT INTO campaigns (
    card_id, title, description, merchant_name, merchant_pattern,
    discount_type, discount_rate, max_discount, min_spend,
    start_date, end_date, conditions, source_url, is_active
  ) VALUES (
    @card_id, @title, @description, @merchant_name, @merchant_pattern,
    @discount_type, @discount_rate, @max_discount, @min_spend,
    @start_date, @end_date, @conditions, @source_url, @is_active
  )
`);

for (const campaign of campaigns) {
  insertCampaign.run({
    card_id: cardIds[campaign.card],
    ...campaign,
    card: undefined
  });
  console.log(`✅ Added campaign: ${campaign.title}`);
}

console.log('\n');

// Özet bilgi
const stats = {
  banks: db.prepare('SELECT COUNT(*) as count FROM banks').get(),
  cards: db.prepare('SELECT COUNT(*) as count FROM cards').get(),
  campaigns: db.prepare('SELECT COUNT(*) as count FROM campaigns').get()
};

console.log('📊 Database Statistics:');
console.log(`   Banks: ${stats.banks.count}`);
console.log(`   Cards: ${stats.cards.count}`);
console.log(`   Campaigns: ${stats.campaigns.count}`);
console.log('\n🎉 Seeding completed successfully!');

db.close();
