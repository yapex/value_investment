"""Standard field constants for pipeline

This module defines all field constants used in calculators and handlers.
Sources:
- Standard IFRS fields: auto-generated from CORE_FIELD_MAPPING
- Custom calculated fields: manually added

Usage:
    from value_investment.pipeline.fields import (
        OPERATING_PROFIT,
        TOTAL_ASSETS,
        ROIC,
    )

    class ROICCalculator:
        required_fields = {
            OPERATING_PROFIT,
            TOTAL_ASSETS,
            CASH_AND_EQUIVALENTS,
            CURRENT_LIABILITIES,
        }
"""

from value_investment.data.mapper import CORE_FIELD_MAPPING

# =============================================================================
# Standard IFRS Fields (auto-generated from CORE_FIELD_MAPPING)
# =============================================================================
for _field in CORE_FIELD_MAPPING.keys():
    globals()[_field.upper()] = _field

# =============================================================================
# Custom Calculated Fields
# =============================================================================
ROIC = "roic"
ROE = "roe"
ROA = "roa"
GROSS_PROFIT_MARGIN = "gross_profit_margin"
NET_PROFIT_MARGIN = "net_profit_margin"
CURRENT_RATIO = "current_ratio"
QUICK_RATIO = "quick_ratio"
