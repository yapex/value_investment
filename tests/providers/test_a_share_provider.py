"""Comprehensive tests for A-Share Provider (Tushare)"""
import pytest
import warnings
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd

from value_investment.providers.a_share import TushareProvider


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_cache():
    """Create a mock cache"""
    cache = MagicMock()
    cache.get.return_value = None
    cache.set.return_value = None
    return cache


@pytest.fixture
def provider(mock_cache):
    """Create TushareProvider with mocked API"""
    provider = TushareProvider(cache=mock_cache, token="mock_token")
    # Mock the internal API
    provider._api = MagicMock()
    return provider


def make_financial_df():
    """Create mock financial DataFrame with standard columns"""
    return pd.DataFrame({
        "end_date": ["20241231", "20231231", "20221231"],
        "update_flag": [1, 1, 1],
        "total_revenue": [150000000000, 140000000000, 130000000000],
        "net_profit": [70000000000, 65000000000, 60000000000],
    })


def make_balance_df():
    """Create mock balance sheet DataFrame"""
    return pd.DataFrame({
        "end_date": ["20241231", "20231231"],
        "update_flag": [1, 1],
        "total_assets": [250000000000, 240000000000],
        "total_liab": [80000000000, 78000000000],
    })


def make_indicator_df():
    """Create mock indicator DataFrame"""
    return pd.DataFrame({
        "end_date": ["20241231", "20231231"],
        "ann_date": ["20250420", "20240420"],
        "roe": [30.5, 28.5],
        "roa": [20.0, 18.5],
        "grossprofit_margin": [92.0, 91.5],
        "netprofit_margin": [50.0, 48.0],
        "current_ratio": [3.5, 3.2],
        "eps": [55.0, 51.0],
        "bps": [180.0, 170.0],
    })


def make_market_df():
    """Create mock market data DataFrame"""
    return pd.DataFrame({
        "ts_code": ["600519.SH"],
        "trade_date": ["20250418"],
        "total_mv": [2500000000000],  # 万元
        "circ_mv": [2400000000000],
        "total_share": [1200000000],
        "float_share": [1150000000],
        "pe_ttm": [25.5],
        "pb": [4.2],
    })


# ============================================================================
# Tests for field classification
# ============================================================================

class TestFieldClassification:
    """Test _get_*_fields methods"""

    def test_balance_fields(self, provider):
        """Test balance sheet field classification"""
        fields = provider._get_balance_fields()
        assert "total_assets" in fields
        assert "total_liabilities" in fields
        assert "total_equity" in fields

    def test_income_fields(self, provider):
        """Test income statement field classification"""
        fields = provider._get_income_fields()
        assert "total_revenue" in fields
        assert "net_profit" in fields
        assert "operating_profit" in fields

    def test_cash_flow_fields(self, provider):
        """Test cash flow field classification"""
        fields = provider._get_cash_flow_fields()
        assert "operating_cash_flow" in fields
        assert "investing_cash_flow" in fields

    def test_market_fields(self, provider):
        """Test market field classification"""
        fields = provider._get_market_fields()
        assert "market_cap" in fields
        assert "pe_ratio" in fields
        assert "pb_ratio" in fields


# ============================================================================
# Tests for fetch_financial_data
# ============================================================================

class TestFetchFinancialData:
    """Test fetch_financial_data method"""

    def test_fetch_balance_sheet_fields(self, provider, mock_cache):
        """Test fetching balance sheet fields"""
        # Setup mock
        provider._api.balancesheet.return_value = make_balance_df()
        
        result = provider.fetch_financial_data(
            stock_code="600519",
            fields={"total_assets", "total_liabilities"},
            end_year=2024,
            years=3,
        )
        
        assert isinstance(result, dict)
        assert "total_assets" in result or "total_liabilities" in result

    def test_fetch_income_statement_fields(self, provider, mock_cache):
        """Test fetching income statement fields"""
        provider._api.income.return_value = make_financial_df()
        
        result = provider.fetch_financial_data(
            stock_code="600519",
            fields={"total_revenue", "net_profit"},
            end_year=2024,
            years=3,
        )
        
        assert "total_revenue" in result or "net_profit" in result

    def test_empty_result_when_no_data(self, provider, mock_cache):
        """Test empty result when API returns nothing"""
        provider._api.balancesheet.return_value = pd.DataFrame()
        provider._api.income.return_value = pd.DataFrame()
        
        result = provider.fetch_financial_data(
            stock_code="600519",
            fields={"total_revenue"},
            end_year=2024,
            years=3,
        )
        
        # Should return empty dict or dict without the field
        assert isinstance(result, dict)


