#!/usr/bin/env python3
"""
Test script for the BaseCrawler implementation.

Usage:
    uv run python scripts/test_base_crawler.py
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawlers.base_crawler import BaseCrawler
from src.models.product import Product, Currency
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger(__name__)


class TestCrawler(BaseCrawler):
    """Simple test implementation of BaseCrawler."""
    
    async def _extract_product_data(self, url: str, firecrawl_data: Dict[str, Any]) -> Product:
        """
        Basic test implementation that just extracts whatever we can find.
        This is just for testing - real implementations will be more sophisticated.
        """
        logger.info("Testing product data extraction from Firecrawl result")
        
        # Get the scraped content
        markdown = firecrawl_data.get('data', {}).get('markdown', '')
        html = firecrawl_data.get('data', {}).get('html', '')
        metadata = firecrawl_data.get('data', {}).get('metadata', {})
        
        # Basic extraction - just for testing
        title = metadata.get('title', '') or metadata.get('ogTitle', '') or 'Test Product'
        description = metadata.get('description', '') or metadata.get('ogDescription', '')
        
        # Create a basic product object
        product = Product(
            name=self._sanitize_text(title),
            description=self._sanitize_text(description),
            url=url,
            site_name=self.site_name,
            currency=self.currency
        )
        
        logger.info(f"Extracted test product: {product.name}")
        logger.info(f"Description: {(product.description or '')[:100]}...")
        logger.info(f"Markdown length: {len(markdown or '')} chars")
        logger.info(f"HTML length: {len(html or '')} chars")
        
        return product


async def test_single_url():
    """Test crawling a single URL."""
    # Just test one URL to keep it fast
    test_url = "https://www.xlmoto.co.uk/product/course-raider-evo-full-face-helmet-matte-black-intercom-tinted-visor_pid-PP-4974724"
    
    print("="*60)
    print("TESTING BASE CRAWLER WITH FIRECRAWL")
    print("="*60)
    
    if True:  # Keep the same indentation structure
        site_name = "xlmoto" if "xlmoto" in test_url else "24mx"
        site_config = config.sites['sites']['eu'][site_name]
        
        print(f"\nTesting {site_name.upper()} URL:")
        print(f"URL: {test_url}")
        print(f"Config: {site_config}")
        
        try:
            # Create test crawler
            crawler = TestCrawler(site_name, site_config)
            
            # Test single URL crawl
            print(f"\n📡 Starting Firecrawl test for {site_name}...")
            result = await crawler.crawl_product(test_url)
            
            if result.success:
                print("✅ SUCCESS!")
                print(f"Product Name: {result.product.name}")
                print(f"Product URL: {result.product.url}")
                print(f"Site: {result.product.site_name}")
                print(f"Currency: {result.product.currency.value}")
                if result.product.description:
                    print(f"Description: {result.product.description[:100]}...")
                
                # Show some Firecrawl data info
                if result.firecrawl_data:
                    data = result.firecrawl_data.get('data', {})
                    print(f"\n🔥 Firecrawl Data:")
                    markdown = data.get('markdown', '') or ''
                    html = data.get('html', '') or ''
                    metadata = data.get('metadata', {}) or {}
                    
                    print(f"  - Markdown: {len(markdown)} chars")
                    print(f"  - HTML: {len(html)} chars")
                    print(f"  - Metadata keys: {list(metadata.keys())}")
                    
                    # Show first few lines of markdown
                    if markdown:
                        lines = markdown.split('\n')[:5]
                        print(f"  - First 5 lines of markdown:")
                        for i, line in enumerate(lines, 1):
                            print(f"    {i}. {line[:80]}...")
            else:
                print("❌ FAILED!")
                print(f"Error: {result.error_message}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
        
        print("-" * 60)
        
        # Wait a bit between tests to be nice to the APIs
        await asyncio.sleep(2)


async def test_batch_crawl():
    """Test batch crawling functionality."""
    print("\n" + "="*60)
    print("TESTING BATCH CRAWL FUNCTIONALITY")
    print("="*60)
    
    # Get a few test URLs
    test_urls = [
        "https://www.xlmoto.co.uk/product/course-raider-evo-full-face-helmet-matte-black-intercom-tinted-visor_pid-PP-4974724",
        "https://www.xlmoto.co.uk/product/course-raider-evo-full-face-helmet-glossy-nardo-grey-intercom-tinted-visor_pid-PP-4974725"
    ]
    
    site_config = config.sites['sites']['eu']['xlmoto']
    crawler = TestCrawler("xlmoto", site_config)
    
    print(f"Testing batch crawl with {len(test_urls)} URLs...")
    
    try:
        results = await crawler.crawl_multiple(test_urls, max_concurrent=2)
        
        print(f"\n📊 Batch Results:")
        successful = sum(1 for r in results if r.success)
        print(f"  - Total: {len(results)}")
        print(f"  - Successful: {successful}")
        print(f"  - Failed: {len(results) - successful}")
        
        for i, result in enumerate(results, 1):
            status = "✅" if result.success else "❌"
            name = result.product.name if result.product else "N/A"
            print(f"  {i}. {status} {name[:50]}...")
            
    except Exception as e:
        print(f"❌ Batch crawl failed: {str(e)}")


async def main():
    """Run single URL test only."""
    print("🚀 Starting BaseCrawler Test (Single URL)")
    print(f"Using Firecrawl API Key: {'✅ Set' if config.get_firecrawl_api_key() else '❌ Missing'}")
    
    try:
        # Test single URL crawling only
        await test_single_url()
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETED")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())