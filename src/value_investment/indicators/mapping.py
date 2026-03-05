"""Field mapping and market configuration for multi-market support

This module provides compatibility layer for legacy field mapping.
New code should use value_investment.data.mapper.CORE_FIELD_MAPPING directly.
"""
from dataclasses import dataclass
from typing import Dict, Optional

# Import unified mapping from data/mapper.py
from value_investment.data.mapper import CORE_FIELD_MAPPING, DataMapper

# Legacy field name aliases (old name -> new standard name)
_LEGACY_FIELD_ALIASES = {
    "revenue": "total_revenue",
    "operating_income": "operating_profit",
    "cash_flow": "operating_cash_flow",
}

# Build FIELD_MAPPING for backward compatibility
# Combines CORE_FIELD_MAPPING with legacy aliases
FIELD_MAPPING: Dict[str, Dict[str, str]] = {}

# Add all core fields
for standard_field, market_map in CORE_FIELD_MAPPING.items():
    FIELD_MAPPING[standard_field] = market_map.copy()

# Add legacy aliases
for legacy_name, standard_name in _LEGACY_FIELD_ALIASES.items():
    if standard_name in CORE_FIELD_MAPPING:
        FIELD_MAPPING[legacy_name] = CORE_FIELD_MAPPING[standard_name].copy()


def get_mapped_field(indicator_name: str, market: str) -> Optional[str]:
    """Get field name for indicator in specific market

    Args:
        indicator_name: Common indicator name (e.g., "revenue", "total_revenue")
        market: Market name ("A股", "港股", "美股")

    Returns:
        Market-specific field name or None if not found

    Note:
        This function supports both legacy names (e.g., "revenue") and
        standard names (e.g., "total_revenue") for backward compatibility.
    """
    # First try direct lookup in FIELD_MAPPING (includes legacy aliases)
    if indicator_name in FIELD_MAPPING:
        return FIELD_MAPPING[indicator_name].get(market)

    # Fall back to DataMapper for standard fields
    return DataMapper.get_market_field(indicator_name, market)


@dataclass
class MarketConfig:
    """Configuration for a specific market"""

    market: str
    indicator_prefix: str
    year_field: str
    data_source: str

    def get_field_mapping(self, indicator_name: str) -> Optional[Dict[str, str]]:
        """Get all market field mappings for an indicator"""
        return FIELD_MAPPING.get(indicator_name)
