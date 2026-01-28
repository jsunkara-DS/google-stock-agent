import logging
from typing import Dict, Optional
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)


class GeminiAgent:
    """Stock analysis agent using Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite"):
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=api_key)
        self.client = genai.Client()
        logger.info(f"Initialized Gemini agent with model: {model}")

    def analyze_stock(self, stock_data: Dict) -> Optional[str]:
        """
        Analyze a single stock using Gemini.
        
        Args:
            stock_data: Dict with symbol, price, change, change_percent, etc.
            
        Returns:
            Analysis summary or None if failed
        """
        if not stock_data:
            return None

        prompt = self._build_analysis_prompt(stock_data)
        
        try:
            response = genai.GenerativeModel(self.model).generate_content(prompt)
            analysis = response.text
            logger.info(f"Generated analysis for {stock_data['symbol']}")
            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze {stock_data['symbol']}: {e}")
            return None

    def analyze_multiple(self, stocks_data: Dict[str, Dict]) -> Dict[str, Optional[str]]:
        """
        Analyze multiple stocks in a single batch request for efficiency.
        
        Args:
            stocks_data: Dict mapping symbol to stock data
            
        Returns:
            Dict mapping symbol to analysis
        """
        valid_stocks = {k: v for k, v in stocks_data.items() if v is not None}
        
        if not valid_stocks:
            logger.warning("No valid stock data to analyze")
            return {}

        prompt = self._build_batch_analysis_prompt(valid_stocks)
        
        try:
            response = genai.GenerativeModel(self.model).generate_content(prompt)
            analysis_text = response.text
            logger.info(f"Generated batch analysis for {len(valid_stocks)} stocks")
            
            # Parse the response and map back to symbols
            return self._parse_batch_response(analysis_text, valid_stocks)
        except Exception as e:
            logger.error(f"Failed to analyze batch: {e}")
            # Fallback to individual analyses
            return {symbol: self.analyze_stock(data) 
                   for symbol, data in valid_stocks.items()}

    def _build_analysis_prompt(self, stock_data: Dict) -> str:
        """Build a prompt for analyzing a single stock."""
        return f"""Analyze this stock data and provide a concise trading insight:

Stock: {stock_data['symbol']}
Current Price: ${stock_data['price']:.2f}
Change: {stock_data['change']:.2f} ({stock_data['change_percent']}%)
Previous Close: ${stock_data['previous_close']:.2f}
Volume: {stock_data.get('volume', 'N/A')}
Timestamp: {stock_data['timestamp'].isoformat()}

Provide:
1. Brief market sentiment (bullish/bearish/neutral)
2. Key price action insights
3. Potential trading signal
4. Risk assessment

Keep response under 150 words."""

    def _build_batch_analysis_prompt(self, stocks_data: Dict[str, Dict]) -> str:
        """Build a prompt for analyzing multiple stocks."""
        stocks_info = "\n".join([
            f"- {symbol}: ${data['price']:.2f} ({data['change_percent']}%)"
            for symbol, data in stocks_data.items()
        ])

        return f"""Analyze these stocks and identify trading opportunities:

{stocks_info}

For each stock, provide:
1. Market sentiment (bullish/bearish/neutral)
2. Key price action
3. Trading signal

Focus on opportunities and risks. Use clear formatting with symbol headers.
Keep response concise and actionable."""

    def _parse_batch_response(self, response_text: str, stocks_data: Dict) -> Dict[str, str]:
        """Parse batch response and map back to symbols."""
        result = {}
        for symbol in stocks_data.keys():
            # Simple parsing: look for symbol mentions in response
            if symbol in response_text:
                result[symbol] = response_text
            else:
                result[symbol] = "Analysis generated but symbol not clearly identified in batch response"
        return result

    def get_model_info(self) -> Dict:
        """Get information about the current model."""
        return {
            "model": self.model,
            "type": "Gemini",
            "cost_tier": "free" if "flash" in self.model.lower() else "premium"
        }
