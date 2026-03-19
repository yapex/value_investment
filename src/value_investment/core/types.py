"""Core types for pipeline"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    """Message class for pipeline"""
    symbol: str
    market: str
    end: str
    years: int
    require: set[str] = field(default_factory=set)
    results: dict[str, dict[int, Any]] = field(default_factory=dict)
    force_refresh: bool = False

    def add_result(self, field_name: str, data: dict[int, Any]) -> None:
        """Add result to results basket"""
        self.results[field_name] = data
        self.require.discard(field_name)
