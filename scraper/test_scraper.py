#!/usr/bin/env python3
"""
Test scraper without hitting real bank websites.
Inserts mock campaign data to verify DB connection and normalizer.
"""
import sys
from supabase_client import SupabaseManager
from normalizer import CampaignNormalizer

def test_connection():
    """Test Supabase connection."""
    print("🔗 Testing Supabase connection...")
    try:
        db = SupabaseManager()

        # Get banks
        banks = db.client.table('banks').select('*').execute()
        print(f"✅ Connected! Found {len(banks.data)} banks:")
        for bank in banks.data:
            print(f"   - {bank['name']} ({bank['slug']})")

        # Get cards for Akbank
        print("\n🎴 Getting cards for Akbank...")
        card_map = db.get_cards_for_bank('akbank')
        print(f"✅ Found {len(card_map)} cards:")
        for slug, card_id in card_map.items():
            print(f"   - {slug} (ID: {card_id})")

        return card_map
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return {}

def test_normalizer():
    """Test Turkish text normalizer."""
    print("\n📝 Testing Normalizer...")
    normalizer = CampaignNormalizer()

    test_cases = [
        {
            "card_id": 1,
            "title": "Trendyol'da %15 İndirim",
            "description": "500 TL ve üzeri alışverişlerinizde",
            "merchant_name": "Trendyol",
            "discount_text": "%15 indirim (maksimum 150 TL)",
            "source_url": "https://test.com",
            "date_text": "1 Şubat - 31 Mart 2026"
        },
        {
            "card_id": 2,
            "title": "Migros'ta 100 TL Bonus",
            "description": "1000 TL ve üstü",
            "merchant_name": "Migros",
            "discount_text": "100 TL hediye",
            "source_url": "https://test.com",
            "date_text": "15.02.2026 - 28.02.2026"
        }
    ]

    normalized = []
    for raw in test_cases:
        norm = normalizer.normalize(raw)
        normalized.append(norm)
        print(f"\n  ✓ {norm['title']}")
        print(f"    Merchant: {norm['merchant_name']} → {norm['merchant_pattern']}")
        print(f"    Discount: {norm['discount_type']} @ {norm['discount_rate']} (max: {norm['max_discount']})")
        print(f"    Min spend: {norm['min_spend']} TL")
        print(f"    Dates: {norm['start_date']} to {norm['end_date']}")

    return normalized

def test_upsert(card_map):
    """Test upserting campaigns."""
    print("\n💾 Testing campaign upsert...")

    if not card_map:
        print("⚠️  No card_map, skipping upsert test")
        return

    db = SupabaseManager()
    normalizer = CampaignNormalizer()

    # Create test campaign
    card_id = list(card_map.values())[0]  # Get first Akbank card
    raw = {
        "card_id": card_id,
        "title": "TEST Kampanya - Scraper Test",
        "description": "Bu bir test kampanyasıdır. 500 TL ve üzeri alışverişlerde geçerlidir.",
        "merchant_name": "Test Market",
        "discount_text": "%10 indirim (maks 50 TL)",
        "source_url": "https://test.example.com/kampanya",
        "date_text": "1 Mart - 31 Mart 2026"
    }

    normalized = normalizer.normalize(raw)

    # Insert
    print(f"  Inserting: {normalized['title']}")
    saved = db.upsert_campaigns([normalized], "test")
    print(f"  ✅ Saved {saved} campaign")

    # Try inserting again (should update, not duplicate)
    print(f"  Inserting again (should update)...")
    saved = db.upsert_campaigns([normalized], "test")
    print(f"  ✅ Saved {saved} campaign (no duplicate)")

    # Verify
    result = db.client.table('campaigns').select('*').eq(
        'title', 'TEST Kampanya - Scraper Test'
    ).execute()

    print(f"  ✅ Found {len(result.data)} test campaign(s) in DB (should be 1)")

    # Cleanup
    print("  🧹 Cleaning up test data...")
    db.client.table('campaigns').delete().eq(
        'title', 'TEST Kampanya - Scraper Test'
    ).execute()
    print("  ✅ Cleanup complete")

def main():
    print("="*60)
    print("SCRAPER SYSTEM TEST")
    print("="*60)

    # Test 1: Connection
    card_map = test_connection()

    # Test 2: Normalizer
    test_normalizer()

    # Test 3: Upsert
    test_upsert(card_map)

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60)
    print("\nNext steps:")
    print("1. Add UNIQUE constraint in Supabase SQL Editor:")
    print("   ALTER TABLE campaigns ADD CONSTRAINT unique_card_campaign UNIQUE (card_id, title);")
    print("\n2. Update bank scrapers with correct CSS selectors from real sites")
    print("\n3. Run: python main.py --banks akbank")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
