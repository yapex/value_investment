"""Tests for CLI fields filter feature"""
import os
import pytest
from typer.testing import CliRunner
from value_investment.cli import app

runner = CliRunner()

# Set TUSHARE_TOKEN for tests
os.environ["TUSHARE_TOKEN"] = "test_token"


def test_income_with_single_field():
    """测试 income 命令只返回指定字段（使用标准字段名）"""
    result = runner.invoke(app, ["income", "600519", "--fields", "net_profit"])
    assert result.exit_code == 0
    # 验证返回结果包含 net_profit
    assert "net_profit" in result.stdout


def test_income_with_multiple_fields():
    """测试 income 命令返回多个指定字段"""
    result = runner.invoke(app, ["income", "600519", "--fields", "report_date,net_profit"])
    assert result.exit_code == 0
    assert "report_date" in result.stdout
    assert "net_profit" in result.stdout


def test_income_with_invalid_field():
    """测试不存在的字段返回错误"""
    result = runner.invoke(app, ["income", "600519", "--fields", "not_exist_field"])
    assert result.exit_code != 0
    # 错误信息输出到 stderr
    assert "not_exist_field" in result.stdout or "not_exist_field" in result.stderr


def test_balance_with_fields():
    """测试 balance 命令返回指定字段"""
    result = runner.invoke(app, ["balance", "600519", "--fields", "total_assets"])
    assert result.exit_code == 0
    assert "total_assets" in result.stdout


def test_cashflow_with_fields():
    """测试 cashflow 命令返回指定字段"""
    result = runner.invoke(app, ["cashflow", "600519", "--fields", "operating_cash_flow"])
    assert result.exit_code == 0
    assert "operating_cash_flow" in result.stdout
