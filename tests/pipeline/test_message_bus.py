"""Tests for MessageBus"""
import asyncio
import pytest
from value_investment.core.types import Message
from value_investment.pipeline.bus import MessageBus
from value_investment.handlers.base import Handler


class MockHandler(Handler):
    def __init__(self, can_handle_fields: set[str]):
        self._can_handle = can_handle_fields

    @property
    def can_handle(self) -> set[str]:
        return self._can_handle

    async def handle(self, message):
        if "ebit" in message.require:
            message.add_result("ebit", {2024: 100.0})


def test_message_bus_single_round():
    """Test message bus processes message in single round"""
    bus = MessageBus()
    handler = MockHandler({"ebit"})
    bus.register(handler)

    msg = Message(
        symbol="600519",
        market="A股",
        end="2024",
        years=10,
        require={"ebit"},
    )

    result = asyncio.run(bus.process(msg))

    assert "ebit" in result.results
    assert "ebit" not in result.require


def test_message_bus_multi_handler():
    """Test message bus with multiple handlers"""
    bus = MessageBus()

    class Handler1(Handler):
        @property
        def can_handle(self) -> set[str]:
            return {"ebit"}

        async def handle(self, message):
            if "ebit" in message.require:
                message.add_result("ebit", {2024: 100.0})

    class Handler2(Handler):
        @property
        def can_handle(self) -> set[str]:
            return {"net_profit"}

        async def handle(self, message):
            if "net_profit" in message.require:
                message.add_result("net_profit", {2024: 80.0})

    bus.register(Handler1())
    bus.register(Handler2())

    msg = Message(
        symbol="600519",
        market="A股",
        end="2024",
        years=10,
        require={"ebit", "net_profit"},
    )

    result = asyncio.run(bus.process(msg))

    assert "ebit" in result.results
    assert "net_profit" in result.results
    assert "ebit" not in result.require
    assert "net_profit" not in result.require
