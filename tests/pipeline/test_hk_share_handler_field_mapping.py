"""Tests for HKShareStatementHandler integration with BaseHandler field mapping"""
import pytest
import pandas as pd

from value_investment.handlers.hk_share import HKShareStatementHandler
from value_investment.core.types import Message


class MockHKProviderFieldMapping:
    """Mock HKProvider that declares FIELD_MAPPINGS"""

    FIELD_MAPPINGS = {
        "balance_sheet": {
            "资产总计": "total_assets",
            "总负债": "total_liabilities",
        },
        "income_statement": {
            "收益": "total_revenue",
            "股东应占溢利": "net_profit",
        },
        "cash_flow": {
            "经营业务现金净额": "operating_cash_flow",
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
            "资产总计": [1000, 900],
            "总负债": [500, 450],
        })

    def fetch_raw_income_statement(self, stock_code, end_year, start_year=None):
        return pd.DataFrame({
            "year": [2023, 2022],
            "收益": [2000, 1800],
            "股东应占溢利": [300, 270],
        })

    def fetch_raw_cash_flow(self, stock_code, end_year, start_year=None):
        return pd.DataFrame({
            "year": [2023, 2022],
            "经营业务现金净额": [500, 450],
        })


class TestHKShareStatementHandlerFieldMapping:
    """HKShareStatementHandler should return mapped fields via BaseHandler"""

    @pytest.mark.asyncio
    async def test_handler_returns_mapped_fields(self):
        """Handler should return standard field names in results"""
        handler = HKShareStatementHandler(MockHKProviderFieldMapping())

        message = Message(
            symbol="00700",
            market="港股",
            require={"total_assets", "total_revenue", "net_profit"},
            end="2023-12-31",
            years=2,
        )

        await handler.handle(message)

        # 验证标准字段在结果中
        assert "total_assets" in message.results
        assert "total_revenue" in message.results
        assert "net_profit" in message.results

        # 验证年份数据
        assert 2023 in message.results["total_assets"]
        assert message.results["total_assets"][2023] == 1000.0
        assert 2023 in message.results["total_revenue"]
        assert message.results["total_revenue"][2023] == 2000.0
        assert 2023 in message.results["net_profit"]
        assert message.results["net_profit"][2023] == 300.0

    @pytest.mark.asyncio
    async def test_handler_cash_flow_mapping(self):
        """Handler should correctly map cash flow fields"""
        handler = HKShareStatementHandler(MockHKProviderFieldMapping())

        message = Message(
            symbol="00700",
            market="港股",
            require={"operating_cash_flow"},
            end="2023-12-31",
            years=2,
        )

        await handler.handle(message)

        assert "operating_cash_flow" in message.results
        assert 2023 in message.results["operating_cash_flow"]
        assert message.results["operating_cash_flow"][2023] == 500.0

    @pytest.mark.asyncio
    async def test_handler_no_provider_returns_nothing(self):
        """Handler without provider doesn't crash"""
        handler = HKShareStatementHandler(None)
        message = Message(
            symbol="00700",
            market="港股",
            require={"total_assets"},
            end="2023-12-31",
            years=1,
        )
        await handler.handle(message)
        # No exception, results may be empty
