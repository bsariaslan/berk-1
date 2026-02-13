"""
İş Bankası scraper - Maximum campaigns from maximum.com.tr
Site: Server-rendered with JSON-LD schema.org data
Structure: h3 > a campaign links, filter-buttons for categories
178+ campaigns available
"""
import sys
sys.path.append('..')

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
from config import BANK_CONFIG
import re
import json
import time
from typing import Dict, List, Any


class IsbankScraper(BaseScraper):
    """Scraper for İş Bankası (Maximum) campaigns."""

    def __init__(self):
        config = BANK_CONFIG["isbank"]
        super().__init__("isbank", config["name"], config)

    def extract_campaigns(self, card_map: Dict[str, int]) -> List[Dict[str, Any]]:
        campaigns = []
        url = self.config["urls"]["campaigns"]
        base_url = self.config.get("base_url", "https://www.maximum.com.tr")
        card_id = list(card_map.values())[0]  # Only Maximum card

        try:
            self.navigate(url, self.config.get("wait_selector"))

            # Scroll to load more campaigns
            for i in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            html = self.page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Strategy 1: Try JSON-LD structured data first
            campaigns_from_json = self._extract_from_jsonld(soup, card_id, base_url)
            if campaigns_from_json:
                self.logger.info(f"Extracted {len(campaigns_from_json)} from JSON-LD")
                return campaigns_from_json

            # Strategy 2: h3 links with campaign URLs
            campaign_links = soup.select('h3 a[href*="/kampanyalar/"]')
            self.logger.info(f"Strategy 2 (h3 links): {len(campaign_links)}")

            if not campaign_links:
                # Strategy 3: all kampanya links, filtering CTA buttons
                campaign_links = soup.select('a[href*="/kampanyalar/"]')
                campaign_links = [l for l in campaign_links
                                  if l.get_text(strip=True)
                                  and len(l.get_text(strip=True)) > 10
                                  and l.get_text(strip=True) not in ('Detaylı Bilgi', "Maximum Kart'a Başvur", 'Kampanyalar')]
                self.logger.info(f"Strategy 3 (filtered links): {len(campaign_links)}")

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
                    self.logger.warning(f"Failed to parse: {e}")

        except Exception as e:
            self.logger.error(f"Failed to extract campaigns: {e}")
            self.errors.append(str(e))

        return campaigns

    def _extract_from_jsonld(self, soup, card_id: int, base_url: str) -> List[Dict[str, Any]]:
        """Extract from JSON-LD schema.org OfferCatalog if present."""
        campaigns = []
        scripts = soup.select('script[type="application/ld+json"]')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'OfferCatalog':
                    items = data.get('itemListElement', [])
                    for item in items:
                        title = item.get('name', '') or item.get('description', '')
                        item_url = item.get('url', '')
                        if not title or len(title) < 5:
                            continue
                        if item_url and not item_url.startswith('http'):
                            item_url = f"{base_url}{item_url}"
                        merchant = self._extract_merchant(title)
                        campaigns.append({
                            "card_id": card_id,
                            "title": title[:200],
                            "description": title[:500],
                            "merchant_name": merchant,
                            "discount_text": self._extract_discount_text(title),
                            "conditions": "",
                            "source_url": item_url or "",
                            "date_text": "",
                        })
            except (json.JSONDecodeError, AttributeError):
                continue
        return campaigns

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
        match = re.search(r"[\d.]+\s*TL'?(?:ye|ye\s+[Vv]aran)?\s*(?:indirim|kazanç|hediye|[Mm]axi[Pp]uan)?", text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        taksit_match = re.search(r'(\d+)\s*(?:[Aa]ya?\s*(?:[Kk]adar|[Vv]aran)\s*)?[Tt]aksit', text)
        if taksit_match:
            return f"{taksit_match.group(1)} taksit"
        return text[:100]
