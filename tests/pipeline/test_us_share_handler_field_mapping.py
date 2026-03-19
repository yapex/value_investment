"""Tests for USShareStatementHandler integration with BaseHandler field mapping"""
import pytest
import pandas as pd

from value_investment.handlers.us_share import USShareStatementHandler
from value_investment.core.types import Message


class MockUSProvider:
    FIELD_MAPPINGS = {
        "balance_sheet": {
            "总资产": "total_assets",
        },
        "income_statement": {
            "主营收入": "total_revenue",
        },
        "cash_flow": {
            "经营活动产生的现金流量净额": "operating_cash_flow",
        },
    }

    SUPPORTED_FIELDS = {"total_assets", "total_revenue", "operating_cash_flow"}

    @property
    def supported_fields(self):
        return self.SUPPORTED_FIELDS

    def fetch_raw_balance_sheet(self, stock_code, end_year, start_year=None):
        return pd.DataFrame({"year": [2023, 2022], "总资产": [1000, 900]})

    def fetch_raw_income_statement(self, stock_code, end_year, start_year=None):
        return pd.DataFrame({"year": [2023, 2022], "主营收入": [5000, 4500]})

    def fetch_raw_cash_flow(self, stock_code, end_year, start_year=None):
        return pd.DataFrame({"year": [2023, 2022], "经营活动产生的现金流量净额": [1000, 900]})


class TestUSShareStatementHandlerFieldMapping:
    """USShareStatementHandler should return mapped fields via BaseHandler"""

    @pytest.mark.asyncio
    async def test_handler_returns_mapped_fields(self):
        """Handler should return standard field names in results"""
        handler = USShareStatementHandler(MockUSProvider())

        message = Message(
            symbol="AAPL",
            market="美股",
            require={"total_assets", "total_revenue"},
            end="2023-12-31",
            years=2,
        )

        await handler.handle(message)

        assert "total_assets" in message.results
        assert "total_revenue" in message.results
        assert 2023 in message.results["total_assets"]
        assert message.results["total_assets"][2023] == 1000.0
        assert 2023 in message.results["total_revenue"]
        assert message.results["total_revenue"][2023] == 5000.0

    @pytest.mark.asyncio
    async def test_handler_cash_flow_mapping(self):
        """Handler should correctly map cash flow fields"""
        handler = USShareStatementHandler(MockUSProvider())

        message = Message(
            symbol="AAPL",
            market="美股",
            require={"operating_cash_flow"},
            end="2023-12-31",
            years=2,
        )

        await handler.handle(message)

        assert "operating_cash_flow" in message.results
        assert 2023 in message.results["operating_cash_flow"]
        assert message.results["operating_cash_flow"][2023] == 1000.0
