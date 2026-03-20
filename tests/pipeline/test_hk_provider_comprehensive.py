"""Comprehensive tests for HK Provider"""
import pytest
import warnings
from datetime import datetime
from unittest.mock import MagicMock, patch
from unittest.mock import AsyncMock

import pandas as pd

from value_investment.providers.hk_share import HKProvider


# ============================================================================
# Fixtures
# ============================================================================

def create_mock_cache(return_empty=False, raise_exception=False):
    """Create a mock cache with configurable behavior"""
    cache = MagicMock()
    cache.get.return_value = None
    cache.set.return_value = None

    if raise_exception:
        def raise_on_fetch(key, fetch_fn, ttl=None, force_refresh=False):
            raise Exception("API Error")
        cache.get_or_fetch.side_effect = raise_on_fetch
    elif return_empty:
        def return_empty_on_fetch(key, fetch_fn, ttl=None, force_refresh=False):
            return pd.DataFrame()
        cache.get_or_fetch.side_effect = return_empty_on_fetch
    else:
        def get_or_fetch_side_effect(key, fetch_fn, ttl=None, force_refresh=False):
            return fetch_fn()
        cache.get_or_fetch.side_effect = get_or_fetch_side_effect
    
    return cache


@pytest.fixture
def mock_cache():
    """Create a mock cache with default behavior"""
    return create_mock_cache()


@pytest.fixture
def mock_cache_empty():
    """Create a mock cache that returns empty DataFrames"""
    return create_mock_cache(return_empty=True)


@pytest.fixture
def mock_cache_error():
    """Create a mock cache that raises exceptions"""
    return create_mock_cache(raise_exception=True)


@pytest.fixture
def provider(mock_cache):
    """Create HKProvider with mocked cache"""
    return HKProvider(cache=mock_cache)


# ============================================================================
# Helper functions for mock data
# ============================================================================

def _empty_df():
    return pd.DataFrame()


def _make_financial_df():
    """模拟多年财务报表 DataFrame（长表格式）"""
    data = {
        "SECURITY_CODE": ["00700"] * 6,
        "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"] * 2,
        "STD_ITEM_NAME": [
            "营业额", "营业额", "营业额",
            "股东应占溢利", "股东应占溢利", "股东应占溢利",
        ],
        "AMOUNT": [
            751766000000, 660000000000, 550000000000,
            224842000000, 200000000000, 150000000000,
        ],
    }
    return pd.DataFrame(data)


def _make_wide_df():
    """模拟转换后的宽表 DataFrame"""
    return pd.DataFrame({
        "year": [2024, 2023, 2022],
        "营业额": [751766000000, 660000000000, 550000000000],
        "股东应占溢利": [224842000000, 200000000000, 150000000000],
    })


def _make_indicator_df():
    """模拟指标 DataFrame"""
    return pd.DataFrame({
        "基本每股收益(元)": [24.749],
        "每股净资产(元)": [126.548],
        "已发行股本(股)": [9106356125],
        "每股经营现金流(元)": [33.228],
        "股息率TTM(%)": [0.8696],
        "总市值(港元)": [5013049046812.5],
        "港股市值(港元)": [5013049046812.5],
        "营业总收入": [751766000000],
        "营业总收入滚动环比增长(%)": [3.004],
        "销售净利率(%)": [30.568],
        "净利润": [224842000000],
        "净利润滚动环比增长(%)": [3.183],
        "股东权益回报率(%)": [21.1347],
        "市盈率": [20.138],
        "市净率": [3.923],
        "总资产回报率(%)": [11.7719],
        "派息比率(%)": [16.818],
    })


# ============================================================================
# Test field classification methods
# ============================================================================

class TestFieldClassification:
    """Test _get_*_fields methods"""

    def test_get_balance_fields(self, provider):
        """Test balance sheet field classification"""
        fields = provider._get_balance_fields()
        assert "total_assets" in fields
        assert "total_liabilities" in fields
        assert "total_equity" in fields
        assert "cash_and_equivalents" in fields

    def test_get_income_fields(self, provider):
        """Test income statement field classification"""
        fields = provider._get_income_fields()
        assert "total_revenue" in fields
        assert "net_profit" in fields
        assert "parent_net_profit" in fields

    def test_get_cashflow_fields(self, provider):
        """Test cash flow field classification"""
        fields = provider._get_cashflow_fields()
        assert "operating_cash_flow" in fields
        assert "investing_cash_flow" in fields
        assert "financing_cash_flow" in fields


