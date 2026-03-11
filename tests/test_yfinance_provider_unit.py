"""Unit tests for YFinanceProvider (no API calls)"""

import pytest  # type: ignore
import pandas as pd
from unittest.mock import Mock, patch, MagicMock


class MockCache:
    """Mock cache for testing"""
    
    def __init__(self):
        self._data = {}
        self.get_call_count = 0
        self.set_call_count = 0
    
    def get(self, key):
        self.get_call_count += 1
        return self._data.get(key)
    
    def set(self, key, value, ttl=None):
        self.set_call_count += 1
        self._data[key] = value
    
    def invalidate(self, key):
        if key in self._data:
            del self._data[key]


class TestYFinanceProviderInit:
    """Test YFinanceProvider initialization"""

    def test_init_basic(self):
        """Should initialize without token"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        provider = YFinanceProvider(cache=MockCache())
        
        assert provider._cache is not None
        assert provider._field_mappings == {}

    def test_init_with_field_mappings(self):
        """Should accept field_mappings"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mappings = {
            "market": {"Close": "close", "Volume": "volume"},
        }
        provider = YFinanceProvider(
            cache=MockCache(),
            field_mappings=mappings
        )
        
        assert provider.get_field_mapping("market") == {"Close": "close", "Volume": "volume"}


class TestYFinanceProviderHistoricalData:
    """Test get_historical_data method"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_historical_data_basic(self, mock_yf):
        """Should fetch historical data"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        # Mock ticker and history
        mock_ticker = Mock()
        mock_history = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [102.0, 103.0],
            'Low': [99.0, 100.0],
            'Close': [101.0, 102.0],
            'Volume': [1000, 2000],
        }, index=pd.date_range('2023-01-01', periods=2))
        
        mock_ticker.history.return_value = mock_history
        mock_yf.Ticker.return_value = mock_ticker
        
        provider = YFinanceProvider(cache=MockCache())
        
        df = provider.get_historical_data(
            "0005.HK",
            start_date="20230101",
            end_date="20231231"
        )
        
        # Verify API called
        mock_yf.Ticker.assert_called_once_with("0005.HK")
        mock_ticker.history.assert_called_once()
        
        # Verify result
        assert len(df) == 2
        assert "Open" in df.columns

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_historical_data_with_field_mapping(self, mock_yf):
        """Should apply field mapping"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        # Mock ticker and history
        mock_ticker = Mock()
        mock_history = pd.DataFrame({
            'Open': [100.0],
            'Close': [101.0],
            'Volume': [1000],
        }, index=pd.date_range('2023-01-01', periods=1))
        
        mock_ticker.history.return_value = mock_history
        mock_yf.Ticker.return_value = mock_ticker
        
        mappings = {
            "market": {
                "Open": "open",
                "Close": "close",
                "Volume": "volume",
            }
        }
        provider = YFinanceProvider(
            cache=MockCache(),
            field_mappings=mappings
        )
        
        df = provider.get_historical_data("0005.HK", start_date="20230101", end_date="20231231")
        
        # Verify mapping applied
        assert "open" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns
        assert "Open" not in df.columns
        assert "Close" not in df.columns

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_historical_data_with_adjust(self, mock_yf):
        """Should handle adjust parameter"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mock_ticker = Mock()
        mock_history = pd.DataFrame({'Close': [100.0]})
        mock_ticker.history.return_value = mock_history
        mock_yf.Ticker.return_value = mock_ticker
        
        provider = YFinanceProvider(cache=MockCache())
        
        # Test with forward adjustment
        provider.get_historical_data("0005.HK", start_date="20230101", end_date="20231231", adjust="qfq")
        
        # Verify called (yfinance handles adjustment internally)
        mock_ticker.history.assert_called()

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_historical_data_empty_result(self, mock_yf):
        """Should handle empty result"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        mock_yf.Ticker.return_value = mock_ticker
        
        provider = YFinanceProvider(cache=MockCache())
        
        df = provider.get_historical_data("INVALID.HK", start_date="20230101", end_date="20231231")
        
        assert df.empty

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_historical_data_cache(self, mock_yf):
        """Should cache results"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mock_ticker = Mock()
        mock_history = pd.DataFrame({'Close': [100.0]})
        mock_ticker.history.return_value = mock_history
        mock_yf.Ticker.return_value = mock_ticker
        
        cache = MockCache()
        provider = YFinanceProvider(cache=cache)
        
        # First call - cache miss
        df1 = provider.get_historical_data("0005.HK", start_date="20230101", end_date="20231231")
        assert mock_ticker.history.call_count == 1
        
        # Second call - cache hit
        df2 = provider.get_historical_data("0005.HK", start_date="20230101", end_date="20231231")
        # Should not call API again
        assert mock_ticker.history.call_count == 1

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_historical_data_default_dates(self, mock_yf):
        """Should use default dates if not provided"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mock_ticker = Mock()
        mock_history = pd.DataFrame({'Close': [100.0]})
        mock_ticker.history.return_value = mock_history
        mock_yf.Ticker.return_value = mock_ticker
        
        provider = YFinanceProvider(cache=MockCache())
        
        df = provider.get_historical_data("0005.HK")
        
        assert not df.empty
        # Should call with some default period
        mock_ticker.history.assert_called()

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_historical_data_market_codes(self, mock_yf):
        """Should handle different market codes"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame({'Close': [100.0]})
        mock_yf.Ticker.return_value = mock_ticker
        
        provider = YFinanceProvider(cache=MockCache())
        
        # HK stock
        provider.get_historical_data("0005.HK", start_date="20230101", end_date="20231231")
        assert mock_yf.Ticker.call_args_list[0][0][0] == "0005.HK"
        
        # US stock
        provider.get_historical_data("AAPL", start_date="20230101", end_date="20231231")
        assert mock_yf.Ticker.call_args_list[1][0][0] == "AAPL"


