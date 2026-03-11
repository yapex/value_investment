"""Profitability indicators - Operating Profit Margin."""

import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class OperatingProfitMarginIndicator(BaseIndicator):
    """Operating Profit Margin = Operating Profit / Revenue * 100"""

    name = "operating_profit_margin"
    description = "Operating Profit Margin (营业利润率 = 营业利润 / 营业收入)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        op_col = self._find_column(data, ['operating_profit', 'OPERATE_PROFIT'])
        revenue_col = self._find_column(data, ['operating_income', 'total_revenue'])

        operating_profit = data[op_col] if op_col else pd.Series(0, index=data.index)
        revenue = data[revenue_col] if revenue_col else pd.Series([1], index=data.index)

        # Avoid division by zero
        margin = (operating_profit / revenue.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(margin.mean()) if len(margin) > 0 else 0.0,
            unit="%",
            description="Operating Profit Margin (营业利润率)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=margin.tolist() if len(margin) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['operating_profit', 'revenue']
