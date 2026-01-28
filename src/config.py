import logging
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini API
    gemini_api_key: str
    
    # Alpha Vantage
    alpha_vantage_api_key: str
    
    # Firebase/Firestore
    firebase_project_id: Optional[str] = None
    firebase_credentials_path: Optional[str] = None
    use_firestore: bool = False
    
    # Stock Configuration
    stocks_to_monitor: str = "AAPL,MSFT,GOOGL,AMZN,NVDA"
    check_frequency_hours: int = 4
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    app_name: str = "Google Stock Agent"
    version: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def stocks_list(self) -> list[str]:
        """Return list of stocks to monitor."""
        return [s.strip().upper() for s in self.stocks_to_monitor.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance (cached)."""
    return Settings()