# ============================================================================
# Tests for fetch_indicators
# ============================================================================

class TestFetchIndicators:
    """Test fetch_indicators method"""

    def test_fetch_indicator_fields(self, provider, mock_cache):
        """Test fetching indicator fields"""
        provider._api.fina_indicator.return_value = make_indicator_df()
        
        result = provider.fetch_indicators(
            stock_code="600519",
            fields={"roe", "roa", "gross_margin"},
            end_year=2024,
            years=3,
        )
        
        assert "roe" in result
        assert "roa" in result
        assert "gross_margin" in result

    def test_empty_result_for_unsupported_fields(self, provider, mock_cache):
        """Test empty result when no supported fields requested"""
        result = provider.fetch_indicators(
            stock_code="600519",
            fields={"unknown_field"},
            end_year=2024,
        )
        
        assert result == {}

    def test_year_extraction(self, provider, mock_cache):
        """Test that years are correctly extracted"""
        provider._api.fina_indicator.return_value = make_indicator_df()
        
        result = provider.fetch_indicators(
            stock_code="600519",
            fields={"roe"},
            end_year=2024,
            years=3,
        )
        
        assert 2024 in result["roe"]


# ============================================================================
# Tests for fetch_market_data
# ============================================================================

class TestFetchMarketData:
    """Test fetch_market_data method"""

    def test_fetch_market_cap(self, provider, mock_cache):
        """Test fetching market cap"""
        provider._api.daily_basic.return_value = make_market_df()
        
        result = provider.fetch_market_data(
            stock_code="600519",
            fields={"market_cap"},
        )
        
        assert "market_cap" in result
        # Market cap should be converted from 万元 to 元
        assert result["market_cap"] == 2500000000000 * 10000

    def test_fetch_pe_and_pb(self, provider, mock_cache):
        """Test fetching PE and PB ratios"""
        provider._api.daily_basic.return_value = make_market_df()
        
        result = provider.fetch_market_data(
            stock_code="600519",
            fields={"pe_ratio", "pb_ratio"},
        )
        
        assert "pe_ratio" in result
        assert "pb_ratio" in result
        assert result["pe_ratio"] == pytest.approx(25.5)
        assert result["pb_ratio"] == pytest.approx(4.2)

    def test_empty_result_when_no_data(self, provider, mock_cache):
        """Test empty result when API returns empty"""
        provider._api.daily_basic.return_value = pd.DataFrame()
        
        result = provider.fetch_market_data(
            stock_code="600519",
            fields={"market_cap"},
        )
        
        assert result == {}

    def test_empty_result_for_unsupported_fields(self, provider, mock_cache):
        """Test empty result for non-market fields"""
        result = provider.fetch_market_data(
            stock_code="600519",
            fields={"total_revenue"},  # Not a market field
        )
        
        assert result == {}


# ============================================================================
# Tests for raw fetch methods
# ============================================================================

class TestRawFetchMethods:
    """Test fetch_raw_* methods"""

    def test_fetch_raw_balance_sheet(self, provider, mock_cache):
        """Test raw balance sheet fetch"""
        df = make_balance_df()
        df["year"] = [2024, 2023]
        provider._api.balancesheet.return_value = df
        
        result = provider.fetch_raw_balance_sheet("600519.SH", 2022, 2024)
        
        assert isinstance(result, pd.DataFrame)

    def test_fetch_raw_income_statement(self, provider, mock_cache):
        """Test raw income statement fetch"""
        df = make_financial_df()
        df["year"] = [2024, 2023, 2022]
        provider._api.income.return_value = df
        
        result = provider.fetch_raw_income_statement("600519.SH", 2022, 2024)
        
        assert isinstance(result, pd.DataFrame)

    def test_fetch_raw_cash_flow(self, provider, mock_cache):
        """Test raw cash flow fetch"""
        provider._api.cashflow.return_value = pd.DataFrame()
        
        result = provider.fetch_raw_cash_flow("600519.SH", 2022, 2024)
        
        assert isinstance(result, pd.DataFrame)

    def test_empty_df_when_api_returns_none(self, provider, mock_cache):
        """Test empty DataFrame when API returns None"""
        provider._api.balancesheet.return_value = None
        
        result = provider.fetch_raw_balance_sheet("600519.SH", 2022, 2024)
        
        assert result.empty


# ============================================================================
# Tests for field mapping
# ============================================================================

