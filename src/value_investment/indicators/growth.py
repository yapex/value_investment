"""Growth indicators: ROIC, CAGR."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class ROICIndicator(BaseIndicator):
    """
    Return on Invested Capital = NOPAT / Invested Capital

    Method 3 (专业机构常用):
    - NOPAT = Net Profit + Interest Expense × (1 - Tax Rate)
    - Invested Capital = Shareholders' Equity + Interest-bearing Debt
      (includes: short-term debt, long-term debt, bonds, lease liability, noncurrent liability due within 1 year)

    Note: This method does NOT subtract cash from invested capital, as cash is considered
    part of the capital used in operations for companies like Moutai with high cash balances.
    """

    name = "ROIC"
    description = "Return on Invested Capital (NOPAT / Invested Capital)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get parameters
        tax_rate = kwargs.get("tax_rate", None)  # Default: auto-detect from data
        use_avg_invested = kwargs.get("use_avg_invested", True)  # Use 2-year average by default

        # === NOPAT Calculation (Method 3) ===
        # NOPAT = Net Profit + Interest Expense × (1 - Tax Rate)

        # Get Net Profit
        net_profit_col = self._find_column(data, ['net_profit', 'parent_net_profit'])
        net_profit = data[net_profit_col].fillna(0) if net_profit_col else pd.Series(0, index=data.index)

        # Get Interest Expense (supports: interest_expense for A-share, finance_cost for HK)
        interest_expense_col = self._find_column(data, ['interest_expense', 'finance_cost'])
        interest_expense = data[interest_expense_col].fillna(0) if interest_expense_col else pd.Series(0, index=data.index)

        # Get tax rate
        if tax_rate is None:
            tax_expense_col = self._find_column(data, ['income_tax'])
            pretax_income_col = self._find_column(data, ['total_profit'])

            if tax_expense_col and pretax_income_col:
                tax_rates = data[tax_expense_col] / data[pretax_income_col]
                tax_rates = tax_rates.fillna(0.25)
                tax_rates = tax_rates.replace([float('inf'), -float('inf')], 0.25)
                tax_rates = tax_rates.apply(lambda x: x if 0 < x < 0.5 else 0.25)
                tax_rate_series = tax_rates
            else:
                tax_rate_series = pd.Series([0.25] * len(data), index=data.index)
        else:
            tax_rate_series = pd.Series([float(tax_rate)] * len(data), index=data.index)

        # NOPAT = Net Profit + Interest Expense × (1 - Tax Rate)
        nopat = net_profit + interest_expense * (1 - tax_rate_series)

        # === Invested Capital Calculation (Method 3) ===
        # Invested Capital = Shareholders' Equity + Interest-bearing Debt
        # Includes: equity + short-term debt + long-term debt + bonds + lease liability + noncurrent liability due within 1 year

        # 1. Get Total Equity
        equity_col = self._find_column(data, ['total_equity'])
        total_equity = data[equity_col].fillna(0) if equity_col is not None else pd.Series(0, index=data.index)

        # 2. Get Interest-bearing Debt (all types)
        debt = pd.Series(0, index=data.index)

        # Short-term debt
        short_debt_col = self._find_column(data, ['short_term_debt'])
        if short_debt_col is not None:
            debt = debt + data[short_debt_col].fillna(0)

        # Long-term debt
        long_debt_col = self._find_column(data, ['long_term_debt'])
        if long_debt_col is not None:
            debt = debt + data[long_debt_col].fillna(0)

        # Bonds payable
        bonds_col = self._find_column(data, ['bonds_payable'])
        if bonds_col is not None:
            debt = debt + data[bonds_col].fillna(0)

        # Lease liability
        lease_liab_col = self._find_column(data, ['lease_liability'])
        if lease_liab_col is not None:
            debt = debt + data[lease_liab_col].fillna(0)

        # Noncurrent liability due within 1 year
        noncurrent_1y_col = self._find_column(data, ['noncurrent_liability_due_1y'])
        if noncurrent_1y_col is not None:
            debt = debt + data[noncurrent_1y_col].fillna(0)

        # Calculate Invested Capital (Equity + Debt, NO cash subtraction)
        invested_capital = total_equity + debt

        # Use average invested capital if requested (2-year average)
        if use_avg_invested and len(invested_capital) >= 2:
            invested_capital_shifted = invested_capital.shift(1)
            invested_capital_shifted.iloc[0] = invested_capital.iloc[1]
            invested_capital_avg = (invested_capital + invested_capital_shifted) / 2
            invested_capital = invested_capital_avg

        # ROIC = NOPAT / Invested Capital
        invested_capital_clean = invested_capital.fillna(0).replace(0, pd.NA)
        roic = nopat / invested_capital_clean * 100
        roic = roic.dropna()

        return IndicatorResult(
            value=float(roic.mean()) if len(roic) > 0 else 0.0,
            unit="%",
            description="Return on Invested Capital (NOPAT / Invested Capital)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=roic.tolist() if len(roic) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['net_profit', 'interest_expense', 'income_tax', 'total_profit', 'total_equity', 'lease_liability', 'noncurrent_liability_due_1y']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        """Find first matching column from candidates - strict mode, no fallback"""
        for col in candidates:
            if col in df.columns:
                return col
        return None


class CAGRIndicator(BaseIndicator):
    """
    Compound Annual Growth Rate = (End Value / Start Value)^(1/years) - 1

    Can calculate for revenue, earnings, or any metric.
    """

    name = "CAGR"
    description = "Compound Annual Growth Rate"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        metric = kwargs.get("metric", "revenue")

        # Define column mappings for each metric (standardized field names after mapping)
        metric_columns = {
            "revenue": ['operating_income', 'total_revenue'],
            "net_profit": ['net_profit', 'parent_net_profit'],
            "total_assets": ['total_assets'],
            "total_equity": ['total_equity']
        }

        # Get candidates for the specific metric
        candidates = metric_columns.get(metric, [metric])

        # Find the metric column
        metric_col = self._find_column(data, candidates)

        if not metric_col:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description=f"CAGR for {metric}",
                years=[],
                values=[]
            )

        values = data[metric_col]

        # Need at least 2 data points
        if len(values) < 2:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description=f"CAGR for {metric}",
                years=[],
                values=[]
            )

        # Sort by year to ensure correct order (ascending)
        if 'year' in data.columns:
            sorted_idx = data['year'].argsort()
            values = values.iloc[sorted_idx]

        start_value = values.iloc[0]  # Earliest year
        end_value = values.iloc[-1]   # Latest year
        years = len(values) - 1  # Period is (n-1) years for n data points

        if start_value <= 0 or end_value <= 0:
            cagr = 0.0
        else:
            cagr = ((end_value / start_value) ** (1 / years) - 1) * 100

        # Build years list - use actual years from data if available
        years_list = data['year'].tolist() if 'year' in data.columns else []
        if not years_list:
            years_list = list(range(len(values)))

        return IndicatorResult(
            value=cagr,
            unit="%",
            description=f"Compound Annual Growth Rate for {metric}",
            years=years_list,
            values=[]  # CAGR is a period metric, show only value not per-year
        )

    def get_required_fields(self) -> List[str]:
        return ['revenue']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