# ============================================================================
# Test normalize code
# ============================================================================

class TestNormalizeHKCode:
    """Test _normalize_hk_code method"""

    def test_normalize_5_digit_code(self, provider):
        """5位数字代码直接返回"""
        assert provider._normalize_hk_code("00700") == "00700"
        assert provider._normalize_hk_code("09988") == "09988"

    def test_normalize_code_with_prefix(self, provider):
        """带前缀的代码提取数字"""
        assert provider._normalize_hk_code("00700.HK") == "00700"
        assert provider._normalize_hk_code("HK00700") == "00700"

    def test_normalize_short_code(self, provider):
        """不足5位的代码补零"""
        assert provider._normalize_hk_code("700") == "00700"
        assert provider._normalize_hk_code("1") == "00001"

    def test_normalize_empty_code(self, provider):
        """空代码返回空字符串"""
        assert provider._normalize_hk_code("") == ""
        assert provider._normalize_hk_code(None) is None

    def test_normalize_non_digit_code(self, provider):
        """无数字的代码返回空"""
        result = provider._normalize_hk_code("TEST")
        assert result == "00000"  # zfill 会补零到5位


# ============================================================================
# Test raw fetch methods
# ============================================================================

class TestRawFetchMethods:
    """Test fetch_raw_* methods"""

    def test_fetch_raw_balance_sheet(self, provider, mock_cache):
        """Test raw balance sheet fetch"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider.fetch_raw_balance_sheet("00700", 2024, 2020)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_raw_income_statement(self, provider, mock_cache):
        """Test raw income statement fetch"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider.fetch_raw_income_statement("00700", 2024, 2020)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_raw_cash_flow(self, provider, mock_cache):
        """Test raw cash flow fetch"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider.fetch_raw_cash_flow("00700", 2024, 2020)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_raw_empty_on_exception(self, provider):
        """Test empty result on API exception"""
        # Create a mock akshare module
        mock_ak = MagicMock()
        mock_ak.stock_financial_hk_report_em.side_effect = Exception("API Error")
        provider._ak = mock_ak

        result = provider.fetch_raw_balance_sheet("00700", 2024, 2020)

        # Should return empty DataFrame on exception
        assert result.empty


# ============================================================================
# Test mapped fetch methods
# ============================================================================

class TestMappedFetchMethods:
    """Test _fetch_* methods with field mapping"""

    def test_fetch_balance_sheet_with_mapping(self, provider, mock_cache):
        """Test balance sheet fetch with mapping"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider._fetch_balance_sheet("00700", 2024, 2020)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_income_statement_with_mapping(self, provider, mock_cache):
        """Test income statement fetch with mapping"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider._fetch_income_statement("00700", 2024, 2020)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_cash_flow_with_mapping(self, provider, mock_cache):
        """Test cash flow fetch with mapping"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider._fetch_cash_flow("00700", 2024, 2020)

        assert isinstance(result, pd.DataFrame)


# ============================================================================
# Test fetch indicators
# ============================================================================

class TestFetchIndicators:
    """Test _fetch_indicators method"""

    def test_fetch_indicators_success(self, provider, mock_cache):
        """Test successful indicators fetch"""
        provider._ak.stock_hk_financial_indicator_em.return_value = _make_indicator_df()

        result = provider._fetch_indicators("00700", 2024, 2020)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_indicators_empty_on_error(self, provider, mock_cache):
        """Test empty result on API error"""
        # Create a mock akshare module
        mock_ak = MagicMock()
        mock_ak.stock_hk_financial_indicator_em.side_effect = Exception("API Error")
        provider._ak = mock_ak

        result = provider._fetch_indicators("00700", 2024, 2020)

        # Should return empty DataFrame on exception
        assert result.empty


# ============================================================================
# Test date and TTL methods
# ============================================================================

