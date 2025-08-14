import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._settings: Optional[Dict[str, Any]] = None
        self._sites: Optional[Dict[str, Any]] = None
    
    @property
    def settings(self) -> Dict[str, Any]:
        """Load and cache settings from settings.yaml."""
        if self._settings is None:
            settings_file = self.config_dir / "settings.yaml"
            with open(settings_file, 'r', encoding='utf-8') as f:
                self._settings = yaml.safe_load(f)
        return self._settings
    
    @property
    def sites(self) -> Dict[str, Any]:
        """Load and cache sites configuration from sites.yaml."""
        if self._sites is None:
            sites_file = self.config_dir / "sites.yaml"
            with open(sites_file, 'r', encoding='utf-8') as f:
                self._sites = yaml.safe_load(f)
        return self._sites
    
    def get_database_path(self) -> str:
        """Get database path from environment or default."""
        return os.getenv("DATABASE_PATH", "data/moto_prices.duckdb")
    
    def get_firecrawl_api_key(self) -> str:
        """Get Firecrawl API key from environment."""
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")
        return api_key
    
    def get_exchange_rate_config(self) -> Dict[str, str]:
        """Get exchange rate API configuration."""
        return {
            "api_key": os.getenv("EXCHANGE_RATE_API_KEY", ""),
            "api_url": os.getenv("EXCHANGE_RATE_API_URL", "https://v6.exchangerate-api.com/v6")
        }
    
    def get_crawl_config(self) -> Dict[str, Any]:
        """Get crawling configuration."""
        return {
            "delay_seconds": int(os.getenv("CRAWL_DELAY_SECONDS", "2")),
            "max_concurrent": int(os.getenv("MAX_CONCURRENT_REQUESTS", "5")),
            "timeout": int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
            "user_agent": self.settings.get("crawling", {}).get(
                "user_agent",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return {
            "directory": os.getenv("CACHE_DIRECTORY", "data/cache"),
            "expiry_hours": int(os.getenv("CACHE_EXPIRY_HOURS", "24"))
        }


# Global config instance
config = Config()