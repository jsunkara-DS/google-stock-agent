"""Batch processing and scheduling utilities."""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from src.config import Settings
from src.stock_fetcher import StockFetcher
from src.gemini_agent import GeminiAgent
from src.storage import StorageService

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Handle batch processing of stock analysis."""

    def __init__(
        self,
        settings: Settings,
        stock_fetcher: StockFetcher,
        gemini_agent: GeminiAgent,
        storage_service: StorageService,
    ):
        self.settings = settings
        self.stock_fetcher = stock_fetcher
        self.gemini_agent = gemini_agent
        self.storage_service = storage_service

    async def process_stocks(self, symbols: Optional[List[str]] = None) -> Dict:
        """
        Process a batch of stocks.
        
        Args:
            symbols: List of symbols to process (uses configured list if None)
            
        Returns:
            Dict with processing results
        """
        symbols = symbols or self.settings.stocks_list
        logger.info(f"Starting batch processing for {len(symbols)} stocks")

        start_time = datetime.now()

        # Fetch all quotes
        logger.info(f"Fetching quotes for {len(symbols)} stocks...")
        quotes = self.stock_fetcher.fetch_multiple(symbols)
        
        successful_fetches = sum(1 for q in quotes.values() if q is not None)
        logger.info(f"Successfully fetched {successful_fetches}/{len(symbols)} quotes")

        # Analyze batch
        logger.info("Analyzing batch with Gemini...")
        analyses = self.gemini_agent.analyze_multiple(quotes)

        # Save results
        logger.info("Saving results...")
        saved_count = 0
        results = []

        for symbol, quote in quotes.items():
            if quote is None:
                logger.warning(f"Skipping {symbol} - no quote data")
                continue

            result = {
                "symbol": symbol,
                "price": quote["price"],
                "change": quote["change"],
                "change_percent": quote["change_percent"],
                "volume": quote["volume"],
                "previous_close": quote["previous_close"],
                "analysis": analyses.get(symbol, "No analysis available"),
                "timestamp": quote["timestamp"].isoformat(),
                "processed_at": datetime.now().isoformat(),
            }

            if self.storage_service.save_analysis(result):
                saved_count += 1
            results.append(result)

        elapsed_time = (datetime.now() - start_time).total_seconds()

        summary = {
            "status": "success",
            "total_stocks": len(symbols),
            "successful_fetches": successful_fetches,
            "analyses_completed": len([a for a in analyses.values() if a]),
            "saved_results": saved_count,
            "results": results,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "elapsed_seconds": elapsed_time,
        }

        logger.info(f"Batch processing completed in {elapsed_time:.2f}s")
        return summary

    async def process_single(self, symbol: str) -> Optional[Dict]:
        """
        Process a single stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Analysis result or None
        """
        logger.info(f"Processing single stock: {symbol}")

        quote = self.stock_fetcher.fetch_quote(symbol)
        if quote is None:
            logger.error(f"Failed to fetch quote for {symbol}")
            return None

        analysis = self.gemini_agent.analyze_stock(quote)

        result = {
            "symbol": symbol,
            "price": quote["price"],
            "change": quote["change"],
            "change_percent": quote["change_percent"],
            "analysis": analysis,
            "timestamp": quote["timestamp"].isoformat(),
            "processed_at": datetime.now().isoformat(),
        }

        self.storage_service.save_analysis(result)
        logger.info(f"Completed processing for {symbol}")

        return result
