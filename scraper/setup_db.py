#!/usr/bin/env python3
"""
Setup script to add UNIQUE constraint to Supabase.
"""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def setup_constraint():
    """Add UNIQUE constraint to campaigns table."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
        return False

    supabase = create_client(url, key)

    print("🔗 Connected to Supabase")
    print(f"   URL: {url}")

    # Check if constraint already exists
    print("\n📋 Checking existing constraints...")
    try:
        result = supabase.rpc(
            'exec_sql',
            {
                'query': """
                SELECT conname, contype
                FROM pg_constraint
                WHERE conrelid = 'campaigns'::regclass
                AND conname = 'unique_card_campaign';
                """
            }
        ).execute()

        if result.data:
            print("✅ Constraint 'unique_card_campaign' already exists")
            return True
    except Exception as e:
        print(f"⚠️  Could not check constraint (expected if not using RPC): {e}")

    # Add constraint using raw SQL
    print("\n➕ Adding UNIQUE constraint...")
    sql = """
    ALTER TABLE campaigns
    ADD CONSTRAINT unique_card_campaign
    UNIQUE (card_id, title);
    """

    print("⚠️  Note: This script cannot execute DDL SQL directly.")
    print("   Please run the following SQL in Supabase Dashboard → SQL Editor:")
    print("\n" + "="*60)
    print(sql)
    print("="*60)
    print("\nDirect link: https://supabase.com/dashboard/project/lmygwmivhbswqnuvsuht/sql")

    return True

if __name__ == "__main__":
    setup_constraint()
