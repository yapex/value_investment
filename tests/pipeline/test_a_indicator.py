"""Tests for AShareIndicatorHandler"""
import pytest
from unittest.mock import MagicMock

from value_investment.handlers.a_share import AShareIndicatorHandler
from value_investment.core.types import Message


class TestAShareIndicatorHandler:
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.supported_fields = {"roe", "roa", "gross_margin"}
        provider.fetch_indicators = MagicMock(
            return_value={
                "roe": {2024: 25.5, 2023: 24.8},
                "roa": {2024: 12.3, 2023: 11.5},
            }
        )
        return provider

    def test_market_filter(self, mock_provider):
        """快速拒绝：港股请求应该被忽略"""
        handler = AShareIndicatorHandler(mock_provider)
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"roe"})

        assert handler._can_handle_market(message) is False

    def test_fields_filter(self, mock_provider):
        """快速拒绝：无支持字段应该被忽略"""
        handler = AShareIndicatorHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})

        # market_cap 是 market data，不是 indicator 字段
        assert handler._can_handle_fields(message) is False

    @pytest.mark.asyncio
    async def test_fetch_indicators(self, mock_provider):
        """正常流程：获取财务指标"""
        handler = AShareIndicatorHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"roe", "roa"})

        await handler.handle(message)

        mock_provider.fetch_indicators.assert_called_once()
        call_kwargs = mock_provider.fetch_indicators.call_args.kwargs
        assert "600519" in call_kwargs.get("stock_code", "")
        assert "roe" in call_kwargs.get("fields", set())
        # 已处理的字段应从 require 中移除
        assert "roe" not in message.require
        assert "roa" not in message.require
        # 结果应包含数据
        assert 2024 in message.results.get("roe", {})
        assert message.results["roe"][2024] == 25.5

    @pytest.mark.asyncio
    async def test_no_provider(self):
        """无 provider 时优雅返回"""
        handler = AShareIndicatorHandler(None)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"roe"})

        await handler.handle(message)

        assert "roe" in message.require
