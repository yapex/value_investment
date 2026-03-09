"""Tests for API layer field filtering and date formatting"""
import pytest
import re
from value_investment.api import ValueInvestment


class TestFinancialSheetFields:
    """测试财务报表字段筛选功能
    
    注意：字段名使用 IFRS 标准字段名（小写），因为 Provider 已应用字段映射
    """

    def test_get_profit_sheet_with_fields(self):
        """测试利润表支持 fields 参数"""
        vi = ValueInvestment(market="A")
        df = vi.get_profit_sheet("600519", end_year=2024, fields=["net_profit"])
        assert "net_profit" in df.columns
        assert "report_date" in df.columns  # 应该自动包含

    def test_get_profit_sheet_fields_auto_include_date(self):
        """测试 fields 参数自动包含 report_date"""
        vi = ValueInvestment(market="A")
        df = vi.get_profit_sheet("600519", end_year=2024, fields=["net_profit"])
        assert not df.empty
        # 验证日期格式为 YYYY-MM-DD
        assert re.match(r'\d{4}-\d{2}-\d{2}', df["report_date"].iloc[0])

    def test_get_balance_sheet_with_fields(self):
        """测试资产负债表支持 fields 参数"""
        vi = ValueInvestment(market="A")
        df = vi.get_balance_sheet("600519", end_year=2024, fields=["total_assets"])
        assert "total_assets" in df.columns
        assert "report_date" in df.columns

    def test_get_balance_sheet_fields_date_format(self):
        """测试资产负债表日期格式"""
        vi = ValueInvestment(market="A")
        df = vi.get_balance_sheet("600519", end_year=2024, fields=["total_assets"])
        assert re.match(r'\d{4}-\d{2}-\d{2}', df["report_date"].iloc[0])

    def test_get_cashflow_sheet_with_fields(self):
        """测试现金流量表支持 fields 参数"""
        vi = ValueInvestment(market="A")
        df = vi.get_cashflow_sheet("600519", end_year=2024, fields=["operating_cash_flow"])
        assert "operating_cash_flow" in df.columns
        assert "report_date" in df.columns

    def test_get_cashflow_sheet_fields_date_format(self):
        """测试现金流量表日期格式"""
        vi = ValueInvestment(market="A")
        df = vi.get_cashflow_sheet("600519", end_year=2024, fields=["operating_cash_flow"])
        assert re.match(r'\d{4}-\d{2}-\d{2}', df["report_date"].iloc[0])

    def test_get_profit_sheet_without_fields(self):
        """测试不传 fields 参数返回所有字段"""
        vi = ValueInvestment(market="A")
        df = vi.get_profit_sheet("600519", end_year=2024)
        assert "net_profit" in df.columns
        assert "report_date" in df.columns
