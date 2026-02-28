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

        income = data[income_col] if income_col else pd.Series(0, index=data.index)
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

        cost = data[cost_col] if cost_col else pd.Series(0, index=data.index)
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

        income = data[income_col] if income_col else pd.Series(0, index=data.index)
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

        cost = data[cost_col] if cost_col else pd.Series(0, index=data.index)
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


class ExpenseRatioIndicator(BaseIndicator):
    """Expense Ratio = (Operating Cost + Sales Expense + Management Expense + Financial Expense) / Operating Income"""

    name = "expense_ratio"
    description = "Expense Ratio ((Operating Cost + Sales/Management/Financial Expense) / Operating Income)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Total expenses = operating_cost + sales_expense + management_expense + financial_expense
        cost_col = self._find_column(data, ['operating_cost'])
        sales_exp_col = self._find_column(data, ['sales_expense'])
        mgmt_exp_col = self._find_column(data, ['management_expense'])
        fin_exp_col = self._find_column(data, ['financial_expense'])
        income_col = self._find_column(data, ['operating_income', 'total_revenue'])

        # Get expenses (default to 0 if not available)
        operating_cost = data[cost_col] if cost_col else pd.Series(0, index=data.index)
        sales_expense = data[sales_exp_col] if sales_exp_col else pd.Series(0, index=data.index)
        mgmt_expense = data[mgmt_exp_col] if mgmt_exp_col else pd.Series(0, index=data.index)
        fin_expense = data[fin_exp_col] if fin_exp_col else pd.Series(0, index=data.index)

        # Total expenses
        total_expense = operating_cost + sales_expense + mgmt_expense + fin_expense

        # Get income
        income = data[income_col] if income_col else pd.Series([1], index=data.index)

        # Calculate ratio (as percentage)
        expense_ratio = (total_expense / income.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(expense_ratio.mean()) if len(expense_ratio) > 0 else 0.0,
            unit="%",
            description="Expense Ratio",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=expense_ratio.tolist() if len(expense_ratio) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_cost', 'operating_income', 'sales_expense', 'management_expense', 'financial_expense']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class FeeRateIndicator(BaseIndicator):
    """Fee Rate = (Sales Expense + Management Expense + Financial Expense) / Operating Income"""

    name = "fee_rate"
    description = "Fee Rate ((Sales/Management/Financial Expense) / Operating Income)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Fee rate = (sales_expense + management_expense + financial_expense) / operating_income
        sales_exp_col = self._find_column(data, ['sales_expense'])
        mgmt_exp_col = self._find_column(data, ['management_expense'])
        fin_exp_col = self._find_column(data, ['financial_expense'])
        income_col = self._find_column(data, ['operating_income', 'total_revenue'])

        # Get fee expenses (default to 0 if not available)
        sales_expense = data[sales_exp_col] if sales_exp_col else pd.Series(0, index=data.index)
        mgmt_expense = data[mgmt_exp_col] if mgmt_exp_col else pd.Series(0, index=data.index)
        fin_expense = data[fin_exp_col] if fin_exp_col else pd.Series(0, index=data.index)

        # Total fee expenses
        total_fee = sales_expense + mgmt_expense + fin_expense

        # Get income
        income = data[income_col] if income_col else pd.Series([1], index=data.index)

        # Calculate ratio (as percentage)
        fee_rate = (total_fee / income.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(fee_rate.mean()) if len(fee_rate) > 0 else 0.0,
            unit="%",
            description="Fee Rate",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=fee_rate.tolist() if len(fee_rate) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_income', 'sales_expense', 'management_expense', 'financial_expense']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class FixedAssetTurnoverIndicator(BaseIndicator):
    """Fixed Asset Turnover = Operating Income / Fixed Assets"""

    name = "fixed_asset_turnover"
    description = "Fixed Asset Turnover (Operating Income / Fixed Assets)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Field mapping is done in API._get_financial_data
        income_col = self._find_column(data, ['operating_income'])
        fa_col = self._find_column(data, ['fixed_assets'])

        income = data[income_col] if income_col else pd.Series(0, index=data.index)
        fixed_assets = data[fa_col] if fa_col else pd.Series([1], index=data.index)

        turnover = income / fixed_assets.replace(0, 1)

        return IndicatorResult(
            value=float(turnover.mean()) if len(turnover) > 0 else 0.0,
            unit="ratio",
            description="Fixed Asset Turnover",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=turnover.tolist() if len(turnover) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_income', 'fixed_assets']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
