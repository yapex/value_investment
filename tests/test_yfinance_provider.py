"""Tests for yfinance provider"""
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch


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
    
    def get_or_fetch_with_range(self, key, date_column, fetch_func, start_date, end_date, ttl, force_refresh):
        cached = self._data.get(key)
        if cached is not None and not force_refresh:
            return cached
        result = fetch_func()
        self._data[key] = result
        return result
    
    def get_or_fetch(self, key, fetch_func, ttl, force_refresh):
        cached = self._data.get(key)
        if cached is not None and not force_refresh:
            return cached
        result = fetch_func()
        self._data[key] = result
        return result


class TestYFinanceProviderInit:
    """Test YFinanceProvider initialization"""

    def test_init_default(self):
        """Should initialize with default market"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        provider = YFinanceProvider(cache=MockCache())
        assert provider._market == "US"

    def test_init_with_market(self):
        """Should initialize with custom market"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        provider = YFinanceProvider(cache=MockCache(), market="US")
        assert provider._market == "US"


class TestYFinanceProviderStockInfo:
    """Test get_stock_info method"""

    def test_get_stock_info_basic(self):
        """Should fetch stock info"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.yfinance_provider.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.info = {"shortName": "Apple Inc.", "sector": "Technology"}
            mock_yf.Ticker.return_value = mock_ticker
            
            provider = YFinanceProvider(cache=cache)
            result = provider.get_stock_info("AAPL")
            
            assert not result.empty


class TestYFinanceProviderHistoricalData:
    """Test get_historical_data method"""

    def test_get_historical_data_basic(self):
        """Should fetch historical data"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.yfinance_provider.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = pd.DataFrame({
                "Open": [150.0, 155.0],
                "High": [155.0, 160.0],
                "Low": [148.0, 153.0],
                "Close": [152.0, 157.0],
                "Volume": [1000000, 1100000]
            }, index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
            mock_yf.Ticker.return_value = mock_ticker
            
            provider = YFinanceProvider(cache=cache)
            result = provider.get_historical_data("AAPL")
            
            assert not result.empty


class TestYFinanceProviderFinancial:
    """Test financial data methods"""

    def test_get_balance_sheet_basic(self):
        """Should fetch balance sheet"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.yfinance_provider.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.balance_sheet = pd.DataFrame({
                "Total Assets": [1000000],
                "Total Liabilities": [500000]
            })
            mock_yf.Ticker.return_value = mock_ticker
            
            provider = YFinanceProvider(cache=cache)
            result = provider.get_balance_sheet("AAPL", 2023)
            
            assert result is not None

    def test_get_income_statement_basic(self):
        """Should fetch income statement"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.yfinance_provider.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.income_stmt = pd.DataFrame({
                "Net Income": [500000]
            })
            mock_yf.Ticker.return_value = mock_ticker
            
            provider = YFinanceProvider(cache=cache)
            result = provider.get_income_statement("AAPL", 2023)
            
            assert result is not None

    def test_get_cash_flow_statement_basic(self):
        """Should fetch cash flow statement"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.yfinance_provider.yf") as mock_yf:
            mock_ticker = MagicMock()
            mock_ticker.cashflow = pd.DataFrame({
                "Operating Cash Flow": [300000]
            })
            mock_yf.Ticker.return_value = mock_ticker
            
            provider = YFinanceProvider(cache=cache)
            result = provider.get_cash_flow_statement("AAPL", 2023)
            
            assert result is not None
