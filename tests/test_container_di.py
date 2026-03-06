"""Tests for Container (dependency-injector version)

These tests verify that the dependency-injector Container works correctly.
The original SimpleContainer has been removed in favor of using the mature
dependency-injector library.
"""

import os
import pytest  # type: ignore
import pandas as pd
from unittest.mock import Mock, patch

from value_investment.core.container import (
    Container,
    create_provider,
    get_financial_provider,
    get_market_provider,
)
from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
from value_investment.core.defaults import DEFAULT_DATASOURCES


class TestContainerInit:
    """Test Container initialization"""

    def test_init_default(self):
        """Should initialize with defaults"""
        container = Container()

        assert container.datasources() == DEFAULT_DATASOURCES
        assert container.cache() is not None

    def test_init_custom_cache_params(self):
        """Should accept custom cache parameters"""
        container = Container()
        container.config.cache_dir.from_value("/tmp/test_cache")
        container.config.cache_ttl.from_value(3600)

        assert container.cache() is not None


class TestContainerProviderCreation:
    """Test provider creation"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_create_yfinance_provider(self, mock_yf):
        """Should create YFinanceProvider"""
        mock_yf.Ticker.return_value = Mock()

        container = Container()
        provider = create_provider(container, "yfinance")

        assert provider is not None
        assert provider.__class__.__name__ == "YFinanceProvider"

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_provider_creates_new_instance(self, mock_yf):
        """Should create provider instance via create_provider"""
        mock_yf.Ticker.return_value = Mock()

        container = Container()

        # Create provider
        provider1 = create_provider(container, "yfinance")

        # Create another - creates new instance each time
        provider2 = create_provider(container, "yfinance")

        assert provider1 is not None
        assert provider2 is not None
        assert provider1.__class__.__name__ == "YFinanceProvider"

    def test_create_provider_not_found(self):
        """Should raise error for unknown provider"""
        container = Container()

        with pytest.raises(KeyError):
            create_provider(container, "unknown_provider")


class TestContainerMarketRouting:
    """Test market-specific provider routing"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_market_provider_hk_market(self, mock_yf):
        """Should return yfinance provider for HK market"""
        mock_yf.Ticker.return_value = Mock()

        container = Container()
        provider = get_market_provider(container, "HK")

        assert provider.__class__.__name__ == "YFinanceProvider"

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_market_provider_us_market(self, mock_yf):
        """Should return yfinance provider for US market"""
        mock_yf.Ticker.return_value = Mock()

        container = Container()
        provider = get_market_provider(container, "US")

        assert provider.__class__.__name__ == "YFinanceProvider"


class TestContainerProperties:
    """Test container properties"""

    def test_datasources_property(self):
        """Should provide datasources property"""
        container = Container()

        assert container.datasources() is not None
        assert container.datasources() == DEFAULT_DATASOURCES

    def test_cache_property(self):
        """Should provide cache property"""
        container = Container()

        assert container.cache() is not None


class TestContainerIntegration:
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

        container = Container()

        # Get provider
        provider = get_market_provider(container, "HK")

        # Use provider
        df = provider.get_historical_data("0005.HK", start_date="20230101", end_date="20231231")

        assert len(df) > 0
