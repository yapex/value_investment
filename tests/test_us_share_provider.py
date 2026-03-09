"""Tests for USShareProvider"""
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


class TestUSShareProviderInit:
    """Test USShareProvider initialization"""

    def test_init_default(self):
        """Should initialize with default market"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        assert provider._market == "US"

    def test_init_with_market(self):
        """Should initialize with custom market"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache(), market="US")
        assert provider._market == "US"


class TestUSShareProviderNormalize:
    """Test date normalization"""

    def test_normalize_date_8_digit(self):
        """Should normalize 8-digit date"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        
        assert provider._normalize_date("20240101") == "2024-01-01"
        assert provider._normalize_date("19991231") == "1999-12-31"

    def test_normalize_date_already_formatted(self):
        """Should handle already formatted date"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        
        assert provider._normalize_date("2024-01-01") == "2024-01-01"
        assert provider._normalize_date(None) is None


class TestUSShareProviderStockInfo:
    """Test get_stock_info method"""

    def test_get_stock_info_basic(self):
        """Should fetch stock info"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            mock_ak.stock_individual_basic_info_us_xq.return_value = pd.DataFrame({
                "item": ["Name"],
                "value": ["Apple Inc."]
            })
            
            provider = USShareProvider(cache=cache)
            result = provider.get_stock_info("AAPL")
            
            assert not result.empty

    def test_get_stock_info_with_cache(self):
        """Should use cache when available"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"item": ["Name"], "value": ["Apple"]})
        cache.set("info_AAPL", cached_data)
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            provider = USShareProvider(cache=cache)
            result = provider.get_stock_info("AAPL")
            
            mock_ak.stock_individual_basic_info_us_xq.assert_not_called()
            assert result.equals(cached_data)


class TestUSShareProviderHistoricalData:
    """Test get_historical_data method"""

    def test_get_historical_data_basic(self):
        """Should fetch historical data"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            mock_ak.stock_us_daily.return_value = pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02"],
                "open": [150.0, 155.0],
                "close": [152.0, 157.0],
                "high": [155.0, 160.0],
                "low": [148.0, 153.0],
                "volume": [1000000, 1100000]
            })
            
            provider = USShareProvider(cache=cache)
            result = provider.get_historical_data("AAPL")
            
            assert not result.empty

    def test_get_historical_data_empty(self):
        """Should handle empty data"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            mock_ak.stock_us_daily.return_value = None
            
            provider = USShareProvider(cache=cache)
            result = provider.get_historical_data("INVALID")
            
            assert result.empty

    def test_get_historical_data_with_dates(self):
        """Should filter by date range"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            mock_ak.stock_us_daily.return_value = pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "open": [150.0, 155.0, 160.0],
                "close": [152.0, 157.0, 162.0],
                "high": [155.0, 160.0, 165.0],
                "low": [148.0, 153.0, 158.0],
                "volume": [1000000, 1100000, 1200000]
            })
            
            provider = USShareProvider(cache=cache)
            result = provider.get_historical_data(
                "AAPL",
                start_date="20240101",
                end_date="20240102"
            )
            
            assert not result.empty


class TestUSShareProviderFinancial:
    """Test financial data methods"""

    def test_get_balance_sheet_basic(self):
        """Should fetch balance sheet"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            mock_ak.stock_financial_us_report_em.return_value = pd.DataFrame({
                "ITEM_NAME": ["Total Assets"],
                "AMOUNT": [1000000],
                "REPORT_DATE": ["2023-12-31"]
            })
            
            provider = USShareProvider(cache=cache)
            result = provider.get_balance_sheet("AAPL", 2023)
            
            assert result is not None

    def test_get_income_statement_basic(self):
        """Should fetch income statement"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            mock_ak.stock_financial_us_report_em.return_value = pd.DataFrame({
                "ITEM_NAME": ["Net Income"],
                "AMOUNT": [500000],
                "REPORT_DATE": ["2023-12-31"]
            })
            
            provider = USShareProvider(cache=cache)
            result = provider.get_income_statement("AAPL", 2023)
            
            assert result is not None

    def test_get_cash_flow_statement_basic(self):
        """Should fetch cash flow statement"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            mock_ak.stock_financial_us_report_em.return_value = pd.DataFrame({
                "ITEM_NAME": ["Operating Cash Flow"],
                "AMOUNT": [300000],
                "REPORT_DATE": ["2023-12-31"]
            })
            
            provider = USShareProvider(cache=cache)
            result = provider.get_cash_flow_statement("AAPL", 2023)
            
            assert result is not None


