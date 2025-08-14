#!/usr/bin/env python3
"""
Enhanced test script that saves Firecrawl results for inspection.

Usage:
    uv run python scripts/save_test_results.py
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
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
        """Basic test implementation that extracts whatever we can find."""
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
        
        return product


async def save_crawl_results():
    """Save crawl results to files for inspection."""
    test_url = "https://www.xlmoto.co.uk/product/course-raider-evo-full-face-helmet-matte-black-intercom-tinted-visor_pid-PP-4974724"
    
    print("🚀 Testing and Saving BaseCrawler Results")
    print(f"URL: {test_url}")
    
    # Create output directory
    output_dir = Path("output/test_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup crawler
    site_name = "xlmoto"
    site_config = config.sites['sites']['eu'][site_name]
    crawler = TestCrawler(site_name, site_config)
    
    print("📡 Crawling with Firecrawl...")
    result = await crawler.crawl_product(test_url)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if result.success:
        print("✅ SUCCESS! Saving results...")
        
        # Save product data as JSON
        product_data = result.product.to_dict()
        product_file = output_dir / f"product_{timestamp}.json"
        with open(product_file, 'w', encoding='utf-8') as f:
            json.dump(product_data, f, indent=2, ensure_ascii=False)
        print(f"📄 Product data saved: {product_file}")
        
        # Save full Firecrawl data
        if result.firecrawl_data:
            firecrawl_file = output_dir / f"firecrawl_{timestamp}.json"
            with open(firecrawl_file, 'w', encoding='utf-8') as f:
                json.dump(result.firecrawl_data, f, indent=2, ensure_ascii=False)
            print(f"🔥 Firecrawl data saved: {firecrawl_file}")
            
            # Save just the markdown for easy reading
            data = result.firecrawl_data.get('data', {})
            markdown = data.get('markdown', '')
            if markdown:
                markdown_file = output_dir / f"markdown_{timestamp}.md"
                with open(markdown_file, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                print(f"📝 Markdown saved: {markdown_file}")
            
            # Save metadata separately for easy inspection
            metadata = data.get('metadata', {})
            if metadata:
                metadata_file = output_dir / f"metadata_{timestamp}.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                print(f"📋 Metadata saved: {metadata_file}")
        
        # Create summary file
        summary = {
            "timestamp": timestamp,
            "url": test_url,
            "site": site_name,
            "success": True,
            "product": {
                "name": result.product.name,
                "description": (result.product.description or "")[:200] + "..." if result.product.description and len(result.product.description) > 200 else result.product.description,
                "currency": result.product.currency.value,
                "site_name": result.product.site_name
            },
            "data_stats": {
                "markdown_chars": len(data.get('markdown', '') or ''),
                "html_chars": len(data.get('html', '') or ''),
                "metadata_fields": len(metadata),
                "metadata_keys": list(metadata.keys())[:10]  # First 10 keys
            }
        }
        
        summary_file = output_dir / f"summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"📊 Summary saved: {summary_file}")
        
        print(f"\n✅ All results saved to: {output_dir}")
        print(f"   - Product data: product_{timestamp}.json")
        print(f"   - Full Firecrawl data: firecrawl_{timestamp}.json") 
        print(f"   - Readable markdown: markdown_{timestamp}.md")
        print(f"   - Metadata: metadata_{timestamp}.json")
        print(f"   - Summary: summary_{timestamp}.json")
        
    else:
        print("❌ FAILED!")
        print(f"Error: {result.error_message}")
        
        # Save error details
        error_data = {
            "timestamp": timestamp,
            "url": test_url,
            "site": site_name,
            "success": False,
            "error": result.error_message,
            "retry_count": result.retry_count
        }
        
        error_file = output_dir / f"error_{timestamp}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2, ensure_ascii=False)
        print(f"❌ Error details saved: {error_file}")


if __name__ == "__main__":
    asyncio.run(save_crawl_results())