"""Tests for TushareFieldMapper"""
import pandas as pd
import pytest

from value_investment.providers.tushare_mapper import TushareFieldMapper
from value_investment.domain.fields import IFRSFields


class TestTushareFieldMapper:
    """Test TushareFieldMapper class"""

    def test_singleton_pattern(self):
        """Test TushareFieldMapper is a singleton"""
        mapper1 = TushareFieldMapper()
        mapper2 = TushareFieldMapper()
        assert mapper1 is mapper2

    def test_balance_sheet_mapping(self):
        """Test balance sheet field mapping"""
        mapper = TushareFieldMapper()
        
        # Verify required balance sheet fields are mapped
        assert IFRSFields.TOTAL_ASSETS in mapper.balance_sheet.values()
        assert IFRSFields.CASH_AND_EQUIVALENTS in mapper.balance_sheet.values()
        assert IFRSFields.CURRENT_LIABILITIES in mapper.balance_sheet.values()
        
        # Verify mapping direction: Tushare field -> standard field
        assert "total_assets" in mapper.balance_sheet
        assert mapper.balance_sheet["total_assets"] == IFRSFields.TOTAL_ASSETS

    def test_income_statement_mapping(self):
        """Test income statement field mapping"""
        mapper = TushareFieldMapper()
        
        # Verify required income statement fields are mapped
        assert IFRSFields.OPERATING_PROFIT in mapper.income_statement.values()
        assert IFRSFields.NET_PROFIT in mapper.income_statement.values()
        
        # Verify mapping direction: Tushare field -> standard field
        assert "operate_profit" in mapper.income_statement
        assert mapper.income_statement["operate_profit"] == IFRSFields.OPERATING_PROFIT

    def test_cash_flow_mapping(self):
        """Test cash flow statement field mapping"""
        mapper = TushareFieldMapper()
        
        # Verify required cash flow fields are mapped
        assert IFRSFields.OPERATING_CASH_FLOW in mapper.cash_flow.values()
        
        # Verify mapping direction
        assert "n_cashflow_act" in mapper.cash_flow
        assert mapper.cash_flow["n_cashflow_act"] == IFRSFields.OPERATING_CASH_FLOW

    def test_indicators_mapping(self):
        """Test financial indicators field mapping from fina_indicator API"""
        mapper = TushareFieldMapper()

        # Verify indicator fields are mapped
        assert IFRSFields.ROE in mapper.indicators.values()
        assert IFRSFields.ROA in mapper.indicators.values()
        assert IFRSFields.GROSS_MARGIN in mapper.indicators.values()
        assert IFRSFields.NET_PROFIT_MARGIN in mapper.indicators.values()

        # Verify mapping direction: Tushare field -> standard field
        assert "roe" in mapper.indicators
        assert mapper.indicators["roe"] == IFRSFields.ROE

        assert "roic" in mapper.indicators
        assert mapper.indicators["roic"] == "roic"

        # Verify reverse index for indicators
        assert IFRSFields.ROE in mapper.reverse.indicators
        assert mapper.reverse.indicators[IFRSFields.ROE] == "roe"

        assert "roic" in mapper.reverse.indicators
        assert mapper.reverse.indicators["roic"] == "roic"

    def test_eps_bps_indicator_fields(self):
        """Test basic_eps, diluted_eps, book_value_per_share mapping"""
        mapper = TushareFieldMapper()

        # basic_eps -> eps
        assert IFRSFields.BASIC_EPS in mapper.reverse.indicators
        assert mapper.reverse.indicators[IFRSFields.BASIC_EPS] == "eps"

        # diluted_eps -> dt_eps
        assert IFRSFields.DILUTED_EPS in mapper.reverse.indicators
        assert mapper.reverse.indicators[IFRSFields.DILUTED_EPS] == "dt_eps"

        # book_value_per_share -> bps
        assert IFRSFields.BOOK_VALUE_PER_SHARE in mapper.reverse.indicators
        assert mapper.reverse.indicators[IFRSFields.BOOK_VALUE_PER_SHARE] == "bps"

    def test_total_shares_mapping(self):
        """Test total_shares from balance_sheet"""
        mapper = TushareFieldMapper()

        assert "total_shares" in mapper.reverse.balance_sheet
        assert mapper.reverse.balance_sheet["total_shares"] == "total_share"

    def test_indicator_dataframe_mapping(self):
        """Test mapping a DataFrame with indicator columns"""
        mapper = TushareFieldMapper()
        
        # Create a DataFrame with Tushare fina_indicator columns
        df = pd.DataFrame({
            "ts_code": ["600519.SH", "600519.SH"],
            "end_date": ["20241231", "20231231"],
            "roe": [30.5, 28.2],
            "roa": [15.2, 14.1],
            "roic": [25.0, 23.5],
            "gross_margin": [75.0, 74.0],
            "netprofit_margin": [45.0, 43.0],
        })
        
        # Map indicators
        result = mapper.map_dataframe(df, "indicators")
        
        # Verify mapped columns
        assert IFRSFields.ROE in result.columns
        assert IFRSFields.ROA in result.columns
        assert "roic" in result.columns
        assert IFRSFields.GROSS_MARGIN in result.columns
        assert IFRSFields.NET_PROFIT_MARGIN in result.columns
        
        # Verify metadata columns preserved
        assert "ts_code" in result.columns
        assert "end_date" in result.columns

    def test_reverse_index_auto_generated(self):
        """Test reverse index is auto-generated"""
        mapper = TushareFieldMapper()
        
        # Reverse index should contain standard field -> Tushare field
        assert IFRSFields.TOTAL_ASSETS in mapper.reverse.balance_sheet
        assert mapper.reverse.balance_sheet[IFRSFields.TOTAL_ASSETS] == "total_assets"
        
        assert IFRSFields.OPERATING_PROFIT in mapper.reverse.income_statement
        assert mapper.reverse.income_statement[IFRSFields.OPERATING_PROFIT] == "operate_profit"

    def test_map_dataframe(self):
        """Test mapping a DataFrame to standard field names"""
        mapper = TushareFieldMapper()
        
        # Create a DataFrame with Tushare column names
        df = pd.DataFrame({
            "total_assets": [1000.0, 900.0],
            "money_cap": [200.0, 180.0],
            "total_cur_liab": [300.0, 280.0],
            "operate_profit": [100.0, 90.0],
            "ts_code": ["600519.SH", "600519.SH"],
            "ann_date": ["20241231", "20231231"],
        })
        
        # Map balance sheet
        balance_df = mapper.map_dataframe(df.copy(), "balance_sheet")
        assert IFRSFields.TOTAL_ASSETS in balance_df.columns
        assert IFRSFields.CASH_AND_EQUIVALENTS in balance_df.columns
        assert IFRSFields.CURRENT_LIABILITIES in balance_df.columns
        
        # Map income statement
        income_df = mapper.map_dataframe(df.copy(), "income_statement")
        assert IFRSFields.OPERATING_PROFIT in income_df.columns
        
        # Unmapped columns should be preserved
        assert "ts_code" in balance_df.columns
        assert "ann_date" in balance_df.columns

    def test_supported_fields(self):
        """Test supported_fields returns all mapped standard fields"""
        mapper = TushareFieldMapper()
        fields = mapper.supported_fields
        
        # Should contain all standard fields from all statement types
        assert IFRSFields.TOTAL_ASSETS in fields
        assert IFRSFields.OPERATING_PROFIT in fields
        assert IFRSFields.OPERATING_CASH_FLOW in fields
        
        # Should contain indicator fields
        assert IFRSFields.ROE in fields
        assert IFRSFields.ROA in fields
        assert IFRSFields.GROSS_MARGIN in fields
        assert IFRSFields.NET_PROFIT_MARGIN in fields
        assert "roic" in fields

    def test_standard_to_tushare_field(self):
        """Test converting standard field to Tushare field"""
        mapper = TushareFieldMapper()
        
        # Standard -> Tushare
        ts_field = mapper.standard_to_tushare(IFRSFields.TOTAL_ASSETS, "balance_sheet")
        assert ts_field == "total_assets"
        
        ts_field = mapper.standard_to_tushare(IFRSFields.OPERATING_PROFIT, "income_statement")
        assert ts_field == "operate_profit"

    def test_tushare_to_standard_field(self):
        """Test converting Tushare field to standard field"""
        mapper = TushareFieldMapper()
        
        # Tushare -> Standard
        std_field = mapper.tushare_to_standard("total_assets", "balance_sheet")
        assert std_field == IFRSFields.TOTAL_ASSETS
        
        std_field = mapper.tushare_to_standard("operate_profit", "income_statement")
        assert std_field == IFRSFields.OPERATING_PROFIT

    def test_empty_dataframe_handling(self):
        """Test mapping empty DataFrame"""
        mapper = TushareFieldMapper()
        
        empty_df = pd.DataFrame()
        result = mapper.map_dataframe(empty_df, "balance_sheet")
        assert result.empty

    def test_partial_columns_handling(self):
        """Test mapping DataFrame with partial Tushare columns"""
        mapper = TushareFieldMapper()
        
        # Only some columns present
        df = pd.DataFrame({
            "total_assets": [1000.0],
            # money_cap not present
            "operate_profit": [100.0],
            "unknown_column": [999.0],  # Should be preserved
        })
        
        result = mapper.map_dataframe(df, "balance_sheet")
        assert IFRSFields.TOTAL_ASSETS in result.columns
        # Note: unknown_column should be preserved
        assert "unknown_column" in result.columns


