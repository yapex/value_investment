"""Tests for CLI fields filter feature"""
import pytest
from typer.testing import CliRunner
from value_investment.cli import app

runner = CliRunner()


def test_income_with_single_field():
    """测试 income 命令只返回指定字段"""
    result = runner.invoke(app, ["income", "600519", "--fields", "NETPROFIT"])
    assert result.exit_code == 0
    # 验证返回结果包含 NETPROFIT
    assert "NETPROFIT" in result.stdout


def test_income_with_multiple_fields():
    """测试 income 命令返回多个指定字段"""
    result = runner.invoke(app, ["income", "600519", "--fields", "REPORT_DATE,NETPROFIT"])
    assert result.exit_code == 0
    assert "REPORT_DATE" in result.stdout
    assert "NETPROFIT" in result.stdout


def test_income_with_invalid_field():
    """测试不存在的字段返回错误"""
    result = runner.invoke(app, ["income", "600519", "--fields", "not_exist_field"])
    assert result.exit_code != 0
    # 错误信息输出到 stderr
    assert "not_exist_field" in result.stdout or "not_exist_field" in result.stderr


def test_balance_with_fields():
    """测试 balance 命令返回指定字段"""
    result = runner.invoke(app, ["balance", "600519", "--fields", "TOTAL_ASSETS"])
    assert result.exit_code == 0
    assert "TOTAL_ASSETS" in result.stdout


def test_cashflow_with_fields():
    """测试 cashflow 命令返回指定字段"""
    result = runner.invoke(app, ["cashflow", "600519", "--fields", "NETCASH_OPERATE"])
    assert result.exit_code == 0
    assert "NETCASH_OPERATE" in result.stdout
