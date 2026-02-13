"""
Base scraper class - provides common functionality for all bank scrapers.
"""
import abc
import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, Page
from supabase_client import SupabaseManager
from normalizer import CampaignNormalizer
from config import USER_AGENT, VIEWPORT, NAVIGATION_TIMEOUT, SELECTOR_TIMEOUT


class BaseScraper(abc.ABC):
    """Abstract base class for all bank scrapers."""

    def __init__(self, bank_slug: str, bank_name: str, config: Dict[str, Any]):
        self.bank_slug = bank_slug
        self.bank_name = bank_name
        self.config = config
        self.logger = logging.getLogger(f"scraper.{bank_slug}")
        self.db = SupabaseManager()
        self.normalizer = CampaignNormalizer()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.context = None
        self.request_delay = config.get('request_delay', 2)
        self.campaigns_scraped = 0
        self.campaigns_saved = 0
        self.errors: List[str] = []

    def setup_browser(self):
        """Launch headless Chromium via Playwright."""
        self.logger.info("Setting up Playwright browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,  # Run in background (production mode)
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        )
        self.context = self.browser.new_context(
            locale='tr-TR',
            user_agent=USER_AGENT,
            viewport=VIEWPORT,
            extra_http_headers={
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            }
        )
        self.page = self.context.new_page()
        self.logger.info("Browser ready")

    def teardown_browser(self):
        """Close browser and playwright."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Browser closed")

    def navigate(self, url: str, wait_selector: Optional[str] = None):
        """Navigate to URL with optional wait for selector."""
        self.logger.info(f"Navigating to {url}")
        try:
            self.page.goto(url, wait_until='domcontentloaded', timeout=NAVIGATION_TIMEOUT)
        except Exception as e:
            self.logger.warning(f"Navigation timeout, continuing anyway: {e}")
            # Don't raise - try to parse whatever loaded

        # Wait for JavaScript to render content
        time.sleep(3)

        if wait_selector:
            try:
                self.page.wait_for_selector(wait_selector, timeout=SELECTOR_TIMEOUT)
            except Exception as e:
                self.logger.warning(f"Selector wait timeout ({wait_selector}), continuing with page content")

        time.sleep(self.request_delay)

    def run(self) -> Dict[str, Any]:
        """
        Main execution flow. Returns summary dict.

        Steps:
        1. Setup browser
        2. Get card IDs from Supabase for this bank
        3. Extract raw campaign data (implemented by subclass)
        4. Normalize each campaign
        5. Write to Supabase (upsert with dedup)
        6. Mark expired campaigns as inactive
        7. Cleanup
        """
        self.logger.info(f"Starting scraper for {self.bank_name}")
        start_time = time.time()

        try:
            self.setup_browser()

            # Step 1: Get card IDs from Supabase for this bank
            card_map = self.db.get_cards_for_bank(self.bank_slug)

            if not card_map:
                raise ValueError(f"No cards found for bank: {self.bank_slug}")

            # Step 2: Extract raw campaign data (implemented by subclass)
            raw_campaigns = self.extract_campaigns(card_map)
            self.campaigns_scraped = len(raw_campaigns)
            self.logger.info(f"Extracted {self.campaigns_scraped} raw campaigns")

            # Step 3: Normalize each campaign
            normalized = []
            for raw in raw_campaigns:
                try:
                    norm = self.normalizer.normalize(raw)
                    normalized.append(norm)
                except Exception as e:
                    self.logger.warning(f"Normalization failed for campaign: {raw.get('title', 'unknown')} - {e}")
                    self.errors.append(f"Normalization: {str(e)}")

            self.logger.info(f"Normalized {len(normalized)} campaigns")

            # Step 4: Write to Supabase (upsert with dedup)
            self.campaigns_saved = self.db.upsert_campaigns(normalized, self.bank_slug)

            # Step 5: Mark expired campaigns as inactive
            self.db.deactivate_expired_campaigns(list(card_map.values()))

        except Exception as e:
            self.logger.error(f"Scraper failed for {self.bank_name}: {e}")
            self.errors.append(f"Fatal: {str(e)}")

        finally:
            self.teardown_browser()

        elapsed = round(time.time() - start_time, 2)
        summary = {
            "bank": self.bank_name,
            "scraped": self.campaigns_scraped,
            "saved": self.campaigns_saved,
            "errors": len(self.errors),
            "error_details": self.errors[:5],  # limit stored errors
            "elapsed_seconds": elapsed
        }
        self.logger.info(f"Completed: {summary}")
        return summary

    @abc.abstractmethod
    def extract_campaigns(self, card_map: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Subclass must implement this.

        Args:
            card_map: Dict mapping card slug to card_id
                      e.g. {"akbank-axess": 1, "akbank-wings": 2}

        Returns:
            List of raw campaign dicts with at least:
            - card_id (int)
            - title (str)
            - description (str, optional)
            - merchant_name (str)
            - discount_text (str) -- raw Turkish text like "%15 indirim"
            - conditions (str, optional)
            - source_url (str)
            - date_text (str, optional) -- raw date text for parsing
        """
        pass
