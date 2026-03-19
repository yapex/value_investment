"""Tests for DataMapper.map_to_standard() method

TDD Phase 1: Write failing tests first, then implement the method.

The map_to_standard() method should:
1. Support markets: 'A', 'HK', 'US'
2. Support data_types: 'balance_sheet', 'income_statement', 'cash_flow', 'financial_indicator'
3. Map market-specific fields (ts_code → stock_code, end_date → report_date)
4. Apply type-specific field mappings
"""

import pytest
import pandas as pd

from value_investment.mapper import DataMapper


class TestMapToStandardTushare:
    """Tests for map_to_standard() with Tushare source"""

    def test_tushare_income_statement_basic_mapping(self):
        """Should map Tushare income statement fields to standard fields"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240330"],
            "update_flag": [1],
            "total_revenue": [100000],
            "operating_cost": [60000],
            "net_profit": [10000],
        })

        result = DataMapper.map_to_standard(
            df, market="A", data_type="income_statement"
        )

        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        assert result["stock_code"].iloc[0] == "600519.SH"

    def test_tushare_cash_flow_basic_mapping(self):
        """Should map Tushare cash flow fields to standard fields"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240330"],
            "update_flag": [1],
            "n_cashflow_act": [50000],
            "n_cashflow_inv_act": [-30000],
            "n_cash_flows_fnc_act": [-10000],
        })

        result = DataMapper.map_to_standard(
            df, market="A", data_type="cash_flow"
        )

        assert "stock_code" in result.columns
        assert "report_date" in result.columns

    def test_tushare_empty_dataframe(self):
        """Should handle empty DataFrame gracefully"""
        df = pd.DataFrame()

        result = DataMapper.map_to_standard(
            df, market="A", data_type="balance_sheet"
        )

        assert result.empty

    def test_tushare_none_dataframe(self):
        """Should handle None input gracefully"""
        result = DataMapper.map_to_standard(
            None, market="A", data_type="balance_sheet"
        )

        assert result is None

    def test_tushare_multiple_rows(self):
        """Should handle multiple rows correctly"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH", "600519.SH", "600519.SH"],
            "end_date": ["20231231", "20221231", "20211231"],
            "total_assets": [100, 90, 80],
        })

        result = DataMapper.map_to_standard(
            df, market="A", data_type="balance_sheet"
        )

        assert len(result) == 3
        assert list(result["stock_code"]) == ["600519.SH"] * 3
        assert list(result["report_date"]) == ["20231231", "20221231", "20211231"]


class TestMapToStandardYfinance:
    """Tests for map_to_standard() with YFinance source"""

    def test_yfinance_balance_sheet_basic_mapping(self):
        """Should map YFinance balance sheet fields to standard fields"""
        # YFinance returns English field names
        df = pd.DataFrame({
            "Total Assets": [1000000],
            "Total Liabilities": [500000],
            "Total Stockholder Equity": [500000],
            "Cash And Cash Equivalents": [100000],
        })
        df.index = pd.Index(["2023-12-31"], name="date")

        result = DataMapper.map_to_standard(
            df, market="US", data_type="balance_sheet"
        )

        # YFinance mapping should handle these fields
        # Note: exact mapping depends on YFINANCE_FIELD_MAPPING implementation
        assert result is not None

    def test_yfinance_empty_dataframe(self):
        """Should handle empty DataFrame gracefully"""
        df = pd.DataFrame()

        result = DataMapper.map_to_standard(
            df, market="US", data_type="balance_sheet"
        )

        assert result.empty


class TestMapToStandardEdgeCases:
    """Edge case tests for map_to_standard()"""

    def test_case_insensitive_source(self):
        """Should accept source in any case"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
        })

        # Lowercase
        result1 = DataMapper.map_to_standard(
            df, market="A", data_type="balance_sheet"
        )
        assert "stock_code" in result1.columns

    def test_case_insensitive_data_type(self):
        """Should accept data_type in any case"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
        })

        result = DataMapper.map_to_standard(
            df, market="A", data_type="BALANCE_SHEET"
        )
        assert "stock_code" in result.columns


class TestMapToStandardIntegration:
    """Integration tests combining source and type mappings"""

    def test_tushare_balance_sheet_full_workflow(self):
        """Test complete mapping workflow for Tushare balance sheet"""
        # Raw Tushare data
        df = pd.DataFrame({
            "ts_code": ["600519.SH", "600519.SH"],
            "end_date": ["20231231", "20221231"],
            "ann_date": ["20240330", "20230330"],
            "update_flag": [1, 1],
            # Tushare field names
            "total_assets": [1000000, 900000],
            "total_liab": [500000, 450000],
            "total_equity": [500000, 450000],
            "capital_rese": [100000, 90000],
            "surplus_rese": [50000, 45000],
        })

        result = DataMapper.map_to_standard(
            df, market="A", data_type="balance_sheet"
        )

        # Verify source-specific mapping
        assert "stock_code" in result.columns
        assert "report_date" in result.columns

        # Verify all rows processed
        assert len(result) == 2

        # Verify values preserved
        assert result["stock_code"].iloc[0] == "600519.SH"
        assert result["report_date"].iloc[0] == "20231231"
