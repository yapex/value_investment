"""Tests for HK handlers"""
import pytest

from value_investment.handlers.hk_share import (
    HKShareStatementHandler,
    HKShareIndicatorHandler,
    HKShareMarketHandler,
)
from value_investment.core.types import Message


class TestHKHandlers:
    def test_statement_rejects_a_stock(self):
        """HKStatementHandler 拒绝 A 股请求"""
        handler = HKShareStatementHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"total_revenue"})
        assert handler._can_handle_market(message) is False

    def test_statement_accepts_hk(self):
        """HKStatementHandler 接受港股请求"""
        handler = HKShareStatementHandler()
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"total_revenue"})
        assert handler._can_handle_market(message) is True

    def test_indicator_rejects_a_stock(self):
        """HKIndicatorHandler 拒绝 A 股请求"""
        handler = HKShareIndicatorHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"roe"})
        assert handler._can_handle_market(message) is False

    def test_market_rejects_a_stock(self):
        """HKMarketHandler 拒绝 A 股请求"""
        handler = HKShareMarketHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})
        assert handler._can_handle_market(message) is False

    def test_all_hk_handlers_have_correct_market(self):
        """所有 HK Handler 的 target_market 为港股"""
        for Handler in [HKShareStatementHandler, HKShareIndicatorHandler, HKShareMarketHandler]:
            handler = Handler()
            assert handler.target_market == "港股"

    @pytest.mark.asyncio
    async def test_handler_no_provider(self):
        """无 provider 时不报错（待 Provider 实现）"""
        handler = HKShareStatementHandler(None)
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"total_revenue"})
        await handler.handle(message)
        assert "total_revenue" in message.require  # 无法处理，因为无 provider
