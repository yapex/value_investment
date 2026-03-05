"""Indicators package"""
from value_investment.indicators.base import (
    BaseIndicator,
    IndicatorMeta,
    IndicatorResult,
    IndicatorType,
)
from value_investment.indicators.mapping import FIELD_MAPPING, MarketConfig, get_mapped_field
from value_investment.indicators.market import Market, detect_market
from value_investment.indicators.registry import IndicatorRegistry, register_defaults

__all__ = [
    "BaseIndicator",
    "IndicatorResult",
    "IndicatorType",
    "IndicatorMeta",
    "Market",
    "detect_market",
    "get_mapped_field",
    "MarketConfig",
    "FIELD_MAPPING",
    "IndicatorRegistry",
    "register_defaults",
]
