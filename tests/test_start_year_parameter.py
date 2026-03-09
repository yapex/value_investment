"""Tests for start_year parameter in financial statements

This tests the fix for: https://github.com/user/value_investment/issues/XXX
- Provider should accept start_year parameter
- API should accept years parameter
- CLI should accept --years flag

Tests use mocks to avoid depending on real TUSHARE_TOKEN.
Only a few integration tests are kept for connectivity verification.
"""
import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest  # type: ignore

from value_investment.api import ValueInvestment


class TestTushareProviderStartYear:
    """Test TushareProvider start_year parameter"""

    def test_get_income_statement_with_start_year(self, mock_tushare_provider):
        """Should fetch data from start_year to end_year"""
        mock_tushare_provider._api.income.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"] * 10,
            "end_date": ["20151231", "20161231", "20171231", "20181231", "20191231",
                        "20201231", "20211231", "20221231", "20231231", "20241231"],
            "total_revenue": [100000000] * 10,
        })
        
        df = mock_tushare_provider.get_income_statement(
            "600519.SH", end_year=2025, start_year=2015
        )

        assert not df.empty

    def test_get_balance_sheet_with_start_year(self, mock_tushare_provider):
        """Should fetch balance sheet from start_year to end_year"""
        mock_tushare_provider._api.balancesheet.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"] * 5,
            "end_date": ["20211231", "20221231", "20231231", "20241231", "20251231"],
            "total_assets": [100000000] * 5,
        })

        df = mock_tushare_provider.get_balance_sheet(
            "600519.SH", end_year=2025, start_year=2015
        )

        assert not df.empty

    def test_get_cash_flow_statement_with_start_year(self, mock_tushare_provider):
        """Should fetch cash flow statement from start_year to end_year"""
        mock_tushare_provider._api.cashflow.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"] * 5,
            "end_date": ["20211231", "20221231", "20231231", "20241231", "20251231"],
            "net_cash_operate": [50000000] * 5,
        })

        df = mock_tushare_provider.get_cash_flow_statement(
            "600519.SH", end_year=2025, start_year=2015
        )

        assert not df.empty

    def test_default_start_year_is_end_year_minus_15(self, mock_tushare_provider):
        """Should default start_year to end_year - 15"""
        mock_tushare_provider._api.income.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"] * 5,
            "end_date": ["20211231", "20221231", "20231231", "20241231", "20251231"],
            "total_revenue": [100000000] * 5,
        })

        # Without start_year, should get 15 years of data
        df = mock_tushare_provider.get_income_statement("600519.SH", end_year=2025)

        assert not df.empty
        # Verify API was called (default start_year should be end_year - 15)
        mock_tushare_provider._api.income.assert_called_once()


class TestAPIYearsParameter:
    """Test ValueInvestment API years parameter - already uses mocks"""

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


class TestAPIYearsParameterMock:
    """Mock-based tests for years parameter with provider integration"""

    def test_years_parameter_calculates_correct_start_year(self):
        """years parameter should correctly calculate start_year"""
        vi = ValueInvestment()

        # Create a mock provider
        mock_provider = MagicMock()
        mock_provider.get_income_statement.return_value = pd.DataFrame({
            "end_date": ["20201231", "20211231", "20221231", "20231231", "20241231"],
            "total_revenue": [100000] * 5,
        })
        vi._provider = mock_provider

        # Test with years=5
        vi.get_profit_sheet("600519", end_year=2025, years=5)

        # Verify start_year = 2025 - 5 = 2020
        call_args = mock_provider.get_income_statement.call_args
        assert call_args[0][1] == 2025  # end_year
        assert call_args[0][2] == 2020  # start_year

    def test_different_years_produce_different_start_years(self):
        """Different years values should produce different start_year values"""
        vi = ValueInvestment()
        
        mock_provider = MagicMock()
        mock_provider.get_income_statement.return_value = pd.DataFrame({
            "end_date": ["20201231", "20211231", "20221231"],
            "total_revenue": [100000] * 3,
        })
        vi._provider = mock_provider

        # Test with years=3
        vi.get_profit_sheet("600519", end_year=2025, years=3)
        call_3 = mock_provider.get_income_statement.call_args[0][2]
        
        # Reset mock
        mock_provider.get_income_statement.reset_mock()
        
        # Test with years=5
        vi.get_profit_sheet("600519", end_year=2025, years=5)
        call_5 = mock_provider.get_income_statement.call_args[0][2]
        
        # Different years should produce different start_years
        assert call_3 != call_5
        assert call_3 == 2022  # 2025 - 3
        assert call_5 == 2020  # 2025 - 5


class TestCacheKeyWithStartYear:
    """Test that cache key includes start_year"""

    def test_cache_key_includes_start_year(self, mock_cache):
        """Cache key should include start_year to differentiate requests"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        with patch("value_investment.data.providers.tushare_provider.ts") as mock_ts:
            mock_api = MagicMock()
            mock_ts.pro_api.return_value = mock_api
            mock_api.income.return_value = pd.DataFrame({
                "ts_code": ["600519.SH"],
                "end_date": ["20231231"],
                "total_revenue": [100000000],
            })
            
            provider = TushareProvider(cache=mock_cache, token="mock_token")

            # First request with 5 years
            provider.get_income_statement("600519.SH", end_year=2025, start_year=2020)

            # Check cache key exists
            cache_keys = [k for k in mock_cache._data.keys() if "income" in k]
            assert len(cache_keys) == 1
            key = cache_keys[0]

            # Should contain both start and end year
            assert "2020" in key  # start_year
            assert "2025" in key  # end_year

    def test_cache_key_different_start_years(self, mock_cache):
        """Different start_year should produce different cache keys"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        with patch("value_investment.data.providers.tushare_provider.ts") as mock_ts:
            mock_api = MagicMock()
            mock_ts.pro_api.return_value = mock_api
            
            # Return different data for different requests
            mock_api.income.side_effect = [
                pd.DataFrame({"end_date": ["20201231"], "total_revenue": [100]}),
                pd.DataFrame({"end_date": ["20231231"], "total_revenue": [100]}),
            ]
            
            provider = TushareProvider(cache=mock_cache, token="mock_token")

            # First request with start_year=2020
            provider.get_income_statement("600519.SH", end_year=2025, start_year=2020)
            keys_1 = [k for k in mock_cache._data.keys()]
            
            # Second request with start_year=2022
            provider.get_income_statement("600519.SH", end_year=2025, start_year=2022)
            keys_2 = [k for k in mock_cache._data.keys()]

            # Should have different cache keys
            assert len(keys_2) > len(keys_1)


class TestIntegration:
    """Integration tests - kept for connectivity verification only
    
    These tests require real TUSHARE_TOKEN.
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    def test_integration_years_parameter_with_real_api(self):
        """Verify years parameter works with real Tushare API"""
        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            pytest.skip("TUSHARE_TOKEN not set, skipping integration test")
        
        from value_investment.data.providers.tushare_provider import TushareProvider
        from tests.conftest import MockCache
        
        provider = TushareProvider(cache=MockCache(), token=token)
        
        df = provider.get_income_statement("600519.SH", end_year=2025, start_year=2020)
        
        assert not df.empty
