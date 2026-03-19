"""Tests for BaseHandler"""
import pytest

from value_investment.pipeline.handlers.base_handler import BaseHandler
from value_investment.pipeline.bus.message import Message


class MockProvider:
    @property
    def supported_fields(self):
        return {"field_a", "field_b"}


class ConcreteHandler(BaseHandler):
    def __init__(self, provider=None):
        super().__init__(provider, "A股", {"field_a", "field_b", "field_c"})

    async def _handle_impl(self, message):
        pass


class TestBaseHandler:
    def test_init(self):
        """初始化时正确设置 target_market 和 supported_fields"""
        handler = ConcreteHandler(MockProvider())
        assert handler.target_market == "A股"
        assert "field_a" in handler.can_handle
        assert "field_b" in handler.can_handle
        assert "field_c" not in handler.can_handle  # provider 不支持

    def test_init_no_provider(self):
        """无 provider 时 can_handle 为空"""
        handler = ConcreteHandler(None)
        assert handler.can_handle == set()

    def test_fast_reject_wrong_market(self):
        """快速拒绝：市场不匹配"""
        handler = ConcreteHandler(MockProvider())
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"field_a"})

        assert handler._can_handle_market(message) is False

    def test_fast_reject_no_fields(self):
        """快速拒绝：无支持的字段"""
        handler = ConcreteHandler(MockProvider())
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"other_field"})

        assert handler._can_handle_fields(message) is False

    @pytest.mark.asyncio
    async def test_handle_fast_rejects_wrong_market(self):
        """handle() 快速拒绝市场不匹配的消息"""
        called = False

        class NoOpHandler(ConcreteHandler):
            async def _handle_impl(self, message):
                nonlocal called
                called = True

        handler = NoOpHandler(MockProvider())
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"field_a"})

        await handler.handle(message)

        # _handle_impl 不应被调用
        assert called is False

    @pytest.mark.asyncio
    async def test_handle_processes_when_eligible(self):
        """handle() 正常处理符合条件的消息"""
        handled = []

        class RecordingHandler(ConcreteHandler):
            async def _handle_impl(self, message):
                handled.append(message)

        provider = MockProvider()
        handler = RecordingHandler(provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"field_a"})

        await handler.handle(message)

        assert message in handled
        # 注意：field_a 是否从 require 移除由 _handle_impl 决定（通过 message.add_result）
        # BaseHandler 只负责调用 _handle_impl，不直接修改 require
