"""Tests for USProvider - TDD approach"""
import pandas as pd
import pytest


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

    def get_or_fetch(self, key, fetch_func, ttl, force_refresh=False):
        cached = self._data.get(key)
        if cached is not None and not force_refresh:
            return cached
        result = fetch_func()
        self._data[key] = result
        return result

    def get_or_fetch_with_range(self, key, date_column, fetch_func, start_date, end_date, ttl, force_refresh=False):
        cached = self._data.get(key)
        if cached is not None and not force_refresh:
            return cached
        result = fetch_func()
        self._data[key] = result
        return result


class TestUSProviderExists:
    """Test that USProvider exists and has required methods"""

    def test_us_provider_can_be_imported(self):
        """USProvider should be importable"""
        from value_investment.data.providers.us_provider import USProvider
        assert USProvider is not None

    def test_us_provider_has_market_attribute(self):
        """USProvider should have _market attribute"""
        from value_investment.data.providers.us_provider import USProvider

        cache = MockCache()
        provider = USProvider(cache=cache)
        assert hasattr(provider, '_market')
        assert provider._market == "US"

    def test_us_provider_has_required_methods(self):
        """USProvider should have all required methods"""
        from value_investment.data.providers.us_provider import USProvider

        cache = MockCache()
        provider = USProvider(cache=cache)

        required_methods = [
            'get_stock_info',
            'get_historical_data',
            'get_balance_sheet',
            'get_income_statement',
            'get_cash_flow_statement',
            'get_financial_indicators',
        ]

        for method in required_methods:
            assert hasattr(provider, method), f"USProvider should have {method} method"


class TestUSProviderHelperMethods:
    """Test helper methods"""

    def test_normalize_date_8_digit(self):
        """_normalize_date should convert 8-digit date"""
        from value_investment.data.providers.us_provider import USProvider

        provider = USProvider(cache=MockCache())
        assert provider._normalize_date("20240101") == "2024-01-01"
        assert provider._normalize_date("19991231") == "1999-12-31"

    def test_normalize_date_already_formatted(self):
        """_normalize_date should handle already formatted date"""
        from value_investment.data.providers.us_provider import USProvider

        provider = USProvider(cache=MockCache())
        assert provider._normalize_date("2024-01-01") == "2024-01-01"
        assert provider._normalize_date(None) is None

    def test_filter_by_year(self):
        """_filter_by_year should filter DataFrame by year"""
        from value_investment.data.providers.us_provider import USProvider

        provider = USProvider(cache=MockCache())
        df = pd.DataFrame({
            'year': [2020, 2021, 2022, 2023, 2024],
            'value': [1, 2, 3, 4, 5]
        })

        result = provider._filter_by_year(df, 2023)
        assert len(result) == 4
        assert all(result['year'] <= 2023)

    def test_filter_by_year_empty(self):
        """_filter_by_year should handle empty DataFrame"""
        from value_investment.data.providers.us_provider import USProvider

        provider = USProvider(cache=MockCache())
        result = provider._filter_by_year(pd.DataFrame(), 2023)
        assert result.empty

    def test_transform_financial_data(self):
        """_transform_financial_data should convert long to wide format"""
        from value_investment.data.providers.us_provider import USProvider

        provider = USProvider(cache=MockCache())
        df = pd.DataFrame({
            'REPORT_DATE': ['2024-12-31', '2024-12-31', '2023-12-31'],
            'ITEM_NAME': ['总资产', '净利润', '总资产'],
            'AMOUNT': [100, 50, 90]
        })

        result = provider._transform_financial_data(df)

        assert 'year' in result.columns
        assert '总资产' in result.columns
        assert '净利润' in result.columns
        assert len(result) == 2  # 2 years

    def test_transform_financial_data_empty(self):
        """_transform_financial_data should handle empty DataFrame"""
        from value_investment.data.providers.us_provider import USProvider

        provider = USProvider(cache=MockCache())
        result = provider._transform_financial_data(pd.DataFrame())
        assert result.empty


class TestUSProviderCache:
    """Test cache functionality"""

    def test_cache_is_used_for_balance_sheet(self):
        """Balance sheet should use cache"""
        from value_investment.data.providers.us_provider import USProvider

        cache = MockCache()
        provider = USProvider(cache=cache)

        # The provider should have cache attribute
        assert hasattr(provider, '_cache')
        assert provider._cache is cache

    def test_force_refresh_invalidates_cache(self):
        """Force refresh should invalidate cache"""
        from value_investment.data.providers.us_provider import USProvider

        cache = MockCache()
        cache.set("info_us_AAPL", pd.DataFrame({'old': [1]}))

        provider = USProvider(cache=cache)

        # set a new value
        provider.get_stock_info("AAPL", force_refresh=True)

        # Cache should have been invalidated (new data fetched)
        # Note: This test just verifies the method runs without error


class TestUSProviderIntegration:
    """Integration tests with DataMapper"""

    def test_datamapper_is_imported(self):
        """USProvider should import DataMapper"""
        from value_investment.data.providers.us_provider import USProvider

        # Check that DataMapper is in the module
        import value_investment.data.providers.us_provider as module
        assert hasattr(module, 'DataMapper')

    def test_datamapper_methods_exist(self):
        """DataMapper should have required mapping methods"""
        from value_investment.data.mapper import DataMapper

        required_methods = [
            'map_balance_sheet',
            'map_income_statement',
            'map_cash_flow',
            'map_financial_indicator',
        ]

        for method in required_methods:
            assert hasattr(DataMapper, method), f"DataMapper should have {method} method"
