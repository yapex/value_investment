"""Efficiency indicators: Asset Turnover, Inventory Turnover, Receivable Turnover, Payable Turnover."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class AssetTurnoverIndicator(BaseIndicator):
    """Asset Turnover = Operating Income / Total Assets"""

    name = "asset_turnover"
    description = "Asset Turnover (Operating Income / Total Assets)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        income_col = self._find_column(data, ['operating_income'])
        assets_col = self._find_column(data, ['total_assets'])

        income = data[income_col] if income_col else pd.Series([0], index=data.index)
        assets = data[assets_col] if assets_col else pd.Series([1], index=data.index)

        turnover = income / assets.replace(0, 1)

        return IndicatorResult(
            value=float(turnover.mean()) if len(turnover) > 0 else 0.0,
            unit="ratio",
            description="Asset Turnover",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=turnover.tolist() if len(turnover) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_income', 'total_assets']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class InventoryTurnoverIndicator(BaseIndicator):
    """Inventory Turnover = Operating Cost / Inventory"""

    name = "inventory_turnover"
    description = "Inventory Turnover (Operating Cost / Inventory)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        cost_col = self._find_column(data, ['operating_cost'])
        inv_col = self._find_column(data, ['inventory'])

        cost = data[cost_col] if cost_col else pd.Series([0], index=data.index)
        inv = data[inv_col] if inv_col else pd.Series([1], index=data.index)

        turnover = cost / inv.replace(0, 1)

        return IndicatorResult(
            value=float(turnover.mean()) if len(turnover) > 0 else 0.0,
            unit="ratio",
            description="Inventory Turnover",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=turnover.tolist() if len(turnover) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_cost', 'inventory']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class ReceivableTurnoverIndicator(BaseIndicator):
    """Receivable Turnover = Operating Income / Accounts Receivable"""

    name = "receivable_turnover"
    description = "Receivable Turnover (Operating Income / Accounts Receivable)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        income_col = self._find_column(data, ['operating_income'])
        ar_col = self._find_column(data, ['accounts_receivable'])

        income = data[income_col] if income_col else pd.Series([0], index=data.index)
        ar = data[ar_col] if ar_col else pd.Series([1], index=data.index)

        turnover = income / ar.replace(0, 1)

        return IndicatorResult(
            value=float(turnover.mean()) if len(turnover) > 0 else 0.0,
            unit="ratio",
            description="Receivable Turnover",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=turnover.tolist() if len(turnover) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_income', 'accounts_receivable']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class PayableTurnoverIndicator(BaseIndicator):
    """Payable Turnover = Operating Cost / Accounts Payable"""

    name = "payable_turnover"
    description = "Payable Turnover (Operating Cost / Accounts Payable)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        cost_col = self._find_column(data, ['operating_cost'])
        ap_col = self._find_column(data, ['accounts_payable'])

        cost = data[cost_col] if cost_col else pd.Series([0], index=data.index)
        ap = data[ap_col] if ap_col else pd.Series([1], index=data.index)

        turnover = cost / ap.replace(0, 1)

        return IndicatorResult(
            value=float(turnover.mean()) if len(turnover) > 0 else 0.0,
            unit="ratio",
            description="Payable Turnover",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=turnover.tolist() if len(turnover) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_cost', 'accounts_payable']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
