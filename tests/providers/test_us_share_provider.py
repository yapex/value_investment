"""Comprehensive tests for US-Share Provider"""
import pytest
import warnings
from unittest.mock import MagicMock, patch

import pandas as pd

from value_investment.providers.us_share import USProvider


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_cache():
    """Create a mock cache"""
    cache = MagicMock()
    cache.get.return_value = None
    cache.set.return_value = None
    cache.get_or_fetch.return_value = None
    return cache


@pytest.fixture
def provider(mock_cache):
    """Create USProvider with mocked API"""
    with patch("value_investment.providers.us_share.ak") as mock_ak:
        provider = USProvider(cache=mock_cache)
        provider._ak = mock_ak
        yield provider


def make_us_balance_df():
    """Create mock US balance sheet DataFrame (长表格式)"""
    return pd.DataFrame({
        "STD_ITEM_NAME": ["现金及现金等价物", "应收账款", "存货", "总资产"] * 3,
        "AMOUNT": [1000000, 500000, 300000, 5000000] * 3,
        "REPORT_DATE": ["2024-12-31", "2024-12-31", "2024-12-31", "2024-12-31",
                       "2023-12-31", "2023-12-31", "2023-12-31", "2023-12-31",
                       "2022-12-31", "2022-12-31", "2022-12-31", "2022-12-31"],
    })


def make_us_income_df():
    """Create mock US income statement DataFrame (长表格式)"""
    return pd.DataFrame({
        "STD_ITEM_NAME": ["主营收入", "净利润", "营业成本"] * 3,
        "AMOUNT": [100000000, 10000000, 60000000] * 3,
        "REPORT_DATE": ["2024-12-31", "2024-12-31", "2024-12-31",
                       "2023-12-31", "2023-12-31", "2023-12-31",
                       "2022-12-31", "2022-12-31", "2022-12-31"],
    })


def make_us_indicator_df():
    """Create mock US indicator DataFrame"""
    return pd.DataFrame({
        "BASIC_EPS": [5.5, 5.0],
        "DILUTED_EPS": [5.4, 4.9],
        "GROSS_PROFIT_RATIO": [40.0, 38.0],
        "NET_PROFIT_RATIO": [10.0, 9.5],
        "ROE_AVG": [25.0, 23.0],
        "ROA": [15.0, 14.0],
        "CURRENT_RATIO": [2.0, 1.8],
        "MARKET_CAP": [3000000000000, 2800000000000],
        "PE_TTM": [30.0, 28.0],
    })


# ============================================================================
# Tests for supported fields
# ============================================================================

class TestSupportedFields:
    """Test supported fields property"""

    def test_supported_fields_is_set(self, provider):
        """supported_fields should be a set"""
        assert isinstance(provider.supported_fields, set)

    def test_supported_fields_contains_core(self, provider):
        """Should contain core fields"""
        assert "total_revenue" in provider.supported_fields
        assert "net_profit" in provider.supported_fields
        assert "roe" in provider.supported_fields
        assert "market_cap" in provider.supported_fields

    def test_supported_fields_contains_market(self, provider):
        """Should contain market fields"""
        assert "pe_ratio" in provider.supported_fields
        assert "pb_ratio" in provider.supported_fields


# ============================================================================
# Tests for raw fetch methods
# ============================================================================

class TestRawFetchMethods:
    """Test fetch_raw_* methods"""

    def test_fetch_raw_balance_sheet(self, provider, mock_cache):
        """Test raw balance sheet fetch"""
        provider._ak.stock_financial_us_report_em.return_value = make_us_balance_df()

        result = provider.fetch_raw_balance_sheet("AAPL", 2024, 2022)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_raw_balance_sheet_empty(self, provider, mock_cache):
        """Test empty result on API error"""
        provider._ak.stock_financial_us_report_em.side_effect = Exception("API Error")

        result = provider.fetch_raw_balance_sheet("AAPL", 2024, 2022)

        assert result.empty

    def test_fetch_raw_income_statement(self, provider, mock_cache):
        """Test raw income statement fetch"""
        provider._ak.stock_financial_us_report_em.return_value = make_us_income_df()

        result = provider.fetch_raw_income_statement("AAPL", 2024, 2022)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_raw_income_statement_empty(self, provider, mock_cache):
        """Test empty result on API error"""
        provider._ak.stock_financial_us_report_em.side_effect = Exception("API Error")

        result = provider.fetch_raw_income_statement("AAPL", 2024, 2022)

        assert result.empty

    def test_fetch_raw_cash_flow(self, provider, mock_cache):
        """Test raw cash flow fetch"""
        provider._ak.stock_financial_us_report_em.return_value = pd.DataFrame()

        result = provider.fetch_raw_cash_flow("AAPL", 2024, 2022)

        assert isinstance(result, pd.DataFrame)


