"""Tests for start_year parameter in financial statements

This tests the fix for: https://github.com/user/value_investment/issues/XXX
- Provider should accept start_year parameter
- API should accept years parameter
- CLI should accept --years flag
"""
import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest  # type: ignore

from value_investment.api import ValueInvestment


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

    def clear(self):
        self._data.clear()


@pytest.fixture
def tushare_token():
    """Get tushare token from environment"""
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        pytest.skip("TUSHARE_TOKEN not set, skipping integration tests")
    return token


class TestTushareProviderStartYear:
    """Test TushareProvider start_year parameter"""

    @pytest.mark.integration
    def test_get_income_statement_with_start_year(self, tushare_token):
        """Should fetch data from start_year to end_year"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        provider = TushareProvider(cache=MockCache(), token=tushare_token)

        # Fetch 10 years of data
        df = provider.get_income_statement("600519.SH", end_year=2025, start_year=2015)

        assert not df.empty

        # Filter to annual reports (use end_date, the original column name)
        date_col = "end_date" if "end_date" in df.columns else "report_date"
        df["_date"] = df[date_col].astype(str)
        annual = df[df["_date"].str.endswith("1231")]
        years = sorted(
            set(pd.to_datetime(annual[date_col]).dt.year.tolist())  # type: ignore[union-attr]
        )

        # Should have data from 2015-2024 (at least)
        assert min(years) <= 2015
        assert max(years) >= 2024

    @pytest.mark.integration
    def test_get_balance_sheet_with_start_year(self, tushare_token):
        """Should fetch balance sheet from start_year to end_year"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        provider = TushareProvider(cache=MockCache(), token=tushare_token)

        df = provider.get_balance_sheet("600519.SH", end_year=2025, start_year=2015)

        assert not df.empty

    @pytest.mark.integration
    def test_get_cash_flow_statement_with_start_year(self, tushare_token):
        """Should fetch cash flow statement from start_year to end_year"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        provider = TushareProvider(cache=MockCache(), token=tushare_token)

        df = provider.get_cash_flow_statement("600519.SH", end_year=2025, start_year=2015)

        assert not df.empty

    @pytest.mark.integration
    def test_default_start_year_is_end_year_minus_15(self, tushare_token):
        """Should default start_year to end_year - 15"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        provider = TushareProvider(cache=MockCache(), token=tushare_token)

        # Without start_year, should get 15 years of data
        df = provider.get_income_statement("600519.SH", end_year=2025)

        assert not df.empty

        date_col = "end_date" if "end_date" in df.columns else "report_date"
        df["_date"] = df[date_col].astype(str)
        annual = df[df["_date"].str.endswith("1231")]
        years = sorted(
            set(pd.to_datetime(annual[date_col]).dt.year.tolist())  # type: ignore[union-attr]
        )

        # Should have data from at least 2010 (2025 - 15)
        assert min(years) <= 2011


