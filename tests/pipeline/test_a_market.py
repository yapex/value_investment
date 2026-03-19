"""Tests for AShareMarketHandler"""
import pytest
from unittest.mock import MagicMock

from value_investment.handlers.a_share import AShareMarketHandler
from value_investment.core.types import Message


class TestAShareMarketHandler:
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.supported_fields = {"market_cap", "pe_ratio", "pb_ratio"}
        provider.fetch_market_data = MagicMock(
            return_value={
                "market_cap": 2.5e12,
                "pe_ratio": 28.5,
            }
        )
        return provider

    def test_market_filter(self):
        """快速拒绝：港股请求应该被忽略"""
        handler = AShareMarketHandler(None)
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"market_cap"})

        assert handler._can_handle_market(message) is False

    def test_fields_filter_no_provider(self):
        """无 provider 时无法处理字段"""
        handler = AShareMarketHandler(None)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})

        # 无 provider，can_handle 为空
        assert handler._can_handle_fields(message) is False

    @pytest.mark.asyncio
    async def test_fetch_market_data(self, mock_provider):
        """正常流程：获取市值数据"""
        handler = AShareMarketHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap", "pe_ratio"})

        await handler.handle(message)

        mock_provider.fetch_market_data.assert_called_once()
        call_kwargs = mock_provider.fetch_market_data.call_args.kwargs
        assert "600519" in call_kwargs.get("stock_code", "")
        # 已处理的字段应从 require 中移除
        assert "market_cap" not in message.require
        assert "pe_ratio" not in message.require
        # 市场数据是单时间点，格式为 {year: value}
        assert 2024 in message.results.get("market_cap", {})
        assert message.results["market_cap"][2024] == 2.5e12

    @pytest.mark.asyncio
    async def test_no_provider(self):
        """无 provider 时优雅返回"""
        handler = AShareMarketHandler(None)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})

        await handler.handle(message)

        # require 保持不变
        assert "market_cap" in message.require