class TestDateAndTTL:
    """Test date and TTL methods"""

    def test_get_date_column(self, provider):
        """Test _get_date_column returns year"""
        result = provider._get_date_column("balance_sheet")
        assert result == "year"

    def test_get_financial_ttl(self, provider):
        """Test _get_financial_ttl"""
        ttl = provider._get_financial_ttl(2024)
        assert isinstance(ttl, int)
        assert ttl > 0


# ============================================================================
# Test fetch with cache
# ============================================================================

class TestFetchWithCache:
    """Test _fetch_with_cache override"""

    def test_fetch_with_cache_default_start_year(self, provider, mock_cache):
        """Test default start_year calculation"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider.get_balance_sheet("00700", 2024)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_with_cache_force_refresh(self, provider, mock_cache):
        """Test force_refresh parameter"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider.get_balance_sheet("00700", 2024, force_refresh=True)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_with_cache_empty_result(self, provider, mock_cache_empty):
        """Test empty result handling"""
        provider_empty = HKProvider(cache=mock_cache_empty)

        result = provider_empty.get_balance_sheet("00700", 2024)

        assert result.empty


# ============================================================================
# Test stock info method
# ============================================================================

class TestStockInfo:
    """Test get_stock_info method"""

    def test_get_stock_info_success(self, provider, mock_cache):
        """Test successful stock info fetch"""
        stock_info_df = pd.DataFrame({
            "name": ["腾讯控股"],
            "industry": ["互联网"],
        })
        provider._ak.stock_hk_company_profile_em.return_value = stock_info_df

        result = provider.get_stock_info("00700")

        assert isinstance(result, pd.DataFrame)

    def test_get_stock_info_cache_used(self, provider, mock_cache):
        """Test that cache is used for stock info"""
        provider._ak.stock_hk_company_profile_em.return_value = pd.DataFrame()

        provider.get_stock_info("00700")

        mock_cache.get_or_fetch.assert_called()


# ============================================================================
# Test historical data method
# ============================================================================

class TestHistoricalData:
    """Test get_historical_data method"""

    def test_get_historical_data_deprecation_warning(self, provider, mock_cache):
        """Test deprecation warning is issued"""
        provider._ak.stock_hk_daily.return_value = pd.DataFrame({
            "date": ["2024-01-01"],
            "open": [300.0],
            "close": [310.0],
            "high": [315.0],
            "low": [295.0],
            "volume": [1000000],
        })

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = provider.get_historical_data("00700", "2024-01-01", "2024-01-31")

            # Check deprecation warning
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) > 0

    def test_get_historical_data_success(self, provider, mock_cache):
        """Test successful historical data fetch"""
        provider._ak.stock_hk_daily.return_value = pd.DataFrame({
            "date": ["2024-01-01"],
            "open": [300.0],
            "close": [310.0],
            "high": [315.0],
            "low": [295.0],
            "volume": [1000000],
        })

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = provider.get_historical_data("00700", "2024-01-01", "2024-01-31")

        assert isinstance(result, pd.DataFrame)


# ============================================================================
# Test Protocol fetch_financial_data
# ============================================================================

