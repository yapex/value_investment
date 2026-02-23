"""Cash flow indicators: CFO to Net Profit, FCF to Revenue, CFO to Net Profit Sum."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class CfoToNetprofitIndicator(BaseIndicator):
    """CFO to Net Profit = Operating Cash Flow / Net Profit"""

    name = "cfo_to_netprofit"
    description = "Operating Cash Flow to Net Profit"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        cfo_col = self._find_column(data, ['operating_cash_flow'])
        np_col = self._find_column(data, ['net_profit'])

        cfo = data[cfo_col] if cfo_col else pd.Series(0, index=data.index)
        np = data[np_col] if np_col else pd.Series([1], index=data.index)

        ratio = (cfo / np.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="%",
            description="CFO to Net Profit",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_cash_flow', 'net_profit']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class FcfToRevenueIndicator(BaseIndicator):
    """FCF to Revenue = Free Cash Flow / Operating Income"""

    name = "fcf_to_revenue"
    description = "Free Cash Flow to Operating Income"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        fcf_col = self._find_column(data, ['free_cash_flow'])
        income_col = self._find_column(data, ['operating_income'])

        fcf = data[fcf_col] if fcf_col else pd.Series(0, index=data.index)
        income = data[income_col] if income_col else pd.Series([1], index=data.index)

        ratio = (fcf / income.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="%",
            description="FCF to Revenue",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['free_cash_flow', 'operating_income']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class CfoToNetprofitSumIndicator(BaseIndicator):
    """CFO to Net Profit Sum = Sum of Operating Cash Flow / Sum of Net Profit (10 years)"""

    name = "cfo_to_netprofit_sum"
    description = "Operating Cash Flow Sum / Net Profit Sum (10 years) - 盈利质量验证"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        cfo_col = self._find_column(data, ['operating_cash_flow'])
        np_col = self._find_column(data, ['net_profit'])

        if cfo_col is None or np_col is None:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description="CFO to Net Profit Sum",
                years=[],
                values=[]
            )

        cfo_sum = data[cfo_col].sum()
        np_sum = data[np_col].sum()

        # Count valid years (non-null values)
        valid_years = data['year'].dropna().tolist() if 'year' in data.columns else []
        years_count = len(valid_years)

        if np_sum == 0:
            ratio = 0.0
        else:
            ratio = (cfo_sum / np_sum) * 100

        return IndicatorResult(
            value=float(ratio),
            unit="%",
            description=f"CFO/NetProfit Sum ({years_count}年)",
            years=valid_years,
            values=[]  # Empty to show as summary metric
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_cash_flow', 'net_profit']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
