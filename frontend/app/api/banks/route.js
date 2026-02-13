import { supabase } from '@/lib/supabase';

/**
 * GET /api/banks
 *
 * Tüm bankaları kartlarıyla birlikte döner
 * Response: [{id, name, slug, color, logo_url, website_url, cards: [...]}]
 */
export async function GET() {
  try {
    // Supabase ile bankaları ve kartlarını çek (nested query)
    const { data: banks, error } = await supabase
      .from('banks')
      .select(`
        id,
        name,
        slug,
        color,
        logo_url,
        website_url,
        cards (
          id,
          name,
          slug,
          type
        )
      `)
      .order('name');

    if (error) {
      throw error;
    }

    return Response.json({
      success: true,
      data: banks
    });

  } catch (error) {
    console.error('Error fetching banks:', error);
    return Response.json(
      {
        success: false,
        error: 'Bankalar yüklenirken bir hata oluştu.'
      },
      { status: 500 }
    );
  }
}