class TestAPIYearsParameter:
    """Test ValueInvestment API years parameter"""

    def test_get_profit_sheet_default_years(self):
        """get_profit_sheet should default to 10 years"""
        vi = ValueInvestment()

        # Mock the provider
        vi._provider.get_income_statement = MagicMock(
            return_value=pd.DataFrame({
                "report_date": ["2023-12-31"],
                "basic_eps": [50.0],
            })
        )

        vi.get_profit_sheet("600519", end_year=2025)

        # Should be called with (symbol, end_year, start_year)
        # start_year = 2025 - 10 = 2015
        vi._provider.get_income_statement.assert_called_once_with(
            "600519", 2025, 2015
        )

    def test_get_profit_sheet_with_years(self):
        """get_profit_sheet should accept years parameter"""
        vi = ValueInvestment()

        vi._provider.get_income_statement = MagicMock(
            return_value=pd.DataFrame({
                "report_date": ["2023-12-31"],
                "basic_eps": [50.0],
            })
        )

        vi.get_profit_sheet("600519", end_year=2025, years=5)

        # start_year = 2025 - 5 = 2020
        vi._provider.get_income_statement.assert_called_once_with(
            "600519", 2025, 2020
        )

    def test_get_balance_sheet_with_years(self):
        """get_balance_sheet should accept years parameter"""
        vi = ValueInvestment()

        vi._provider.get_balance_sheet = MagicMock(
            return_value=pd.DataFrame({
                "report_date": ["2023-12-31"],
                "total_assets": [1000000],
            })
        )

        vi.get_balance_sheet("600519", end_year=2025, years=8)

        # start_year = 2025 - 8 = 2017
        vi._provider.get_balance_sheet.assert_called_once_with(
            "600519", 2025, 2017
        )

    def test_get_cashflow_sheet_with_years(self):
        """get_cashflow_sheet should accept years parameter"""
        vi = ValueInvestment()

        vi._provider.get_cash_flow_statement = MagicMock(
            return_value=pd.DataFrame({
                "report_date": ["2023-12-31"],
                "net_cash_operate": [50000],
            })
        )

        vi.get_cashflow_sheet("600519", end_year=2025, years=12)

        # start_year = 2025 - 12 = 2013
        vi._provider.get_cash_flow_statement.assert_called_once_with(
            "600519", 2025, 2013
        )

    def test_get_profit_sheet_without_end_year_uses_current(self):
        """get_profit_sheet should use current year if end_year not provided"""
        vi = ValueInvestment()

        vi._provider.get_income_statement = MagicMock(
            return_value=pd.DataFrame({
                "report_date": ["2023-12-31"],
                "basic_eps": [50.0],
            })
        )

        from datetime import datetime
        current_year = datetime.now().year

        vi.get_profit_sheet("600519", years=5)

        # end_year = current_year, start_year = current_year - 5
        vi._provider.get_income_statement.assert_called_once_with(
            "600519", current_year, current_year - 5
        )


class TestAPIYearsParameterIntegration:
    """Integration tests for years parameter"""

    @pytest.mark.integration
    def test_maotai_10_years_eps(self, tushare_token):
        """Should fetch 10 years of EPS data for Maotai"""
        vi = ValueInvestment()

        # Clear cache first
        vi.clear_cache("600519")

        # Get 10 years of income statements
        df = vi.get_profit_sheet("600519", end_year=2025, years=10)

        assert not df.empty

        # Filter to annual reports
        df["report_date"] = df["report_date"].astype(str)
        annual = df[df["report_date"].str.endswith("1231")].copy()
        annual = annual.sort_values("report_date", ascending=False).drop_duplicates(  # type: ignore[call-overload]
            subset=["report_date"]
        )
        annual = annual.sort_values("report_date")  # type: ignore[call-overload]
        annual["year"] = pd.to_datetime(annual["report_date"]).dt.year

        eps_data = annual[["year", "basic_eps"]].dropna()

        # Should have 10 years of data
        assert len(eps_data) >= 10

        # Should include 2015
        years = eps_data["year"].tolist()
        assert 2015 in years

    @pytest.mark.integration
    def test_maotai_5_years_fewer_data(self, tushare_token):
        """5 years should return fewer data than 10 years"""
        import numpy as np

        vi = ValueInvestment()

        vi.clear_cache("600519")

        # Get 5 years
        df_5y = vi.get_profit_sheet("600519", end_year=2025, years=5)
        df_5y["report_date"] = df_5y["report_date"].astype(str)
        annual_5y = df_5y[df_5y["report_date"].str.endswith("1231")]
        years_5y = len(np.unique(annual_5y["report_date"]))

        vi.clear_cache("600519")

        # Get 10 years
        df_10y = vi.get_profit_sheet("600519", end_year=2025, years=10)
        df_10y["report_date"] = df_10y["report_date"].astype(str)
        annual_10y = df_10y[df_10y["report_date"].str.endswith("1231")]
        years_10y = len(np.unique(annual_10y["report_date"]))

        # 10 years should have more data
        assert years_10y > years_5y


class TestCacheKeyWithStartYear:
    """Test that cache key includes start_year"""

    def test_cache_key_includes_start_year(self, tushare_token):
        """Cache key should include start_year to differentiate requests"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        cache = MockCache()
        provider = TushareProvider(cache=cache, token=tushare_token)

        # First request with 5 years
        provider.get_income_statement("600519.SH", end_year=2025, start_year=2020)

        # Check cache key exists
        cache_keys_5y = [k for k in cache._data.keys() if "income" in k and "600519" in k]
        assert len(cache_keys_5y) == 1
        key_5y = cache_keys_5y[0]

        # Should contain both start and end year
        assert "2020" in key_5y  # start_year
        assert "2025" in key_5y  # end_year
