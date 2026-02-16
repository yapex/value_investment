"""API validation tests - Phase 0"""
import pytest
import pandas as pd


class TestAkshareAPIs:
    """Test akshare API responses to understand actual field names"""

    def test_stock_individual_info_em_fields(self):
        """验证个股信息接口返回字段"""
        import akshare as ak

        df = ak.stock_individual_info_em(symbol="600519")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "Should return data"

        # 打印实际字段名
        print("\n=== stock_individual_info_em ===")
        print(f"Columns: {list(df.columns)}")
        print(df.head())

    def test_stock_zh_a_hist_fields(self):
        """验证历史行情接口返回字段"""
        import akshare as ak

        df = ak.stock_zh_a_hist(
            symbol="600519",
            period="daily",
            start_date="20240101",
            end_date="20240131",
            adjust=""
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "Should return data"

        print("\n=== stock_zh_a_hist ===")
        print(f"Columns: {list(df.columns)}")
        print(df.head())

    def test_balance_sheet_fields(self):
        """验证资产负债表接口返回字段"""
        import akshare as ak

        df = ak.stock_balance_sheet_by_yearly_em(symbol="SH600519")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "Should return data"

        print("\n=== stock_balance_sheet_by_yearly_em ===")
        print(f"Columns: {list(df.columns)[:20]}")  # 前20个
        print(f"Total columns: {len(df.columns)}")
        print(df.head())

    def test_profit_sheet_fields(self):
        """验证利润表接口返回字段"""
        import akshare as ak

        df = ak.stock_profit_sheet_by_yearly_em(symbol="SH600519")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "Should return data"

        print("\n=== stock_profit_sheet_by_yearly_em ===")
        print(f"Columns: {list(df.columns)[:20]}")  # 前20个
        print(f"Total columns: {len(df.columns)}")
        print(df.head())

    def test_cashflow_sheet_fields(self):
        """验证现金流量表接口返回字段"""
        import akshare as ak

        df = ak.stock_cash_flow_sheet_by_yearly_em(symbol="SH600519")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0, "Should return data"

        print("\n=== stock_cash_flow_sheet_by_yearly_em ===")
        print(f"Columns: {list(df.columns)[:20]}")  # 前20个
        print(f"Total columns: {len(df.columns)}")
        print(df.head())
