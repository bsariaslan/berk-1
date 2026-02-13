import { supabase } from '@/lib/supabase';
import { compareCards, getMerchantSuggestions } from '@/lib/engine';

/**
 * POST /api/compare
 *
 * Seçili kartlar için kampanya karşılaştırması yapar
 *
 * Request body:
 * {
 *   selectedCards: [1, 2, 3],  // Kart ID'leri
 *   merchant: "Trendyol",       // Mağaza/site adı
 *   amount: 500                 // Harcama tutarı (TL)
 * }
 *
 * Response:
 * {
 *   success: true,
 *   data: {
 *     results: [...],           // Kart bazlı sonuçlar (kazanca göre sıralı)
 *     merchant: "Trendyol",
 *     amount: 500
 *   }
 * }
 */
export async function POST(request) {
  try {
    const body = await request.json();
    const { selectedCards, merchant, amount } = body;

    // Validasyon
    if (!selectedCards || !Array.isArray(selectedCards) || selectedCards.length === 0) {
      return Response.json(
        {
          success: false,
          error: 'En az bir kart seçmelisiniz.'
        },
        { status: 400 }
      );
    }

    if (!merchant || merchant.trim() === '') {
      return Response.json(
        {
          success: false,
          error: 'Mağaza/site adı girmelisiniz.'
        },
        { status: 400 }
      );
    }

    if (!amount || amount <= 0) {
      return Response.json(
        {
          success: false,
          error: 'Geçerli bir harcama tutarı girmelisiniz.'
        },
        { status: 400 }
      );
    }

    // Supabase'den aktif kampanyaları çek (cards ve banks ile joined)
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format

    const { data: campaigns, error } = await supabase
      .from('campaigns')
      .select(`
        id,
        card_id,
        title,
        description,
        merchant_name,
        merchant_pattern,
        discount_type,
        discount_rate,
        max_discount,
        min_spend,
        conditions,
        source_url,
        cards (
          id,
          name,
          slug,
          banks (
            id,
            name,
            slug,
            color
          )
        )
      `)
      .in('card_id', selectedCards)
      .eq('is_active', true)
      .or(`end_date.is.null,end_date.gte.${today}`)
      .order('card_id');

    if (error) {
      throw error;
    }

    // Karşılaştırma motorunu çalıştır
    const results = compareCards(campaigns || [], merchant, amount);

    return Response.json({
      success: true,
      data: {
        results,
        merchant,
        amount,
        totalCards: selectedCards.length,
        matchingCards: results.length
      }
    });

  } catch (error) {
    console.error('Error comparing cards:', error);
    return Response.json(
      {
        success: false,
        error: 'Karşılaştırma yapılırken bir hata oluştu.'
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/compare
 *
 * Autocomplete için mağaza önerileri döner
 */
export async function GET() {
  try {
    // Tüm aktif kampanyaları çek
    const today = new Date().toISOString().split('T')[0];

    const { data: campaigns, error } = await supabase
      .from('campaigns')
      .select('merchant_name')
      .eq('is_active', true)
      .or(`end_date.is.null,end_date.gte.${today}`)
      .order('merchant_name');

    if (error) {
      throw error;
    }

    const suggestions = getMerchantSuggestions(campaigns || []);

    return Response.json({
      success: true,
      data: suggestions
    });

  } catch (error) {
    console.error('Error fetching merchant suggestions:', error);
    return Response.json(
      {
        success: false,
        error: 'Öneriler yüklenirken bir hata oluştu.'
      },
      { status: 500 }
    );
  }
}