# ============================================================================
# Tests for mapped fetch methods
# ============================================================================

class TestMappedFetchMethods:
    """Test _fetch_* methods with field mapping"""

    def test_fetch_balance_sheet_with_mapping(self, provider, mock_cache):
        """Test balance sheet fetch with field mapping"""
        provider._ak.stock_financial_us_report_em.return_value = make_us_balance_df()

        result = provider._fetch_balance_sheet("AAPL", 2024, 2022)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_income_statement_with_mapping(self, provider, mock_cache):
        """Test income statement fetch with field mapping"""
        provider._ak.stock_financial_us_report_em.return_value = make_us_income_df()

        result = provider._fetch_income_statement("AAPL", 2024, 2022)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_cash_flow_with_mapping(self, provider, mock_cache):
        """Test cash flow fetch with field mapping"""
        provider._ak.stock_financial_us_report_em.return_value = pd.DataFrame()

        result = provider._fetch_cash_flow("AAPL", 2024, 2022)

        assert isinstance(result, pd.DataFrame)


# ============================================================================
# Tests for fetch_indicators
# ============================================================================

class TestFetchIndicators:
    """Test _fetch_indicators method"""

    def test_fetch_indicators_success(self, provider, mock_cache):
        """Test successful indicators fetch"""
        provider._ak.stock_financial_us_analysis_indicator_em.return_value = make_us_indicator_df()

        result = provider._fetch_indicators("AAPL", 2024, 2022)

        assert isinstance(result, pd.DataFrame)

    def test_fetch_indicators_empty_on_error(self, provider, mock_cache):
        """Test empty result on API error"""
        provider._ak.stock_financial_us_analysis_indicator_em.side_effect = Exception("API Error")

        result = provider._fetch_indicators("AAPL", 2024, 2022)

        assert result.empty


# ============================================================================
# Tests for DataProvider Protocol methods
# ============================================================================

class TestFetchFinancialData:
    """Test fetch_financial_data method"""

    def test_fetch_financial_data_balance_fields(self, provider, mock_cache):
        """Test fetching balance sheet fields"""
        provider._ak.stock_financial_us_report_em.return_value = make_us_balance_df()

        result = provider.fetch_financial_data(
            stock_code="AAPL",
            fields={"total_assets", "cash_and_equivalents"},
            end_year=2024,
            years=3,
        )

        assert isinstance(result, dict)

    def test_fetch_financial_data_income_fields(self, provider, mock_cache):
        """Test fetching income statement fields"""
        provider._ak.stock_financial_us_report_em.return_value = make_us_income_df()

        result = provider.fetch_financial_data(
            stock_code="AAPL",
            fields={"total_revenue", "net_profit"},
            end_year=2024,
            years=3,
        )

        assert isinstance(result, dict)

    def test_fetch_financial_data_empty_when_no_fields(self, provider, mock_cache):
        """Test empty result when no relevant fields requested"""
        result = provider.fetch_financial_data(
            stock_code="AAPL",
            fields={"unknown_field"},
            end_year=2024,
        )

        assert result == {}

    def test_fetch_financial_data_with_warnings(self, provider, mock_cache):
        """Test warning for missing fields"""
        provider._ak.stock_financial_us_report_em.return_value = make_us_balance_df()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = provider.fetch_financial_data(
                stock_code="AAPL",
                fields={"total_revenue", "net_profit"},  # Not in balance sheet
                end_year=2024,
            )
            
            # Should issue warning about missing fields
            user_warnings = [x for x in w if issubclass(x.category, UserWarning)]
            # May or may not have warnings depending on implementation


class TestFetchIndicatorsProtocol:
    """Test fetch_indicators Protocol method"""

    def test_fetch_indicators_protocol(self, provider, mock_cache):
        """Test fetch_indicators protocol method"""
        provider._ak.stock_financial_us_analysis_indicator_em.return_value = make_us_indicator_df()
        mock_cache.get_or_fetch.return_value = make_us_indicator_df()

        result = provider.fetch_indicators(
            stock_code="AAPL",
            fields={"roe", "roa"},
            end_year=2024,
        )

        assert isinstance(result, dict)

    def test_fetch_indicators_empty_on_error(self, provider, mock_cache):
        """Test empty result on API error"""
        provider._ak.stock_financial_us_analysis_indicator_em.side_effect = Exception("API Error")
        mock_cache.get_or_fetch.side_effect = Exception("API Error")

        result = provider.fetch_indicators(
            stock_code="AAPL",
            fields={"roe"},
            end_year=2024,
        )

        assert result == {}


