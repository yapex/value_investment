"""Indicator base module"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, TYPE_CHECKING, Any, Dict, Optional, Protocol

if TYPE_CHECKING:
    import pandas as pd


class IIndicator(Protocol):
    """Indicator protocol - defines interface for all indicators"""

    name: str

    def calculate(self, data: "pd.DataFrame", **kwargs) -> "IndicatorResult":
        """Calculate the indicator"""
        ...

    def get_required_fields(self) -> list:
        """Return list of required data fields"""
        ...

    @property
    def needs(self) -> list:
        """Return list of external data dependencies"""
        return []


class IndicatorType(str, Enum):
    """Types of indicators"""

    RAW = "RAW"  # Raw financial data from API (direct field mapping)
    CALCULATED = "CALCULATED"  # Calculated indicators (need computation logic)


@dataclass
class IndicatorMeta:
    """Metadata for an indicator"""

    name: str
    display_name: str
    type: IndicatorType
    field_names: List[str] = field(default_factory=list)
    market_fields: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    unit: str = ""

    def get_field_for_market(self, market: str) -> Optional[str]:
        """Get field name for specific market"""
        return self.market_fields.get(market)


@dataclass
class IndicatorResult:
    """Result of an indicator calculation"""

    value: float
    unit: str
    description: str
    years: List[int]
    values: List[float] = None  # Per-year values

    def __post_init__(self):
        if self.values is None:
            self.values = []


class BaseIndicator(ABC):
    """Base class for all indicators

    Uses data-passing pattern: indicators receive pre-fetched data
    and focus only on calculation logic.
    """

    name: str = ""
    description: str = ""
    type: IndicatorType = IndicatorType.CALCULATED  # Default to CALCULATED
    needs: list = []  # External data dependencies (stock_info, prices, quarterly)

    @abstractmethod
    def calculate(
        self,
        data: "pd.DataFrame",
        **kwargs: Any,
    ) -> IndicatorResult:
        """Calculate the indicator

        Args:
            data: DataFrame with financial data columns
            **kwargs: Additional parameters (e.g., tax_rate, growth_rate)

        Returns:
            IndicatorResult with calculated value
        """
        pass

    def get_required_fields(self) -> list:
        """Return list of required data fields for this indicator"""
        return []
