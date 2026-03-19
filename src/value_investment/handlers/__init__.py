"""Handlers for different markets"""
from value_investment.handlers.base import Handler
from value_investment.handlers.base_handler import BaseHandler
from value_investment.handlers.a_share import (
    AShareStatementHandler,
    AShareIndicatorHandler,
    AShareMarketHandler,
)
from value_investment.handlers.hk_share import (
    HKShareStatementHandler,
    HKShareIndicatorHandler,
    HKShareMarketHandler,
)
from value_investment.handlers.us_share import (
    USShareStatementHandler,
    USShareIndicatorHandler,
    USShareMarketHandler,
)

__all__ = [
    "Handler",
    "BaseHandler",
    # A 股
    "AShareStatementHandler",
    "AShareIndicatorHandler",
    "AShareMarketHandler",
    # 港股
    "HKShareStatementHandler",
    "HKShareIndicatorHandler",
    "HKShareMarketHandler",
    # 美股
    "USShareStatementHandler",
    "USShareIndicatorHandler",
    "USShareMarketHandler",
]
