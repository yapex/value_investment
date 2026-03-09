"""Tests for HKShareProvider"""
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


class TestHKShareProviderInit:
    """Test HKShareProvider initialization"""

    def test_init_default(self):
        """Should initialize with default market"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        assert provider._market == "HK"

    def test_init_with_market(self):
        """Should initialize with custom market"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache(), market="HK")
        assert provider._market == "HK"


class TestHKShareProviderNormalize:
    """Test code normalization"""

    def test_normalize_hk_code_5_digit(self):
        """Should normalize HK code to 5 digits"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        assert provider._normalize_hk_code("700") == "00700"
        assert provider._normalize_hk_code("7") == "00007"
        assert provider._normalize_hk_code("00700") == "00700"
        assert provider._normalize_hk_code("09988") == "09988"

    def test_normalize_date(self):
        """Should normalize date format"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        assert provider._normalize_date("20240101") == "2024-01-01"
        assert provider._normalize_date("2024-01-01") == "2024-01-01"
        assert provider._normalize_date(None) is None


class TestHKShareProviderStockInfo:
    """Test get_stock_info method"""

    def test_get_stock_info_basic(self):
        """Should fetch stock info"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            mock_ak.stock_hk_company_profile_em.return_value = pd.DataFrame({
                "公司名称": ["腾讯控股"],
                "上市日期": ["20040616"]
            })
            
            provider = HKShareProvider(cache=cache)
            result = provider.get_stock_info("00700")
            
            assert not result.empty
            assert "item" in result.columns
            assert "value" in result.columns

    def test_get_stock_info_with_cache(self):
        """Should use cache when available"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"item": ["code"], "value": ["00700"]})
        cache.set("info_00700", cached_data)
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            provider = HKShareProvider(cache=cache)
            result = provider.get_stock_info("00700")
            
            # Should return cached data, not call API
            mock_ak.stock_hk_company_profile_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_stock_info_force_refresh(self):
        """Should refresh when force_refresh=True"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"item": ["code"], "value": ["00700"]})
        cache.set("info_00700", cached_data)
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            mock_ak.stock_hk_company_profile_em.return_value = pd.DataFrame({
                "公司名称": ["腾讯控股"]
            })
            
            provider = HKShareProvider(cache=cache)
            result = provider.get_stock_info("00700", force_refresh=True)
            
            # Should call API even though cache exists
            mock_ak.stock_hk_company_profile_em.assert_called_once()


class TestHKShareProviderHistoricalData:
    """Test get_historical_data method"""

    def test_get_historical_data_basic(self):
        """Should fetch historical data"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            mock_ak.stock_hk_daily.return_value = pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02"],
                "open": [300, 310],
                "close": [305, 315],
                "high": [310, 320],
                "low": [295, 305],
                "volume": [1000000, 1100000]
            })
            
            provider = HKShareProvider(cache=cache)
            result = provider.get_historical_data("00700")
            
            assert not result.empty

    def test_get_historical_data_with_dates(self):
        """Should filter by date range"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            mock_ak.stock_hk_daily.return_value = pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "open": [300, 310, 320],
                "close": [305, 315, 325],
                "high": [310, 320, 330],
                "low": [295, 305, 315],
                "volume": [1000000, 1100000, 1200000]
            })
            
            provider = HKShareProvider(cache=cache)
            result = provider.get_historical_data(
                "00700",
                start_date="20240101",
                end_date="20240102"
            )
            
            assert not result.empty


class TestHKShareProviderFinancial:
    """Test financial data methods"""

    def test_get_balance_sheet_basic(self):
        """Should fetch balance sheet"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = pd.DataFrame({
                "REPORT_DATE": ["2023-12-31"],
                "total_assets": [1000000]
            })
            
            provider = HKShareProvider(cache=cache)
            result = provider.get_balance_sheet("00700", 2023)
            
            assert result is not None

    def test_get_income_statement_basic(self):
        """Should fetch income statement"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = pd.DataFrame({
                "REPORT_DATE": ["2023-12-31"],
                "net_profit": [500000]
            })
            
            provider = HKShareProvider(cache=cache)
            result = provider.get_income_statement("00700", 2023)
            
            assert result is not None

    def test_get_cash_flow_statement_basic(self):
        """Should fetch cash flow statement"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = pd.DataFrame({
                "REPORT_DATE": ["2023-12-31"],
                "operating_cash_flow": [300000]
            })
            
            provider = HKShareProvider(cache=cache)
            result = provider.get_cash_flow_statement("00700", 2023)
            
            assert result is not None


