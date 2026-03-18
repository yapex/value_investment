"""Standard field constants for pipeline

This module defines all field constants used in calculators and handlers.
Sources:
- Standard IFRS fields: from CORE_FIELD_MAPPING
- Custom calculated fields: manually added

Usage:
    from value_investment.pipeline.fields import OPERATING_PROFIT, ROIC

    class ROICCalculator:
        required_fields = {OPERATING_PROFIT, TOTAL_ASSETS, CASH_AND_EQUIVALENTS, CURRENT_LIABILITIES}
"""

from value_investment.data.mapper import CORE_FIELD_MAPPING

# =============================================================================
# Standard IFRS Fields
# =============================================================================
# Note: This list should match CORE_FIELD_MAPPING keys
# For IDE support, use these constants instead of string literals

OPERATING_PROFIT = "operating_profit"
TOTAL_ASSETS = "total_assets"
CASH_AND_EQUIVALENTS = "cash_and_equivalents"
CURRENT_LIABILITIES = "current_liabilities"
NET_PROFIT = "net_profit"
TOTAL_EQUITY = "total_equity"
REVENUE = "revenue"
GROSS_PROFIT = "gross_profit"
# ... other fields from CORE_FIELD_MAPPING

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
