"""Tests for SimpleContainer"""

import os

import pytest  # type: ignore
import pandas as pd
from unittest.mock import Mock, patch

from value_investment.core.container_simple import SimpleContainer
from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
from value_investment.core.defaults import DEFAULT_DATASOURCES


class MockCache:
    """Mock cache for testing"""
    
    def __init__(self):
        self._data = {}
    
    def get(self, key):
        return self._data.get(key)
    
    def set(self, key, value, ttl=None):
        self._data[key] = value
    
    def invalidate(self, key):
        if key in self._data:
            del self._data[key]
    
    def clear(self):
        self._data.clear()


class TestSimpleContainerInit:
    """Test SimpleContainer initialization"""

    def test_init_default(self):
        """Should initialize with defaults"""
        container = SimpleContainer()
        
        assert container._datasources == DEFAULT_DATASOURCES
        assert container._cache is not None

    def test_init_custom_datasources(self):
        """Should accept custom datasources"""
        custom_config = DEFAULT_DATASOURCES
        
        container = SimpleContainer(datasources=custom_config)
        
        assert container._datasources == custom_config

    def test_init_custom_cache_params(self):
        """Should accept custom cache parameters"""
        container = SimpleContainer(
            cache_dir="/tmp/test_cache",
            cache_ttl=3600
        )
        
        assert container._cache is not None


class TestSimpleContainerProviderCreation:
    """Test provider creation"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_create_yfinance_provider(self, mock_yf):
        """Should create YFinanceProvider"""
        mock_yf.Ticker.return_value = Mock()
        
        container = SimpleContainer()
        provider = container.create_provider("yfinance")
        
        assert provider is not None
        assert provider.__class__.__name__ == "YFinanceProvider"

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_create_yfinance_provider(self, mock_yf):
        """Should create YFinanceProvider"""
        mock_yf.Ticker.return_value = Mock()
        
        container = SimpleContainer()
        provider = container.create_provider("yfinance")
        
        assert provider is not None
        assert provider.__class__.__name__ == "YFinanceProvider"

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_create_provider_singleton(self, mock_yf):
        """Should cache provider instances"""
        mock_yf.Ticker.return_value = Mock()
        
        container = SimpleContainer()
        
        # First call - creates provider
        provider1 = container.get_provider("yfinance")
        
        # Second call - returns cached provider
        provider2 = container.get_provider("yfinance")
        
        assert provider1 is provider2

    def test_create_provider_not_found(self):
        """Should raise error for unknown provider"""
        container = SimpleContainer()
        
        with pytest.raises(KeyError):
            container.create_provider("unknown_provider")


class TestSimpleContainerMarketRouting:
    """Test market-specific provider routing"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_market_provider_hk_market(self, mock_yf):
        """Should return yfinance provider for HK market"""
        mock_yf.Ticker.return_value = Mock()
        
        container = SimpleContainer()
        provider = container.get_market_provider("HK")
        
        assert provider.__class__.__name__ == "YFinanceProvider"

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_market_provider_us_market(self, mock_yf):
        """Should return yfinance provider for US market"""
        mock_yf.Ticker.return_value = Mock()
        
        container = SimpleContainer()
        provider = container.get_market_provider("US")
        
        assert provider.__class__.__name__ == "YFinanceProvider"

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_provider_for_data_type_market(self, mock_yf):
        """Should route based on data type"""
        mock_yf.Ticker.return_value = Mock()
        
        container = SimpleContainer()
        
        # Market data for HK
        provider = container.get_provider_for_data_type("HK", "market")
        assert provider.__class__.__name__ == "YFinanceProvider"


class TestSimpleContainerProperties:
    """Test container properties"""

    def test_datasources_property(self):
        """Should provide datasources property"""
        container = SimpleContainer()
        
        assert container.datasources is not None
        assert container.datasources == DEFAULT_DATASOURCES

    def test_cache_property(self):
        """Should provide cache property"""
        container = SimpleContainer()
        
        assert container.cache is not None


class TestSimpleContainerClearCache:
    """Test cache clearing"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_clear_cache(self, mock_yf):
        """Should clear all caches"""
        mock_yf.Ticker.return_value = Mock()
        
        container = SimpleContainer()
        
        # Create provider (cached)
        provider = container.get_provider("yfinance")
        
        # Clear provider cache
        container._providers.clear()
        
        # Provider cache should be cleared
        assert "yfinance" not in container._providers


class TestSimpleContainerIntegration:
    """Integration tests"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_yfinance_workflow(self, mock_yf):
        """Should work end-to-end with yfinance"""
        mock_ticker = Mock()
        mock_history = pd.DataFrame({
            'Open': [100.0],
            'Close': [101.0],
        }, index=pd.date_range('2023-01-01', periods=1))
        mock_ticker.history.return_value = mock_history
        mock_yf.Ticker.return_value = mock_ticker
        
        container = SimpleContainer()
        
        # Get provider
        provider = container.get_market_provider("HK")
        
        # Use provider
        df = provider.get_historical_data("0005.HK", start_date="20230101", end_date="20231231")
        
        assert len(df) > 0
