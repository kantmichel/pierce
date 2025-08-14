#!/usr/bin/env python3
"""
Script to parse XML sitemaps and extract categorized product URLs.

Usage:
    uv run python scripts/parse_sitemaps.py
    uv run python scripts/parse_sitemaps.py --site 24mx
    uv run python scripts/parse_sitemaps.py --site xlmoto
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors.sitemap_parser import SitemapParser
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Parse XML sitemaps and extract product URLs")
    parser.add_argument(
        "--site", 
        choices=["24mx", "xlmoto", "both"], 
        default="both",
        help="Which site to process (default: both)"
    )
    parser.add_argument(
        "--output",
        default="config/products.csv",
        help="Output CSV file path (default: config/products.csv)"
    )
    
    args = parser.parse_args()
    
    sitemap_parser = SitemapParser()
    
    results = {}
    
    if args.site in ["24mx", "both"]:
        xml_path = "data/xml/24mx_sitemap.xml"
        if Path(xml_path).exists():
            logger.info("Processing 24MX sitemap...")
            results["24mx"] = sitemap_parser.process_sitemap(xml_path, "24mx")
        else:
            logger.warning(f"24MX sitemap not found at {xml_path}")
    
    if args.site in ["xlmoto", "both"]:
        xml_path = "data/xml/xlmoto_sitemap.xml"
        if Path(xml_path).exists():
            logger.info("Processing XLMoto sitemap...")
            results["xlmoto"] = sitemap_parser.process_sitemap(xml_path, "xlmoto")
        else:
            logger.warning(f"XLMoto sitemap not found at {xml_path}")
    
    # Print summary
    print("\n" + "="*50)
    print("SITEMAP PROCESSING SUMMARY")
    print("="*50)
    
    for site_name, stats in results.items():
        print(f"\n{site_name.upper()}:")
        print(f"  Total URLs extracted: {stats.get('total_entries', 0)}")
        
        categories = stats.get('categories', {})
        for category, category_stats in categories.items():
            print(f"  {category}: {category_stats['count']}/{category_stats['limit']} URLs")
            
            # Show sample URLs
            sample_urls = category_stats.get('sample_urls', [])
            if sample_urls:
                print(f"    Sample: {sample_urls[0]}")
    
    print(f"\nResults saved to: {args.output}")
    print("="*50)


if __name__ == "__main__":
    main()