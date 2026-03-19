"""Tests for Handler base class"""
import pytest
from value_investment.handlers.base import Handler


def test_handler_interface():
    """Test Handler has required interface"""
    class TestHandler(Handler):
        @property
        def can_handle(self) -> set[str]:
            return {"ebit", "total_assets"}

        async def handle(self, message):
            pass

    handler = TestHandler()
    assert "ebit" in handler.can_handle
    assert handler.can_handle == {"ebit", "total_assets"}
