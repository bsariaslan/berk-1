"""
Campaign data normalizer - parses Turkish text into structured data.
"""
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class CampaignNormalizer:
    """Normalizes raw scraped data into campaigns table schema format."""

    # Turkish month names for date parsing
    TURKISH_MONTHS = {
        'ocak': 1, 'şubat': 2, 'subat': 2, 'mart': 3, 'nisan': 4,
        'mayıs': 5, 'mayis': 5, 'haziran': 6, 'temmuz': 7,
        'ağustos': 8, 'agustos': 8, 'eylül': 9, 'eylul': 9,
        'ekim': 10, 'kasım': 11, 'kasim': 11, 'aralık': 12, 'aralik': 12
    }

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw campaign dict into normalized schema dict.

        Input keys: card_id, title, description, merchant_name, discount_text,
                    source_url, date_text (optional), conditions (optional)

        Output keys: card_id, title, description, merchant_name, merchant_pattern,
                     discount_type, discount_rate, max_discount, min_spend,
                     start_date, end_date, conditions, source_url, scraped_at, is_active
        """
        discount_type, discount_rate, max_discount = self.parse_discount(
            raw.get("discount_text", "") or raw.get("title", "")
        )
        min_spend = self.parse_min_spend(
            (raw.get("description", "") or "") + " " + (raw.get("discount_text", "") or "")
        )
        start_date, end_date = self.parse_dates(raw.get("date_text", ""))
        merchant_pattern = self.generate_merchant_pattern(raw.get("merchant_name", ""))

        return {
            "card_id": raw["card_id"],
            "title": (raw.get("title", "") or "")[:200],
            "description": (raw.get("description", "") or "")[:500],
            "merchant_name": raw.get("merchant_name", "Bilinmeyen"),
            "merchant_pattern": merchant_pattern,
            "discount_type": discount_type,
            "discount_rate": discount_rate,
            "max_discount": max_discount,
            "min_spend": min_spend,
            "start_date": start_date,
            "end_date": end_date,
            "conditions": (raw.get("conditions", "") or "")[:500] or None,
            "source_url": raw.get("source_url", ""),
            "scraped_at": datetime.utcnow().isoformat(),
            "is_active": True,
        }

    def parse_discount(self, text: str) -> Tuple[str, float, Optional[float]]:
        """
        Parse discount from Turkish text.

        Examples:
            "%15 indirim"              -> ("percentage", 0.15, None)
            "%20'ye varan indirim"     -> ("percentage", 0.20, None)
            "100 TL indirim"           -> ("fixed", 100.0, 100.0)
            "%10 indirim (maks 75 TL)" -> ("percentage", 0.10, 75.0)
            "300 TL hediye"            -> ("fixed", 300.0, 300.0)
        """
        if not text:
            return ("percentage", 0.0, None)

        text_lower = text.lower()

        # Check for percentage first
        pct_match = re.search(r'%(\d+(?:[.,]\d+)?)', text)
        if pct_match:
            rate = float(pct_match.group(1).replace(',', '.')) / 100.0
            # Check for max discount cap
            max_match = re.search(
                r'(?:maks(?:imum)?|en fazla|max|maksimum)\s*[:.]?\s*(\d+(?:[.,]\d+)?)\s*TL',
                text, re.IGNORECASE
            )
            max_discount = float(max_match.group(1).replace(',', '.')) if max_match else None
            return ("percentage", rate, max_discount)

        # Check for fixed TL amount
        tl_match = re.search(r'(\d+(?:[.,]\d+)?)\s*TL', text, re.IGNORECASE)
        if tl_match:
            amount = float(tl_match.group(1).replace(',', '.'))
            return ("fixed", amount, amount)

        # Fallback
        return ("percentage", 0.0, None)

    def parse_min_spend(self, text: str) -> float:
        """
        Extract minimum spend from text.

        Examples:
            "500 TL ve üzeri" -> 500.0
            "1000 TL üstü"    -> 1000.0
            "minimum 750 TL"  -> 750.0
        """
        if not text:
            return 0.0

        patterns = [
            r'(\d+(?:[.,]\d+)?)\s*TL\s*(?:ve\s+)?(?:üzeri|üstü|üzerinde)',
            r'(?:minimum|min\.?|en az)\s*(\d+(?:[.,]\d+)?)\s*TL',
            r'(\d+(?:[.,]\d+)?)\s*TL\s*(?:ve üzeri|ve üstü)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', '.'))

        return 0.0

    def parse_dates(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse start/end dates from Turkish text.

        Examples:
            "1 Şubat - 31 Mart 2026"       -> ("2026-02-01", "2026-03-31")
            "15.02.2026 - 28.02.2026"       -> ("2026-02-15", "2026-02-28")
            "Son tarih: 31 Mart 2026"       -> (None, "2026-03-31")
        """
        if not text:
            return (None, None)

        # Try DD.MM.YYYY pattern
        date_pattern = r'(\d{1,2})[./](\d{1,2})[./](\d{4})'
        dates = re.findall(date_pattern, text)
        if len(dates) >= 2:
            start = f"{dates[0][2]}-{dates[0][1].zfill(2)}-{dates[0][0].zfill(2)}"
            end = f"{dates[1][2]}-{dates[1][1].zfill(2)}-{dates[1][0].zfill(2)}"
            return (start, end)
        elif len(dates) == 1:
            d = f"{dates[0][2]}-{dates[0][1].zfill(2)}-{dates[0][0].zfill(2)}"
            return (None, d)

        # Try Turkish month names: "1 Şubat 2026"
        month_pattern = r'(\d{1,2})\s+(' + '|'.join(self.TURKISH_MONTHS.keys()) + r')\s+(\d{4})'
        month_dates = re.findall(month_pattern, text.lower())
        if len(month_dates) >= 2:
            start = self._turkish_date_to_iso(month_dates[0])
            end = self._turkish_date_to_iso(month_dates[1])
            return (start, end)
        elif len(month_dates) == 1:
            d = self._turkish_date_to_iso(month_dates[0])
            return (None, d)

        return (None, None)

    def _turkish_date_to_iso(self, parts: tuple) -> str:
        """Convert Turkish date tuple to ISO format."""
        day, month_name, year = parts
        month = self.TURKISH_MONTHS.get(month_name, 1)
        return f"{year}-{str(month).zfill(2)}-{day.zfill(2)}"

    def generate_merchant_pattern(self, merchant_name: str) -> str:
        """
        Generate a lowercase search pattern for fuzzy matching.
        Strips punctuation, normalizes Turkish characters.
        """
        if not merchant_name:
            return ""
        pattern = merchant_name.lower().strip()
        # Remove common Turkish suffixes
        pattern = re.sub(r"[''](?:da|de|ta|te|nda|nde)$", "", pattern)
        # Remove trailing .com, .com.tr
        pattern = re.sub(r'\.com(?:\.tr)?$', '', pattern)
        # Strip extra whitespace
        pattern = re.sub(r'\s+', ' ', pattern).strip()
        return pattern
