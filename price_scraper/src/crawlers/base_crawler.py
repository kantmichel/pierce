import asyncio
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from firecrawl import FirecrawlApp

from src.models.product import Product, ProductStatus, Currency
from src.utils.logger import get_logger
from src.utils.config import config

logger = get_logger(__name__)


@dataclass
class CrawlResult:
    """Result of a crawl operation."""
    success: bool
    product: Optional[Product] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    firecrawl_data: Optional[Dict[str, Any]] = None


class RateLimiter:
    """Simple rate limiter for Firecrawl requests."""
    
    def __init__(self, requests_per_second: float = 2.0, delay_between_requests: float = 0.5):
        self.requests_per_second = requests_per_second
        self.delay_between_requests = delay_between_requests
        self.last_request_time = 0.0
    
    async def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay_between_requests:
            wait_time = self.delay_between_requests - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()


class BaseCrawler(ABC):
    """Abstract base crawler for product data extraction using Firecrawl."""
    
    def __init__(self, site_name: str, site_config: Dict[str, Any]):
        self.site_name = site_name
        self.site_config = site_config
        self.base_url = site_config.get('base_url', '')
        self.currency = Currency(site_config.get('currency', 'EUR'))
        
        # Rate limiting
        rate_config = site_config.get('rate_limit', {})
        self.rate_limiter = RateLimiter(
            requests_per_second=rate_config.get('requests_per_second', 2.0),
            delay_between_requests=rate_config.get('delay_between_requests', 0.5)
        )
        
        # Firecrawl configuration
        self.max_retries = 3
        self.firecrawl_app: Optional[FirecrawlApp] = None
        
        # Initialize Firecrawl
        self._initialize_firecrawl()
        
        logger.info(f"Initialized Firecrawl crawler for {site_name} with base URL: {self.base_url}")
    
    def _initialize_firecrawl(self):
        """Initialize Firecrawl app with API key."""
        try:
            api_key = config.get_firecrawl_api_key()
            self.firecrawl_app = FirecrawlApp(api_key=api_key)
            logger.debug("Firecrawl app initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firecrawl: {e}")
            raise
    
    async def _scrape_with_firecrawl(self, url: str) -> Dict[str, Any]:
        """Scrape URL using Firecrawl with rate limiting and retries."""
        await self.rate_limiter.wait_if_needed()
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Scraping {url} with Firecrawl (attempt {attempt + 1}/{self.max_retries})")
                
                # Use Firecrawl to scrape the page with timeout for page loading
                result = self.firecrawl_app.scrape_url(
                    url,
                    wait_for=10000,  # Wait 10 seconds for page to load
                    timeout=30000,   # Total timeout of 30 seconds
                )
                
                if result and hasattr(result, 'success') and result.success:
                    logger.debug(f"Successfully scraped {url}")
                    # Convert ScrapeResponse to dict format for consistency
                    return {
                        'success': result.success,
                        'data': {
                            'markdown': getattr(result, 'markdown', ''),
                            'html': getattr(result, 'html', ''),
                            'metadata': getattr(result, 'metadata', {}),
                            'links': getattr(result, 'links', []),
                        }
                    }
                else:
                    error_msg = getattr(result, 'error', 'Unknown Firecrawl error') if result else 'Empty result from Firecrawl'
                    logger.warning(f"Firecrawl scraping failed for {url}: {error_msg}")
                    last_exception = Exception(error_msg)
                
            except Exception as e:
                last_exception = e
                wait_time = (2 ** attempt) + 1
                logger.warning(f"Firecrawl request failed for {url}, waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}: {e}")
                await asyncio.sleep(wait_time)
        
        # All retries failed
        error_msg = f"Failed to scrape {url} with Firecrawl after {self.max_retries} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def _validate_product_data(self, product: Product) -> bool:
        """Validate extracted product data."""
        if not product.name or not product.name.strip():
            logger.warning("Product name is empty or whitespace")
            return False
        
        if not product.url:
            logger.warning("Product URL is missing")
            return False
        
        if product.price is not None and product.price < 0:
            logger.warning(f"Invalid price: {product.price}")
            return False
        
        return True
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize and clean text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.strip().split())
        
        # Remove common unwanted characters
        text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
        
        return text.strip()
    
    async def crawl_product(self, url: str) -> CrawlResult:
        """
        Main method to crawl a product URL and extract data using Firecrawl.
        This is the public interface that handles errors and returns results.
        """
        logger.info(f"Crawling product: {url}")
        
        try:
            # Scrape page with Firecrawl
            firecrawl_result = await self._scrape_with_firecrawl(url)
            
            # Extract product data (implemented by subclasses)
            product = await self._extract_product_data(url, firecrawl_result)
            
            # Validate data
            if not self._validate_product_data(product):
                return CrawlResult(
                    success=False,
                    error_message="Product data validation failed",
                    firecrawl_data=firecrawl_result
                )
            
            logger.info(f"Successfully extracted product: {product.name}")
            return CrawlResult(
                success=True,
                product=product,
                firecrawl_data=firecrawl_result
            )
            
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {str(e)}")
            return CrawlResult(
                success=False,
                error_message=str(e)
            )
    
    @abstractmethod
    async def _extract_product_data(self, url: str, firecrawl_data: Dict[str, Any]) -> Product:
        """
        Extract product data from Firecrawl result.
        Must be implemented by subclasses for each specific site.
        
        Args:
            url: The product URL that was scraped
            firecrawl_data: The result from Firecrawl containing markdown, html, metadata, etc.
            
        Returns:
            Product object with extracted data
        """
        pass
    
    async def crawl_multiple(self, urls: List[str], max_concurrent: int = 3) -> List[CrawlResult]:
        """
        Crawl multiple URLs concurrently.
        Note: Lower concurrency limit for Firecrawl to respect rate limits.
        """
        logger.info(f"Starting batch crawl of {len(urls)} URLs for {self.site_name}")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(url: str) -> CrawlResult:
            async with semaphore:
                return await self.crawl_product(url)
        
        results = await asyncio.gather(
            *[crawl_with_semaphore(url) for url in urls],
            return_exceptions=True
        )
        
        # Handle any exceptions that weren't caught
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Unexpected error crawling {urls[i]}: {result}")
                processed_results.append(CrawlResult(
                    success=False,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        successful = sum(1 for r in processed_results if r.success)
        logger.info(f"Batch crawl completed: {successful}/{len(urls)} successful")
        
        return processed_results