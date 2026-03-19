"""Tests for AShareStatementHandler"""
import pytest
import pandas as pd
from unittest.mock import MagicMock

from value_investment.handlers.a_share import AShareStatementHandler
from value_investment.core.types import Message


class TestAShareStatementHandler:
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.supported_fields = {"total_revenue", "net_profit", "total_assets"}
        # fetch_raw_* 返回原始（未映射）数据，_standardize 执行映射
        provider.fetch_raw_income_statement = MagicMock(
            return_value=pd.DataFrame({
                "year": [2024, 2023],
                "total_operate_income": [100e9, 90e9],
                "netprofit": [50e9, 45e9],
            })
        )
        provider.fetch_raw_balance_sheet = MagicMock(
            return_value=pd.DataFrame()
        )
        provider.fetch_raw_cash_flow = MagicMock(
            return_value=pd.DataFrame()
        )
        # Tushare 字段映射
        provider.FIELD_MAPPINGS = {
            "income_statement": {
                "total_operate_income": "total_revenue",
                "netprofit": "net_profit",
            },
            "balance_sheet": {},
            "cash_flow": {},
        }
        return provider

    def test_market_filter(self, mock_provider):
        """快速拒绝：港股请求应该被忽略"""
        handler = AShareStatementHandler(mock_provider)
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"total_revenue"})

        assert handler._can_handle_market(message) is False

    def test_fields_filter(self, mock_provider):
        """快速拒绝：无支持字段应该被忽略"""
        handler = AShareStatementHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})

        # market_cap 是 market data，不在 statement fields 中
        assert handler._can_handle_fields(message) is False

    @pytest.mark.asyncio
    async def test_fetch_financial_data(self, mock_provider):
        """正常流程：获取财务报表数据"""
        handler = AShareStatementHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"total_revenue", "net_profit"})

        await handler.handle(message)

        # 调用了 fetch_raw_income_statement
        mock_provider.fetch_raw_income_statement.assert_called_once()
        call_args = mock_provider.fetch_raw_income_statement.call_args
        # 已处理的字段应从 require 中移除
        assert "total_revenue" not in message.require
        assert "net_profit" not in message.require
        # 结果应包含数据
        assert 2024 in message.results.get("total_revenue", {})
        assert message.results["total_revenue"][2024] == 100e9

    @pytest.mark.asyncio
    async def test_handle_mixed_fields(self, mock_provider):
        """混合字段：只处理 statement 字段，忽略 indicator/market 字段"""
        handler = AShareStatementHandler(mock_provider)
        # roe 是 indicator，不是 statement 字段
        message = Message(
            symbol="600519", market="A股", end="2024", years=5,
            require={"total_revenue", "roe"}
        )

        await handler.handle(message)

        # 调用了 fetch_raw_income_statement
        mock_provider.fetch_raw_income_statement.assert_called_once()
        # roe 仍在 require 中（statement handler 无法处理）
        assert "roe" in message.require

    @pytest.mark.asyncio
    async def test_no_provider(self):
        """无 provider 时优雅返回"""
        handler = AShareStatementHandler(None)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"total_revenue"})

        await handler.handle(message)

        # require 保持不变（无法处理）
        assert "total_revenue" in message.require
