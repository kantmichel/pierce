#!/usr/bin/env python3
"""
Test version: Extract product names from first 10 EU URLs.

Usage:
    uv run python scripts/extract_eu_products_test.py
"""

import sys
import asyncio
import csv
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawlers.base_crawler import BaseCrawler
from src.models.product import Product, Currency
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class ProductExtractor(BaseCrawler):
    """Product extractor that focuses on getting clean product names."""
    
    async def _extract_product_data(self, url: str, firecrawl_data: Dict[str, Any]) -> Product:
        """Extract product data focusing on clean names for search."""
        
        # Get the scraped content
        markdown = firecrawl_data.get('data', {}).get('markdown', '')
        metadata = firecrawl_data.get('data', {}).get('metadata', {})
        
        # Extract title from multiple sources
        title = (
            metadata.get('title', '') or 
            metadata.get('ogTitle', '') or 
            metadata.get('og:title', '') or
            'Unknown Product'
        )
        
        description = (
            metadata.get('description', '') or 
            metadata.get('ogDescription', '') or
            metadata.get('og:description', '') or
            ''
        )
        
        # Clean the title - remove site branding, sale info, etc.
        clean_name = self._clean_product_name(title)
        
        # Create product object
        product = Product(
            name=clean_name,
            description=self._sanitize_text(description),
            url=url,
            site_name=self.site_name,
            currency=self.currency
        )
        
        return product
    
    def _clean_product_name(self, title: str) -> str:
        """Clean product name for better search terms."""
        if not title:
            return ""
        
        # Remove common site suffixes
        title = re.sub(r'\s*\|\s*(XLMOTO|24MX).*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*-\s*(XLMOTO|24MX).*$', '', title, flags=re.IGNORECASE)
        
        # Remove promotional text
        promotional_patterns = [
            r'\s*-\s*Now\s+\d+%\s+Savings.*$',
            r'\s*-\s*Free\s+shipping.*$',
            r'\s*-\s*Best\s+price.*$',
            r'\s*-\s*UK\'s\s+best.*$',
            r'\s*\+\s+[^+]*\+\s+[^+]*$',  # Remove "+ Intercom + Tinted Visor" type additions
        ]
        
        for pattern in promotional_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        return self._sanitize_text(title)


def load_test_product_urls() -> List[Dict[str, str]]:
    """Load first 10 product URLs from our products.csv."""
    products_file = Path("config/products.csv")
    
    if not products_file.exists():
        logger.error(f"Products file not found: {products_file}")
        return []
    
    products = []
    with open(products_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if row.get('site') in ['24mx', 'xlmoto'] and row.get('product_url') and count < 2:
                products.append(row)
                count += 1
    
    logger.info(f"Loaded {len(products)} test EU product URLs (first 2)")
    return products


def generate_search_terms(product_name: str) -> List[str]:
    """Generate multiple search term variations for a product."""
    if not product_name:
        return []
    
    search_terms = []
    
    # Original name
    search_terms.append(product_name)
    
    # Remove model years, sizes, colors that might not match
    simplified = re.sub(r'\b(20\d{2}|Matt?e?|Gloss?y?|Black|White|Red|Blue|Green|Yellow)\b', '', product_name, flags=re.IGNORECASE)
    simplified = re.sub(r'\s+', ' ', simplified).strip()
    if simplified and simplified != product_name:
        search_terms.append(simplified)
    
    # Brand + main model only (first 2-3 words)
    words = product_name.split()
    if len(words) >= 2:
        short_name = ' '.join(words[:3])
        search_terms.append(short_name)
    
    # Remove duplicates while preserving order
    unique_terms = []
    seen = set()
    for term in search_terms:
        if term.lower() not in seen and len(term.strip()) > 3:
            unique_terms.append(term.strip())
            seen.add(term.lower())
    
    return unique_terms


async def main():
    """Extract product names from first 10 EU URLs."""
    print("🧪 TEST: Extracting Product Names from First 2 EU URLs")
    
    # Load test products
    products = load_test_product_urls()
    if not products:
        print("❌ No products found to process")
        return
    
    print(f"📋 Processing {len(products)} test products")
    
    # Create output directory
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # Results storage
    extracted_products = []
    
    # Process each site separately to respect rate limits
    for site in ['xlmoto', '24mx']:
        site_products = [p for p in products if p['site'] == site]
        if not site_products:
            continue
            
        print(f"\n📡 Processing {len(site_products)} products from {site.upper()}")
        
        # Setup crawler for this site
        site_config = config.sites['sites']['eu'][site]
        extractor = ProductExtractor(site, site_config)
        
        # Process all URLs for this site at once (small batch)
        urls = [p['product_url'] for p in site_products]
        
        try:
            results = await extractor.crawl_multiple(urls, max_concurrent=2)
            
            for j, result in enumerate(results):
                original_product = site_products[j]
                
                if result.success and result.product:
                    search_terms = generate_search_terms(result.product.name)
                    
                    extracted_products.append({
                        'original_url': original_product['product_url'],
                        'site': original_product['site'],
                        'category': original_product.get('category', ''),
                        'original_breadcrumb': original_product.get('breadcrumb', ''),
                        'extracted_name': result.product.name,
                        'search_term_1': search_terms[0] if len(search_terms) > 0 else '',
                        'search_term_2': search_terms[1] if len(search_terms) > 1 else '',
                        'search_term_3': search_terms[2] if len(search_terms) > 2 else '',
                        'extraction_status': 'success'
                    })
                    
                    print(f"    ✅ {result.product.name}")
                else:
                    extracted_products.append({
                        'original_url': original_product['product_url'],
                        'site': original_product['site'],
                        'category': original_product.get('category', ''),
                        'original_breadcrumb': original_product.get('breadcrumb', ''),
                        'extracted_name': '',
                        'search_term_1': '',
                        'search_term_2': '',
                        'search_term_3': '',
                        'extraction_status': f'failed: {result.error_message}'
                    })
                    
                    print(f"    ❌ Failed: {original_product['product_url']}")
            
        except Exception as e:
            logger.error(f"Site processing failed: {e}")
            # Add failed entries for this site
            for product in site_products:
                extracted_products.append({
                    'original_url': product['product_url'],
                    'site': product['site'],
                    'category': product.get('category', ''),
                    'original_breadcrumb': product.get('breadcrumb', ''),
                    'extracted_name': '',
                    'search_term_1': '',
                    'search_term_2': '',
                    'search_term_3': '',
                    'extraction_status': f'site_failed: {str(e)}'
                })
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"eu_products_test_{timestamp}.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'original_url', 'site', 'category', 'original_breadcrumb',
            'extracted_name', 'search_term_1', 'search_term_2', 'search_term_3',
            'extraction_status'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(extracted_products)
    
    # Summary
    successful = len([p for p in extracted_products if p['extraction_status'] == 'success'])
    failed = len(extracted_products) - successful
    
    print(f"\n📊 TEST EXTRACTION COMPLETE")
    print(f"   Total processed: {len(extracted_products)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Results saved: {output_file}")
    
    if successful > 0:
        print(f"\n✅ Test successful! Ready for full extraction with all 120 URLs")


if __name__ == "__main__":
    asyncio.run(main())