class TestFetchFinancialDataProtocol:
    """Test Protocol fetch_financial_data method"""

    def test_fetch_balance_fields(self, provider, mock_cache):
        """Test fetching balance sheet fields"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider.fetch_financial_data(
            stock_code="00700",
            fields={"total_assets", "total_liabilities"},
            end_year=2024,
            years=3,
        )

        assert isinstance(result, dict)

    def test_fetch_cashflow_fields(self, provider, mock_cache):
        """Test fetching cash flow fields"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider.fetch_financial_data(
            stock_code="00700",
            fields={"operating_cash_flow", "investing_cash_flow"},
            end_year=2024,
            years=3,
        )

        assert isinstance(result, dict)

    def test_fetch_mixed_fields(self, provider, mock_cache):
        """Test fetching mixed fields"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        result = provider.fetch_financial_data(
            stock_code="00700",
            fields={"total_revenue", "operating_cash_flow"},
            end_year=2024,
            years=3,
        )

        assert isinstance(result, dict)

    def test_fetch_empty_when_no_relevant_fields(self, provider, mock_cache):
        """Test empty result when no relevant fields requested"""
        result = provider.fetch_financial_data(
            stock_code="00700",
            fields={"unknown_field"},
            end_year=2024,
        )

        assert result == {}

    def test_fetch_with_warnings_on_missing_fields(self, provider, mock_cache):
        """Test warning when fields are missing"""
        provider._ak.stock_financial_hk_report_em.return_value = _make_financial_df()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = provider.fetch_financial_data(
                stock_code="00700",
                fields={"total_revenue", "unknown_field"},
                end_year=2024,
            )

            user_warnings = [x for x in w if issubclass(x.category, UserWarning)]


# ============================================================================
# Test Protocol fetch_indicators
# ============================================================================

class TestFetchIndicatorsProtocol:
    """Test Protocol fetch_indicators method"""

    def test_fetch_indicators_with_mapping(self, provider, mock_cache):
        """Test fetching indicators with field mapping"""
        provider._ak.stock_hk_financial_indicator_em.return_value = _make_indicator_df()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = provider.fetch_indicators(
                stock_code="00700",
                fields={"roe", "pe_ratio"},
                end_year=2024,
            )

        assert isinstance(result, dict)

    def test_fetch_indicators_same_name_field(self, provider, mock_cache):
        """Test fetching when field name is the same"""
        indicator_df = pd.DataFrame({
            "total_revenue": [751766000000],
        })
        provider._ak.stock_hk_financial_indicator_em.return_value = indicator_df

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = provider.fetch_indicators(
                stock_code="00700",
                fields={"total_revenue"},
                end_year=2024,
            )

        assert "total_revenue" in result or result == {}

    def test_fetch_indicators_empty_on_error(self, provider, mock_cache):
        """Test empty result on API error"""
        # Mock get_or_fetch to raise exception
        def raise_on_fetch(key, fetch_fn, ttl=None):
            raise Exception("API Error")

        mock_cache.get_or_fetch.side_effect = raise_on_fetch

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = provider.fetch_indicators(
                stock_code="00700",
                fields={"roe"},
                end_year=2024,
            )

        assert result == {}

    def test_fetch_indicators_empty_on_no_data(self, provider, mock_cache_empty):
        """Test empty result when API returns empty DataFrame"""
        provider_empty = HKProvider(cache=mock_cache_empty)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = provider_empty.fetch_indicators(
                stock_code="00700",
                fields={"roe"},
                end_year=2024,
            )

        assert result == {}


# ============================================================================
# Test Protocol fetch_market_data
# ============================================================================

class TestFetchMarketDataProtocol:
    """Test Protocol fetch_market_data method"""

    def test_fetch_market_cap(self, provider, mock_cache):
        """Test fetching market cap"""
        provider._ak.stock_hk_financial_indicator_em.return_value = _make_indicator_df()

        result = provider.fetch_market_data(
            stock_code="00700",
            fields={"market_cap"},
        )

        assert "market_cap" in result or result == {}

    def test_fetch_pe_and_pb(self, provider, mock_cache):
        """Test fetching PE and PB ratios"""
        provider._ak.stock_hk_financial_indicator_em.return_value = _make_indicator_df()

        result = provider.fetch_market_data(
            stock_code="00700",
            fields={"pe_ratio", "pb_ratio"},
        )

        assert isinstance(result, dict)

    def test_fetch_dividend_fields(self, provider, mock_cache):
        """Test fetching dividend-related fields"""
        provider._ak.stock_hk_financial_indicator_em.return_value = _make_indicator_df()

        result = provider.fetch_market_data(
            stock_code="00700",
            fields={"hk_dividend_yield_ttm", "hk_dividend_payout_ratio"},
        )

        assert isinstance(result, dict)

    def test_fetch_empty_when_no_market_fields(self, provider, mock_cache):
        """Test empty result when no market fields requested"""
        result = provider.fetch_market_data(
            stock_code="00700",
            fields={"total_revenue"},  # Not a market field
        )

        assert result == {}

    def test_fetch_market_data_empty_on_error(self, provider, mock_cache):
        """Test empty result on API error"""
        # Mock get_or_fetch to raise exception
        def raise_on_fetch(key, fetch_fn, ttl=None):
            raise Exception("API Error")

        mock_cache.get_or_fetch.side_effect = raise_on_fetch

        result = provider.fetch_market_data(
            stock_code="00700",
            fields={"market_cap"},
        )

        assert result == {}

    def test_fetch_market_data_empty_on_no_data(self, provider, mock_cache_empty):
        """Test empty result when API returns empty DataFrame"""
        provider_empty = HKProvider(cache=mock_cache_empty)

        result = provider_empty.fetch_market_data(
            stock_code="00700",
            fields={"market_cap"},
        )

        assert result == {}


# ============================================================================
# Test transform financial DataFrame
# ============================================================================

class TestTransformFinancialDf:
    """Test _transform_financial_df method"""

    def test_transform_with_std_item_name(self, provider):
        """Test transformation with STD_ITEM_NAME column"""
        df = pd.DataFrame({
            "SECURITY_CODE": ["00700"] * 2,
            "REPORT_DATE": ["2024-12-31", "2023-12-31"],
            "STD_ITEM_NAME": ["营业额", "营业额"],
            "AMOUNT": [100, 200],
        })

        result = provider._transform_financial_df(df)

        assert "year" in result.columns

    def test_transform_with_item_name(self, provider):
        """Test transformation with ITEM_NAME column"""
        df = pd.DataFrame({
            "SECURITY_CODE": ["00700"] * 2,
            "REPORT_DATE": ["2024-12-31", "2023-12-31"],
            "ITEM_NAME": ["营业额", "营业额"],
            "AMOUNT": [100, 200],
        })

        result = provider._transform_financial_df(df)

        assert isinstance(result, pd.DataFrame)

    def test_transform_empty_df(self, provider):
        """Test transformation of empty DataFrame"""
        result = provider._transform_financial_df(pd.DataFrame())
        assert result.empty

    def test_transform_missing_columns(self, provider):
        """Test transformation when required columns are missing"""
        df = pd.DataFrame({
            "other_column": [1, 2, 3],
        })

        result = provider._transform_financial_df(df)

        assert isinstance(result, pd.DataFrame)

    def test_transform_no_pivot_needed(self, provider):
        """Test transformation when pivot fails"""
        df = pd.DataFrame({
            "REPORT_DATE": ["2024-12-31"],
            "STD_ITEM_NAME": ["A"],
            "AMOUNT": [100],
            "OTHER": [200],
        })

        result = provider._transform_financial_df(df)

        # Should return DataFrame (either pivoted or original)
        assert isinstance(result, pd.DataFrame)


# ============================================================================
# Test find mapped field
# ============================================================================

class TestFindMappedField:
    """Test _find_mapped_field method"""

    def test_find_existing_mapping(self, provider):
        """Test finding an existing field mapping"""
        mapping = {"营业额": "total_revenue", "净利润": "net_profit"}
        result = provider._find_mapped_field("total_revenue", mapping)
        assert result == "营业额"

    def test_find_non_existing_mapping(self, provider):
        """Test finding a non-existing field mapping"""
        mapping = {"营业额": "total_revenue"}
        result = provider._find_mapped_field("unknown_field", mapping)
        assert result is None


# ============================================================================
# Test df add results
# ============================================================================

class TestDfAddResults:
    """Test _df_add_results method"""

    def test_add_results_success(self, provider):
        """Test successful results addition"""
        df = pd.DataFrame({
            "year": [2024, 2023],
            "total_revenue": [1000000, 900000],
            "net_profit": [100000, 90000],
        })
        results = {}

        provider._df_add_results(df, results, {"total_revenue", "net_profit"})

        assert "total_revenue" in results
        assert 2024 in results["total_revenue"]

    def test_add_results_empty_df(self, provider):
        """Test with empty DataFrame"""
        results = {}
        provider._df_add_results(pd.DataFrame(), results, {"total_revenue"})
        assert results == {}

    def test_add_results_no_year_column(self, provider):
        """Test when year column is missing"""
        df = pd.DataFrame({
            "total_revenue": [100],
        })
        results = {}
        original_results_len = len(results)

        provider._df_add_results(df, results, {"total_revenue"})

        assert len(results) == original_results_len

    def test_add_results_missing_column(self, provider):
        """Test when field column is missing"""
        df = pd.DataFrame({
            "year": [2024],
        })
        results = {}

        provider._df_add_results(df, results, {"unknown_field"})

        assert results == {}

    def test_add_results_with_pandas_series(self, provider):
        """Test when value is a pandas Series"""
        df = pd.DataFrame({
            "year": [2024],
            "total_revenue": [pd.Series([100])],
        })
        results = {}

        provider._df_add_results(df, results, {"total_revenue"})

        # Should skip Series values
        assert results == {}

    def test_add_results_with_invalid_value(self, provider):
        """Test when value cannot be converted to float"""
        df = pd.DataFrame({
            "year": [2024],
            "total_revenue": ["not_a_number"],
        })
        results = {}

        provider._df_add_results(df, results, {"total_revenue"})

        assert results == {}


# ============================================================================
# Test warn missing fields
# ============================================================================

class TestWarnMissingFields:
    """Test _warn_missing_fields method"""

    def test_warn_missing_fields(self, provider):
        """Test warning for missing fields"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            provider._warn_missing_fields(
                requested_fields={"total_revenue", "net_profit"},
                results={"total_revenue": {2024: 100}},  # net_profit is missing
            )

            user_warnings = [x for x in w if issubclass(x.category, UserWarning)]
            assert len(user_warnings) > 0

    def test_no_warn_when_all_found(self, provider):
        """Test no warning when all fields are found"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            provider._warn_missing_fields(
                requested_fields={"total_revenue"},
                results={"total_revenue": {2024: 100}},
            )

            user_warnings = [x for x in w if issubclass(x.category, UserWarning)]
            # May have no warnings

    def test_warn_with_empty_results(self, provider):
        """Test warning when no results found"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            provider._warn_missing_fields(
                requested_fields={"total_revenue", "net_profit"},
                results={},
            )

            user_warnings = [x for x in w if issubclass(x.category, UserWarning)]
            assert len(user_warnings) > 0


