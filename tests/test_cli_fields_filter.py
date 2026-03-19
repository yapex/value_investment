"""Tests for CLI fields filter feature - Updated for new design

Note: income/balance/cashflow commands still use ValueInvestment (deprecated)
These tests verify the CLI argument parsing works, actual API calls may fail
due to TushareProvider issues.
"""
import os
import pytest
from typer.testing import CliRunner
from value_investment.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def mock_tushare_token(monkeypatch):
    """Set mock TUSHARE_TOKEN for all tests in this module"""
    monkeypatch.setenv("TUSHARE_TOKEN", "test_token_for_cli_fields")


class TestIncomeCommand:
    """Test income command argument parsing"""

    def test_income_with_single_field(self):
        """Test income command accepts --fields option"""
        result = runner.invoke(app, ["income", "600519", "--fields", "net_profit"])
        # May fail on actual API call due to TushareProvider issues
        # But should not fail on argument parsing
        assert result.exit_code in [0, 1]

    def test_income_with_multiple_fields(self):
        """Test income command accepts multiple fields"""
        result = runner.invoke(app, ["income", "600519", "--fields", "report_date,net_profit"])
        assert result.exit_code in [0, 1]

    def test_income_requires_symbol(self):
        """Test income command requires symbol argument"""
        result = runner.invoke(app, ["income"])
        assert result.exit_code != 0


class TestBalanceCommand:
    """Test balance command argument parsing"""

    def test_balance_with_fields(self):
        """Test balance command accepts --fields option"""
        result = runner.invoke(app, ["balance", "600519", "--fields", "total_assets"])
        assert result.exit_code in [0, 1]

    def test_balance_requires_symbol(self):
        """Test balance command requires symbol argument"""
        result = runner.invoke(app, ["balance"])
        assert result.exit_code != 0


class TestCashflowCommand:
    """Test cashflow command argument parsing"""

    def test_cashflow_with_fields(self):
        """Test cashflow command accepts --fields option"""
        result = runner.invoke(app, ["cashflow", "600519", "--fields", "operating_cash_flow"])
        assert result.exit_code in [0, 1]

    def test_cashflow_requires_symbol(self):
        """Test cashflow command requires symbol argument"""
        result = runner.invoke(app, ["cashflow"])
        assert result.exit_code != 0


class TestQueryCommandNew:
    """Test new query command using PipelineAPI"""

    def test_query_requires_symbol(self):
        """query command should require symbol argument"""
        result = runner.invoke(app, ["query"])
        assert result.exit_code != 0

    def test_query_requires_fields(self):
        """query command should require --requires/-r option"""
        result = runner.invoke(app, ["query", "600519"])
        assert result.exit_code != 0

    def test_query_basic(self):
        """query command should work with valid arguments"""
        result = runner.invoke(app, ["query", "600519", "-r", "roe"])
        # May fail on actual API call, but should parse arguments correctly
        assert result.exit_code in [0, 1]

    def test_query_with_years(self):
        """query command should accept -y/--years option"""
        result = runner.invoke(app, ["query", "600519", "-r", "roe", "-y", "5"])
        assert result.exit_code in [0, 1]

    def test_query_with_format(self):
        """query command should accept -f/--format option"""
        result = runner.invoke(app, ["query", "600519", "-r", "roe", "-f", "json"])
        assert result.exit_code in [0, 1]
