"""Complex financial indicators: ROIC, DCF, CAGR."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class ROICIndicator(BaseIndicator):
    """
    Return on Invested Capital = NOPAT / (Total Equity + Total Debt - Cash)

    NOPAT = Net Operating Profit After Tax
    = Operating Income * (1 - Tax Rate)
    """

    name = "ROIC"
    description = "Return on Invested Capital"
    type = IndicatorType.COMPLEX

    name = "ROIC"
    description = "Return on Invested Capital (NOPAT / Invested Capital)"

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get parameters
        tax_rate = kwargs.get("tax_rate", 0.25)  # Default 25%

        # Get data fields - use flexible column matching
        operating_income_col = self._find_column(data, [
            'operating_profit', 'OPERATING_PROFIT', '营业利润', 'OPERATE_PROFIT'
        ])
        operating_income = data[operating_income_col] if operating_income_col else pd.Series([0], index=data.index)

        # NOPAT = Operating Income * (1 - Tax Rate)
        nopat = operating_income * (1 - tax_rate)

        # Invested Capital = Total Assets - Interest-free Current Liabilities
        # Components: Accounts Payable + Contract Liab + Deposits + Staff Salary Payable + Tax Payable + Other Payable + Other Current Liabilities

        # Get total assets
        assets_col = self._find_column(data, ['total_assets', 'TOTAL_ASSETS', '资产总计', 'ASSET_BALANCE'])
        total_assets = data[assets_col] if assets_col else pd.Series([0], index=data.index)

        # Get interest-free current liabilities (all should be non-interest bearing)
        interest_free_liab = pd.Series(0, index=data.index)

        # Accounts Payable
        ap_col = self._find_column(data, ['accounts_payable', 'ACCOUNTS_PAYABLE', '应付账款'])
        if ap_col is not None:
            interest_free_liab = interest_free_liab + data[ap_col].fillna(0)

        # Contract Liabilities (预收款项/合同负债)
        cl_col = self._find_column(data, ['CONTRACT_LIAB', '合同负债', '预收款项'])
        if cl_col is not None:
            interest_free_liab = interest_free_liab + data[cl_col].fillna(0)

        # Deposits and Interbank Placements (吸收存款及同业存放)
        deposit_col = self._find_column(data, ['ACCEPT_DEPOSIT_INTERBANK', '吸收存款及同业存放'])
        if deposit_col is not None:
            interest_free_liab = interest_free_liab + data[deposit_col].fillna(0)

        # Staff Salary Payable (应付职工薪酬)
        ssp_col = self._find_column(data, ['STAFF_SALARY_PAYABLE', '应付职工薪酬'])
        if ssp_col is not None:
            interest_free_liab = interest_free_liab + data[ssp_col].fillna(0)

        # Tax Payable (应交税费)
        tp_col = self._find_column(data, ['TAX_PAYABLE', '应交税费'])
        if tp_col is not None:
            interest_free_liab = interest_free_liab + data[tp_col].fillna(0)

        # Other Payable (其他应付款)
        op_col = self._find_column(data, ['TOTAL_OTHER_PAYABLE', '其他应付款'])
        if op_col is not None:
            interest_free_liab = interest_free_liab + data[op_col].fillna(0)

        # Other Current Liabilities (其他流动负债)
        ocl_col = self._find_column(data, ['other_current_liabilities', 'OTHER_CURRENT_LIAB', '其他流动负债'])
        if ocl_col is not None:
            interest_free_liab = interest_free_liab + data[ocl_col].fillna(0)

        # Invested Capital = Total Assets - Interest-free Current Liabilities
        invested_capital = total_assets - interest_free_liab

        # ROIC = NOPAT / Invested Capital
        roic = nopat / invested_capital.replace(0, pd.NA) * 100
        roic = roic.dropna()

        return IndicatorResult(
            value=float(roic.mean()) if len(roic) > 0 else 0.0,
            unit="%",
            description="Return on Invested Capital",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=roic.tolist() if len(roic) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['operating_profit', 'total_assets', 'accounts_payable', 'advance_receivables', 'TAX_PAYABLE', 'OTHER_PAYABLE']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        """Find first matching column from candidates"""
        for col in candidates:
            if col in df.columns:
                return col
        # Try case-insensitive search
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class CAGRIndicator(BaseIndicator):
    """
    Compound Annual Growth Rate = (End Value / Start Value)^(1/years) - 1

    Can calculate for revenue, earnings, or any metric.
    """

    name = "CAGR"
    description = "Compound Annual Growth Rate"
    type = IndicatorType.COMPLEX

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        metric = kwargs.get("metric", "revenue")

        # Define column mappings for each metric
        metric_columns = {
            "revenue": ['operating_income', 'OPERATING_INCOME', '营业收入', 'total_revenue', 'TOTAL_REVENUE'],
            "net_profit": ['net_profit', 'NET_PROFIT', '净利润', 'parent_net_profit', 'PARENT_NET_PROFIT'],
            "total_assets": ['total_assets', 'TOTAL_ASSETS', '资产总计', 'ASSET_BALANCE'],
            "total_equity": ['total_equity', 'TOTAL_EQUITY', '股东权益', 'EQUITY_BALANCE']
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


class ImpliedGrowthIndicator(BaseIndicator):
    """
    Implied Growth Rate based on DCF model and market cap.

    Calculates the annual growth rate that justifies the current market cap,
    assuming a constant WACC and terminal growth rate.

    Formula:
    - Projects FCF for 10 years at growth rate g
    - Calculates terminal value at terminal_growth
    - Discounts all cash flows to present
    - Solves for g where PV equals market_cap
    """

    name = "ImpliedGrowth"
    description = "市场隐含增长率 (基于DCF模型)"
    type = IndicatorType.COMPLEX

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get parameters
        growth_rate = kwargs.get("growth_rate", 0.03)  # Terminal growth
        wacc = kwargs.get("wacc", 0.10)  # Weighted Average Cost of Capital
        market_cap = kwargs.get("market_cap", None)  # Required for implied growth

        # Calculate FCF = Operating Cash Flow - Capital Expenditure
        op_cash_flow_col = self._find_column(data, [
            'operating_cash_flow', 'OPERATING_CASH_FLOW', '经营活动现金流'
        ])
        capex_col = self._find_column(data, [
            'capital_expenditure', 'CAPITAL_EXPENDITURE', '资本支出'
        ])

        if not op_cash_flow_col:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description="Implied Growth (no cash flow data)",
                years=[],
                values=[]
            )

        operating_cf = data[op_cash_flow_col]
        capex = data[capex_col].fillna(0) if capex_col else 0
        fcf = operating_cf - capex

        if len(fcf) == 0 or fcf.iloc[-1] <= 0:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description=f"Implied Growth (invalid FCF)",
                years=[],
                values=[]
            )

        if not market_cap or market_cap <= 0:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description="Implied Growth (requires market_cap)",
                years=[],
                values=[]
            )

        # Calculate implied growth rate
        latest_fcf = fcf.iloc[-1]
        implied_growth = self._calculate_implied_growth(latest_fcf, market_cap, wacc, growth_rate)
        return IndicatorResult(
            value=implied_growth * 100,  # Convert to percentage
            unit="%",
            description=f"市场隐含增长率 (市值={market_cap/1e9:.0f}亿, WACC={wacc})",
            years=[int(data['year'].iloc[0])] if 'year' in data.columns else [],
            values=[]
        )

    def _calculate_implied_growth(self, current_fcf: float, market_cap: float, wacc: float, terminal_growth: float) -> float:
        """
        Calculate the implied annual growth rate given market cap.

        Uses a simplified approach with 10-year projection period:
        - Projects FCF for 10 years at implied growth rate g
        - Calculates terminal value at terminal_growth
        - Discounts all cash flows to present
        - Solves for g where PV equals market_cap
        """
        import numpy as np

        n_years = 10  # 10-year projection period for stability

        def dcf_value(g: float) -> float:
            """Calculate DCF value for a given growth rate"""
            if g >= wacc:
                return float('inf')
            if g <= -0.1:  # Cap minimum growth
                return 0

            # Project FCF for n years
            projected_fcf = [current_fcf * ((1 + g) ** i) for i in range(1, n_years + 1)]

            # Terminal value
            tv = (projected_fcf[-1] * (1 + terminal_growth)) / (wacc - terminal_growth)

            # Discount all cash flows
            pv = sum(fc / ((1 + wacc) ** i) for i, fc in enumerate(projected_fcf, 1))
            pv += tv / ((1 + wacc) ** n_years)

            return pv

        # Solve for g numerically using binary search
        # Search range: -5% to 30%
        low, high = -0.05, 0.30
        tolerance = 0.0001  # 0.01% precision

        for _ in range(100):  # Max iterations
            mid = (low + high) / 2
            pv = dcf_value(mid)

            if abs(pv - market_cap) / market_cap < tolerance:
                return mid

            if pv > market_cap:
                # Need lower growth to reduce value
                high = mid
            else:
                # Need higher growth to increase value
                low = mid

        return (low + high) / 2

    def get_required_fields(self) -> List[str]:
        return ['free_cash_flow', 'operating_cash_flow']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
