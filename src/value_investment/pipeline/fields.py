"""Standard field constants for pipeline

This module defines all field constants used in calculators and handlers.
Sources:
- Standard IFRS fields: from CORE_FIELD_MAPPING

Usage:
    from value_investment.pipeline.fields import OPERATING_PROFIT, TOTAL_ASSETS

    class ROICCalculator:
        required_fields = {OPERATING_PROFIT, TOTAL_ASSETS, ...}
"""

# =============================================================================
# Standard IFRS Fields (from CORE_FIELD_MAPPING)
# =============================================================================

# Income Statement
NET_PROFIT = "net_profit"
OPERATING_PROFIT = "operating_profit"
GROSS_PROFIT = "gross_profit"
TOTAL_REVENUE = "total_revenue"
OPERATING_COST = "operating_cost"
BASIC_EPS = "basic_eps"
DILUTED_EPS = "diluted_eps"
GROSS_MARGIN = "gross_margin"
NET_PROFIT_MARGIN = "net_profit_margin"

# Balance Sheet
TOTAL_ASSETS = "total_assets"
TOTAL_EQUITY = "total_equity"
TOTAL_LIABILITIES = "total_liabilities"
CURRENT_ASSETS = "current_assets"
CURRENT_LIABILITIES = "current_liabilities"
CASH_AND_EQUIVALENTS = "cash_and_equivalents"
INVENTORY = "inventory"
ACCOUNTS_RECEIVABLE = "accounts_receivable"
ACCOUNTS_PAYABLE = "accounts_payable"
PREPAYMENT = "prepayment"
ADV_RECEIPTS = "adv_receipts"
CONTRACT_ASSETS = "contract_assets"
CONTRACT_LIAB = "contract_liab"
FIXED_ASSETS = "fixed_assets"

# Cash Flow
OPERATING_CASH_FLOW = "operating_cash_flow"
INVESTING_CASH_FLOW = "investing_cash_flow"
FINANCING_CASH_FLOW = "financing_cash_flow"
CAPITAL_EXPENDITURE = "capital_expenditure"

# Market Data
MARKET_CAP = "market_cap"
TOTAL_SHARES = "total_shares"
PE_RATIO = "pe_ratio"
PB_RATIO = "pb_ratio"

# Ratios
ROE = "roe"
ROA = "roa"
ASSET_TURNOVER = "asset_turnover"
INVENTORY_TURNOVER = "inventory_turnover"
RECEIVABLE_TURNOVER = "receivable_turnover"
CURRENT_RATIO = "current_ratio"
QUICK_RATIO = "quick_ratio"
DEBT_RATIO = "debt_ratio"
BOOK_VALUE_PER_SHARE = "book_value_per_share"