class TestHKShareProviderTransform:
    """Test data transformation"""

    def test_transform_hk_financial_data_basic(self):
        """Should transform financial data"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        df = pd.DataFrame({
            "STD_ITEM_NAME": ["Total Assets", "Net Income"],
            "AMOUNT": [1000000, 500000],
            "REPORT_DATE": ["2023-12-31", "2023-12-31"]
        })
        
        result = provider._transform_hk_financial_data(df)
        
        assert not result.empty

    def test_transform_hk_financial_data_empty(self):
        """Should handle empty DataFrame"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        result = provider._transform_hk_financial_data(pd.DataFrame())
        
        assert result.empty

    def test_transform_hk_financial_data_no_required_columns(self):
        """Should handle missing columns"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        df = pd.DataFrame({"other_column": [1, 2]})
        
        result = provider._transform_hk_financial_data(df)
        
        assert result.equals(df)

    def test_transform_hk_financial_data_with_item_name(self):
        """Should transform using ITEM_NAME column"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        df = pd.DataFrame({
            "ITEM_NAME": ["Total Assets", "Net Income"],
            "AMOUNT": [1000000, 500000],
            "REPORT_DATE": ["2023-12-31", "2023-12-31"]
        })
        
        result = provider._transform_hk_financial_data(df)
        
        assert not result.empty


class TestHKShareProviderFilter:
    """Test year filtering"""

    def test_filter_by_year_basic(self):
        """Should filter by year"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        df = pd.DataFrame({
            "year": [2020, 2021, 2022, 2023],
            "value": [100, 200, 300, 400]
        })
        
        result = provider._filter_by_year(df, 2022)
        
        assert len(result) == 3

    def test_filter_by_year_empty(self):
        """Should handle empty DataFrame"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        result = provider._filter_by_year(pd.DataFrame(), 2022)
        
        assert result.empty

    def test_filter_by_year_no_year_column(self):
        """Should handle DataFrame without year column"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        provider = HKShareProvider(cache=MockCache())
        
        df = pd.DataFrame({"value": [100, 200]})
        
        result = provider._filter_by_year(df, 2022)
        
        assert result.equals(df)


class TestHKShareProviderCache:
    """Test cache functionality"""

    def test_get_balance_sheet_uses_cache(self):
        """Should use cache for balance sheet"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT_DATE": ["2023-12-31"], "total_assets": [100]})
        cache.set("balance_sheet_hk_00700", cached_data)
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            provider = HKShareProvider(cache=cache)
            result = provider.get_balance_sheet("00700", 2023)
            
            mock_ak.stock_financial_hk_report_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_income_statement_uses_cache(self):
        """Should use cache for income statement"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT_DATE": ["2023-12-31"], "net_profit": [100]})
        cache.set("profit_sheet_hk_00700", cached_data)
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            provider = HKShareProvider(cache=cache)
            result = provider.get_income_statement("00700", 2023)
            
            mock_ak.stock_financial_hk_report_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_cash_flow_statement_uses_cache(self):
        """Should use cache for cash flow statement"""
        from value_investment.data.providers.hk_share_provider import HKShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT_DATE": ["2023-12-31"], "operating_cash_flow": [100]})
        cache.set("cashflow_sheet_hk_00700", cached_data)
        
        with patch("value_investment.data.providers.hk_share_provider.ak") as mock_ak:
            provider = HKShareProvider(cache=cache)
            result = provider.get_cash_flow_statement("00700", 2023)
            
            mock_ak.stock_financial_hk_report_em.assert_not_called()
            assert result.equals(cached_data)
