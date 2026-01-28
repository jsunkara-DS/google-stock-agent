import logging
import time
from typing import Dict, Optional
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StockFetcher:
    """Fetch real-time stock data from Alpha Vantage API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_delay = 12  # 5 requests per minute = 12 seconds per request
        self.last_request_time = 0
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl_minutes = 60

    def _respect_rate_limit(self):
        """Respect Alpha Vantage rate limit (5 req/min)."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid."""
        if symbol not in self.cache:
            return False
        cache_time = self.cache[symbol].get("timestamp")
        if cache_time is None:
            return False
        age_minutes = (datetime.now() - cache_time).total_seconds() / 60
        return age_minutes < self.cache_ttl_minutes

    def fetch_quote(self, symbol: str) -> Optional[Dict]:
        """
        Fetch latest stock quote for a symbol.
        
        Returns:
            Dict with keys: symbol, price, change, change_percent, timestamp
            or None if fetch failed
        """
        # Check cache first
        if self._is_cache_valid(symbol):
            logger.info(f"Using cached data for {symbol}")
            return self.cache[symbol]

        self._respect_rate_limit()

        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key,
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error for {symbol}: {data['Error Message']}")
                return None
            
            if "Note" in data:
                logger.warning(f"Alpha Vantage rate limit hit: {data['Note']}")
                return None

            quote = data.get("Global Quote", {})
            
            if not quote or "05. price" not in quote:
                logger.warning(f"No quote data returned for {symbol}")
                return None

            result = {
                "symbol": symbol,
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%").rstrip("%"),
                "timestamp": datetime.now(),
                "volume": quote.get("06. volume", "0"),
                "previous_close": float(quote.get("08. previous close", 0)),
            }
            
            # Cache the result
            self.cache[symbol] = result
            
            logger.info(f"Fetched {symbol}: ${result['price']} ({result['change_percent']}%)")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {symbol}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to parse response for {symbol}: {e}")
            return None

    def fetch_multiple(self, symbols: list[str]) -> Dict[str, Optional[Dict]]:
        """
        Fetch quotes for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dict mapping symbol to quote data (or None if failed)
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.fetch_quote(symbol)
        return results

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()
        logger.info("Cache cleared")
