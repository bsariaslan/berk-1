"""
Yapı Kredi scraper - World and Play campaigns from worldcard.com.tr
Site: Underscore.js templates, Bootstrap grid (col-lg-4)
Structure: picture + img + .last-day date + p title
"""
import sys
sys.path.append('..')

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
from config import BANK_CONFIG
import re
import time
from typing import Dict, List, Any


class YapikrediScraper(BaseScraper):
    """Scraper for Yapı Kredi (World, Play) campaigns."""

    def __init__(self):
        config = BANK_CONFIG["yapikredi"]
        super().__init__("yapikredi", config["name"], config)

    def extract_campaigns(self, card_map: Dict[str, int]) -> List[Dict[str, Any]]:
        campaigns = []
        url = self.config["urls"]["campaigns"]
        base_url = self.config.get("base_url", "https://www.worldcard.com.tr")

        try:
            self.navigate(url, self.config.get("wait_selector"))

            # Scroll to trigger "Daha Fazla Göster" and load more
            for i in range(5):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            # Try clicking "Daha Fazla Göster" button
            try:
                more_btn = self.page.query_selector('text="Daha Fazla Göster"')
                if more_btn:
                    for _ in range(3):
                        more_btn.click()
                        time.sleep(2)
                        more_btn = self.page.query_selector('text="Daha Fazla Göster"')
                        if not more_btn:
                            break
            except Exception:
                pass

            html = self.page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Strategy 1: col-lg-4 grid items (real site structure)
            grid_items = soup.select('.col-lg-4')
            self.logger.info(f"Strategy 1 (.col-lg-4 items): {len(grid_items)}")

            if grid_items:
                for item in grid_items:
                    try:
                        raw = self._parse_grid_item(item, card_map, base_url)
                        if raw and raw.get('title'):
                            campaigns.append(raw)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse grid item: {e}")
            else:
                # Strategy 2: links with kampanya
                campaign_links = soup.select('a[href*="/kampanyalar/"]')
                campaign_links = [l for l in campaign_links
                                  if l.get_text(strip=True) and len(l.get_text(strip=True)) > 10]
                self.logger.info(f"Strategy 2 (links): {len(campaign_links)}")

                seen_titles = set()
                for link in campaign_links:
                    try:
                        # Get title from img alt
                        title = ''
                        img = link.select_one('img')
                        if img:
                            title = img.get('alt', '')
                        if not title:
                            title = link.get_text(strip=True)

                        if not title or len(title) < 5 or title in seen_titles:
                            continue
                        seen_titles.add(title)

                        href = link.get('href', '')
                        if href and not href.startswith('http'):
                            href = f"{base_url}{href}"

                        card_id = self._match_card(title, card_map)
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

    def _parse_grid_item(self, elem, card_map: Dict[str, int], base_url: str) -> Dict[str, Any]:
        """Parse a col-lg-4 campaign grid item."""
        title = ''

        # Get title from img alt (most reliable)
        img = elem.select_one('img')
        if img:
            title = img.get('alt', '') or img.get('title', '')

        # Or from <p> tag (PageTitle in template)
        if not title:
            p_tag = elem.select_one('p')
            if p_tag:
                title = p_tag.get_text(strip=True)

        if not title or len(title) < 5:
            return None

        # Get URL
        link = elem.select_one('a[href]')
        source_url = ''
        if link:
            source_url = link.get('href', '')
            if source_url and not source_url.startswith('http'):
                source_url = f"{base_url}{source_url}"

        # Get date from .last-day element
        date_text = ''
        last_day = elem.select_one('.last-day p')
        if last_day:
            date_text = last_day.get_text(strip=True)

        card_id = self._match_card(title, card_map)
        merchant = self._extract_merchant(title)

        return {
            "card_id": card_id,
            "title": title[:200],
            "description": title[:500],
            "merchant_name": merchant,
            "discount_text": self._extract_discount_text(title),
            "conditions": "",
            "source_url": source_url,
            "date_text": date_text,
        }

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
        match = re.search(r'%\d+[\s,]*(?:indirim|kazanç|bonus|hediye)?', text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        match = re.search(r"[\d.]+\s*TL'?(?:ye|ye\s+varan)?\s*(?:indirim|kazanç|hediye|puan)?", text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        taksit_match = re.search(r'(\d+)\s*(?:aya?\s*(?:kadar|varan)\s*)?taksit', text, re.IGNORECASE)
        if taksit_match:
            return f"{taksit_match.group(1)} taksit"
        return text[:100]
