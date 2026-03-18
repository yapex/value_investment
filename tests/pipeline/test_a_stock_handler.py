"""Tests for AStockHandler"""
import pytest
from value_investment.pipeline.handlers.a_stock import AStockHandler


class MockCache:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value


def test_a_stock_handler_provides_fields():
    """Test AStockHandler can handle A-share fields"""
    handler = AStockHandler(cache=MockCache())

    # Handler 能处理 A 股的哪些字段（从 CORE_FIELD_MAPPING 获取）
    assert "net_profit" in handler.can_handle
    assert "total_assets" in handler.can_handle
    # 注意：ROIC 需要的是 ebit, cash, current_liabilities
    # 但 A 股映射里没有 ebit，用 operating_profit 代替
    # cash -> cash_and_equivalents
    # current_liabilities 存在
    assert "current_liabilities" in handler.can_handle
    assert "operating_profit" in handler.can_handle
    assert "cash_and_equivalents" in handler.can_handle
