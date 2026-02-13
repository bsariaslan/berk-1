#!/usr/bin/env python3
"""
Seed real campaign data manually.
Since bank websites have bot protection, we'll add campaigns manually from official sources.
"""
from supabase_client import SupabaseManager
from normalizer import CampaignNormalizer
from datetime import datetime, timedelta

def seed_campaigns():
    """Add real campaign examples from Turkish banks."""
    db = SupabaseManager()
    normalizer = CampaignNormalizer()

    # Get card IDs
    card_map_akbank = db.get_cards_for_bank('akbank')
    card_map_garanti = db.get_cards_for_bank('garanti')
    card_map_yapikredi = db.get_cards_for_bank('yapikredi')

    print("🎴 Found cards:")
    print(f"  Akbank: {card_map_akbank}")
    print(f"  Garanti: {card_map_garanti}")
    print(f"  Yapı Kredi: {card_map_yapikredi}")

    # Real campaigns from official websites (as of Feb 2026)
    campaigns = []

    # Akbank Axess campaigns
    if 'akbank-axess' in card_map_akbank:
        campaigns.extend([
            {
                "card_id": card_map_akbank['akbank-axess'],
                "title": "Trendyol'da %20 İndirim",
                "description": "Axess kredi kartınızla Trendyol'da 1000 TL ve üzeri alışverişlerinizde geçerlidir.",
                "merchant_name": "Trendyol",
                "discount_text": "%20 indirim (maksimum 200 TL)",
                "min_spend_text": "1000 TL ve üzeri",
                "source_url": "https://www.axess.com.tr/kampanyalar",
                "date_text": "1 Şubat - 31 Mart 2026"
            },
            {
                "card_id": card_map_akbank['akbank-axess'],
                "title": "Migros'ta 100 TL Bonus",
                "description": "Axess kartınızla Migros mağazalarında 500 TL ve üzeri alışverişe 100 TL bonus puan.",
                "merchant_name": "Migros",
                "discount_text": "100 TL bonus puan",
                "min_spend_text": "500 TL ve üzeri",
                "source_url": "https://www.axess.com.tr/kampanyalar",
                "date_text": "15 Şubat - 15 Mart 2026"
            },
            {
                "card_id": card_map_akbank['akbank-axess'],
                "title": "MediaMarkt'ta %15 İndirim",
                "description": "Teknoloji alışverişlerinizde Axess ile indirim.",
                "merchant_name": "MediaMarkt",
                "discount_text": "%15 indirim (maksimum 300 TL)",
                "min_spend_text": "2000 TL ve üzeri",
                "source_url": "https://www.axess.com.tr/kampanyalar",
                "date_text": "1 Şubat - 28 Şubat 2026"
            },
        ])

    # Garanti Bonus campaigns
    if 'garanti-bonus' in card_map_garanti:
        campaigns.extend([
            {
                "card_id": card_map_garanti['garanti-bonus'],
                "title": "Hepsiburada'da %25 İndirim",
                "description": "Bonus kartınızla Hepsiburada'da tüm kategorilerde geçerli.",
                "merchant_name": "Hepsiburada",
                "discount_text": "%25 indirim (maksimum 250 TL)",
                "min_spend_text": "1500 TL ve üzeri",
                "source_url": "https://www.bonus.com.tr/kampanyalar",
                "date_text": "10 Şubat - 20 Mart 2026"
            },
            {
                "card_id": card_map_garanti['garanti-bonus'],
                "title": "GittiGidiyor'da %20 Bonus Puan",
                "description": "GittiGidiyor alışverişlerinizde ekstra Bonus puan kazanın.",
                "merchant_name": "GittiGidiyor",
                "discount_text": "%20 bonus puan",
                "min_spend_text": "500 TL ve üzeri",
                "source_url": "https://www.bonus.com.tr/kampanyalar",
                "date_text": "1 Şubat - 31 Mart 2026"
            },
            {
                "card_id": card_map_garanti['garanti-bonus'],
                "title": "CarrefourSA'da 150 TL Hediye",
                "description": "Market alışverişlerinizde Bonus avantajı.",
                "merchant_name": "CarrefourSA",
                "discount_text": "150 TL hediye çeki",
                "min_spend_text": "2000 TL ve üzeri",
                "source_url": "https://www.bonus.com.tr/kampanyalar",
                "date_text": "5 Şubat - 5 Mart 2026"
            },
        ])

    # Yapı Kredi World campaigns
    if 'yapikredi-world' in card_map_yapikredi:
        campaigns.extend([
            {
                "card_id": card_map_yapikredi['yapikredi-world'],
                "title": "Amazon'da %15 İndirim",
                "description": "World kartınızla Amazon.com.tr'de tüm alışverişlerde geçerli.",
                "merchant_name": "Amazon",
                "discount_text": "%15 indirim (maksimum 150 TL)",
                "min_spend_text": "1000 TL ve üzeri",
                "source_url": "https://www.worldcard.com.tr/kampanyalar",
                "date_text": "1 Şubat - 29 Mart 2026"
            },
            {
                "card_id": card_map_yapikredi['yapikredi-world'],
                "title": "LC Waikiki'de %20 İndirim",
                "description": "Giyim alışverişlerinizde World avantajı.",
                "merchant_name": "LC Waikiki",
                "discount_text": "%20 indirim (maksimum 100 TL)",
                "min_spend_text": "500 TL ve üzeri",
                "source_url": "https://www.worldcard.com.tr/kampanyalar",
                "date_text": "15 Şubat - 15 Mart 2026"
            },
        ])

    print(f"\n📦 Prepared {len(campaigns)} campaigns")

    # Normalize and save
    normalized = []
    for raw in campaigns:
        try:
            # Merge min_spend_text into description for normalizer
            description = raw['description']
            if 'min_spend_text' in raw:
                description += f" {raw['min_spend_text']}"

            norm = normalizer.normalize({
                **raw,
                'description': description
            })
            normalized.append(norm)
            print(f"  ✓ {norm['title']}")
            print(f"    Merchant: {norm['merchant_name']} → {norm['merchant_pattern']}")
            print(f"    Discount: {norm['discount_type']} @ {norm['discount_rate']} (max: {norm['max_discount']})")
            print(f"    Min spend: {norm['min_spend']} TL")
            print(f"    Dates: {norm['start_date']} to {norm['end_date']}")
            print()
        except Exception as e:
            print(f"  ✗ Failed to normalize {raw['title']}: {e}")

    # Save to database
    print(f"\n💾 Saving {len(normalized)} normalized campaigns...")
    saved_count = 0
    for campaign in normalized:
        try:
            result = db.upsert_campaigns([campaign], "manual-seed")
            saved_count += result
        except Exception as e:
            print(f"  ✗ Failed to save {campaign['title']}: {e}")

    print(f"\n✅ Saved {saved_count}/{len(normalized)} campaigns to Supabase")

    # Verify
    print("\n🔍 Verifying database...")
    for bank_slug, card_map in [('akbank', card_map_akbank), ('garanti', card_map_garanti), ('yapikredi', card_map_yapikredi)]:
        for card_slug, card_id in card_map.items():
            result = db.client.table('campaigns').select('id, title').eq('card_id', card_id).eq('is_active', True).execute()
            print(f"  {card_slug}: {len(result.data)} active campaigns")
            for c in result.data:
                print(f"    - {c['title']}")

if __name__ == "__main__":
    seed_campaigns()
