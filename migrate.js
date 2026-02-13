// Supabase Migration Script
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

const SUPABASE_URL = 'https://lmygwmivhbswqnuvsuht.supabase.co';
const SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxteWd3bWl2aGJzd3FudXZzdWh0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTAxMTIwNSwiZXhwIjoyMDg2NTg3MjA1fQ.VCExgkIYiNPCXIwLzLPHD-_J3fj1e88GZfJ_OailHcI';

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

async function migrate() {
  console.log('🚀 Starting Supabase migration...\n');

  try {
    // Step 1: Create schema
    console.log('📝 Creating schema...');
    const schemaSQL = fs.readFileSync('./supabase_schema.sql', 'utf-8');

    // Supabase'de SQL çalıştırmak için RPC endpoint kullanmalıyız
    // Ancak bu tablolar için direkt REST API kullanabiliriz

    // Schema için kullanıcıdan manuel çalıştırmasını iste
    console.log('⚠️  Schema (CREATE TABLE) işlemleri için lütfen Supabase Dashboard → SQL Editor\'da aşağıdaki SQL\'i çalıştırın:\n');
    console.log('---SCHEMA SQL---');
    console.log(schemaSQL);
    console.log('---END SCHEMA SQL---\n');

    console.log('Schema SQL\'i çalıştırdıktan sonra Enter\'a basın...');

    // Wait for user input
    await new Promise(resolve => {
      process.stdin.once('data', () => resolve());
    });

    // Step 2: Insert seed data using Supabase client
    console.log('\n📦 Inserting seed data...\n');

    // Banks
    const banks = [
      { name: 'Akbank', slug: 'akbank', color: '#FF6600', logo_url: '/logos/akbank.svg', website_url: 'https://www.akbank.com' },
      { name: 'Garanti BBVA', slug: 'garanti', color: '#00854A', logo_url: '/logos/garanti.svg', website_url: 'https://www.garantibbva.com.tr' },
      { name: 'Yapı Kredi', slug: 'yapikredi', color: '#005EB8', logo_url: '/logos/yapikredi.svg', website_url: 'https://www.yapikredi.com.tr' },
      { name: 'İş Bankası', slug: 'isbank', color: '#EA0029', logo_url: '/logos/isbank.svg', website_url: 'https://www.isbank.com.tr' },
      { name: 'QNB Finansbank', slug: 'finansbank', color: '#702082', logo_url: '/logos/finansbank.svg', website_url: 'https://www.qnbfinansbank.com' }
    ];

    const { data: insertedBanks, error: banksError } = await supabase
      .from('banks')
      .insert(banks)
      .select();

    if (banksError) throw banksError;
    console.log(`✅ Inserted ${insertedBanks.length} banks`);

    // Cards
    const cards = [
      { bank_id: 1, name: 'Axess', slug: 'akbank-axess', type: 'credit' },
      { bank_id: 1, name: 'Wings', slug: 'akbank-wings', type: 'credit' },
      { bank_id: 2, name: 'Bonus', slug: 'garanti-bonus', type: 'credit' },
      { bank_id: 2, name: 'Shop&Fly', slug: 'garanti-shopfly', type: 'credit' },
      { bank_id: 3, name: 'World', slug: 'yapikredi-world', type: 'credit' },
      { bank_id: 3, name: 'Play', slug: 'yapikredi-play', type: 'credit' },
      { bank_id: 4, name: 'Maximum', slug: 'isbank-maximum', type: 'credit' },
      { bank_id: 5, name: 'CardFinans', slug: 'finansbank-cardfinans', type: 'credit' }
    ];

    const { data: insertedCards, error: cardsError } = await supabase
      .from('cards')
      .insert(cards)
      .select();

    if (cardsError) throw cardsError;
    console.log(`✅ Inserted ${insertedCards.length} cards`);

    // Campaigns
    const campaigns = [
      { card_id: 1, title: 'Trendyol\'da %15 İndirim', description: 'Trendyol alışverişlerinizde Axess kartınızla %15 indirim kazanın.', merchant_name: 'Trendyol', merchant_pattern: 'trendyol', discount_type: 'percentage', discount_rate: 0.15, max_discount: 150, min_spend: 500, start_date: '2026-02-01', end_date: '2026-03-31', conditions: 'Tek seferde geçerlidir. Kampanya sadece online alışverişlerde geçerlidir.', source_url: 'https://www.akbank.com/kampanyalar', is_active: true },
      { card_id: 2, title: 'Hepsiburada\'da 100 TL İndirim', description: 'Hepsiburada\'da Wings kartınızla 1000 TL ve üzeri alışverişlerinizde 100 TL indirim.', merchant_name: 'Hepsiburada', merchant_pattern: 'hepsiburada', discount_type: 'fixed', discount_rate: 100, max_discount: 100, min_spend: 1000, start_date: '2026-02-01', end_date: '2026-02-28', conditions: 'Ayda bir kez kullanılabilir.', source_url: 'https://www.akbank.com/kampanyalar', is_active: true },
      { card_id: 3, title: 'Migros\'ta %10 BonusFlaş', description: 'Migros marketlerde Bonus kartınızla %10 BonusFlaş kazanın.', merchant_name: 'Migros', merchant_pattern: 'migros', discount_type: 'percentage', discount_rate: 0.10, max_discount: 75, min_spend: 300, start_date: '2026-02-01', end_date: '2026-12-31', conditions: 'Haftada bir kez geçerlidir.', source_url: 'https://www.garantibbva.com.tr/kampanyalar', is_active: true },
      { card_id: 4, title: 'Trendyol\'da %20 İndirim', description: 'Trendyol alışverişlerinizde Shop&Fly kartınızla %20\'ye varan indirim.', merchant_name: 'Trendyol', merchant_pattern: 'trendyol', discount_type: 'percentage', discount_rate: 0.20, max_discount: 200, min_spend: 750, start_date: '2026-02-01', end_date: '2026-03-31', conditions: '3 taksit ve üzeri işlemlerde geçerlidir.', source_url: 'https://www.garantibbva.com.tr/kampanyalar', is_active: true },
      { card_id: 5, title: 'MediaMarkt\'ta 300 TL İndirim', description: 'MediaMarkt mağazalarında World kartınızla 2000 TL ve üzeri alışverişlerinizde 300 TL indirim.', merchant_name: 'MediaMarkt', merchant_pattern: 'mediamarkt', discount_type: 'fixed', discount_rate: 300, max_discount: 300, min_spend: 2000, start_date: '2026-02-01', end_date: '2026-02-28', conditions: 'Sadece mağazalarda geçerlidir.', source_url: 'https://www.yapikredi.com.tr/kampanyalar', is_active: true },
      { card_id: 6, title: 'Spotify Premium 6 Ay Hediye', description: 'Play kartınızla Spotify Premium üyeliğinizi 6 ay ücretsiz kullanın.', merchant_name: 'Spotify', merchant_pattern: 'spotify', discount_type: 'percentage', discount_rate: 1.0, max_discount: null, min_spend: 0, start_date: '2026-01-01', end_date: '2026-12-31', conditions: 'Yeni üyelere özeldir. Kampanya süresi sonunda ücretlendirme başlar.', source_url: 'https://www.yapikredi.com.tr/kampanyalar', is_active: true },
      { card_id: 7, title: 'Teknosa\'da %12 İndirim', description: 'Teknosa alışverişlerinizde Maximum kartınızla %12 indirim fırsatı.', merchant_name: 'Teknosa', merchant_pattern: 'teknosa', discount_type: 'percentage', discount_rate: 0.12, max_discount: 500, min_spend: 1500, start_date: '2026-02-01', end_date: '2026-03-15', conditions: '6 taksit ve üzeri alışverişlerde geçerlidir.', source_url: 'https://www.isbank.com.tr/kampanyalar', is_active: true },
      { card_id: 8, title: 'Hepsiburada\'da %8 İndirim', description: 'Hepsiburada\'da CardFinans ile yapacağınız alışverişlerde %8 indirim.', merchant_name: 'Hepsiburada', merchant_pattern: 'hepsiburada', discount_type: 'percentage', discount_rate: 0.08, max_discount: 120, min_spend: 600, start_date: '2026-02-01', end_date: '2026-02-28', conditions: 'Online alışverişlerde geçerlidir.', source_url: 'https://www.qnbfinansbank.com/kampanyalar', is_active: true },
      { card_id: 3, title: 'Hepsiburada\'da 150 TL Chip-Para', description: 'Hepsiburada alışverişlerinizde 1200 TL ve üzeri harcamalarınızda 150 TL Chip-Para kazanın.', merchant_name: 'Hepsiburada', merchant_pattern: 'hepsiburada', discount_type: 'fixed', discount_rate: 150, max_discount: 150, min_spend: 1200, start_date: '2026-02-01', end_date: '2026-03-31', conditions: 'Chip-Para 30 gün içinde kullanılmalıdır.', source_url: 'https://www.garantibbva.com.tr/kampanyalar', is_active: true }
    ];

    const { data: insertedCampaigns, error: campaignsError } = await supabase
      .from('campaigns')
      .insert(campaigns)
      .select();

    if (campaignsError) throw campaignsError;
    console.log(`✅ Inserted ${insertedCampaigns.length} campaigns`);

    // Verification
    console.log('\n📊 Verifying migration...');
    const { count: banksCount } = await supabase.from('banks').select('*', { count: 'exact', head: true });
    const { count: cardsCount } = await supabase.from('cards').select('*', { count: 'exact', head: true });
    const { count: campaignsCount } = await supabase.from('campaigns').select('*', { count: 'exact', head: true });

    console.log(`   Banks: ${banksCount}`);
    console.log(`   Cards: ${cardsCount}`);
    console.log(`   Campaigns: ${campaignsCount}`);

    console.log('\n🎉 Migration completed successfully!');

  } catch (error) {
    console.error('❌ Migration failed:', error.message);
    if (error.details) console.error('Details:', error.details);
    if (error.hint) console.error('Hint:', error.hint);
    process.exit(1);
  }
}

migrate();
