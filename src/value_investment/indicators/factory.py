"""Indicator factory module"""
from typing import TYPE_CHECKING, Dict

from value_investment.indicators.base import BaseIndicator
from value_investment.indicators.simple import (
    ROEIndicator,
    ROAIndicator,
    GrossMarginIndicator,
    NetProfitMarginIndicator,
    CurrentRatioIndicator,
)
from value_investment.indicators.complex import (
    ROICIndicator,
    CAGRIndicator,
    DCFIndicator,
)

if TYPE_CHECKING:
    from value_investment.data.providers.akshare_provider import AkshareProvider


class IndicatorFactory:
    """Factory for creating and managing indicators"""

    def __init__(self, provider: "AkshareProvider" = None):
        self._provider = provider
        self._indicators: Dict[str, BaseIndicator] = {}
        self._register_default_indicators()

    def _register_default_indicators(self) -> None:
        """Register all default indicators"""
        indicators = [
            ROEIndicator(),
            ROAIndicator(),
            GrossMarginIndicator(),
            NetProfitMarginIndicator(),
            CurrentRatioIndicator(),
            ROICIndicator(),
            CAGRIndicator(),
            DCFIndicator(),
        ]
        for indicator in indicators:
            self.register(indicator)

    def register(self, indicator: BaseIndicator) -> None:
        """Register an indicator"""
        self._indicators[indicator.name] = indicator

    def get(self, name: str) -> BaseIndicator:
        """Get an indicator by name"""
        if name not in self._indicators:
            raise ValueError(f"Unknown indicator: {name}")
        return self._indicators[name]

    def list_indicators(self) -> list:
        """List all registered indicators"""
        return list(self._indicators.keys())
