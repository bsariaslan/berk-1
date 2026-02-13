"""
Bank scraper modules.
"""
from .akbank import AkbankScraper
from .garanti import GarantiScraper
from .yapikredi import YapikrediScraper
from .isbank import IsbankScraper
from .finansbank import FinansbankScraper

__all__ = [
    'AkbankScraper',
    'GarantiScraper',
    'YapikrediScraper',
    'IsbankScraper',
    'FinansbankScraper',
]
