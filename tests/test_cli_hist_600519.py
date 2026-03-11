"""测试CLI hist命令对600519的兼容性

这些测试使用 mock 来避免依赖真实的 TUSHARE_TOKEN。
"""
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from value_investment.api import ValueInvestment


class TestHistoricalDataColumns:
    """Test historical data output columns"""

    def test_hist_command_with_600519(self):
        """测试hist命令能否正确获取600519的历史数据"""
        vi = ValueInvestment(market="A")
        
        # Mock the market_provider's get_historical_data method (historical data uses market_provider)
        vi._market_provider.get_historical_data = MagicMock(
            return_value=pd.DataFrame({
                "ts_code": ["600519.SH"] * 5,
                "trade_date": ["20240101", "20240102", "20240103", "20240104", "20240105"],
                "open": [1700.0, 1710.0, 1720.0, 1715.0, 1725.0],
                "high": [1710.0, 1720.0, 1730.0, 1725.0, 1735.0],
                "low": [1690.0, 1700.0, 1710.0, 1705.0, 1715.0],
                "close": [1705.0, 1715.0, 1725.0, 1720.0, 1730.0],
                "vol": [1000000, 1100000, 1050000, 1080000, 1120000],
            })
        )
        
        # 获取600519最近1年的历史数据
        df = vi.get_historical_data("600519", end_date="20241231", start_date="20240101")
        
        # 验证返回的数据
        assert df is not None, "应该返回数据"
        assert not df.empty, "数据不应为空"
        assert len(df) > 0, "应该有历史记录"
        
        # 验证必要的列存在
        required_columns = ["trade_date", "open", "high", "low", "close"]
        for col in required_columns:
            assert col in df.columns or col.upper() in df.columns, f"缺少列: {col}"

        # 验证成交量列存在（可能是vol或volume）
        assert "vol" in df.columns or "volume" in df.columns, "应该有成交量列"

    def test_hist_command_returns_correct_columns(self):
        """测试hist命令返回正确的列"""
        vi = ValueInvestment(market="A")
        
        # Create mock DataFrame with data
        mock_df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "trade_date": ["20240101"],
            "open": [1700.0],
            "high": [1710.0],
            "low": [1690.0],
            "close": [1705.0],
            "vol": [1000000],
        })
        
        # Replace the market_provider with a mock (historical data uses market_provider)
        vi._market_provider = MagicMock()
        vi._market_provider.get_historical_data.return_value = mock_df
        
        df = vi.get_historical_data("600519", end_date="20240101", start_date="20240101")
        
        # 验证基本列
        assert "close" in df.columns
        assert "open" in df.columns
        assert "high" in df.columns
        assert "low" in df.columns


class TestBalanceSheetColumns:
    """Test balance sheet output columns"""

    def test_balance_sheet_has_column_names(self):
        """测试资产负债表输出是否有列名"""
        vi = ValueInvestment(market="A")
        
        vi._provider.get_balance_sheet = MagicMock(
            return_value=pd.DataFrame({
                "ts_code": ["600519.SH"],
                "end_date": ["20241231"],
                "total_assets": [250000000000],
                "total_liab": [80000000000],
            })
        )
        
        df = vi.get_balance_sheet("600519", end_year=2024)
        
        assert df is not None, "应该返回数据"
        assert not df.empty, "数据不应为空"
        
        assert len(df.columns) > 0, "应该有列名"
        assert all(df.columns.notna()), "列名不应为空"
        
        assert "report_date" in df.columns or "end_date" in df.columns or "ann_date" in df.columns, "应该有日期列"


class TestIncomeStatementColumns:
    """Test income statement output columns"""

    def test_income_statement_has_column_names(self):
        """测试利润表输出是否有列名"""
        vi = ValueInvestment(market="A")
        
        vi._provider.get_income_statement = MagicMock(
            return_value=pd.DataFrame({
                "ts_code": ["600519.SH"],
                "end_date": ["20241231"],
                "total_revenue": [150000000000],
                "net_profit": [70000000000],
            })
        )
        
        df = vi.get_profit_sheet("600519", end_year=2024)
        
        # 验证返回的数据
        assert df is not None, "应该返回数据"
        assert not df.empty, "数据不应为空"
        
        # 验证有列名
        assert len(df.columns) > 0, "应该有列名"


class TestCashFlowColumns:
    """Test cash flow output columns"""

    def test_cashflow_has_column_names(self):
        """测试现金流量表输出是否有列名"""
        vi = ValueInvestment(market="A")
        
        vi._provider.get_cash_flow_statement = MagicMock(
            return_value=pd.DataFrame({
                "ts_code": ["600519.SH"],
                "end_date": ["20241231"],
                "net_cash_operate": [60000000000],
                "net_cash_invest": [-20000000000],
            })
        )
        
        df = vi.get_cashflow_sheet("600519", end_year=2024)
        
        assert df is not None, "应该返回数据"
        assert not df.empty, "数据不应为空"
        
        assert len(df.columns) > 0, "应该有列名"


class TestIntegration:
    """Integration tests - kept for connectivity verification only
    
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    def test_integration_historical_data(self):
        """验证与真实 Tushare API 的连接"""
        import os
        
        if not os.getenv("TUSHARE_TOKEN"):
            pytest.skip("TUSHARE_TOKEN not set, skipping integration test")
        
        vi = ValueInvestment(market="A")
        
        df = vi.get_historical_data("600519", end_date="20240131", start_date="20240101")
        
        assert df is not None
        assert not df.empty
        assert "close" in df.columns

    @pytest.mark.integration
    def test_integration_balance_sheet(self):
        """验证与真实 Tushare API 的连接"""
        import os
        
        if not os.getenv("TUSHARE_TOKEN"):
            pytest.skip("TUSHARE_TOKEN not set, skipping integration test")
        
        vi = ValueInvestment(market="A")
        
        df = vi.get_balance_sheet("600519", end_year=2024)
        
        assert df is not None
        assert not df.empty
