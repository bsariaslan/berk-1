"""
Scraper configuration for all banks.
Contains URLs, card mappings, and CSS selectors.
"""

BANK_CONFIG = {
    "akbank": {
        "name": "Akbank",
        "urls": {
            "campaigns": "https://www.axess.com.tr/kampanyalar",
        },
        "cards": {
            "akbank-axess": ["axess", "akbank axess"],
            "akbank-wings": ["wings", "akbank wings"],
        },
        # Real selectors from axess.com.tr: owl-carousel based layout
        "wait_selector": ".boutiqueWrapper, .owl-carousel, .owl-item",
        "campaign_selector": ".owl-item a[href*='kampanyadetay']",
        "needs_playwright": True,
        "request_delay": 3,
        "base_url": "https://www.axess.com.tr",
    },
    "garanti": {
        "name": "Garanti BBVA",
        "urls": {
            "campaigns": "https://www.bonus.com.tr/kampanyalar",
        },
        "cards": {
            "garanti-bonus": ["bonus", "bonus card", "bonuscard"],
            "garanti-shopfly": ["shop&fly", "shop and fly", "shopfly", "shop & fly"],
        },
        "wait_selector": "li a[href*='/kampanyalar/'], h3",
        "campaign_selector": "li a[href*='/kampanyalar/']",
        "needs_playwright": True,
        "request_delay": 3,
        "base_url": "https://www.bonus.com.tr",
    },
    "yapikredi": {
        "name": "Yapı Kredi",
        "urls": {
            "campaigns": "https://www.worldcard.com.tr/kampanyalar",
        },
        "cards": {
            "yapikredi-world": ["world", "world card", "worldcard"],
            "yapikredi-play": ["play", "play card", "playcard"],
        },
        # Real structure: col-lg-4 grid with picture + p + last-day
        "wait_selector": ".col-lg-4 a[href], .last-day",
        "campaign_selector": ".col-lg-4",
        "needs_playwright": True,
        "request_delay": 3,
        "base_url": "https://www.worldcard.com.tr",
    },
    "isbank": {
        "name": "İş Bankası",
        "urls": {
            "campaigns": "https://www.maximum.com.tr/kampanyalar",
        },
        "cards": {
            "isbank-maximum": ["maximum", "maximum card", "maximum kart"],
        },
        # Real structure: campaign-card div with h3 > a
        "wait_selector": "h3 a[href*='/kampanyalar/']",
        "campaign_selector": "h3 a[href*='/kampanyalar/']",
        "needs_playwright": True,
        "request_delay": 3,
        "base_url": "https://www.maximum.com.tr",
    },
    "finansbank": {
        "name": "QNB Finansbank",
        "urls": {
            # cardfinans.com.tr redirects to qnbcard.com.tr
            "campaigns": "https://www.qnbcard.com.tr/kampanyalar",
        },
        "cards": {
            "finansbank-cardfinans": ["cardfinans", "card finans", "qnb", "parapuan"],
        },
        # Real structure: .box-item inside col-lg-4 grid
        "wait_selector": ".box-item",
        "campaign_selector": ".box-item",
        "needs_playwright": True,
        "request_delay": 3,
        "base_url": "https://www.qnbcard.com.tr",
    },
}

# Updated Chrome user agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# Browser viewport
VIEWPORT = {"width": 1280, "height": 720}

# Timeouts (milliseconds)
NAVIGATION_TIMEOUT = 60000  # 60 seconds
SELECTOR_TIMEOUT = 20000    # 20 seconds
