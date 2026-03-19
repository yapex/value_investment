"""Tests for new CLI design with PipelineAPI"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from typer.testing import CliRunner

from value_investment.cli import app

runner = CliRunner()


class TestQueryCommand:
    """Test query command using PipelineAPI"""

    def test_query_requires_symbol(self):
        """query command should require symbol argument"""
        result = runner.invoke(app, ["query"])
        assert result.exit_code != 0

    def test_query_requires_fields(self):
        """query command should require --requires/-r option"""
        result = runner.invoke(app, ["query", "600519"])
        assert result.exit_code != 0

    def test_query_basic(self):
        """query command should fetch data using PipelineAPI"""
        # Test that command accepts valid arguments and calls PipelineAPI
        # Mock at the module level where it's imported
        with patch("value_investment.cli.PipelineAPI") as MockPipelineAPI:
            mock_instance = MagicMock()
            mock_instance.get_data = AsyncMock(return_value={
                "roe": {2024: 0.32, 2023: 0.30},
            })
            MockPipelineAPI.return_value = mock_instance

            result = runner.invoke(app, ["query", "600519", "-r", "roe,net_profit"])
            assert result.exit_code == 0
            assert "roe" in result.stdout

    def test_query_with_years_option(self):
        """query command should accept -y/--years option"""
        result = runner.invoke(app, ["query", "600519", "-r", "roe", "-y", "5"])
        # Should not fail on argument parsing
        # May fail on actual API call, but argument parsing should pass
        assert result.exit_code in [0, 1]

    def test_query_with_end_option(self):
        """query command should accept --end option"""
        result = runner.invoke(app, ["query", "600519", "-r", "roe", "--end", "20231231"])
        assert result.exit_code in [0, 1]

    def test_query_output_format_json(self):
        """query command should support --format json"""
        with patch("value_investment.cli.PipelineAPI") as MockPipelineAPI:
            mock_instance = MagicMock()
            mock_instance.get_data = AsyncMock(return_value={"roe": {2024: 0.32}})
            MockPipelineAPI.return_value = mock_instance

            result = runner.invoke(app, ["query", "600519", "-r", "roe", "-f", "json"])
            assert result.exit_code == 0
            # JSON output should have "roe" as a key
            assert '"roe"' in result.stdout

    def test_query_output_format_plain(self):
        """query command should support --format plain"""
        with patch("value_investment.cli.PipelineAPI") as MockPipelineAPI:
            mock_instance = MagicMock()
            mock_instance.get_data = AsyncMock(return_value={"roe": {2024: 0.32}})
            MockPipelineAPI.return_value = mock_instance

            result = runner.invoke(app, ["query", "600519", "-r", "roe", "-f", "plain"])
            assert result.exit_code == 0
            # Plain format should have tab-separated values
            assert "\t" in result.stdout

    def test_query_auto_detect_a_stock(self):
        """query command should auto-detect A股 market (6-digit starting with 0/3/6)"""
        with patch("value_investment.cli.PipelineAPI") as MockPipelineAPI:
            mock_instance = MagicMock()
            mock_instance.get_data = AsyncMock(return_value={"roe": {2024: 0.32}})
            MockPipelineAPI.return_value = mock_instance

            result = runner.invoke(app, ["query", "600519", "-r", "roe"])
            # Should succeed (market auto-detected as A股)
            assert result.exit_code == 0

    def test_query_auto_detect_hk_stock(self):
        """query command should auto-detect 港股 market (5-digit)"""
        with patch("value_investment.cli.PipelineAPI") as MockPipelineAPI:
            mock_instance = MagicMock()
            mock_instance.get_data = AsyncMock(return_value={"roe": {2024: 0.32}})
            MockPipelineAPI.return_value = mock_instance

            result = runner.invoke(app, ["query", "00700", "-r", "roe"])
            # Should succeed (market auto-detected as 港股)
            assert result.exit_code == 0

    def test_query_auto_detect_us_stock(self):
        """query command should auto-detect 美股 market (letters)"""
        with patch("value_investment.cli.PipelineAPI") as MockPipelineAPI:
            mock_instance = MagicMock()
            mock_instance.get_data = AsyncMock(return_value={"roe": {2024: 0.32}})
            MockPipelineAPI.return_value = mock_instance

            result = runner.invoke(app, ["query", "AAPL", "-r", "roe"])
            # Should succeed (market auto-detected as 美股)
            assert result.exit_code == 0

    def test_query_with_market_override(self):
        """query command should allow --market override"""
        with patch("value_investment.cli.PipelineAPI") as MockPipelineAPI:
            mock_instance = MagicMock()
            mock_instance.get_data = AsyncMock(return_value={"roe": {2024: 0.32}})
            MockPipelineAPI.return_value = mock_instance

            result = runner.invoke(app, ["query", "600519", "-r", "roe", "--market", "港股"])
            # Should accept market override
            assert result.exit_code == 0


class TestFieldsCommand:
    """Test fields command for listing available fields"""

    def test_fields_list_all(self):
        """fields command should list all available fields"""
        result = runner.invoke(app, ["fields"])
        assert result.exit_code == 0

        fields = result.stdout.strip().split("\n")
        assert "roe" in fields
        assert "net_profit" in fields
        assert "total_assets" in fields

    def test_fields_filter_by_prefix(self):
        """fields command should filter fields by prefix"""
        result = runner.invoke(app, ["fields", "--prefix", "ro"])
        assert result.exit_code == 0

        fields = result.stdout.strip().split("\n")
        assert all(f.startswith("ro") for f in fields if f)

    def test_fields_filter_by_total_prefix(self):
        """fields command should filter fields by 'total' prefix"""
        result = runner.invoke(app, ["fields", "-p", "total"])
        assert result.exit_code == 0

        fields = result.stdout.strip().split("\n")
        assert all(f.startswith("total") for f in fields if f)


class TestCacheCommands:
    """Test cache-related commands"""

    def test_cache_clear_all(self):
        """cache-clear should clear all cache"""
        result = runner.invoke(app, ["cache-clear"])
        assert result.exit_code == 0
        assert "cache" in result.stdout.lower()

    def test_cache_clear_symbol(self):
        """cache-clear with symbol should clear specific stock cache"""
        result = runner.invoke(app, ["cache-clear", "600519"])
        assert result.exit_code == 0
        # Should indicate what was cleared
        assert "600519" in result.stdout or "cache" in result.stdout.lower()

    def test_cache_stats(self):
        """cache-stats should show cache statistics"""
        result = runner.invoke(app, ["cache-stats"])
        assert result.exit_code == 0
        assert "memory" in result.stdout.lower() or "disk" in result.stdout.lower() or "entries" in result.stdout.lower()

    def test_cache_list(self):
        """cache-list should list cached items"""
        result = runner.invoke(app, ["cache-list"])
        # May be empty but should not error
        assert result.exit_code == 0

    def test_cache_list_with_symbol_filter(self):
        """cache-list with symbol should filter by stock code"""
        result = runner.invoke(app, ["cache-list", "600519"])
        assert result.exit_code == 0


class TestInfoCommand:
    """Test info command for stock basic information"""

    def test_info_requires_symbol(self):
        """info command should require symbol"""
        result = runner.invoke(app, ["info"])
        assert result.exit_code != 0

    def test_info_with_symbol(self):
        """info command should accept symbol argument"""
        result = runner.invoke(app, ["info", "600519"])
        # May fail due to API call but should not have argument errors
        assert result.exit_code in [0, 1]

    def test_info_with_format(self):
        """info command should support --format option"""
        result = runner.invoke(app, ["info", "600519", "-f", "json"])
        # Should accept format option
        assert result.exit_code in [0, 1]


class TestHistCommand:
    """Test hist command for historical prices"""

    def test_hist_requires_symbol(self):
        """hist command should require symbol"""
        result = runner.invoke(app, ["hist"])
        assert result.exit_code != 0

    def test_hist_with_defaults(self):
        """hist command should work with just symbol"""
        result = runner.invoke(app, ["hist", "600519"])
        # May fail due to API call but should not have argument errors
        assert result.exit_code in [0, 1]

    def test_hist_with_date_range(self):
        """hist command should support start and end dates"""
        result = runner.invoke(app, [
            "hist", "600519",
            "--start", "20230101",
            "--end", "20231231"
        ])
        assert result.exit_code in [0, 1]

    def test_hist_with_format(self):
        """hist command should support --format option"""
        result = runner.invoke(app, ["hist", "600519", "-f", "json"])
        assert result.exit_code in [0, 1]