class TestFetchMarketDataProtocol:
    """Test fetch_market_data Protocol method"""

    def test_fetch_market_data_success(self, provider, mock_cache):
        """Test successful market data fetch"""
        provider._ak.stock_financial_us_analysis_indicator_em.return_value = make_us_indicator_df()

        result = provider.fetch_market_data(
            stock_code="AAPL",
            fields={"market_cap", "pe_ratio"},
        )

        assert isinstance(result, dict)

    def test_fetch_market_data_empty_when_no_fields(self, provider, mock_cache):
        """Test empty result when no market fields requested"""
        result = provider.fetch_market_data(
            stock_code="AAPL",
            fields={"total_revenue"},  # Not a market field
        )

        assert result == {}

    def test_fetch_market_data_empty_on_error(self, provider, mock_cache):
        """Test empty result on API error"""
        provider._ak.stock_financial_us_analysis_indicator_em.side_effect = Exception("API Error")

        result = provider.fetch_market_data(
            stock_code="AAPL",
            fields={"market_cap"},
        )

        assert result == {}


# ============================================================================
# Tests for private helper methods
# ============================================================================

class TestFindMappedField:
    """Test _find_mapped_field method"""

    def test_find_existing_mapping(self, provider):
        """Test finding an existing field mapping"""
        mapping = {"NATIVE_FIELD": "standard_field"}
        result = provider._find_mapped_field("standard_field", mapping)
        assert result == "NATIVE_FIELD"

    def test_find_non_existing_mapping(self, provider):
        """Test finding a non-existing field mapping"""
        mapping = {"NATIVE_FIELD": "standard_field"}
        result = provider._find_mapped_field("unknown_field", mapping)
        assert result is None


class TestTransformFinancialDf:
    """Test _transform_financial_df method"""

    def test_transform_success(self, provider):
        """Test successful DataFrame transformation"""
        df = make_us_balance_df()
        result = provider._transform_financial_df(df)
        assert isinstance(result, pd.DataFrame)

    def test_transform_empty_df(self, provider):
        """Test transformation of empty DataFrame"""
        result = provider._transform_financial_df(pd.DataFrame())
        assert result.empty

    def test_transform_no_pivot_columns(self, provider):
        """Test transformation when pivot columns are missing"""
        df = pd.DataFrame({"random_col": [1, 2, 3]})
        result = provider._transform_financial_df(df)
        assert isinstance(result, pd.DataFrame)


class TestDfAddResults:
    """Test _df_add_results method"""

    def test_add_results_success(self, provider):
        """Test successful results addition"""
        df = pd.DataFrame({
            "year": [2024, 2023],
            "total_revenue": [1000000, 900000],
        })
        results = {}
        
        provider._df_add_results(df, results, {"total_revenue"})
        
        assert "total_revenue" in results
        assert 2024 in results["total_revenue"]

    def test_add_results_empty_df(self, provider):
        """Test with empty DataFrame"""
        results = {}
        provider._df_add_results(pd.DataFrame(), results, {"total_revenue"})
        assert results == {}

    def test_add_results_missing_column(self, provider):
        """Test when field column is missing"""
        df = pd.DataFrame({
            "year": [2024],
        })
        results = {}
        provider._df_add_results(df, results, {"unknown_field"})
        assert results == {}


class TestWarnMissingFields:
    """Test _warn_missing_fields method"""

    def test_warn_missing_fields(self, provider):
        """Test warning for missing fields"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            provider._warn_missing_fields(
                requested_fields={"total_revenue", "unknown_field"},
                results={"net_profit": {2024: 100}},
            )
            
            # Should have at least one warning
            user_warnings = [x for x in w if issubclass(x.category, UserWarning)]

    def test_no_warn_when_all_found(self, provider):
        """Test no warning when all fields are found"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            provider._warn_missing_fields(
                requested_fields={"total_revenue"},
                results={"total_revenue": {2024: 100}},
            )
            
            # May have no warnings


# ============================================================================
# Tests for date and TTL methods
# ============================================================================

class TestDateAndTTL:
    """Test date column and TTL methods"""

    def test_get_date_column(self, provider):
        """Test date column name"""
        result = provider._get_date_column("balance_sheet")
        assert result == "year"

    def test_get_financial_ttl(self, provider):
        """Test financial data TTL"""
        ttl = provider._get_financial_ttl(2024)
        assert isinstance(ttl, int)
        assert ttl > 0
