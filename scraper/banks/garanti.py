"""
Garanti BBVA scraper - Bonus and Shop&Fly campaigns from bonus.com.tr
"""
import sys
sys.path.append('..')

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
from config import BANK_CONFIG
import re
from typing import Dict, List, Any


class GarantiScraper(BaseScraper):
    """Scraper for Garanti BBVA (Bonus, Shop&Fly) campaigns."""

    def __init__(self):
        config = BANK_CONFIG["garanti"]
        super().__init__("garanti", config["name"], config)

    def extract_campaigns(self, card_map: Dict[str, int]) -> List[Dict[str, Any]]:
        """Extract campaigns from bonus.com.tr"""
        campaigns = []
        url = self.config["urls"]["campaigns"]

        try:
            self.navigate(url, self.config.get("wait_selector"))
            html = self.page.content()
            soup = BeautifulSoup(html, 'html.parser')

            campaign_elements = soup.select(
                '.campaign-item, .kampanya-item, '
                '[class*="campaign"], [class*="kampanya"], '
                'article, .card'
            )

            self.logger.info(f"Found {len(campaign_elements)} potential campaign elements")

            for elem in campaign_elements:
                try:
                    raw = self._parse_campaign_element(elem, card_map)
                    if raw and raw.get('title'):
                        campaigns.append(raw)
                except Exception as e:
                    self.logger.warning(f"Failed to parse element: {e}")

        except Exception as e:
            self.logger.error(f"Failed to extract campaigns: {e}")
            self.errors.append(str(e))

        return campaigns

    def _parse_campaign_element(self, elem, card_map: Dict[str, int]) -> Dict[str, Any]:
        """Parse single campaign element - similar to Akbank logic."""
        title_elem = elem.select_one('h1, h2, h3, h4, .title, [class*="title"]')
        title_text = title_elem.get_text(strip=True) if title_elem else ""

        if not title_text or len(title_text) < 5:
            return None

        full_text = elem.get_text(strip=True)
        card_id = self._match_card(full_text, card_map)
        merchant = self._extract_merchant(title_text)
        discount_text = self._extract_discount_text(full_text)

        desc_elem = elem.select_one('p, .description')
        description = desc_elem.get_text(strip=True) if desc_elem else full_text[:200]

        link = elem.select_one('a[href]')
        source_url = link['href'] if link else self.config["urls"]["campaigns"]
        if source_url and not source_url.startswith('http'):
            source_url = f"https://www.bonus.com.tr{source_url}"

        return {
            "card_id": card_id,
            "title": title_text[:200],
            "description": description[:500],
            "merchant_name": merchant,
            "discount_text": discount_text,
            "conditions": "",
            "source_url": source_url,
            "date_text": "",
        }

    def _match_card(self, text: str, card_map: Dict[str, int]) -> int:
        """Match card by keywords."""
        text_lower = text.lower()
        for card_slug, card_id in card_map.items():
            keywords = self.config["cards"].get(card_slug, [card_slug])
            if any(kw.lower() in text_lower for kw in keywords):
                return card_id
        return list(card_map.values())[0]

    def _extract_merchant(self, title_text: str) -> str:
        """Extract merchant from title."""
        match = re.search(r"([\w\s&.]+?)['']?(?:da|de|ta|te)\s", title_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        words = title_text.split()
        for w in words:
            if len(w) > 2 and not w.startswith('%'):
                return w
        return "Bilinmeyen"

    def _extract_discount_text(self, text: str) -> str:
        """Extract discount text."""
        match = re.search(r'%\d+[\s,]*(?:indirim|bonus|chip|hediye)', text, re.IGNORECASE)
        if match:
            return match.group(0)
        match = re.search(r'\d+\s*TL\s*(?:indirim|bonus|hediye)', text, re.IGNORECASE)
        if match:
            return match.group(0)
        return text[:100]
