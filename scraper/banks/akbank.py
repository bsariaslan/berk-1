"""
Akbank scraper - Axess and Wings campaigns from axess.com.tr
Site: jQuery + Owl Carousel, campaigns as image cards
Detail links: /axess/kampanyadetay/8/{id}/{slug}
"""
import sys
sys.path.append('..')

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
from config import BANK_CONFIG
import re
import time
from typing import Dict, List, Any


class AkbankScraper(BaseScraper):
    """Scraper for Akbank (Axess, Wings) campaigns."""

    def __init__(self):
        config = BANK_CONFIG["akbank"]
        super().__init__("akbank", config["name"], config)

    def extract_campaigns(self, card_map: Dict[str, int]) -> List[Dict[str, Any]]:
        campaigns = []
        url = self.config["urls"]["campaigns"]
        base_url = self.config.get("base_url", "https://www.axess.com.tr")

        try:
            self.navigate(url, self.config.get("wait_selector"))

            # Scroll to trigger lazy-loaded content
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            html = self.page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Strategy 1: campaign detail links
            campaign_links = soup.select('a[href*="kampanyadetay"]')
            self.logger.info(f"Strategy 1 (kampanyadetay links): {len(campaign_links)}")

            if not campaign_links:
                # Strategy 2: any kampanya link
                campaign_links = soup.select('a[href*="kampanya"]')
                self.logger.info(f"Strategy 2 (kampanya links): {len(campaign_links)}")

            if not campaign_links:
                # Strategy 3: owl-item links
                campaign_links = soup.select('.owl-item a[href]')
                self.logger.info(f"Strategy 3 (owl-item links): {len(campaign_links)}")

            seen_urls = set()
            for link in campaign_links:
                try:
                    href = link.get('href', '')
                    if not href or href in seen_urls or href == '#':
                        continue
                    seen_urls.add(href)

                    if not href.startswith('http'):
                        href = f"{base_url}{href}"

                    # Get title from img alt or link text
                    title = ''
                    img = link.select_one('img')
                    if img:
                        title = img.get('alt', '') or img.get('title', '')
                    if not title:
                        title = link.get_text(strip=True)
                    if not title:
                        title = link.get('title', '')

                    if not title or len(title) < 5:
                        continue

                    card_id = self._match_card(title, card_map)
                    merchant = self._extract_merchant(title)

                    campaigns.append({
                        "card_id": card_id,
                        "title": title[:200],
                        "description": title[:500],
                        "merchant_name": merchant,
                        "discount_text": self._extract_discount_text(title),
                        "conditions": "",
                        "source_url": href,
                        "date_text": "",
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to parse link: {e}")

        except Exception as e:
            self.logger.error(f"Failed to extract campaigns from {url}: {e}")
            self.errors.append(f"Extraction failed: {str(e)}")

        return campaigns

    def _match_card(self, text: str, card_map: Dict[str, int]) -> int:
        text_lower = text.lower()
        for card_slug, card_id in card_map.items():
            keywords = self.config["cards"].get(card_slug, [card_slug])
            if any(kw.lower() in text_lower for kw in keywords):
                return card_id
        return list(card_map.values())[0]

    def _extract_merchant(self, title_text: str) -> str:
        match = re.search(r"([\w\s&.]+?)[''\u2019]?(?:da|de|ta|te|nda|nde)\s", title_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        match = re.search(r'([A-ZĞÜŞÖÇİ][a-zğüşöçı]+(?:\s+[A-ZĞÜŞÖÇİ][a-zğüşöçı]+)*)', title_text)
        if match:
            return match.group(1).strip()
        words = title_text.split()
        for w in words:
            if len(w) > 2 and not w.startswith('%'):
                return w
        return "Bilinmeyen"

    def _extract_discount_text(self, text: str) -> str:
        match = re.search(r'%\d+[\s,]*(?:indirim|kazanç|bonus|hediye|chip-?para)?', text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        match = re.search(r"[\d.]+\s*TL'?(?:ye|ye\s+varan)?\s*(?:indirim|kazanç|hediye|bonus)?", text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        taksit_match = re.search(r'(\d+)\s*(?:aya?\s*(?:kadar|varan)\s*)?taksit', text, re.IGNORECASE)
        if taksit_match:
            return f"{taksit_match.group(1)} taksit"
        return text[:100]
