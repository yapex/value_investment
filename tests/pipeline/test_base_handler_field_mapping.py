"""Tests for BaseHandler field mapping functionality"""
import pytest
import pandas as pd

from value_investment.handlers.base_handler import BaseHandler
from value_investment.core.types import Message


class MockProviderFieldMapping:
    """Mock Provider that declares FIELD_MAPPINGS"""

    FIELD_MAPPINGS = {
        "balance_sheet": {
            "原始资产": "total_assets",
            "原始负债": "total_liabilities",
        },
        "income_statement": {
            "原始收入": "total_revenue",
            "原始利润": "net_profit",
        },
        "cash_flow": {
            "原始经营现金流": "operating_cash_flow",
        },
    }

    SUPPORTED_FIELDS = {
        "total_assets",
        "total_liabilities",
        "total_revenue",
        "net_profit",
        "operating_cash_flow",
    }

    @property
    def supported_fields(self):
        return self.SUPPORTED_FIELDS

    def fetch_raw_balance_sheet(self, stock_code, end_year, start_year=None):
        return pd.DataFrame({
            "year": [2023, 2022],
            "原始资产": [1000, 900],
            "原始负债": [500, 450],
        })

    def fetch_raw_income_statement(self, stock_code, end_year, start_year=None):
        return pd.DataFrame({
            "year": [2023, 2022],
            "原始收入": [2000, 1800],
            "原始利润": [300, 270],
        })

    def fetch_raw_cash_flow(self, stock_code, end_year, start_year=None):
        return pd.DataFrame({
            "year": [2023, 2022],
            "原始经营现金流": [500, 450],
        })


class ConcreteFieldMappingHandler(BaseHandler):
    """Concrete handler for testing field mapping"""

    def __init__(self, provider=None):
        fields = {
            "total_assets",
            "total_liabilities",
            "total_revenue",
            "net_profit",
            "operating_cash_flow",
        }
        super().__init__(provider, "A股", fields)

    async def _handle_impl(self, message):
        pass


class TestHandlerFieldMapping:
    """Test handler field mapping via _standardize()"""

    def test_handler_standardizes_fields(self):
        """Handler should map native fields to standard fields via _standardize()"""
        handler = ConcreteFieldMappingHandler(MockProviderFieldMapping())

        df = handler.get_balance_sheet("000001", 2023, 2022)

        assert "total_assets" in df.columns
        assert "total_liabilities" in df.columns
        assert "原始资产" not in df.columns  # 原字段应被映射
        assert "原始负债" not in df.columns

    def test_handler_standardize_income_statement(self):
        """get_income_statement should map native fields to standard fields"""
        handler = ConcreteFieldMappingHandler(MockProviderFieldMapping())

        df = handler.get_income_statement("000001", 2023, 2022)

        assert "total_revenue" in df.columns
        assert "net_profit" in df.columns
        assert "原始收入" not in df.columns
        assert "原始利润" not in df.columns

    def test_handler_standardize_cash_flow(self):
        """get_cash_flow_statement should map native fields to standard fields"""
        handler = ConcreteFieldMappingHandler(MockProviderFieldMapping())

        df = handler.get_cash_flow_statement("000001", 2023, 2022)

        assert "operating_cash_flow" in df.columns
        assert "原始经营现金流" not in df.columns

    def test_handler_standardize_ignores_missing_fields(self):
        """_standardize should silently ignore fields that don't exist in raw data"""

        class PartialMappingProvider:
            FIELD_MAPPINGS = {
                "balance_sheet": {
                    "存在字段": "total_assets",
                    "不存在字段": "total_liabilities",  # 原始数据中没有
                },
            }

            SUPPORTED_FIELDS = {"total_assets", "total_liabilities"}

            @property
            def supported_fields(self):
                return self.SUPPORTED_FIELDS

            def fetch_raw_balance_sheet(self, stock_code, end_year, start_year=None):
                return pd.DataFrame({
                    "year": [2023],
                    "存在字段": [1000],
                    "其他字段": [500],  # 映射中没有，保持原样
                })

        handler = ConcreteFieldMappingHandler(PartialMappingProvider())
        df = handler.get_balance_sheet("000001", 2023, 2022)

        assert "total_assets" in df.columns
        assert "存在字段" not in df.columns
        assert "其他字段" in df.columns  # 未映射的字段保留

    def test_handler_standardize_empty_df(self):
        """_standardize should return empty DataFrame when input is empty"""
        handler = ConcreteFieldMappingHandler(MockProviderFieldMapping())

        result = handler._standardize(pd.DataFrame(), "balance_sheet")
        assert result.empty

        result = handler._standardize(None, "balance_sheet")
        assert result.empty

    def test_handler_standardize_no_mappings(self):
        """_standardize should return original df when no mappings declared"""

        class NoMappingProvider:
            FIELD_MAPPINGS = {}

            SUPPORTED_FIELDS = set()

            @property
            def supported_fields(self):
                return self.SUPPORTED_FIELDS

            def fetch_raw_balance_sheet(self, stock_code, end_year, start_year=None):
                return pd.DataFrame({
                    "year": [2023],
                    "some_field": [100],
                })

        handler = ConcreteFieldMappingHandler(NoMappingProvider())
        df = handler.get_balance_sheet("000001", 2023, 2022)

        assert "some_field" in df.columns
        assert "year" in df.columns
