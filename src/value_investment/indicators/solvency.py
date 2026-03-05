"""Solvency indicators: Current Ratio, Quick Ratio, Debt Ratio."""

import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class CurrentRatioIndicator(BaseIndicator):
    """Current Ratio = Current Assets / Current Liabilities"""

    name = "current_ratio"
    description = "Current Ratio (Current Assets / Current Liabilities)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        current_assets_col = self._find_column(data, ['current_assets'])
        current_liab_col = self._find_column(data, ['current_liabilities'])

        current_assets = data[current_assets_col] if current_assets_col else pd.Series(0, index=data.index)
        current_liab = data[current_liab_col] if current_liab_col else pd.Series([1], index=data.index)

        cr = current_assets / current_liab.replace(0, 1)

        return IndicatorResult(
            value=float(cr.mean()) if len(cr) > 0 else 0.0,
            unit="ratio",
            description="Current Ratio",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=cr.tolist() if len(cr) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['current_assets', 'current_liabilities']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class QuickRatioIndicator(BaseIndicator):
    """Quick Ratio = (Current Assets - Inventory) / Current Liabilities"""

    name = "quick_ratio"
    description = "Quick Ratio ((Current Assets - Inventory) / Current Liabilities)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        current_assets_col = self._find_column(data, ['current_assets'])
        inventory_col = self._find_column(data, ['inventory'])
        current_liab_col = self._find_column(data, ['current_liabilities'])

        current_assets = data[current_assets_col] if current_assets_col else pd.Series(0, index=data.index)
        inventory = data[inventory_col] if inventory_col else pd.Series(0, index=data.index)
        current_liab = data[current_liab_col] if current_liab_col else pd.Series([1], index=data.index)

        quick_assets = current_assets - inventory
        qr = quick_assets / current_liab.replace(0, 1)

        return IndicatorResult(
            value=float(qr.mean()) if len(qr) > 0 else 0.0,
            unit="ratio",
            description="Quick Ratio",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=qr.tolist() if len(qr) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['current_assets', 'inventory', 'current_liabilities']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class DebtRatioIndicator(BaseIndicator):
    """Debt Ratio = Total Liabilities / Total Assets"""

    name = "debt_ratio"
    description = "Debt Ratio (Total Liabilities / Total Assets)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        liab_col = self._find_column(data, ['total_liabilities'])
        assets_col = self._find_column(data, ['total_assets'])

        liabilities = data[liab_col] if liab_col else pd.Series(0, index=data.index)
        assets = data[assets_col] if assets_col else pd.Series([1], index=data.index)

        dr = (liabilities / assets.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(dr.mean()) if len(dr) > 0 else 0.0,
            unit="%",
            description="Debt Ratio",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=dr.tolist() if len(dr) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['total_liabilities', 'total_assets']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