class TestTushareFieldMapperIntegration:
    """Integration tests for TushareFieldMapper"""

    def test_all_required_roic_fields_mapped(self):
        """Test all fields needed for ROIC calculation are mapped"""
        mapper = TushareFieldMapper()
        
        roic_fields = {
            IFRSFields.OPERATING_PROFIT,
            IFRSFields.TOTAL_ASSETS,
            IFRSFields.CASH_AND_EQUIVALENTS,
            IFRSFields.CURRENT_LIABILITIES,
        }
        
        for field in roic_fields:
            # Check field exists in reverse index
            found = False
            for statement_type in ["balance_sheet", "income_statement"]:
                if field in getattr(mapper.reverse, statement_type, {}):
                    found = True
                    break
            assert found, f"ROIC field {field} not mapped in TushareFieldMapper"

    def test_real_tushare_columns_mapping(self):
        """Test mapping with real Tushare API column names"""
        mapper = TushareFieldMapper()
        
        # Real Tushare balancesheet() columns
        real_columns = {
            "ts_code", "ann_date", "end_date", "total_assets", "total_liab",
            "total_cur_liab", "total_ncur_liab", "money_cap", "accounts_rece",
            "inventory", "total_cur_assets", "total_ncur_assets", "fix_assets",
            "cip", "total_equity", "parent_equity", "minority_equity",
            "cap_rese", "undist_profit", "surplus_rese"
        }
        
        # Real Tushare income() columns
        real_income_columns = {
            "ts_code", "ann_date", "end_date", "total_operate_income",
            "operate_income", "total_operate_cost", "operate_cost",
            "operate_profit", "total_profit", "netprofit", "netprofit_attr_p",
            "basic_eps", "diluted_eps"
        }
        
        # Verify Tushare columns are in mappings
        for col in real_columns:
            if col in mapper.balance_sheet:
                # Verify mapping direction
                mapped = mapper.balance_sheet[col]
                assert isinstance(mapped, str)
        
        for col in real_income_columns:
            if col in mapper.income_statement:
                mapped = mapper.income_statement[col]
                assert isinstance(mapped, str)
