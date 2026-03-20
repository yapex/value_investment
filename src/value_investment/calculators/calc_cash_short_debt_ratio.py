"""Cash to Short-term Debt Ratio Calculator

Cash Short-term Debt Ratio = (Cash + Trading Financial Assets) / Short-term Interest-bearing Debt

Where:
- Cash = 货币资金
- Trading Financial Assets = 交易性金融资产（可迅速变现）
- Short-term Interest-bearing Debt = 短期有息负债 = 短期借款

This ratio measures a company's ability to pay off its short-term debt with liquid assets.
Values > 1 indicate sufficient liquidity to cover short-term obligations.

Formula: (cash + trading_financial_assets) / short_term_borrowings

Reference: IFRSFields.CASH_AND_EQUIVALENTS, CustomFields.TRADING_FINANCIAL_ASSETS
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "cash_short_debt_ratio"

# 依赖字段
required_fields = ["cash_and_equivalents", "short_term_borrowings"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Cash to Short-term Debt Ratio

    Args:
        results: {field: {year: value}}
            - cash_and_equivalents: Cash and equivalents values by year
            - short_term_borrowings: Short-term borrowings values by year

    Returns:
        {year: ratio or None if short_term_borrowings is missing/zero}
    """
    cash = results.get("cash_and_equivalents", {})
    short_term_debt = results.get("short_term_borrowings", {})

    ratio = {}
    for year in cash:
        # 现金类资产 = 货币资金 + 交易性金融资产
        cash_assets = cash.get(year, 0)
        # 如果有交易性金融资产字段，也加入计算
        # trading_financial_assets = results.get("trading_financial_assets", {}).get(year, 0)
        # cash_assets = cash_assets + trading_financial_assets

        debt = short_term_debt.get(year, 0)

        # 避免除以零
        if not debt:
            ratio[year] = None
        else:
            ratio[year] = cash_assets / debt

    return ratio
