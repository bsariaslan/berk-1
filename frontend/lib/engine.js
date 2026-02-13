/**
 * Kredi Kartı Kampanya Karşılaştırma Motoru
 *
 * Kullanıcının seçtiği kartlar için kampanya eşleştirmesi yapar
 * ve en avantajlı kartı bulur.
 */

/**
 * Fuzzy matching - Mağaza adı eşleştirmesi
 * MVP için basit toLowerCase().includes() kullanıyoruz
 *
 * @param {string} userInput - Kullanıcının girdiği mağaza adı (örn: "trendyol")
 * @param {string} pattern - Kampanyadaki merchant_pattern (örn: "trendyol")
 * @returns {boolean} - Eşleşme varsa true
 */
function fuzzyMatch(userInput, pattern) {
  if (!userInput || !pattern) return false;

  const normalizedInput = userInput.toLowerCase().trim();
  const normalizedPattern = pattern.toLowerCase().trim();

  // Basit includes kontrolü - MVP için yeterli
  return normalizedInput.includes(normalizedPattern) ||
         normalizedPattern.includes(normalizedInput);
}

/**
 * Kampanya için kazanç hesapla
 *
 * @param {object} campaign - Kampanya bilgisi
 * @param {number} amount - Harcama tutarı (TL)
 * @returns {number} - Kazanç miktarı (TL)
 */
function calculateSavings(campaign, amount) {
  // Min spend kontrolü
  if (amount < campaign.min_spend) {
    return 0;
  }

  let savings = 0;

  if (campaign.discount_type === 'percentage') {
    // Yüzde indirim
    savings = amount * campaign.discount_rate;
  } else if (campaign.discount_type === 'fixed') {
    // Sabit TL indirim
    savings = campaign.discount_rate;
  }

  // Max discount kontrolü
  if (campaign.max_discount && savings > campaign.max_discount) {
    savings = campaign.max_discount;
  }

  return Math.round(savings * 100) / 100; // 2 ondalık basamak
}

/**
 * Seçili kartlar için kampanyaları bul ve kazançları hesapla
 *
 * @param {array} campaigns - Supabase'den gelen kampanya verisi (cards ve banks ile joined)
 * @param {string} merchant - Mağaza/site adı
 * @param {number} amount - Harcama tutarı (TL)
 * @returns {array} - Kart bazlı sonuçlar (kazanca göre sıralı)
 */
function compareCards(campaigns, merchant, amount) {
  if (!campaigns || campaigns.length === 0) {
    return [];
  }

  // Kartları grupla
  const cardResults = {};

  for (const campaign of campaigns) {
    // Fuzzy matching - mağaza eşleşmesi
    if (!fuzzyMatch(merchant, campaign.merchant_pattern)) {
      continue;
    }

    // Kazanç hesapla
    const savings = calculateSavings(campaign, amount);

    if (savings <= 0) {
      continue; // Min spend karşılanmamış veya indirim yok
    }

    // Nested data'dan bilgileri al
    const card = campaign.cards;
    const bank = card.banks;

    // Kart grubu yoksa oluştur
    if (!cardResults[campaign.card_id]) {
      cardResults[campaign.card_id] = {
        card_id: campaign.card_id,
        card_name: card.name,
        card_slug: card.slug,
        bank_name: bank.name,
        bank_slug: bank.slug,
        bank_color: bank.color,
        total_savings: 0,
        campaigns: []
      };
    }

    // Kampanyayı ekle
    cardResults[campaign.card_id].campaigns.push({
      campaign_id: campaign.id,
      title: campaign.title,
      description: campaign.description,
      merchant_name: campaign.merchant_name,
      discount_type: campaign.discount_type,
      discount_rate: campaign.discount_rate,
      max_discount: campaign.max_discount,
      min_spend: campaign.min_spend,
      conditions: campaign.conditions,
      source_url: campaign.source_url,
      savings: savings
    });

    // Toplam kazancı güncelle (birden fazla kampanya olabilir)
    cardResults[campaign.card_id].total_savings += savings;
  }

  // Array'e çevir ve kazanca göre sırala
  const results = Object.values(cardResults)
    .map(card => ({
      ...card,
      total_savings: Math.round(card.total_savings * 100) / 100
    }))
    .sort((a, b) => b.total_savings - a.total_savings);

  return results;
}

/**
 * Tüm kampanyalardaki mağaza isimlerini getir (autocomplete için)
 *
 * @param {array} campaigns - Tüm aktif kampanyalar
 * @returns {array} - Unique merchant isimleri
 */
function getMerchantSuggestions(campaigns) {
  const uniqueMerchants = [...new Set(campaigns.map(c => c.merchant_name))];
  return uniqueMerchants.sort();
}

export {
  fuzzyMatch,
  calculateSavings,
  compareCards,
  getMerchantSuggestions
};
