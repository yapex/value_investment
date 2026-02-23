"""Growth indicators: ROIC, CAGR."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class ROICIndicator(BaseIndicator):
    """
    Return on Invested Capital = NOPAT / Invested Capital

    Invested Capital = Shareholders' Equity + Interest-bearing Debt - Cash and Deposits

    This is the classic ROIC definition that reflects capital actually used in operations.
    Cash and deposits are subtracted because they don't generate operating returns.

    NOPAT = Net Operating Profit After Tax = Operating Income * (1 - Tax Rate)
    """

    name = "ROIC"
    description = "Return on Invested Capital (NOPAT / Invested Capital)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get parameters
        tax_rate = kwargs.get("tax_rate", None)  # Default: auto-detect from data
        use_avg_invested = kwargs.get("use_avg_invested", True)  # Use 2-year average by default

        # Field mapping is done in API._get_financial_data, so we use standardized field names
        operating_income_col = self._find_column(data, ['operating_profit'])
        operating_income = data[operating_income_col] if operating_income_col else pd.Series([0], index=data.index)

        # Try to get actual tax rate from data if not provided
        if tax_rate is None:
            tax_expense_col = self._find_column(data, ['income_tax'])
            pretax_income_col = self._find_column(data, ['total_profit'])

            if tax_expense_col and pretax_income_col:
                # Calculate actual tax rate row by row for each year
                tax_rates = data[tax_expense_col] / data[pretax_income_col]
                tax_rates = tax_rates.fillna(0.25)
                # Replace invalid values (inf, negative, >50%)
                tax_rates = tax_rates.replace([float('inf'), -float('inf')], 0.25)
                tax_rates = tax_rates.apply(lambda x: x if 0 < x < 0.5 else 0.25)
                # Use per-year tax rates for NOPAT calculation
                tax_rate_series = tax_rates
            else:
                tax_rate_series = pd.Series([0.25] * len(data), index=data.index)
        else:
            tax_rate_series = pd.Series([float(tax_rate)] * len(data), index=data.index)

        # NOPAT = Operating Income * (1 - Tax Rate) - use per-year tax rates
        nopat = operating_income * (1 - tax_rate_series)

        # === Classic ROIC Method ===
        # Invested Capital = Shareholders' Equity + Interest-bearing Debt - Cash and Deposits

        # 1. Get Total Equity
        equity_col = self._find_column(data, ['total_equity'])
        total_equity = data[equity_col].fillna(0) if equity_col is not None else pd.Series([0], index=data.index)

        # 2. Get Interest-bearing Debt
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

        # 3. Get Cash and Deposits
        cash = pd.Series(0, index=data.index)

        # Cash and cash equivalents
        cash_col = self._find_column(data, ['cash_and_equivalents'])
        if cash_col is not None:
            cash = cash + data[cash_col].fillna(0)

        # Note: 受限制存款及现金 (restricted cash) is intentionally NOT included
        # as it's not available for general business use and shouldn't be
        # subtracted from invested capital for ROIC calculation

        # Calculate Invested Capital
        invested_capital = total_equity + debt - cash

        # Use average invested capital if requested (2-year average)
        if use_avg_invested and len(invested_capital) >= 2:
            # Data is sorted descending by year (2024, 2023, ...)
            # Calculate 2-year average: (current + previous) / 2
            # For 2024: (2024 + 2023) / 2
            # For 2023: (2023 + 2022) / 2
            # Use bfill to handle first row: it will pair with the next available year
            invested_capital_shifted = invested_capital.shift(1)
            invested_capital_shifted.iloc[0] = invested_capital.iloc[1]  # Use 2023 for 2024
            invested_capital_avg = (invested_capital + invested_capital_shifted) / 2
            invested_capital = invested_capital_avg

        # ROIC = NOPAT / Invested Capital
        # Handle NaN values: convert to 0, then replace 0 with NA to drop invalid rows
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
        return ['operating_profit', 'total_assets', 'accounts_payable', 'advance_receivables', 'TAX_PAYABLE', 'OTHER_PAYABLE']

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
