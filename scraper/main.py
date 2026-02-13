#!/usr/bin/env python3
"""
Main scraper orchestrator - runs all bank scrapers.

Usage:
    python main.py                    # Run all banks
    python main.py --banks akbank     # Run only Akbank
    python main.py --banks akbank garanti  # Run Akbank and Garanti
"""
import sys
import logging
import argparse
from datetime import datetime
from banks.akbank import AkbankScraper
from banks.garanti import GarantiScraper
from banks.yapikredi import YapikrediScraper
from banks.isbank import IsbankScraper
from banks.finansbank import FinansbankScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger("scraper.main")

SCRAPERS = {
    "akbank": AkbankScraper,
    "garanti": GarantiScraper,
    "yapikredi": YapikrediScraper,
    "isbank": IsbankScraper,
    "finansbank": FinansbankScraper,
}


def run_all(bank_filter=None):
    """Run all scrapers (or a subset) and collect results."""
    results = []
    scrapers_to_run = SCRAPERS

    if bank_filter:
        scrapers_to_run = {k: v for k, v in SCRAPERS.items() if k in bank_filter}

    logger.info(f"Starting scrape run for {len(scrapers_to_run)} banks: {list(scrapers_to_run.keys())}")
    logger.info("=" * 80)

    for bank_slug, ScraperClass in scrapers_to_run.items():
        logger.info(f"\n{'='*80}")
        logger.info(f"Running {bank_slug.upper()} scraper...")
        logger.info(f"{'='*80}")
        try:
            scraper = ScraperClass()
            summary = scraper.run()
            results.append(summary)
        except Exception as e:
            logger.error(f"Fatal error running {bank_slug}: {e}")
            results.append({
                "bank": bank_slug,
                "scraped": 0,
                "saved": 0,
                "errors": 1,
                "error_details": [str(e)],
                "elapsed_seconds": 0,
            })

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("SCRAPE RUN SUMMARY")
    logger.info("=" * 80)
    total_scraped = 0
    total_saved = 0
    total_errors = 0
    for r in results:
        status = "✓ OK" if r["errors"] == 0 else f"✗ {r['errors']} ERRORS"
        logger.info(
            f"  {r['bank']:20s} | scraped: {r['scraped']:3d} | "
            f"saved: {r['saved']:3d} | {r['elapsed_seconds']:5.1f}s | {status}"
        )
        if r['error_details']:
            for err in r['error_details'][:3]:
                logger.info(f"    └─ {err}")
        total_scraped += r["scraped"]
        total_saved += r["saved"]
        total_errors += r["errors"]

    logger.info(f"  {'─'*76}")
    logger.info(
        f"  {'TOTAL':20s} | scraped: {total_scraped:3d} | "
        f"saved: {total_saved:3d} | errors: {total_errors}"
    )
    logger.info("=" * 80)

    # Exit with error code if any scraper had errors
    if total_errors > 0:
        logger.warning(f"⚠️  Completed with {total_errors} errors")
        return 1
    else:
        logger.info(f"✓ All scrapers completed successfully!")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Credit card campaign scraper for Turkish banks"
    )
    parser.add_argument(
        '--banks',
        nargs='+',
        choices=list(SCRAPERS.keys()),
        help='Only scrape specific banks (default: all)',
        metavar='BANK'
    )
    args = parser.parse_args()

    try:
        exit_code = run_all(bank_filter=args.banks)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Scraper interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)
