"""Indicator base module"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from value_investment.data.providers.akshare_provider import AkshareProvider


@dataclass
class IndicatorResult:
    """Result of an indicator calculation"""

    value: float
    unit: str
    description: str
    years: List[int]


class BaseIndicator(ABC):
    """Base class for all indicators"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def calculate(
        self,
        stock_code: str,
        years: int,
        provider: "AkshareProvider",
        **kwargs,
    ) -> IndicatorResult:
        """Calculate the indicator"""
        pass
