"""Tests for US handlers"""
import pytest

from value_investment.handlers.us_share import (
    USShareStatementHandler,
    USShareIndicatorHandler,
    USShareMarketHandler,
)
from value_investment.core.types import Message


class TestUSHandlers:
    def test_statement_rejects_a_stock(self):
        """USStatementHandler 拒绝 A 股请求"""
        handler = USShareStatementHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"total_revenue"})
        assert handler._can_handle_market(message) is False

    def test_statement_accepts_us(self):
        """USStatementHandler 接受美股请求"""
        handler = USShareStatementHandler()
        message = Message(symbol="AAPL", market="美股", end="2024", years=5, require={"total_revenue"})
        assert handler._can_handle_market(message) is True

    def test_indicator_rejects_a_stock(self):
        """USIndicatorHandler 拒绝 A 股请求"""
        handler = USShareIndicatorHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"roe"})
        assert handler._can_handle_market(message) is False

    def test_market_rejects_a_stock(self):
        """USMarketHandler 拒绝 A 股请求"""
        handler = USShareMarketHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})
        assert handler._can_handle_market(message) is False

    def test_all_us_handlers_have_correct_market(self):
        """所有 US Handler 的 target_market 为美股"""
        for Handler in [USShareStatementHandler, USShareIndicatorHandler, USShareMarketHandler]:
            handler = Handler()
            assert handler.target_market == "美股"

    @pytest.mark.asyncio
    async def test_handler_no_provider(self):
        """无 provider 时不报错（待 Provider 实现）"""
        handler = USShareStatementHandler(None)
        message = Message(symbol="AAPL", market="美股", end="2024", years=5, require={"total_revenue"})
        await handler.handle(message)
        assert "total_revenue" in message.require  # 无法处理，因为无 provider