class TestUSShareProviderTransform:
    """Test data transformation"""

    def test_transform_us_financial_data_basic(self):
        """Should transform financial data"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        
        df = pd.DataFrame({
            "ITEM_NAME": ["Total Assets", "Net Income"],
            "AMOUNT": [1000000, 500000],
            "REPORT_DATE": ["2023-12-31", "2023-12-31"]
        })
        
        result = provider._transform_us_financial_data(df)
        
        assert not result.empty

    def test_transform_us_financial_data_empty(self):
        """Should handle empty DataFrame"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        
        result = provider._transform_us_financial_data(pd.DataFrame())
        
        assert result.empty

    def test_transform_us_financial_data_no_required_columns(self):
        """Should handle missing columns"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        
        df = pd.DataFrame({"other_column": [1, 2]})
        
        result = provider._transform_us_financial_data(df)
        
        assert result.equals(df)


class TestUSShareProviderFilter:
    """Test year filtering"""

    def test_filter_by_year_basic(self):
        """Should filter by year"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        
        df = pd.DataFrame({
            "year": [2020, 2021, 2022, 2023],
            "value": [100, 200, 300, 400]
        })
        
        result = provider._filter_by_year(df, 2022)
        
        assert len(result) == 3
        assert all(result["year"] <= 2022)

    def test_filter_by_year_empty(self):
        """Should handle empty DataFrame"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        
        result = provider._filter_by_year(pd.DataFrame(), 2022)
        
        assert result.empty

    def test_filter_by_year_no_year_column(self):
        """Should handle DataFrame without year column"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        provider = USShareProvider(cache=MockCache())
        
        df = pd.DataFrame({"value": [100, 200]})
        
        result = provider._filter_by_year(df, 2022)
        
        assert result.equals(df)


class TestUSShareProviderCache:
    """Test cache functionality"""

    def test_get_balance_sheet_uses_cache(self):
        """Should use cache for balance sheet"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"year": [2023], "total_assets": [100]})
        cache.set("balance_sheet_us_AAPL", cached_data)
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            provider = USShareProvider(cache=cache)
            result = provider.get_balance_sheet("AAPL", 2023)
            
            mock_ak.stock_financial_us_report_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_income_statement_uses_cache(self):
        """Should use cache for income statement"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"year": [2023], "net_profit": [100]})
        cache.set("profit_sheet_us_AAPL", cached_data)
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            provider = USShareProvider(cache=cache)
            result = provider.get_income_statement("AAPL", 2023)
            
            mock_ak.stock_financial_us_report_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_cash_flow_statement_uses_cache(self):
        """Should use cache for cash flow statement"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"year": [2023], "operating_cash_flow": [100]})
        cache.set("cashflow_sheet_us_AAPL", cached_data)
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            provider = USShareProvider(cache=cache)
            result = provider.get_cash_flow_statement("AAPL", 2023)
            
            mock_ak.stock_financial_us_report_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_balance_sheet_force_refresh(self):
        """Should refresh when force_refresh=True"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"year": [2023], "total_assets": [100]})
        cache.set("balance_sheet_us_AAPL", cached_data)
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            mock_ak.stock_financial_us_report_em.return_value = pd.DataFrame({
                "ITEM_NAME": ["Total Assets"],
                "AMOUNT": [200],
                "REPORT_DATE": ["2023-12-31"]
            })
            
            provider = USShareProvider(cache=cache)
            result = provider.get_balance_sheet("AAPL", 2023, force_refresh=True)
            
            mock_ak.stock_financial_us_report_em.assert_called_once()

    def test_get_historical_data_uses_cache(self):
        """Should use cache for historical data"""
        from value_investment.data.providers.us_share_provider import USShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"date": ["2024-01-01"], "close": [150]})
        cache.set("hist_us_AAPL", cached_data)
        
        with patch("value_investment.data.providers.us_share_provider.ak") as mock_ak:
            provider = USShareProvider(cache=cache)
            result = provider.get_historical_data("AAPL")
            
            mock_ak.stock_us_daily.assert_not_called()
            assert result.equals(cached_data)
