#!/usr/bin/env python3
"""Check database for scraped campaigns."""
from supabase_client import SupabaseManager

db = SupabaseManager()

# Get all active campaigns count by bank
print("=" * 70)
print("VERITABANINDA AKTIF KAMPANYALAR")
print("=" * 70)

banks = ['akbank', 'garanti', 'yapikredi', 'isbank', 'finansbank']
total = 0

for bank_slug in banks:
    card_map = db.get_cards_for_bank(bank_slug)
    bank_total = 0

    for card_slug, card_id in card_map.items():
        result = db.client.table('campaigns').select('id, title, merchant_name').eq('card_id', card_id).eq('is_active', True).execute()
        count = len(result.data)
        bank_total += count
        total += count

        if count > 0:
            print(f"\n{card_slug.upper()}: {count} kampanya")
            for i, c in enumerate(result.data[:3], 1):  # Show first 3
                print(f"  {i}. {c['title']} - {c['merchant_name']}")
            if count > 3:
                print(f"  ... ve {count - 3} kampanya daha")

print("\n" + "=" * 70)
print(f"TOPLAM: {total} AKTİF KAMPANYA")
print("=" * 70)
