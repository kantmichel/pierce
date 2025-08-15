"""
AI-powered search term generator using Claude Sonnet 3.7.

This service analyzes motorcycle product pages and generates human-like 
search terms optimized for Turkish e-commerce sites.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

import anthropic
from anthropic.types import MessageParam

from src.utils.logger import get_logger
from src.utils.rate_limiter import RateLimiter

logger = get_logger(__name__)


class AISearchGenerator:
    """AI-powered search term generator using Claude Sonnet 3.7."""
    
    def __init__(self):
        """Initialize the AI service with rate limiting."""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
        # Rate limiting: Anthropic allows high throughput but let's be conservative
        # Start with 10 requests per minute for safety
        self.rate_limiter = RateLimiter(requests_per_second=10/60, burst_size=5)
        
        self.model = "claude-3-7-sonnet-20250219"  # Sonnet 3.7 (latest available)
        logger.info(f"Initialized AI Search Generator with model: {self.model}")
    
    async def generate_search_terms(
        self, 
        product_data: Dict[str, Any],
        product_url: str,
        category: str = ""
    ) -> Dict[str, Any]:
        """
        Generate search terms for a motorcycle product using AI analysis.
        
        Args:
            product_data: Raw Firecrawl data (markdown, metadata)
            product_url: Original product URL
            category: Product category (helmets, chains, etc.)
            
        Returns:
            Dictionary with AI-generated search terms and analysis
        """
        try:
            await self.rate_limiter.acquire()
            
            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(product_data, product_url, category)
            
            logger.info(f"Generating AI search terms for product: {product_url[:60]}...")
            
            # Call Claude Sonnet 3.7
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.2,  # Low temperature for consistent, structured output
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            response_text = response.content[0].text if response.content else ""
            
            # Extract JSON from response
            search_data = self._parse_ai_response(response_text)
            
            logger.info(f"Successfully generated {len(search_data.get('search_terms', []))} AI search terms")
            
            return {
                'success': True,
                'search_terms': search_data.get('search_terms', []),
                'brand': search_data.get('brand', ''),
                'product_type': search_data.get('product_type', ''),
                'key_features': search_data.get('key_features', []),
                'confidence': search_data.get('confidence', 0.0),
                'ai_analysis': search_data.get('analysis', ''),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI search term generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'search_terms': [],
                'brand': '',
                'product_type': '',
                'key_features': [],
                'confidence': 0.0,
                'generated_at': datetime.now().isoformat()
            }
    
    def _build_analysis_prompt(self, product_data: Dict[str, Any], product_url: str, category: str) -> str:
        """Build the analysis prompt for Claude."""
        
        # Extract key data
        markdown = product_data.get('data', {}).get('markdown', '')[:4000]  # Limit to avoid token limits
        metadata = product_data.get('data', {}).get('metadata', {})
        
        title = (
            metadata.get('title', '') or 
            metadata.get('ogTitle', '') or 
            metadata.get('og:title', '') or
            'Unknown Product'
        )
        
        description = (
            metadata.get('description', '') or 
            metadata.get('ogDescription', '') or 
            ''
        )
        
        prompt = f"""You are an expert in motorcycle parts and Turkish e-commerce search behavior. 

Analyze this motorcycle product page and generate optimized search terms that Turkish customers would use to find this product on local e-commerce sites like motomax.com.tr and mototas.com.tr.

PRODUCT INFO:
URL: {product_url}
Category: {category}
Title: {title}
Description: {description}

PAGE CONTENT (first 4000 chars):
{markdown}

TASK: Generate search terms following these rules:

1. EXTRACT core product information:
   - Brand name (exact spelling matters)
   - Product type/category 
   - Model name/number
   - Key differentiating features

2. GENERATE 5 search term variations:
   - Term 1: Full brand + model + type (most specific)
   - Term 2: Brand + simplified model name  
   - Term 3: Brand + product type only
   - Term 4: Alternative spelling/abbreviation if common
   - Term 5: Generic category term (fallback)

3. TURKISH MARKET CONTEXT:
   - Consider common Turkish abbreviations (MC for motorcycle, kask for helmet)
   - Remove promotional text (discounts, shipping info)
   - Focus on technical specifications that matter for matching
   - Consider brand recognition in Turkish market

4. CONFIDENCE SCORING:
   - Rate your confidence in these search terms (0.0-1.0)
   - Higher score = more specific product identification

Return ONLY valid JSON in this exact format:
{{
  "brand": "exact brand name",
  "product_type": "helmet/visor/chain/etc",
  "key_features": ["feature1", "feature2", "feature3"],
  "search_terms": [
    "term 1 - most specific",
    "term 2 - simplified", 
    "term 3 - brand + type",
    "term 4 - alternative",
    "term 5 - generic"
  ],
  "confidence": 0.85,
  "analysis": "Brief explanation of your approach"
}}"""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response and extract JSON."""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON found in AI response")
                return {}
            
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['search_terms', 'brand', 'product_type']
            for field in required_fields:
                if field not in data:
                    data[field] = [] if field == 'search_terms' else ''
            
            # Ensure search_terms is a list
            if not isinstance(data.get('search_terms'), list):
                data['search_terms'] = []
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
            return {}
    
    async def generate_batch_search_terms(
        self, 
        products_data: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate search terms for multiple products concurrently.
        
        Args:
            products_data: List of product data dictionaries
            max_concurrent: Maximum concurrent AI requests
            
        Returns:
            List of search term results
        """
        logger.info(f"Starting batch AI generation for {len(products_data)} products")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_product(product_info: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                return await self.generate_search_terms(
                    product_data=product_info.get('firecrawl_data', {}),
                    product_url=product_info.get('url', ''),
                    category=product_info.get('category', '')
                )
        
        # Process all products concurrently
        tasks = [process_product(product) for product in products_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Product {i} failed: {result}")
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'search_terms': []
                })
            else:
                processed_results.append(result)
        
        successful = len([r for r in processed_results if r.get('success')])
        logger.info(f"Batch AI generation complete: {successful}/{len(products_data)} successful")
        
        return processed_results


# Utility function for easy import
async def generate_ai_search_terms(
    product_data: Dict[str, Any],
    product_url: str,
    category: str = ""
) -> Dict[str, Any]:
    """Convenience function to generate search terms for a single product."""
    generator = AISearchGenerator()
    return await generator.generate_search_terms(product_data, product_url, category)