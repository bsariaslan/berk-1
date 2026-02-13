"""
Supabase client for database operations.
"""
import os
import logging
from datetime import date
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("scraper.supabase")


class SupabaseManager:
    """Handles all Supabase read/write operations for the scraper."""

    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
        self.client: Client = create_client(url, key)
        logger.info(f"Connected to Supabase: {url}")

    def get_cards_for_bank(self, bank_slug: str) -> Dict[str, int]:
        """
        Fetch card slug -> card id mapping for a given bank.

        Args:
            bank_slug: Bank slug (e.g., "akbank", "garanti")

        Returns:
            Dict mapping card slug to card id
            Example: {"akbank-axess": 1, "akbank-wings": 2}
        """
        try:
            response = self.client.table('cards').select(
                'id, slug, name, bank_id, banks!inner(slug)'
            ).eq('banks.slug', bank_slug).execute()

            card_map = {}
            for card in response.data:
                card_map[card['slug']] = card['id']

            logger.info(f"Found {len(card_map)} cards for bank {bank_slug}: {list(card_map.keys())}")
            return card_map
        except Exception as e:
            logger.error(f"Failed to get cards for bank {bank_slug}: {e}")
            return {}

    def upsert_campaigns(self, campaigns: List[Dict[str, Any]], bank_slug: str) -> int:
        """
        Insert or update campaigns with deduplication.

        Dedup strategy: A campaign is considered duplicate if it has the same
        card_id + title. On duplicate, we update scraped_at and any changed fields.

        Args:
            campaigns: List of normalized campaign dicts
            bank_slug: Bank slug for logging

        Returns:
            Number of campaigns saved
        """
        if not campaigns:
            logger.warning(f"No campaigns to save for {bank_slug}")
            return 0

        saved = 0
        for campaign in campaigns:
            try:
                # Check for existing campaign with same card_id + title
                existing = self.client.table('campaigns').select('id').eq(
                    'card_id', campaign['card_id']
                ).eq(
                    'title', campaign['title']
                ).execute()

                if existing.data:
                    # Update existing campaign
                    campaign_id = existing.data[0]['id']
                    self.client.table('campaigns').update(campaign).eq(
                        'id', campaign_id
                    ).execute()
                    logger.debug(f"Updated campaign: {campaign['title']}")
                else:
                    # Insert new campaign
                    self.client.table('campaigns').insert(campaign).execute()
                    logger.debug(f"Inserted campaign: {campaign['title']}")
                saved += 1

            except Exception as e:
                logger.error(f"Failed to save campaign '{campaign.get('title', '?')}': {e}")

        logger.info(f"Saved {saved}/{len(campaigns)} campaigns for {bank_slug}")
        return saved

    def deactivate_expired_campaigns(self, card_ids: List[int]):
        """
        Mark campaigns as inactive if their end_date has passed.

        Args:
            card_ids: List of card IDs to check
        """
        if not card_ids:
            return

        today = date.today().isoformat()
        try:
            # Only update campaigns that have an end_date AND it has passed
            result = self.client.table('campaigns').update(
                {'is_active': False}
            ).in_(
                'card_id', card_ids
            ).lt(
                'end_date', today
            ).eq(
                'is_active', True
            ).execute()

            count = len(result.data) if result.data else 0
            if count > 0:
                logger.info(f"Deactivated {count} expired campaigns")
        except Exception as e:
            logger.error(f"Failed to deactivate expired campaigns: {e}")

    def get_active_campaign_count(self) -> int:
        """Get total active campaign count for health check."""
        try:
            result = self.client.table('campaigns').select(
                'id', count='exact'
            ).eq('is_active', True).execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Failed to get campaign count: {e}")
            return 0
