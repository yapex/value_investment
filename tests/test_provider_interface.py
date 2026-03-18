"""Tests for Provider interface protocol - standardize_columns and get_supported_fields

This test file defines the Provider interface contract:
1. standardize_columns(df, data_type) -> DataFrame: Standardize column names
2. get_supported_fields(data_type) -> list[str]: Get supported standard fields
3. fetch_xxx methods return standardized DataFrames
"""

import pandas as pd
import pytest  # type: ignore


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


class TestProviderInterfaceProtocol:
    """Test Provider interface protocol definition"""

    def test_provider_has_standardize_columns_method(self):
        """Provider must have standardize_columns method"""
        from value_investment.data.providers.base_provider import BaseProvider

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache())

        assert hasattr(provider, 'standardize_columns')
        assert callable(getattr(provider, 'standardize_columns'))

    def test_provider_has_get_supported_fields_method(self):
        """Provider must have get_supported_fields method"""
        from value_investment.data.providers.base_provider import BaseProvider

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache())

        assert hasattr(provider, 'get_supported_fields')
        assert callable(getattr(provider, 'get_supported_fields'))


class TestStandardizeColumns:
    """Test standardize_columns method behavior"""

    def test_standardize_columns_renames_native_to_standard(self):
        """standardize_columns should rename native fields to standard fields"""
        from value_investment.data.providers.base_provider import BaseProvider

        field_mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "total_assets": "total_assets",
            }
        }

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache(), field_mappings=field_mappings)

        # Create DataFrame with native field names
        df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "total_assets": [1000000],
        })

        result = provider.standardize_columns(df, "balance")
        assert result is not None  # Type guard

        # Should have standard field names
        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        assert "total_assets" in result.columns
        # Should not have native field names
        assert "ts_code" not in result.columns
        assert "end_date" not in result.columns

    def test_standardize_columns_preserves_unmapped_columns(self):
        """standardize_columns should preserve columns not in mapping"""
        from value_investment.data.providers.base_provider import BaseProvider

        field_mappings = {
            "income": {
                "total_revenue_native": "total_revenue",
            }
        }

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache(), field_mappings=field_mappings)

        df = pd.DataFrame({
            "total_revenue_native": [1000],
            "unmapped_column": [500],
        })

        result = provider.standardize_columns(df, "income")
        assert result is not None  # Type guard

        # Mapped column should be renamed
        assert "total_revenue" in result.columns
        assert "total_revenue_native" not in result.columns
        # Unmapped column should be preserved
        assert "unmapped_column" in result.columns

    def test_standardize_columns_handles_none_df(self):
        """standardize_columns should handle None DataFrame"""
        from value_investment.data.providers.base_provider import BaseProvider

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache())

        result = provider.standardize_columns(None, "balance")

        assert result is None

    def test_standardize_columns_handles_empty_df(self):
        """standardize_columns should handle empty DataFrame"""
        from value_investment.data.providers.base_provider import BaseProvider

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache())

        empty_df = pd.DataFrame()
        result = provider.standardize_columns(empty_df, "balance")

        assert result is not None
        assert result.empty

    def test_standardize_columns_unknown_data_type(self):
        """standardize_columns should return df unchanged for unknown data_type"""
        from value_investment.data.providers.base_provider import BaseProvider

        field_mappings = {
            "income": {
                "native_revenue": "total_revenue",
            }
        }

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache(), field_mappings=field_mappings)

        df = pd.DataFrame({
            "native_revenue": [1000],
        })

        # Using "balance" which is not in field_mappings
        result = provider.standardize_columns(df, "balance")
        assert result is not None  # Type guard

        # Should return unchanged
        assert "native_revenue" in result.columns
        assert "total_revenue" not in result.columns


