"""Application settings using Pydantic Settings"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings
    
    Loads configuration from:
    1. Environment variables
    2. .env file
    3. Default values
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore',
    )
    
    # Cache settings
    cache_dir: str = Field(default="./.cache", description="Cache directory path")
    cache_ttl: int = Field(default=86400, description="Cache TTL in seconds (default: 24h)")
    
    # Market settings
    default_market: str = Field(default="A", description="Default market: A, HK, or US")
    
    # API tokens (sensitive, should be set via environment)
    tushare_token: str = Field(default="", description="Tushare API token")
    
    @property
    def market_display(self) -> str:
        """Human-readable market name"""
        return {"A": "A 股", "HK": "港股", "US": "美股"}.get(self.default_market, self.default_market)


# Global settings instance (singleton)
settings = Settings()
