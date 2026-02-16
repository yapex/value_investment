"""Indicators package"""
from value_investment.indicators.base import (
    BaseIndicator,
    IndicatorResult,
    IndicatorType,
    IndicatorMeta,
)
from value_investment.indicators.market import Market, detect_market
from value_investment.indicators.mapping import get_mapped_field, MarketConfig, FIELD_MAPPING
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