class TestFieldMapping:
    """Test field mapping functionality"""

    def test_apply_field_mapping_balance_sheet(self, provider):
        """Test balance sheet field mapping"""
        df = pd.DataFrame({
            "total_liab": [100],
            "total_assets": [200],
        })
        
        result = provider._apply_field_mapping(df, "balance_sheet")
        
        assert "total_liabilities" in result.columns
        assert "total_assets" in result.columns

    def test_apply_field_mapping_income_statement(self, provider):
        """Test income statement field mapping"""
        df = pd.DataFrame({
            "n_income": [100],
            "total_revenue": [200],
        })
        
        result = provider._apply_field_mapping(df, "income_statement")
        
        assert "net_profit" in result.columns

    def test_apply_field_mapping_empty_df(self, provider):
        """Test with empty DataFrame"""
        result = provider._apply_field_mapping(pd.DataFrame(), "balance_sheet")
        assert result.empty

    def test_standardize_columns(self, provider):
        """Test standardize_columns method"""
        df = pd.DataFrame({
            "total_liab": [100],
            "unknown_col": [200],
        })
        
        # TushareProvider uses FIELD_MAPPINGS from the class
        result = provider._apply_field_mapping(df, "balance_sheet")
        
        assert "total_liabilities" in result.columns

    def test_get_field_mapping(self, provider):
        """Test get_field_mapping method - TushareProvider doesn't use _field_mappings"""
        # TushareProvider uses FIELD_MAPPINGS instead
        mapping = provider.FIELD_MAPPINGS.get("balance_sheet", {})
        assert isinstance(mapping, dict)
        assert "total_liab" in mapping

    def test_get_supported_fields(self, provider):
        """Test get_supported_fields method"""
        # TushareProvider doesn't implement this via get_field_mapping
        # Instead it uses FIELD_MAPPINGS
        fields = provider.supported_fields
        assert isinstance(fields, set)
        assert "total_revenue" in fields


# ============================================================================
# Tests for date filtering
# ============================================================================

class TestDateFiltering:
    """Test date filtering functionality"""

    def test_filter_latest_by_update_flag(self, provider):
        """Test update_flag filtering"""
        df = pd.DataFrame({
            "end_date": ["20241231", "20241231"],
            "update_flag": [0, 1],
            "total_assets": [100, 150],
        })
        
        result = provider._filter_latest_by_update_flag(df, "end_date")
        
        # Should keep only update_flag=1 record
        assert len(result) == 1

    def test_extract_year(self, provider):
        """Test year extraction"""
        df = pd.DataFrame({
            "end_date": ["20241231", "20231231"],
        })
        
        result = provider._extract_year(df, "end_date")
        
        assert "year" in result.columns
        assert 2024 in result["year"].values


# ============================================================================
# Tests for stock code conversion
# ============================================================================

class TestStockCodeConversion:
    """Test _to_ts_code method"""

    def test_convert_6_digit_sh(self, provider):
        """Test conversion of 6-digit SH code"""
        result = provider._to_ts_code("600519")
        assert result == "600519.SH"

    def test_convert_6_digit_sz(self, provider):
        """Test conversion of 6-digit SZ code"""
        result = provider._to_ts_code("000001")
        assert result == "000001.SZ"

    def test_convert_3_digit(self, provider):
        """Test conversion of 3-digit (创业板) code"""
        result = provider._to_ts_code("300001")
        assert result == "300001.SZ"

    def test_already_formatted(self, provider):
        """Test already formatted code"""
        result = provider._to_ts_code("600519.SH")
        assert result == "600519.SH"


# ============================================================================
# Tests for TTL calculation
# ============================================================================

class TestTTLCalculation:
    """Test TTL calculation methods"""

    def test_get_ttl_until_june_next_year(self, provider):
        """Test TTL calculation"""
        ttl = provider._get_ttl_until_june_next_year()
        
        assert isinstance(ttl, int)
        assert ttl > 0
        # TTL should be reasonable (less than 2 years)
        assert ttl < 2 * 365 * 24 * 60 * 60


# ============================================================================
# Tests for cache operations
# ============================================================================

class TestCacheOperations:
    """Test cache helper methods"""

    def test_get_cache_key(self, provider):
        """Test cache key building"""
        key = provider._get_cache_key("prefix", "stock", "suffix")
        assert "prefix" in key
        assert "stock" in key

    def test_get_from_cache(self, provider):
        """Test get from cache"""
        provider._cache.get.return_value = {"data": "value"}
        result = provider._get_from_cache("test_key")
        assert result == {"data": "value"}

    def test_set_to_cache(self, provider):
        """Test set to cache"""
        provider._set_to_cache("test_key", "value", ttl=3600)
        provider._cache.set.assert_called_once()

    def test_invalidate_cache(self, provider):
        """Test cache invalidation"""
        provider._invalidate_cache("test_key")
        provider._cache.invalidate.assert_called_once_with("test_key")
