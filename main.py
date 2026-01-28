import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

from src.config import get_settings
from src.stock_fetcher import StockFetcher
from src.gemini_agent import GeminiAgent
from src.storage import StorageService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
settings = None
stock_fetcher = None
gemini_agent = None
storage_service = None


# Pydantic models for API responses
class StockQuote(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: str
    timestamp: str
    volume: str
    previous_close: float


class StockAnalysis(BaseModel):
    symbol: str
    price: float
    change_percent: str
    analysis: Optional[str]
    timestamp: str


class HealthCheck(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic."""
    global settings, stock_fetcher, gemini_agent, storage_service
    
    logger.info("Starting up application...")
    
    # Initialize services
    settings = get_settings()
    stock_fetcher = StockFetcher(settings.alpha_vantage_api_key)
    gemini_agent = GeminiAgent(settings.gemini_api_key)
    storage_service = StorageService(
        use_firestore=settings.use_firestore,
        credentials_path=settings.firebase_credentials_path
    )
    
    logger.info(f"Application initialized with {len(settings.stocks_list)} stocks to monitor")
    
    yield
    
    # Cleanup
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Google Stock Agent",
    description="AI-powered stock data fetching and analysis using Google Gemini",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services={
            "stock_fetcher": "ready",
            "gemini_agent": "ready",
            "storage": "ready"
        }
    )


@app.get("/stocks/quote/{symbol}", response_model=StockQuote)
async def get_stock_quote(symbol: str):
    """
    Get latest stock quote for a symbol.
    
    Args:
        symbol: Stock symbol (e.g., AAPL)
    """
    if not stock_fetcher:
        raise HTTPException(status_code=503, detail="Stock fetcher not initialized")
    
    quote = stock_fetcher.fetch_quote(symbol.upper())
    
    if quote is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch quote for {symbol}"
        )
    
    return StockQuote(
        symbol=quote["symbol"],
        price=quote["price"],
        change=quote["change"],
        change_percent=quote["change_percent"],
        timestamp=quote["timestamp"].isoformat(),
        volume=quote["volume"],
        previous_close=quote["previous_close"]
    )


@app.post("/analyze/single/{symbol}", response_model=StockAnalysis)
async def analyze_single_stock(symbol: str):
    """
    Analyze a single stock using Gemini AI.
    
    Args:
        symbol: Stock symbol (e.g., AAPL)
    """
    if not stock_fetcher or not gemini_agent or not storage_service:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    # Fetch stock data
    quote = stock_fetcher.fetch_quote(symbol.upper())
    if quote is None:
        raise HTTPException(status_code=404, detail=f"Could not fetch {symbol}")
    
    # Analyze with Gemini
    analysis = gemini_agent.analyze_stock(quote)
    
    # Prepare result
    result = {
        "symbol": quote["symbol"],
        "price": quote["price"],
        "change_percent": quote["change_percent"],
        "analysis": analysis,
        "timestamp": quote["timestamp"].isoformat()
    }
    
    # Save to storage
    storage_service.save_analysis(result)
    
    return StockAnalysis(**result)


@app.post("/analyze/batch")
async def analyze_batch():
    """
    Analyze all configured stocks in batch.
    
    Returns detailed analysis for each stock.
    """
    if not stock_fetcher or not gemini_agent or not storage_service:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    stocks = settings.stocks_list
    logger.info(f"Starting batch analysis for {len(stocks)} stocks")
    
    # Fetch all quotes
    quotes = stock_fetcher.fetch_multiple(stocks)
    
    # Analyze batch
    analyses = gemini_agent.analyze_multiple(quotes)
    
    # Prepare results
    results = []
    for symbol, quote in quotes.items():
        if quote is None:
            continue
        
        result = {
            "symbol": symbol,
            "price": quote["price"],
            "change": quote["change"],
            "change_percent": quote["change_percent"],
            "analysis": analyses.get(symbol, "No analysis available"),
            "timestamp": quote["timestamp"].isoformat()
        }
        
        results.append(result)
        storage_service.save_analysis(result)
    
    logger.info(f"Completed batch analysis for {len(results)} stocks")
    
    return {
        "count": len(results),
        "timestamp": datetime.now().isoformat(),
        "analyses": results
    }


@app.get("/history/{symbol}")
async def get_analysis_history(symbol: str, limit: int = 10):
    """
    Get recent analyses for a symbol.
    
    Args:
        symbol: Stock symbol
        limit: Number of recent analyses to return
    """
    if not storage_service:
        raise HTTPException(status_code=503, detail="Storage service not initialized")
    
    latest = storage_service.get_latest_analysis(symbol.upper())
    
    if latest is None:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis history found for {symbol}"
        )
    
    return {
        "symbol": symbol.upper(),
        "latest_analysis": latest
    }


@app.get("/config")
async def get_config():
    """Get current configuration (public info only)."""
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "stocks_monitored": settings.stocks_list,
        "check_frequency_hours": settings.check_frequency_hours,
        "environment": settings.environment,
        "gemini_model": "gemini-2.5-flash-lite",
        "estimated_monthly_cost": "$0.95 - $2.00 (Gemini tokens only)"
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Google Stock Agent API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "stock_quote": "/stocks/quote/{symbol}",
            "analyze_single": "/analyze/single/{symbol}",
            "analyze_batch": "/analyze/batch",
            "history": "/history/{symbol}",
            "config": "/config",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
