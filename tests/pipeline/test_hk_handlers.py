"""Tests for HK handlers"""
import pytest

from value_investment.pipeline.handlers.hk_statement import HKStockStatementHandler
from value_investment.pipeline.handlers.hk_indicator import HKStockIndicatorHandler
from value_investment.pipeline.handlers.hk_market import HKStockMarketHandler
from value_investment.pipeline.bus.message import Message


class TestHKHandlers:
    def test_statement_rejects_a_stock(self):
        """HKStatementHandler 拒绝 A 股请求"""
        handler = HKStockStatementHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"total_revenue"})
        assert handler._can_handle_market(message) is False

    def test_statement_accepts_hk(self):
        """HKStatementHandler 接受港股请求"""
        handler = HKStockStatementHandler()
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"total_revenue"})
        assert handler._can_handle_market(message) is True

    def test_indicator_rejects_a_stock(self):
        """HKIndicatorHandler 拒绝 A 股请求"""
        handler = HKStockIndicatorHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"roe"})
        assert handler._can_handle_market(message) is False

    def test_market_rejects_a_stock(self):
        """HKMarketHandler 拒绝 A 股请求"""
        handler = HKStockMarketHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})
        assert handler._can_handle_market(message) is False

    def test_all_hk_handlers_have_correct_market(self):
        """所有 HK Handler 的 target_market 为港股"""
        for Handler in [HKStockStatementHandler, HKStockIndicatorHandler, HKStockMarketHandler]:
            handler = Handler()
            assert handler.target_market == "港股"

    @pytest.mark.asyncio
    async def test_handler_no_provider(self):
        """无 provider 时不报错（待 Provider 实现）"""
        handler = HKStockStatementHandler(None)
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"total_revenue"})
        await handler.handle(message)
        assert "total_revenue" in message.require  # 无法处理，因为无 provider
