"""Tests for Message class"""
import pytest
from value_investment.core.types import Message


def test_message_two_baskets():
    """Test message has two baskets: require and results"""
    msg = Message(
        symbol="600519",
        market="A股",
        end="2024",
        years=10,
        require={"ebit", "total_assets"},
    )
    # 需求篮子
    assert "ebit" in msg.require
    assert "total_assets" in msg.require
    # 结果篮子初始为空
    assert msg.results == {}
    # 放入结果
    msg.add_result("ebit", {2024: 100.0})
    assert "ebit" in msg.results
    assert msg.results["ebit"][2024] == 100.0
    # 从需求篮子移除
    assert "ebit" not in msg.require
