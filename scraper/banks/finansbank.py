"""
QNB Finansbank scraper - QNB Card campaigns from qnbcard.com.tr
Note: cardfinans.com.tr redirects to qnbcard.com.tr
Site: Underscore.js templates, .box-item cards in Bootstrap grid
"""
import sys
sys.path.append('..')

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
from config import BANK_CONFIG
import re
import time
from typing import Dict, List, Any


class FinansbankScraper(BaseScraper):
    """Scraper for QNB Finansbank (CardFinans) campaigns."""

    def __init__(self):
        config = BANK_CONFIG["finansbank"]
        super().__init__("finansbank", config["name"], config)

    def extract_campaigns(self, card_map: Dict[str, int]) -> List[Dict[str, Any]]:
        campaigns = []
        url = self.config["urls"]["campaigns"]
        base_url = self.config.get("base_url", "https://www.qnbcard.com.tr")
        card_id = list(card_map.values())[0]

        try:
            self.navigate(url, self.config.get("wait_selector"))

            # Scroll to load dynamic content
            for i in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            html = self.page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Strategy 1: .box-item cards
            box_items = soup.select('.box-item')
            self.logger.info(f"Strategy 1 (.box-item): {len(box_items)}")

            if box_items:
                for item in box_items:
                    try:
                        raw = self._parse_box_item(item, card_id, base_url)
                        if raw and raw.get('title'):
                            campaigns.append(raw)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse box-item: {e}")
            else:
                # Strategy 2: kampanya links
                campaign_links = soup.select('a[href*="/kampanyalar/"]')
                campaign_links = [l for l in campaign_links
                                  if l.get_text(strip=True) and len(l.get_text(strip=True)) > 10]
                self.logger.info(f"Strategy 2 (links): {len(campaign_links)}")

                seen_titles = set()
                for link in campaign_links:
                    try:
                        title = link.get_text(strip=True)
                        if not title or len(title) < 5 or title in seen_titles:
                            continue
                        seen_titles.add(title)

                        href = link.get('href', '')
                        if href and not href.startswith('http'):
                            href = f"{base_url}{href}"

                        merchant = self._extract_merchant(title)
                        campaigns.append({
                            "card_id": card_id,
                            "title": title[:200],
                            "description": title[:500],
                            "merchant_name": merchant,
                            "discount_text": self._extract_discount_text(title),
                            "conditions": "",
                            "source_url": href or url,
                            "date_text": "",
                        })
                    except Exception as e:
                        self.logger.warning(f"Failed to parse link: {e}")

        except Exception as e:
            self.logger.error(f"Failed to extract campaigns: {e}")
            self.errors.append(str(e))

        return campaigns

    def _parse_box_item(self, elem, card_id: int, base_url: str) -> Dict[str, Any]:
        """Parse a .box-item campaign card."""
        title = ''
        img = elem.select_one('img')
        if img:
            title = img.get('alt', '') or img.get('title', '')

        if not title:
            heading = elem.select_one('h1, h2, h3, h4, p')
            if heading:
                title = heading.get_text(strip=True)

        if not title:
            link = elem.select_one('a')
            if link:
                title = link.get_text(strip=True)

        if not title or len(title) < 5:
            return None

        link = elem.select_one('a[href]')
        source_url = ''
        if link:
            source_url = link.get('href', '')
            if source_url and not source_url.startswith('http'):
                source_url = f"{base_url}{source_url}"

        merchant = self._extract_merchant(title)

        return {
            "card_id": card_id,
            "title": title[:200],
            "description": title[:500],
            "merchant_name": merchant,
            "discount_text": self._extract_discount_text(title),
            "conditions": "",
            "source_url": source_url,
            "date_text": "",
        }

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
        match = re.search(r'%\d+[\s,]*(?:indirim|kazanç|bonus|hediye)?', text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        match = re.search(r"[\d.]+\s*TL'?(?:ye|ye\s+varan)?\s*(?:indirim|kazanç|hediye|[Pp]ara[Pp]uan)?", text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        taksit_match = re.search(r'(\d+)\s*(?:aya?\s*(?:kadar|varan)\s*)?taksit', text, re.IGNORECASE)
        if taksit_match:
            return f"{taksit_match.group(1)} taksit"
        return text[:100]
