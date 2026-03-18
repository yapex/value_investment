"""Tests for AStockHandler"""
import pytest
from value_investment.pipeline.handlers.a_stock import AStockHandler
from value_investment.pipeline.data.tushare_provider import TushareProvider


class MockCache:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, ttl=None):
        self.data[key] = value


def test_a_stock_handler_with_provider():
    """Test AStockHandler with TushareProvider"""
    cache = MockCache()
    # 需要 token 才能创建 provider
    import os
    token = os.environ.get("TUSHARE_TOKEN", "")
    if not token:
        pytest.skip("TUSHARE_TOKEN not set")

    provider = TushareProvider(cache=cache, token=token)
    handler = AStockHandler(provider=provider)

    # Handler 能处理 provider 支持的字段
    assert len(handler.can_handle) > 0
    assert "total_assets" in handler.can_handle
    assert "net_profit" in handler.can_handle


def test_a_stock_handler_without_provider():
    """Test AStockHandler without provider"""
    handler = AStockHandler(provider=None)

    # 没有 provider，不能处理任何字段
    assert handler.can_handle == set()
