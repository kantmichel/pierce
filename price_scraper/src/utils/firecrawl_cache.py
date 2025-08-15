"""
Firecrawl results caching system to avoid repeated API calls during development.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from src.utils.logger import get_logger

logger = get_logger(__name__)


class FirecrawlCache:
    """Cache for Firecrawl API results."""
    
    def __init__(self, cache_dir: str = "data/firecrawl_cache", ttl_hours: int = 24):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cached results
            ttl_hours: Time to live for cache entries in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"Initialized Firecrawl cache: {self.cache_dir}")
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL."""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result for URL.
        
        Args:
            url: Product URL
            
        Returns:
            Cached Firecrawl result or None if not found/expired
        """
        cache_key = self._get_cache_key(url)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            logger.debug(f"Cache miss for {url[:60]}...")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if expired
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_at > self.ttl:
                logger.debug(f"Cache expired for {url[:60]}...")
                cache_file.unlink()  # Remove expired cache
                return None
            
            logger.info(f"Cache hit for {url[:60]}...")
            return cache_data['firecrawl_result']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Invalid cache file for {url}: {e}")
            cache_file.unlink()  # Remove corrupted cache
            return None
    
    def set(self, url: str, firecrawl_result: Dict[str, Any]) -> None:
        """
        Store Firecrawl result in cache.
        
        Args:
            url: Product URL
            firecrawl_result: Firecrawl API response
        """
        cache_key = self._get_cache_key(url)
        cache_file = self._get_cache_file(cache_key)
        
        cache_data = {
            'url': url,
            'cached_at': datetime.now().isoformat(),
            'firecrawl_result': firecrawl_result
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cached result for {url[:60]}...")
        except Exception as e:
            logger.error(f"Failed to cache result for {url}: {e}")
    
    def clear_expired(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of expired entries removed
        """
        removed_count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_at = datetime.fromisoformat(cache_data['cached_at'])
                if datetime.now() - cached_at > self.ttl:
                    cache_file.unlink()
                    removed_count += 1
                    
            except (json.JSONDecodeError, KeyError, ValueError):
                # Remove corrupted cache files
                cache_file.unlink()
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleared {removed_count} expired cache entries")
        
        return removed_count
    
    def clear_all(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries removed
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        for cache_file in cache_files:
            cache_file.unlink()
        
        logger.info(f"Cleared {len(cache_files)} cache entries")
        return len(cache_files)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_entries': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }