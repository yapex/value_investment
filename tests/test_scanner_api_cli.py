"""测试 Scanner Scan API 和 CLI"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd


class TestScannerScanAPI:
    """Scanner scan 方法测试"""

    def test_parse_filter_returns_filterbuilder(self):
        """测试 parse_filter 返回 FilterBuilder"""
        from value_investment.scanner import parse_filter

        fb = parse_filter("ROE 连续5年 ≥15%")
        assert fb is not None
        assert len(fb) == 1

    def test_parse_filter_multiple_conditions(self):
        """测试多条件 AND"""
        from value_investment.scanner import parse_filter

        fb = parse_filter("ROE 连续5年 ≥15% 且 毛利率 连续5年 ≥30%")
        assert len(fb) == 2


class TestCLIScan:
    """CLI scan 命令测试"""

    def test_scan_command_help(self):
        """测试 scan 命令 --help"""
        from typer.testing import CliRunner
        from value_investment.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["scan", "--help"])
        
        assert result.exit_code == 0
        assert "filter" in result.stdout.lower()

    def test_scan_command_requires_filter(self):
        """测试 scan 命令必须提供 filter 参数"""
        from typer.testing import CliRunner
        from value_investment.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["scan"])
        
        # 没有 --filter 应该失败
        assert result.exit_code != 0
