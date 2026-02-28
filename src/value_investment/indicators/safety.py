"""Safety indicators: Cash to Debt, Debt Ratio (Total)."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class CashToDebtIndicator(BaseIndicator):
    """Cash to Debt Ratio = Cash and Equivalents / Interest-bearing Debt"""

    name = "cash_to_debt"
    description = "Cash to Debt Ratio (Cash and Equivalents / Interest-bearing Debt)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get cash and equivalents
        cash_col = self._find_column(data, ['cash_and_equivalents', 'MONETARYFUNDS'])
        cash = data[cash_col].fillna(0) if cash_col else pd.Series(0, index=data.index)

        # Get interest-bearing debt (sum of all types)
        debt = pd.Series(0, index=data.index)

        # Short-term debt
        short_debt_col = self._find_column(data, ['short_term_debt', 'SHORT_LOAN'])
        if short_debt_col is not None:
            debt = debt + data[short_debt_col].fillna(0)

        # Long-term debt
        long_debt_col = self._find_column(data, ['long_term_debt', 'LONG_LOAN'])
        if long_debt_col is not None:
            debt = debt + data[long_debt_col].fillna(0)

        # Bonds payable
        bonds_col = self._find_column(data, ['bonds_payable', 'BOND_PAYABLE'])
        if bonds_col is not None:
            debt = debt + data[bonds_col].fillna(0)

        # Lease liability
        lease_liab_col = self._find_column(data, ['lease_liability', 'LEASE_LIAB'])
        if lease_liab_col is not None:
            debt = debt + data[lease_liab_col].fillna(0)

        # Noncurrent liability due within 1 year
        noncurrent_1y_col = self._find_column(data, ['noncurrent_liability_due_1y', 'NONCURRENT_LIAB_1YEAR'])
        if noncurrent_1y_col is not None:
            debt = debt + data[noncurrent_1y_col].fillna(0)

        # Calculate ratio
        debt_clean = debt.replace(0, pd.NA)
        ratio = cash / debt_clean
        ratio = ratio.dropna()

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="ratio",
            description="Cash to Debt Ratio",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['cash_and_equivalents', 'short_term_debt', 'long_term_debt', 
                'bonds_payable', 'lease_liability', 'noncurrent_liability_due_1y']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class DebtRatioTotalIndicator(BaseIndicator):
    """Debt Ratio (Total) = Interest-bearing Debt / Total Assets"""

    name = "debt_ratio_total"
    description = "Debt Ratio (Interest-bearing Debt / Total Assets)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get total assets
        assets_col = self._find_column(data, ['total_assets', 'TOTAL_ASSETS'])
        total_assets = data[assets_col].fillna(0) if assets_col else pd.Series(0, index=data.index)

        # Get interest-bearing debt (sum of all types)
        debt = pd.Series(0, index=data.index)

        # Short-term debt
        short_debt_col = self._find_column(data, ['short_term_debt', 'SHORT_LOAN'])
        if short_debt_col is not None:
            debt = debt + data[short_debt_col].fillna(0)

        # Long-term debt
        long_debt_col = self._find_column(data, ['long_term_debt', 'LONG_LOAN'])
        if long_debt_col is not None:
            debt = debt + data[long_debt_col].fillna(0)

        # Bonds payable
        bonds_col = self._find_column(data, ['bonds_payable', 'BOND_PAYABLE'])
        if bonds_col is not None:
            debt = debt + data[bonds_col].fillna(0)

        # Lease liability
        lease_liab_col = self._find_column(data, ['lease_liability', 'LEASE_LIAB'])
        if lease_liab_col is not None:
            debt = debt + data[lease_liab_col].fillna(0)

        # Noncurrent liability due within 1 year
        noncurrent_1y_col = self._find_column(data, ['noncurrent_liability_due_1y', 'NONCURRENT_LIAB_1YEAR'])
        if noncurrent_1y_col is not None:
            debt = debt + data[noncurrent_1y_col].fillna(0)

        # Calculate ratio
        assets_clean = total_assets.replace(0, pd.NA)
        ratio = (debt / assets_clean) * 100
        ratio = ratio.dropna()

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="%",
            description="Debt Ratio (Interest-bearing Debt / Total Assets)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['total_assets', 'short_term_debt', 'long_term_debt',
                'bonds_payable', 'lease_liability', 'noncurrent_liability_due_1y']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
