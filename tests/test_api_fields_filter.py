"""Tests for API layer field filtering and date formatting"""
import pytest
from value_investment.api import ValueInvestment


class TestFinancialSheetFields:
    """测试财务报表字段筛选功能"""

    def test_get_profit_sheet_with_fields(self):
        """测试利润表支持 fields 参数"""
        vi = ValueInvestment(market="A")
        df = vi.get_profit_sheet("600519", end_year=2024, fields=["NETPROFIT"])
        assert "NETPROFIT" in df.columns
        assert "REPORT_DATE" in df.columns  # 应该自动包含

    def test_get_profit_sheet_fields_auto_include_date(self):
        """测试 fields 参数自动包含 REPORT_DATE"""
        vi = ValueInvestment(market="A")
        df = vi.get_profit_sheet("600519", end_year=2024, fields=["NETPROFIT"])
        assert not df.empty
        # 验证日期格式为 YYYY-MM-DD
        assert df["REPORT_DATE"].iloc[0] == "2024-12-31"

    def test_get_balance_sheet_with_fields(self):
        """测试资产负债表支持 fields 参数"""
        vi = ValueInvestment(market="A")
        df = vi.get_balance_sheet("600519", end_year=2024, fields=["TOTAL_ASSETS"])
        assert "TOTAL_ASSETS" in df.columns
        assert "REPORT_DATE" in df.columns

    def test_get_balance_sheet_fields_date_format(self):
        """测试资产负债表日期格式"""
        vi = ValueInvestment(market="A")
        df = vi.get_balance_sheet("600519", end_year=2024, fields=["TOTAL_ASSETS"])
        assert df["REPORT_DATE"].iloc[0] == "2024-12-31"

    def test_get_cashflow_sheet_with_fields(self):
        """测试现金流量表支持 fields 参数"""
        vi = ValueInvestment(market="A")
        df = vi.get_cashflow_sheet("600519", end_year=2024, fields=["NETCASH_OPERATE"])
        assert "NETCASH_OPERATE" in df.columns
        assert "REPORT_DATE" in df.columns

    def test_get_cashflow_sheet_fields_date_format(self):
        """测试现金流量表日期格式"""
        vi = ValueInvestment(market="A")
        df = vi.get_cashflow_sheet("600519", end_year=2024, fields=["NETCASH_OPERATE"])
        assert df["REPORT_DATE"].iloc[0] == "2024-12-31"

    def test_get_profit_sheet_without_fields(self):
        """测试不传 fields 参数返回所有字段"""
        vi = ValueInvestment(market="A")
        df = vi.get_profit_sheet("600519", end_year=2024)
        assert "NETPROFIT" in df.columns
        assert "REPORT_DATE" in df.columns
