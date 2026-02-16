"""Complex financial indicators: ROIC, DCF, CAGR."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult


class ROICIndicator(BaseIndicator):
    """
    Return on Invested Capital = NOPAT / (Total Equity + Total Debt - Cash)

    NOPAT = Net Operating Profit After Tax
    = Operating Income * (1 - Tax Rate)
    """

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
            years=[int(y) for y in data.index.tolist()] if hasattr(data.index, 'tolist') else []
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

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        metric = kwargs.get("metric", "revenue")

        # Find the metric column
        metric_col = self._find_column(data, [
            metric.lower(),
            metric.upper(),
            'revenue', 'REVENUE', '营业收入',
            'net_profit', 'NET_PROFIT', '净利润',
            'total_assets', 'TOTAL_ASSETS', '资产总计',
            'total_equity', 'TOTAL_EQUITY', '股东权益'
        ])

        if not metric_col:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description=f"CAGR for {metric}",
                years=[]
            )

        values = data[metric_col]

        # Need at least 2 data points
        if len(values) < 2:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description=f"CAGR for {metric}",
                years=[]
            )

        start_value = values.iloc[0]
        end_value = values.iloc[-1]
        years = len(values)

        if start_value <= 0 or end_value <= 0:
            cagr = 0.0
        else:
            cagr = ((end_value / start_value) ** (1 / years) - 1) * 100

        return IndicatorResult(
            value=cagr,
            unit="%",
            description=f"Compound Annual Growth Rate for {metric}",
            years=list(range(years))
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


class DCFIndicator(BaseIndicator):
    """
    Discounted Cash Flow valuation

    Terminal Value = Final FCF * (1 + g) / (WACC - g)
    Enterprise Value = Sum of discounted FCFs + Terminal Value
    """

    name = "DCF"
    description = "DCF Valuation"

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get parameters
        growth_rate = kwargs.get("growth_rate", 0.03)  # Terminal growth
        wacc = kwargs.get("wacc", 0.10)  # Weighted Average Cost of Capital
        discount_rate = kwargs.get("discount_rate", wacc)

        # Get free cash flow - try multiple column names
        fcf_col = self._find_column(data, [
            'free_cash_flow', 'FREE_CASH_FLOW', '自由现金流',
            'operating_cash_flow', 'OPERATING_CASH_FLOW', '经营活动现金流'
        ])

        if not fcf_col:
            return IndicatorResult(
                value=0.0,
                unit="CNY",
                description="DCF Valuation (no FCF data)",
                years=[]
            )

        fcf = data[fcf_col]

        if len(fcf) == 0 or fcf.iloc[-1] <= 0:
            return IndicatorResult(
                value=0.0,
                unit="CNY",
                description=f"DCF Valuation (WACC={wacc}, g={growth_rate})",
                years=[]
            )

        # Calculate terminal value
        final_fcf = fcf.iloc[-1]

        # Avoid division by zero or negative denominator
        if wacc <= growth_rate:
            return IndicatorResult(
                value=0.0,
                unit="CNY",
                description=f"DCF Valuation (invalid WACC <= growth rate)",
                years=[]
            )

        terminal_value = (final_fcf * (1 + growth_rate)) / (wacc - growth_rate)

        # Discount FCFs and terminal value
        total_value = 0.0
        for i, fc in enumerate(fcf):
            total_value += fc / ((1 + discount_rate) ** (i + 1))

        # Add terminal value
        total_value += terminal_value / ((1 + discount_rate) ** len(fcf))

        return IndicatorResult(
            value=total_value,
            unit="CNY",
            description=f"DCF Valuation (WACC={wacc}, g={growth_rate})",
            years=[int(y) for y in data.index.tolist()] if hasattr(data.index, 'tolist') else []
        )

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
