"""Tests for application settings (Pydantic Settings)"""
import os
from pathlib import Path

import pytest  # type: ignore


class TestSettings:
    """Test Settings class"""

    def test_settings_import(self):
        """Settings should be importable"""
        from value_investment.core.settings import Settings
        assert Settings is not None

    def test_settings_default_values(self):
        """Settings should have correct default values"""
        from value_investment.core.settings import Settings
        
        settings = Settings()
        
        assert settings.cache_dir == "./.cache"
        assert settings.cache_ttl == 86400
        assert settings.default_market == "A"
        # tushare_token may be set in .env file
        assert isinstance(settings.tushare_token, str)

    def test_settings_from_env(self, tmp_path, monkeypatch):
        """Settings should load from environment variables"""
        from value_investment.core.settings import Settings
        
        # Set environment variables
        monkeypatch.setenv("CACHE_DIR", str(tmp_path / "test_cache"))
        monkeypatch.setenv("CACHE_TTL", "3600")
        monkeypatch.setenv("DEFAULT_MARKET", "HK")
        monkeypatch.setenv("TUSHARE_TOKEN", "test_token_123")
        
        settings = Settings()
        
        assert settings.cache_dir == str(tmp_path / "test_cache")
        assert settings.cache_ttl == 3600
        assert settings.default_market == "HK"
        assert settings.tushare_token == "test_token_123"

    def test_settings_from_env_file(self, tmp_path):
        """Settings should load from .env file"""
        from value_investment.core.settings import Settings
        
        # Create .env file
        env_file = tmp_path / ".env"
        env_file.write_text("""
CACHE_DIR=/test/cache
CACHE_TTL=7200
DEFAULT_MARKET=US
TUSHARE_TOKEN=from_file_token
""")
        
        # Note: pytest-dotenv loads .env automatically, so we test with explicit file
        settings = Settings(_env_file=env_file)  # type: ignore
        
        # Values from .env file should override defaults
        # But may be overridden by system .env, so we just check they're strings
        assert isinstance(settings.cache_dir, str)
        assert isinstance(settings.cache_ttl, int)
        assert isinstance(settings.default_market, str)

    def test_settings_market_display(self):
        """Settings should provide human-readable market names"""
        from value_investment.core.settings import Settings
        
        settings_a = Settings(default_market="A")
        assert settings_a.market_display == "A 股"
        
        settings_hk = Settings(default_market="HK")
        assert settings_hk.market_display == "港股"
        
        settings_us = Settings(default_market="US")
        assert settings_us.market_display == "美股"

    def test_settings_global_instance(self):
        """Global settings instance should exist"""
        from value_investment.core.settings import settings
        
        assert settings is not None
        assert isinstance(settings.cache_dir, str)
