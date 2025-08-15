#!/usr/bin/env python3
"""
AI-Enhanced EU Product Extraction.

Uses Claude Sonnet 3.5 to analyze product pages and generate intelligent 
search terms for Turkish e-commerce sites.

Usage:
    uv run python scripts/extract_eu_products_ai.py
"""

import sys
import asyncio
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawlers.base_crawler import BaseCrawler
from src.models.product import Product, Currency
from src.services.ai_search_generator import AISearchGenerator
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class AIEnhancedProductExtractor(BaseCrawler):
    """Product extractor enhanced with AI-powered search term generation."""
    
    def __init__(self, site_name: str, site_config: Dict[str, Any]):
        """Initialize with AI search generator."""
        super().__init__(site_name, site_config)
        self.ai_generator = AISearchGenerator()
    
    async def _extract_product_data(self, url: str, firecrawl_data: Dict[str, Any]) -> Product:
        """Extract product data with basic cleaning (AI will do the advanced analysis)."""
        
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
        
        # Basic cleaning (AI will do the intelligent analysis)
        clean_name = self._sanitize_text(title)
        
        # Create product object
        product = Product(
            name=clean_name,
            description=self._sanitize_text(description),
            url=url,
            site_name=self.site_name,
            currency=self.currency
        )
        
        return product
    
    async def extract_with_ai_search_terms(
        self, 
        url: str, 
        category: str = ""
    ) -> Dict[str, Any]:
        """
        Extract product data and generate AI-powered search terms.
        
        Returns:
            Dictionary with product data and AI-generated search terms
        """
        try:
            # First, crawl the page using Firecrawl
            crawl_result = await self.crawl_product(url)
            
            if not crawl_result.success:
                return {
                    'success': False,
                    'error': crawl_result.error_message,
                    'url': url,
                    'category': category
                }
            
            # Generate AI search terms using the full Firecrawl data
            ai_result = await self.ai_generator.generate_search_terms(
                product_data=crawl_result.firecrawl_data,
                product_url=url,
                category=category
            )
            
            return {
                'success': True,
                'url': url,
                'category': category,
                'product': {
                    'name': crawl_result.product.name,
                    'description': crawl_result.product.description,
                    'site_name': crawl_result.product.site_name,
                    'currency': crawl_result.product.currency.value
                },
                'ai_search_terms': ai_result.get('search_terms', []),
                'ai_brand': ai_result.get('brand', ''),
                'ai_product_type': ai_result.get('product_type', ''),
                'ai_key_features': ai_result.get('key_features', []),
                'ai_confidence': ai_result.get('confidence', 0.0),
                'ai_analysis': ai_result.get('ai_analysis', ''),
                'ai_success': ai_result.get('success', False),
                'ai_error': ai_result.get('error', ''),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI-enhanced extraction failed for {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url,
                'category': category,
                'extracted_at': datetime.now().isoformat()
            }


def load_test_product_urls(limit: int = 2) -> List[Dict[str, str]]:
    """Load first N product URLs from our products.csv."""
    products_file = Path("config/products.csv")
    
    if not products_file.exists():
        logger.error(f"Products file not found: {products_file}")
        return []
    
    products = []
    with open(products_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if row.get('site') in ['24mx', 'xlmoto'] and row.get('product_url') and count < limit:
                products.append(row)
                count += 1
    
    logger.info(f"Loaded {len(products)} test EU product URLs")
    return products


async def main():
    """Test AI-enhanced product extraction."""
    print("🤖 AI-ENHANCED: Extracting Product Names with Claude Sonnet 3.7")
    
    # Load test products
    products = load_test_product_urls(limit=2)
    if not products:
        print("❌ No products found to process")
        return
    
    print(f"📋 Processing {len(products)} products with AI analysis")
    
    # Create output directory
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # Results storage
    all_results = []
    
    # Process each site separately
    for site in ['xlmoto', '24mx']:
        site_products = [p for p in products if p['site'] == site]
        if not site_products:
            continue
            
        print(f"\n🧠 AI-Processing {len(site_products)} products from {site.upper()}")
        
        # Setup AI-enhanced extractor for this site
        site_config = config.sites['sites']['eu'][site]
        extractor = AIEnhancedProductExtractor(site, site_config)
        
        # Process each product with AI
        for product_info in site_products:
            url = product_info['product_url']
            category = product_info.get('category', '')
            
            print(f"  🔍 Analyzing: {url[:60]}...")
            
            try:
                result = await extractor.extract_with_ai_search_terms(url, category)
                
                if result['success'] and result.get('ai_success'):
                    ai_terms = result['ai_search_terms']
                    brand = result['ai_brand']
                    confidence = result['ai_confidence']
                    
                    print(f"    ✅ Brand: {brand} | Confidence: {confidence:.2f}")
                    print(f"    🔍 AI Search Terms: {', '.join(ai_terms[:3])}...")
                    
                    # Prepare CSV row
                    csv_row = {
                        'original_url': url,
                        'site': product_info['site'],
                        'category': category,
                        'original_breadcrumb': product_info.get('breadcrumb', ''),
                        'extracted_name': result['product']['name'],
                        'ai_brand': brand,
                        'ai_product_type': result['ai_product_type'],
                        'ai_confidence': confidence,
                        'ai_search_term_1': ai_terms[0] if len(ai_terms) > 0 else '',
                        'ai_search_term_2': ai_terms[1] if len(ai_terms) > 1 else '',
                        'ai_search_term_3': ai_terms[2] if len(ai_terms) > 2 else '',
                        'ai_search_term_4': ai_terms[3] if len(ai_terms) > 3 else '',
                        'ai_search_term_5': ai_terms[4] if len(ai_terms) > 4 else '',
                        'ai_key_features': '|'.join(result['ai_key_features']),
                        'ai_analysis': result['ai_analysis'],
                        'extraction_status': 'success'
                    }
                    
                else:
                    error_msg = result.get('ai_error', result.get('error', 'Unknown error'))
                    print(f"    ❌ Failed: {error_msg}")
                    
                    csv_row = {
                        'original_url': url,
                        'site': product_info['site'],
                        'category': category,
                        'original_breadcrumb': product_info.get('breadcrumb', ''),
                        'extracted_name': result.get('product', {}).get('name', ''),
                        'ai_brand': '',
                        'ai_product_type': '',
                        'ai_confidence': 0.0,
                        'ai_search_term_1': '',
                        'ai_search_term_2': '',
                        'ai_search_term_3': '',
                        'ai_search_term_4': '',
                        'ai_search_term_5': '',
                        'ai_key_features': '',
                        'ai_analysis': '',
                        'extraction_status': f'failed: {error_msg}'
                    }
                
                all_results.append(csv_row)
                
            except Exception as e:
                logger.error(f"Product processing failed: {e}")
                csv_row = {
                    'original_url': url,
                    'site': product_info['site'],
                    'category': category,
                    'original_breadcrumb': product_info.get('breadcrumb', ''),
                    'extracted_name': '',
                    'ai_brand': '',
                    'ai_product_type': '',
                    'ai_confidence': 0.0,
                    'ai_search_term_1': '',
                    'ai_search_term_2': '',
                    'ai_search_term_3': '',
                    'ai_search_term_4': '',
                    'ai_search_term_5': '',
                    'ai_key_features': '',
                    'ai_analysis': '',
                    'extraction_status': f'exception: {str(e)}'
                }
                all_results.append(csv_row)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"eu_products_ai_enhanced_{timestamp}.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'original_url', 'site', 'category', 'original_breadcrumb',
            'extracted_name', 'ai_brand', 'ai_product_type', 'ai_confidence',
            'ai_search_term_1', 'ai_search_term_2', 'ai_search_term_3', 
            'ai_search_term_4', 'ai_search_term_5',
            'ai_key_features', 'ai_analysis', 'extraction_status'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    # Summary
    successful = len([r for r in all_results if r['extraction_status'] == 'success'])
    failed = len(all_results) - successful
    
    print(f"\n📊 AI-ENHANCED EXTRACTION COMPLETE")
    print(f"   Total processed: {len(all_results)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Results saved: {output_file}")
    
    if successful > 0:
        avg_confidence = sum(float(r['ai_confidence']) for r in all_results if r['extraction_status'] == 'success') / successful
        print(f"   Average AI Confidence: {avg_confidence:.2f}")
        print(f"\n🧠 AI Analysis ready for Turkish site searches!")


if __name__ == "__main__":
    asyncio.run(main())