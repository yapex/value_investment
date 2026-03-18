import pytest
from value_investment.pipeline.bus.message import Message


def test_message_creation():
    msg = Message(
        symbol="600519",
        market="A股",
        end="2024",
        years=10,
        require={"ebit", "total_assets", "cash", "current_liabilities"},
    )
    assert msg.symbol == "600519"
    assert msg.market == "A股"
    assert "ebit" in msg.require
