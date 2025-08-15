"""
Rate limiting utilities for API requests.
"""

import asyncio
import time
from typing import Optional


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, requests_per_second: float = 2.0, burst_size: int = 5):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
            burst_size: Maximum burst of requests before rate limiting kicks in
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire permission to make a request (blocks if rate limited)."""
        async with self._lock:
            now = time.time()
            
            # Refill tokens based on elapsed time
            elapsed = now - self.last_refill
            self.tokens = min(self.burst_size, self.tokens + elapsed * self.requests_per_second)
            self.last_refill = now
            
            # If no tokens available, wait
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.requests_per_second
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1
    
    async def wait_if_needed(self, delay_between_requests: float = 0.5) -> None:
        """
        Simple delay-based rate limiting (legacy method for compatibility).
        
        Args:
            delay_between_requests: Minimum delay between requests
        """
        if hasattr(self, '_last_request_time'):
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            
            if time_since_last < delay_between_requests:
                wait_time = delay_between_requests - time_since_last
                await asyncio.sleep(wait_time)
        
        self._last_request_time = time.time()


class DelayRateLimiter:
    """Simple delay-based rate limiter (for backward compatibility)."""
    
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