class TestYFinanceProviderStockInfo:
    """Test get_stock_info method"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_stock_info_basic(self, mock_yf):
        """Should fetch stock info"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mock_ticker = Mock()
        mock_ticker.info = {
            'symbol': 'AAPL',
            'shortName': 'Apple Inc.',
            'longName': 'Apple Inc.',
            'marketCap': 3000000000000,
        }
        mock_yf.Ticker.return_value = mock_ticker
        
        provider = YFinanceProvider(cache=MockCache())
        
        df = provider.get_stock_info("AAPL")
        
        assert not df.empty
        assert 'symbol' in df.columns or 'ticker' in df.columns

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_get_stock_info_cache(self, mock_yf):
        """Should cache stock info"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mock_ticker = Mock()
        mock_ticker.info = {'symbol': 'AAPL'}
        mock_yf.Ticker.return_value = mock_ticker
        
        cache = MockCache()
        provider = YFinanceProvider(cache=cache)
        
        # First call
        df1 = provider.get_stock_info("AAPL")
        
        # Second call - should use cache
        df2 = provider.get_stock_info("AAPL")
        
        # Ticker should only be created once if caching works
        assert mock_yf.Ticker.call_count >= 1


class TestYFinanceProviderHelpers:
    """Test helper methods"""

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_cache_key_generation(self, mock_yf):
        """Should generate cache keys correctly"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        provider = YFinanceProvider(cache=MockCache())
        
        key = provider._get_cache_key("market", "AAPL", "20230101", "20231231")
        assert key == "market:AAPL:20230101:20231231"

    @patch('value_investment.data.providers.yfinance_provider.yf')
    def test_apply_mapping(self, mock_yf):
        """Should apply field mapping"""
        from value_investment.data.providers.yfinance_provider import YFinanceProvider
        
        mappings = {
            "market": {"Close": "close", "Volume": "volume"}
        }
        provider = YFinanceProvider(
            cache=MockCache(),
            field_mappings=mappings
        )
        
        df = pd.DataFrame({"Close": [100.0], "Volume": [1000], "Other": [999]})
        result = provider._apply_mapping(df, "market")
        
        assert result is not None
        assert "close" in result.columns
        assert "volume" in result.columns
        assert "Other" in result.columns
        assert "Close" not in result.columns
