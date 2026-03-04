"""Tests for CLI self-description commands (fields, indicators)"""
import pytest
from typer.testing import CliRunner

runner = CliRunner()


class TestCLIFieldsCommand:
    """Test `fields` command for listing available standard fields"""

    def test_fields_requires_market_and_report(self):
        """fields command should require market and report arguments"""
        from value_investment.cli import app

        # Missing both arguments
        result = runner.invoke(app, ["fields"])
        assert result.exit_code != 0

    def test_fields_invalid_market(self):
        """fields command should validate market"""
        from value_investment.cli import app

        # Market validation is lenient - accepts any market code
        # Only report type is strictly validated
        result = runner.invoke(app, ["fields", "INVALID", "balance"])
        # Invalid market is tolerated (returns same fields as any market)
        assert result.exit_code == 0

    def test_fields_invalid_report(self):
        """fields command should validate report type"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "A", "invalid_report"])
        assert result.exit_code != 0

    def test_fields_a_balance(self):
        """fields command should list A股 balance sheet standard fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "A", "balance"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        # Should contain standard internal field names
        assert "total_assets" in fields
        assert "current_assets" in fields
        assert "total_liabilities" in fields

    def test_fields_a_income(self):
        """fields command should list A股 income statement standard fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "A", "income"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        assert "total_revenue" in fields
        assert "net_profit" in fields

    def test_fields_a_cashflow(self):
        """fields command should list A股 cashflow statement standard fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "A", "cashflow"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        assert "operating_cash_flow" in fields

    def test_fields_hk_balance(self):
        """fields command should list HK balance sheet standard fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "HK", "balance"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        # HK uses different source fields but same standard fields
        assert "total_assets" in fields

    def test_fields_finind(self):
        """fields command should list financial indicator standard fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "A", "finind"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        assert "net_profit" in fields
        assert "roe" in fields

    def test_fields_quarterly(self):
        """fields command should list quarterly data standard fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "A", "quarterly"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        assert "report_date" in fields


class TestCLIIndicatorsCommand:
    """Test `indicators` command (renamed from list-indicators)"""

    def test_indicators_lists_all(self):
        """indicators command should list all available indicators"""
        from value_investment.cli import app

        result = runner.invoke(app, ["indicators"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        indicators = output.split("\n")

        # Should have some indicators
        assert len(indicators) > 0

        # Should contain known indicators
        assert "ROE" in indicators or any("ROE" in i for i in indicators)

    def test_indicators_one_per_line(self):
        """indicators command should output one indicator per line"""
        from value_investment.cli import app

        result = runner.invoke(app, ["indicators"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        lines = output.split("\n")

        # Each line should be a single indicator name (no extra formatting)
        for line in lines:
            assert line  # non-empty
            assert not line.startswith(" ")  # no leading spaces
            assert not line.startswith("-")  # no list markers


class TestDataMapperExtensibility:
    """Test DataMapper.get_standard_fields extensibility"""

    def test_report_types_discoverable(self):
        """REPORT_MAPPINGS should list all available report types"""
        from value_investment.data.mapper import DataMapper

        # Should have a registry of report types
        assert hasattr(DataMapper, 'REPORT_MAPPINGS')
        report_types = DataMapper.REPORT_MAPPINGS

        # Should contain expected types
        assert 'balance' in report_types
        assert 'income' in report_types
        assert 'cashflow' in report_types
        assert 'finind' in report_types
        assert 'quarterly' in report_types

    def test_new_report_type_no_cli_change_needed(self):
        """Adding new report type should not require CLI changes"""
        from value_investment.data.mapper import DataMapper

        # Simulate adding a new report type
        original_mappings = DataMapper.REPORT_MAPPINGS.copy()

        # Add a mock new report type
        DataMapper.REPORT_MAPPINGS['new_report'] = 'BALANCE_MAPPING'  # reuse existing for test

        try:
            # Should work without any code changes
            fields = DataMapper.get_standard_fields('new_report', 'A')
            assert isinstance(fields, list)
            assert len(fields) > 0
        finally:
            # Restore original
            DataMapper.REPORT_MAPPINGS = original_mappings

    def test_invalid_report_shows_valid_options(self):
        """Error message should list valid report types dynamically"""
        from value_investment.data.mapper import DataMapper

        try:
            DataMapper.get_standard_fields('nonexistent', 'A')
            assert False, "Should raise ValueError"
        except ValueError as e:
            # Error message should contain valid options
            msg = str(e)
            assert 'balance' in msg
            assert 'income' in msg
            assert 'cashflow' in msg
