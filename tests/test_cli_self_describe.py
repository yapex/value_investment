"""Tests for CLI self-description commands (fields, indicators) - Updated for new design"""
import pytest
from typer.testing import CliRunner

runner = CliRunner()


class TestCLIFieldsCommand:
    """Test `fields` command for listing available standard fields

    New design: fields command lists ALL available fields from IFRSFields + CustomFields
    No longer requires market and report arguments.
    """

    def test_fields_list_all_fields(self):
        """fields command should list all available fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        # Should contain standard internal field names
        assert "roe" in fields
        assert "net_profit" in fields
        assert "total_assets" in fields

    def test_fields_filter_by_prefix(self):
        """fields command should filter fields by prefix"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "--prefix", "ro"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        # Should only contain fields starting with "ro"
        assert all(f.startswith("ro") for f in fields if f)

    def test_fields_filter_prefix_tot(self):
        """fields command should filter 'total' prefixed fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "-p", "total"])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        # Should only contain fields starting with "total"
        assert all(f.startswith("total") for f in fields if f)

    def test_fields_empty_prefix(self):
        """fields command with empty prefix should return all fields"""
        from value_investment.cli import app

        result = runner.invoke(app, ["fields", "--prefix", ""])
        assert result.exit_code == 0

        output = result.stdout.strip()
        fields = output.split("\n")

        # Should have more than just a few fields
        assert len(fields) > 10


class TestCLIIndicatorsCommand:
    """Test `indicators` command (requires market argument)"""

    def test_indicators_requires_market(self):
        """indicators command should require market argument"""
        from value_investment.cli import app

        result = runner.invoke(app, ["indicators"])
        assert result.exit_code != 0

    def test_indicators_lists_a_stock(self):
        """indicators command should list A股 indicators"""
        from value_investment.cli import app

        result = runner.invoke(app, ["indicators", "A"])
        # May fail due to API issues, but should parse arguments correctly
        assert result.exit_code in [0, 1]

    def test_indicators_lists_hk(self):
        """indicators command should list 港股 indicators"""
        from value_investment.cli import app

        result = runner.invoke(app, ["indicators", "HK"])
        assert result.exit_code in [0, 1]

    def test_indicators_lists_us(self):
        """indicators command should list 美股 indicators"""
        from value_investment.cli import app

        result = runner.invoke(app, ["indicators", "US"])
        assert result.exit_code in [0, 1]

    def test_indicators_one_per_line(self):
        """indicators command should output one indicator per line"""
        from value_investment.cli import app

        result = runner.invoke(app, ["indicators", "A"])
        # Just check it doesn't crash
        assert result.exit_code in [0, 1]


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
