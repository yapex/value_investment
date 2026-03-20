"""Comprehensive tests for BaseProvider"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd

from value_investment.providers.base import BaseProvider, get_ttl_until_june_next_year


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_cache():
    """Create a mock cache"""
    cache = MagicMock()
    cache.get.return_value = None
    cache.set.return_value = None
    cache.get_or_fetch.return_value = pd.DataFrame()
    cache.get_or_fetch_with_range.return_value = pd.DataFrame()
    return cache


@pytest.fixture
def concrete_provider(mock_cache):
    """Create a concrete implementation of BaseProvider for testing"""
    class ConcreteProvider(BaseProvider):
        def _fetch_balance_sheet(self, stock_code, end_year, start_year):
            return pd.DataFrame({
                "report_date": ["2024-12-31"],
                "total_assets": [1000000],
            })

        def _fetch_income_statement(self, stock_code, end_year, start_year):
            return pd.DataFrame({
                "report_date": ["2024-12-31"],
                "total_revenue": [500000],
            })

        def _fetch_cash_flow(self, stock_code, end_year, start_year):
            return pd.DataFrame({
                "report_date": ["2024-12-31"],
                "operating_cash_flow": [100000],
            })

        def _fetch_indicators(self, stock_code, end_year, start_year):
            return pd.DataFrame({
                "report_date": ["2024-12-31"],
                "roe": [25.0],
            })

    return ConcreteProvider(cache=mock_cache)


# ============================================================================
# Tests for get_ttl_until_june_next_year
# ============================================================================

class TestTTLCalculation:
    """Test TTL calculation function"""

    def test_ttl_is_positive(self):
        """TTL should be a positive number"""
        ttl = get_ttl_until_june_next_year(2024)
        assert ttl > 0

    def test_ttl_is_reasonable(self):
        """TTL should be less than 2 years"""
        ttl = get_ttl_until_june_next_year(2024)
        # June 30 next year should be within ~18 months
        assert ttl < 2 * 365 * 24 * 60 * 60

    def test_ttl_calculation_with_different_years(self):
        """TTL should vary based on current date"""
        ttl1 = get_ttl_until_june_next_year(2024)
        ttl2 = get_ttl_until_june_next_year(2025)
        # Both should be reasonable values
        assert ttl1 > 0
        assert ttl2 > 0


# ============================================================================
# Tests for BaseProvider initialization
# ============================================================================

class TestBaseProviderInit:
    """Test BaseProvider initialization"""

    def test_init_with_cache(self, concrete_provider):
        """Test initialization with cache"""
        assert concrete_provider._cache is not None

    def test_init_with_field_mappings(self, mock_cache):
        """Test initialization with custom field mappings"""
        class TestProvider(BaseProvider):
            def _fetch_balance_sheet(self, stock_code, end_year, start_year):
                return pd.DataFrame()
            def _fetch_income_statement(self, stock_code, end_year, start_year):
                return pd.DataFrame()
            def _fetch_cash_flow(self, stock_code, end_year, start_year):
                return pd.DataFrame()
            def _fetch_indicators(self, stock_code, end_year, start_year):
                return pd.DataFrame()

        mappings = {"balance_sheet": {"old_name": "new_name"}}
        provider = TestProvider(cache=mock_cache, field_mappings=mappings)
        assert provider._field_mappings == mappings

    def test_init_with_kwargs(self, mock_cache):
        """Test initialization with additional kwargs"""
        class TestProvider(BaseProvider):
            def _fetch_balance_sheet(self, stock_code, end_year, start_year):
                return pd.DataFrame()
            def _fetch_income_statement(self, stock_code, end_year, start_year):
                return pd.DataFrame()
            def _fetch_cash_flow(self, stock_code, end_year, start_year):
                return pd.DataFrame()
            def _fetch_indicators(self, stock_code, end_year, start_year):
                return pd.DataFrame()

        provider = TestProvider(cache=mock_cache, extra_arg="value")
        assert provider._init_kwargs.get("extra_arg") == "value"


# ============================================================================
# Tests for Template Methods (get_*)
# ============================================================================

class TestTemplateMethods:
    """Test Template Method pattern"""

    def test_get_balance_sheet(self, concrete_provider, mock_cache):
        """Test get_balance_sheet calls _fetch_with_cache"""
        result = concrete_provider.get_balance_sheet("600519", 2024)
        assert isinstance(result, pd.DataFrame)
        mock_cache.get_or_fetch_with_range.assert_called()

    def test_get_balance_sheet_with_start_year(self, concrete_provider, mock_cache):
        """Test get_balance_sheet with explicit start_year"""
        result = concrete_provider.get_balance_sheet("600519", 2024, start_year=2020)
        assert isinstance(result, pd.DataFrame)

    def test_get_balance_sheet_force_refresh(self, concrete_provider, mock_cache):
        """Test force_refresh parameter"""
        result = concrete_provider.get_balance_sheet("600519", 2024, force_refresh=True)
        assert isinstance(result, pd.DataFrame)

    def test_get_income_statement(self, concrete_provider, mock_cache):
        """Test get_income_statement calls _fetch_with_cache"""
        result = concrete_provider.get_income_statement("600519", 2024)
        assert isinstance(result, pd.DataFrame)

    def test_get_cash_flow_statement(self, concrete_provider, mock_cache):
        """Test get_cash_flow_statement calls _fetch_with_cache"""
        result = concrete_provider.get_cash_flow_statement("600519", 2024)
        assert isinstance(result, pd.DataFrame)

    def test_get_financial_indicators(self, concrete_provider, mock_cache):
        """Test get_financial_indicators calls _fetch_with_cache"""
        result = concrete_provider.get_financial_indicators("600519", 2024)
        assert isinstance(result, pd.DataFrame)


# ============================================================================
# Tests for _fetch_with_cache
# ============================================================================

class TestFetchWithCache:
    """Test _fetch_with_cache method"""

    def test_default_start_year(self, concrete_provider, mock_cache):
        """Test default start_year calculation"""
        concrete_provider.get_balance_sheet("600519", 2024)
        # Should call with calculated start_year (2024 - 10 + 1 = 2015)

    def test_cache_key_generation(self, concrete_provider, mock_cache):
        """Test cache key is generated correctly"""
        concrete_provider.get_balance_sheet("600519", 2024)
        # Check cache key format

    def test_date_column_filtering(self, concrete_provider, mock_cache):
        """Test date column filtering in cache"""
        mock_cache.get_or_fetch_with_range.return_value = pd.DataFrame({
            "report_date": ["2024-12-31", "2023-12-31"],
            "total_assets": [1000000, 900000],
        })
        result = concrete_provider.get_balance_sheet("600519", 2024)


# ============================================================================
# Tests for field mapping methods
# ============================================================================

class TestFieldMapping:
    """Test field mapping methods"""

    def test_apply_field_mapping_with_mappings(self, concrete_provider):
        """Test _apply_field_mapping with FIELD_MAPPINGS"""
        df = pd.DataFrame({
            "old_name": [100],
            "new_name": [200],
        })
        # Set up mappings
        concrete_provider.FIELD_MAPPINGS = {
            "balance_sheet": {"old_name": "mapped_name"}
        }
        result = concrete_provider._apply_field_mapping(df, "balance_sheet")
        assert "mapped_name" in result.columns

    def test_apply_field_mapping_empty_df(self, concrete_provider):
        """Test with empty DataFrame"""
        result = concrete_provider._apply_field_mapping(pd.DataFrame(), "balance_sheet")
        assert result.empty

    def test_apply_field_mapping_none_df(self, concrete_provider):
        """Test with None DataFrame"""
        result = concrete_provider._apply_field_mapping(None, "balance_sheet")
        assert result.empty

    def test_standardize_columns(self, concrete_provider):
        """Test standardize_columns method"""
        df = pd.DataFrame({
            "native_field": [100],
        })
        concrete_provider._field_mappings = {
            "balance_sheet": {"native_field": "standard_field"}
        }
        result = concrete_provider.standardize_columns(df, "balance_sheet")
        assert "standard_field" in result.columns

    def test_standardize_columns_empty_df(self, concrete_provider):
        """Test standardize_columns with empty DataFrame"""
        result = concrete_provider.standardize_columns(pd.DataFrame(), "balance_sheet")
        assert result.empty

    def test_apply_mapping_alias(self, concrete_provider):
        """Test _apply_mapping is alias for standardize_columns"""
        df = pd.DataFrame({"col": [1]})
        result = concrete_provider._apply_mapping(df, "balance_sheet")
        assert isinstance(result, pd.DataFrame)

    def test_get_field_mapping(self, concrete_provider):
        """Test get_field_mapping method - uses _field_mappings"""
        concrete_provider._field_mappings = {
            "balance_sheet": {"a": "b"}
        }
        mapping = concrete_provider.get_field_mapping("balance_sheet")
        assert mapping == {"a": "b"}

    def test_get_supported_fields(self, concrete_provider):
        """Test get_supported_fields method"""
        concrete_provider._field_mappings = {
            "balance_sheet": {"native": "standard"}
        }
        fields = concrete_provider.get_supported_fields("balance_sheet")
        assert "standard" in fields


# ============================================================================
# Tests for filter and cache methods
# ============================================================================

class TestFilterAndCacheMethods:
    """Test filter and cache helper methods"""

    def test_filter_latest_by_update_flag(self, concrete_provider):
        """Test _filter_latest_by_update_flag"""
        df = pd.DataFrame({
            "report_date": ["2024-12-31", "2024-12-31"],
            "update_flag": [0, 1],
            "total_assets": [100, 150],
        })
        result = concrete_provider._filter_latest_by_update_flag(df)
        assert len(result) == 1

    def test_filter_latest_by_update_flag_no_flag(self, concrete_provider):
        """Test when update_flag column is missing"""
        df = pd.DataFrame({
            "report_date": ["2024-12-31", "2024-12-31"],
            "total_assets": [100, 150],
        })
        result = concrete_provider._filter_latest_by_update_flag(df)
        # Should return unchanged
        assert len(result) == 2

    def test_filter_latest_by_update_flag_empty_df(self, concrete_provider):
        """Test with empty DataFrame"""
        result = concrete_provider._filter_latest_by_update_flag(pd.DataFrame())
        assert result.empty

    def test_filter_latest_by_update_flag_none_df(self, concrete_provider):
        """Test with None DataFrame"""
        result = concrete_provider._filter_latest_by_update_flag(None)
        assert result is None

    def test_get_from_cache(self, concrete_provider, mock_cache):
        """Test _get_from_cache"""
        mock_cache.get.return_value = {"data": "value"}
        result = concrete_provider._get_from_cache("test_key")
        assert result == {"data": "value"}

    def test_get_from_cache_exception(self, concrete_provider, mock_cache):
        """Test _get_from_cache handles exceptions"""
        mock_cache.get.side_effect = Exception("Cache error")
        result = concrete_provider._get_from_cache("test_key")
        assert result is None

    def test_set_to_cache(self, concrete_provider, mock_cache):
        """Test _set_to_cache"""
        concrete_provider._set_to_cache("test_key", "value", ttl=3600)
        mock_cache.set.assert_called_once()

    def test_set_to_cache_exception(self, concrete_provider, mock_cache):
        """Test _set_to_cache handles exceptions"""
        mock_cache.set.side_effect = Exception("Cache error")
        # Should not raise
        concrete_provider._set_to_cache("test_key", "value")

    def test_invalidate_cache(self, concrete_provider, mock_cache):
        """Test _invalidate_cache"""
        concrete_provider._invalidate_cache("test_key")
        mock_cache.invalidate.assert_called_once_with("test_key")

    def test_invalidate_cache_exception(self, concrete_provider, mock_cache):
        """Test _invalidate_cache handles exceptions"""
        mock_cache.invalidate.side_effect = Exception("Cache error")
        # Should not raise
        concrete_provider._invalidate_cache("test_key")

    def test_get_cache_key(self, concrete_provider):
        """Test _get_cache_key"""
        key = concrete_provider._get_cache_key("part1", "part2", "part3")
        assert "part1" in key
        assert "part2" in key
        assert "part3" in key


# ============================================================================
# Tests for optional methods (NotImplementedError)
# ============================================================================

class TestOptionalMethods:
    """Test optional methods that raise NotImplementedError"""

    def test_get_stock_info_not_implemented(self, concrete_provider):
        """Test get_stock_info raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            concrete_provider.get_stock_info("600519")

    def test_get_historical_data_not_implemented(self, concrete_provider):
        """Test get_historical_data raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            concrete_provider.get_historical_data("600519")


# ============================================================================
# Tests for date and TTL methods
# ============================================================================

class TestDateAndTTLMethods:
    """Test date column and TTL methods"""

    def test_get_financial_ttl(self, concrete_provider):
        """Test _get_financial_ttl"""
        ttl = concrete_provider._get_financial_ttl(2024)
        assert isinstance(ttl, int)
        assert ttl > 0

    def test_get_date_column_default(self, concrete_provider):
        """Test _get_date_column returns default"""
        result = concrete_provider._get_date_column("balance_sheet")
        assert result == "report_date"