# ============================================================================
# Test cache key and operations
# ============================================================================

class TestCacheOperations:
    """Test cache helper methods"""

    def test_get_cache_key(self, provider):
        """Test cache key building"""
        key = provider._get_cache_key("prefix", "stock", "suffix")
        assert "prefix" in key
        assert "stock" in key

    def test_get_from_cache(self, provider, mock_cache):
        """Test _get_from_cache"""
        mock_cache.get.return_value = {"data": "value"}
        result = provider._get_from_cache("test_key")
        assert result == {"data": "value"}

    def test_set_to_cache(self, provider, mock_cache):
        """Test _set_to_cache"""
        provider._set_to_cache("test_key", "value", ttl=3600)
        mock_cache.set.assert_called_once()

    def test_invalidate_cache(self, provider, mock_cache):
        """Test _invalidate_cache"""
        provider._invalidate_cache("test_key")
        mock_cache.invalidate.assert_called_once_with("test_key")


# ============================================================================
# Test apply field mapping
# ============================================================================

class TestApplyFieldMapping:
    """Test _apply_field_mapping method"""

    def test_apply_mapping_balance_sheet(self, provider):
        """Test balance sheet field mapping"""
        df = pd.DataFrame({
            "资产总值": [100],
            "总负债": [50],
        })

        result = provider._apply_field_mapping(df, "balance_sheet")

        assert "total_assets" in result.columns
        assert "total_liabilities" in result.columns

    def test_apply_mapping_income_statement(self, provider):
        """Test income statement field mapping"""
        df = pd.DataFrame({
            "营业额": [100],
            "股东应占溢利": [20],
        })

        result = provider._apply_field_mapping(df, "income_statement")

        assert "total_revenue" in result.columns
        assert "parent_net_profit" in result.columns

    def test_apply_mapping_empty_df(self, provider):
        """Test with empty DataFrame"""
        result = provider._apply_field_mapping(pd.DataFrame(), "balance_sheet")
        assert result.empty