class TestGetSupportedFields:
    """Test get_supported_fields method behavior"""

    def test_get_supported_fields_returns_list(self):
        """get_supported_fields should return a list of field names"""
        from value_investment.data.providers.base_provider import BaseProvider

        field_mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "total_assets": "total_assets",
                "total_liab": "total_liabilities",
            },
            "income": {
                "ts_code": "stock_code",
                "total_revenue": "total_revenue",
                "net_profit": "net_profit",
            }
        }

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache(), field_mappings=field_mappings)

        balance_fields = provider.get_supported_fields("balance")
        income_fields = provider.get_supported_fields("income")

        assert isinstance(balance_fields, list)
        assert isinstance(income_fields, list)
        assert "total_assets" in balance_fields
        assert "total_revenue" in income_fields

    def test_get_supported_fields_unknown_type(self):
        """get_supported_fields should return empty list for unknown data_type"""
        from value_investment.data.providers.base_provider import BaseProvider

        field_mappings = {
            "balance": {
                "ts_code": "stock_code",
                "total_assets": "total_assets",
            },
        }

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache(), field_mappings=field_mappings)

        result = provider.get_supported_fields("unknown_type")

        assert result == []

    def test_get_supported_fields_returns_standard_field_names(self):
        """get_supported_fields should return standard (not native) field names"""
        from value_investment.data.providers.base_provider import BaseProvider

        field_mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "total_assets_native": "total_assets",
                "total_liab_native": "total_liabilities",
            },
        }

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache(), field_mappings=field_mappings)

        fields = provider.get_supported_fields("balance")

        # Should return standard field names (values from mapping)
        assert "stock_code" in fields
        assert "report_date" in fields
        assert "total_assets" in fields
        assert "total_liabilities" in fields
        # Should NOT return native field names (keys from mapping)
        assert "ts_code" not in fields
        assert "end_date" not in fields
        assert "total_assets_native" not in fields


class TestProviderIntegration:
    """Test Provider interface integration with fetch methods"""

    def test_fetch_method_returns_standardized_columns(self):
        """Fetch methods should return DataFrame with standardized column names"""
        from value_investment.data.providers.base_provider import BaseProvider

        field_mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "total_assets": "total_assets",
            }
        }

        class TestProvider(BaseProvider):
            def _fetch_raw_data(self, stock_code: str) -> pd.DataFrame:
                """Simulate fetching raw data from API"""
                return pd.DataFrame({
                    "ts_code": [stock_code],
                    "end_date": ["2023-12-31"],
                    "total_assets": [1000000],
                })

            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame | None:
                """Fetch and standardize balance sheet data"""
                raw_df = self._fetch_raw_data(stock_code)
                return self.standardize_columns(raw_df, "balance")

        provider = TestProvider(cache=MockCache(), field_mappings=field_mappings)

        result = provider.get_balance_sheet("000001.SZ", 2023)
        assert result is not None  # Type guard

        # Should have standardized column names
        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        assert "ts_code" not in result.columns
        assert "end_date" not in result.columns

    def test_provider_uses_field_mappings_from_config(self):
        """Provider should use field_mappings from configuration"""
        from value_investment.data.providers.base_provider import BaseProvider

        config_mappings = {
            "balance": {
                "native_code": "stock_code",
                "native_date": "report_date",
            }
        }

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache(), field_mappings=config_mappings)

        df = pd.DataFrame({
            "native_code": ["000001.SZ"],
            "native_date": ["2023-12-31"],
        })

        result = provider.standardize_columns(df, "balance")
        assert result is not None  # Type guard

        assert "stock_code" in result.columns
        assert "report_date" in result.columns

    def test_apply_mapping_backward_compatibility(self):
        """_apply_mapping should delegate to standardize_columns for backward compatibility"""
        from value_investment.data.providers.base_provider import BaseProvider

        field_mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
            }
        }

        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()

        provider = TestProvider(cache=MockCache(), field_mappings=field_mappings)

        df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
        })

        # _apply_mapping should work the same as standardize_columns
        result = provider._apply_mapping(df, "balance")
        assert result is not None  # Type guard

        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        assert "ts_code" not in result.columns
