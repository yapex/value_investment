"""Standard field constants for pipeline

Structure:
1. 国际标准字段 - from CORE_FIELD_MAPPING (IFRS standard)
2. 自定义字段 - calculated fields defined in system

Usage:
    from value_investment.pipeline.fields import TOTAL_ASSETS, OPERATING_PROFIT, ROIC

    class ROICCalculator:
        required_fields = {OPERATING_PROFIT, TOTAL_ASSETS, CASH_AND_EQUIVALENTS, CURRENT_LIABILITIES}

Validation:
    All calculators are validated at container setup time to ensure
    only valid fields are used.
"""

from value_investment.data.mapper import CORE_FIELD_MAPPING

# All valid fields for calculators
ALL_FIELDS = frozenset(CORE_FIELD_MAPPING.keys())


def validate_fields(calculator_cls) -> None:
    """Validate calculator's required_fields are all standard fields

    Raises:
        ValueError: If any field is not in ALL_FIELDS
    """
    for field in calculator_cls.required_fields:
        if field not in ALL_FIELDS:
            raise ValueError(
                f"Calculator {calculator_cls.__name__} uses invalid field: {field}. "
                f"Valid fields: {sorted(ALL_FIELDS)}"
            )


# =============================================================================
# 1. 国际标准字段 (IFRS Standard Fields)
# =============================================================================

# --- 资产负债表 (Balance Sheet) ---
TOTAL_ASSETS = "total_assets"
TOTAL_LIABILITIES = "total_liabilities"
TOTAL_EQUITY = "total_equity"
CURRENT_ASSETS = "current_assets"
CURRENT_LIABILITIES = "current_liabilities"
CASH_AND_EQUIVALENTS = "cash_and_equivalents"
INVENTORY = "inventory"
ACCOUNTS_RECEIVABLE = "accounts_receivable"
ACCOUNTS_PAYABLE = "accounts_payable"
FIXED_ASSETS = "fixed_assets"
PREPAYMENT = "prepayment"
ADV_RECEIPTS = "adv_receipts"
CONTRACT_ASSETS = "contract_assets"
CONTRACT_LIAB = "contract_liab"

# --- 利润表 (Income Statement) ---
TOTAL_REVENUE = "total_revenue"
NET_PROFIT = "net_profit"
OPERATING_PROFIT = "operating_profit"
GROSS_PROFIT = "gross_profit"
OPERATING_COST = "operating_cost"

# --- 现金流量表 (Cash Flow Statement) ---
OPERATING_CASH_FLOW = "operating_cash_flow"
INVESTING_CASH_FLOW = "investing_cash_flow"
FINANCING_CASH_FLOW = "financing_cash_flow"
CAPITAL_EXPENDITURE = "capital_expenditure"

# --- 关键比率 (Key Ratios) ---
ROE = "roe"
ROA = "roa"
GROSS_MARGIN = "gross_margin"
NET_PROFIT_MARGIN = "net_profit_margin"
CURRENT_RATIO = "current_ratio"
QUICK_RATIO = "quick_ratio"
DEBT_RATIO = "debt_ratio"
ASSET_TURNOVER = "asset_turnover"
INVENTORY_TURNOVER = "inventory_turnover"
RECEIVABLE_TURNOVER = "receivable_turnover"

# --- 市场数据 (Market Data) ---
MARKET_CAP = "market_cap"
TOTAL_SHARES = "total_shares"
PE_RATIO = "pe_ratio"
PB_RATIO = "pb_ratio"
BASIC_EPS = "basic_eps"
DILUTED_EPS = "diluted_eps"
BOOK_VALUE_PER_SHARE = "book_value_per_share"


# =============================================================================
# 2. 自定义字段 (Custom Calculated Fields)
# =============================================================================
# These fields are defined by the system and need to be calculated

# ROIC - 投入资本回报率
# Formula: Operating Profit / (Total Assets - Cash - Current Liabilities)
ROIC = "roic"
