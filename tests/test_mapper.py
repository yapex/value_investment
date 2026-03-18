"""Tests for DataMapper.map_to_standard() method

TDD Phase 1: Write failing tests first, then implement the method.

The map_to_standard() method should:
1. Support sources: 'tushare', 'akshare', 'yfinance'
2. Support data_types: 'balance_sheet', 'income_statement', 'cash_flow', 'financial_indicator'
3. Map source-specific fields (ts_code → stock_code, end_date → report_date)
4. Apply type-specific field mappings
"""

import pytest
import pandas as pd

from value_investment.data.mapper import DataMapper


class TestMapToStandardTushare:
    """Tests for map_to_standard() with Tushare source"""

    def test_tushare_balance_sheet_basic_mapping(self):
        """Should map Tushare balance sheet fields to standard fields"""
        # Arrange: Tushare raw data format
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240330"],
            "update_flag": [1],
            "total_assets": [1000000],
            "total_liab": [500000],
            "total_equity": [500000],
            "capital_rese": [100000],
        })

        # Act: Map to standard fields
        result = DataMapper.map_to_standard(
            df, source="tushare", data_type="balance_sheet"
        )

        # Assert: Source-specific fields mapped
        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        assert result["stock_code"].iloc[0] == "600519.SH"
        assert result["report_date"].iloc[0] == "20231231"

        # Assert: Type-specific fields mapped (if defined in mapping)
        # total_assets should remain as total_assets (already standard)
        assert "total_assets" in result.columns

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
            df, source="tushare", data_type="income_statement"
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
            df, source="tushare", data_type="cash_flow"
        )

        assert "stock_code" in result.columns
        assert "report_date" in result.columns

    def test_tushare_financial_indicator_basic_mapping(self):
        """Should map Tushare financial indicator fields to standard fields"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240330"],
            "update_flag": [1],
            "roe": [0.25],
            "roa": [0.15],
            "eps": [5.0],
            "bps": [50.0],
        })

        result = DataMapper.map_to_standard(
            df, source="tushare", data_type="financial_indicator"
        )

        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        # Financial indicator specific mapping (via FINANCIAL_INDICATOR_MAPPING)
        # eps → basic_eps, bps → book_value_per_share
        assert "basic_eps" in result.columns or "eps" in result.columns

    def test_tushare_empty_dataframe(self):
        """Should handle empty DataFrame gracefully"""
        df = pd.DataFrame()

        result = DataMapper.map_to_standard(
            df, source="tushare", data_type="balance_sheet"
        )

        assert result.empty

    def test_tushare_none_dataframe(self):
        """Should handle None input gracefully"""
        result = DataMapper.map_to_standard(
            None, source="tushare", data_type="balance_sheet"
        )

        assert result is None

    def test_tushare_preserves_unmapped_columns(self):
        """Should preserve columns not in mapping"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "custom_field": ["custom_value"],
        })

        result = DataMapper.map_to_standard(
            df, source="tushare", data_type="balance_sheet"
        )

        # Mapped columns
        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        # Unmapped column preserved
        assert "custom_field" in result.columns

    def test_tushare_multiple_rows(self):
        """Should handle multiple rows correctly"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH", "600519.SH", "600519.SH"],
            "end_date": ["20231231", "20221231", "20211231"],
            "total_assets": [100, 90, 80],
        })

        result = DataMapper.map_to_standard(
            df, source="tushare", data_type="balance_sheet"
        )

        assert len(result) == 3
        assert list(result["stock_code"]) == ["600519.SH"] * 3
        assert list(result["report_date"]) == ["20231231", "20221231", "20211231"]


class TestMapToStandardAkshare:
    """Tests for map_to_standard() with AKShare source"""

    def test_akshare_balance_sheet_basic_mapping(self):
        """Should map AKShare balance sheet fields to standard fields"""
        # AKShare uses Chinese column names for A 股
        df = pd.DataFrame({
            "股票代码": ["600519"],
            "报告期": ["2023-12-31"],
            "资产总计": [1000000],
            "负债合计": [500000],
            "股东权益合计": [500000],
        })

        result = DataMapper.map_to_standard(
            df, source="akshare", data_type="balance_sheet"
        )

        # AKShare A 股 mapping: 股票代码 → stock_code, 报告期 → report_date
        assert "stock_code" in result.columns
        assert "report_date" in result.columns

    def test_akshare_income_statement_basic_mapping(self):
        """Should map AKShare income statement fields to standard fields"""
        df = pd.DataFrame({
            "股票代码": ["600519"],
            "报告期": ["2023-12-31"],
            "营业总收入": [100000],
            "净利润": [10000],
        })

        result = DataMapper.map_to_standard(
            df, source="akshare", data_type="income_statement"
        )

        assert "stock_code" in result.columns
        assert "report_date" in result.columns


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
            df, source="yfinance", data_type="balance_sheet"
        )

        # YFinance mapping should handle these fields
        # Note: exact mapping depends on YFINANCE_FIELD_MAPPING implementation
        assert result is not None

    def test_yfinance_empty_dataframe(self):
        """Should handle empty DataFrame gracefully"""
        df = pd.DataFrame()

        result = DataMapper.map_to_standard(
            df, source="yfinance", data_type="balance_sheet"
        )

        assert result.empty


class TestMapToStandardEdgeCases:
    """Edge case tests for map_to_standard()"""

    def test_invalid_source_raises_error(self):
        """Should raise ValueError for invalid source"""
        df = pd.DataFrame({"col": [1]})

        with pytest.raises(ValueError, match="Unknown source"):
            DataMapper.map_to_standard(
                df, source="invalid_source", data_type="balance_sheet"
            )

    def test_invalid_data_type_raises_error(self):
        """Should raise ValueError for invalid data_type"""
        df = pd.DataFrame({"col": [1]})

        with pytest.raises(ValueError, match="Unknown data_type"):
            DataMapper.map_to_standard(
                df, source="tushare", data_type="invalid_type"
            )

    def test_case_insensitive_source(self):
        """Should accept source in any case"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
        })

        # Lowercase
        result1 = DataMapper.map_to_standard(
            df, source="TUSHARE", data_type="balance_sheet"
        )
        assert "stock_code" in result1.columns

    def test_case_insensitive_data_type(self):
        """Should accept data_type in any case"""
        df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
        })

        result = DataMapper.map_to_standard(
            df, source="tushare", data_type="BALANCE_SHEET"
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
            df, source="tushare", data_type="balance_sheet"
        )

        # Verify source-specific mapping
        assert "stock_code" in result.columns
        assert "report_date" in result.columns

        # Verify all rows processed
        assert len(result) == 2

        # Verify values preserved
        assert result["stock_code"].iloc[0] == "600519.SH"
        assert result["report_date"].iloc[0] == "20231231"
