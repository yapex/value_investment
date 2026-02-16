"""Simple financial indicators: ROE, ROA, Gross Margin, etc."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult


class ROEIndicator(BaseIndicator):
    """Return on Equity = Net Profit / Shareholder's Equity"""

    name = "ROE"
    description = "Return on Equity (Net Profit / Shareholder's Equity)"

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Map column names - akshare uses uppercase with underscores
        net_profit_col = self._find_column(data, ['net_profit', 'NET_PROFIT', '净利润', 'NET_PROFIT_ATTRIBUTABLE'])
        equity_col = self._find_column(data, ['total_equity', 'TOTAL_EQUITY', '股东权益', 'HOLDERS_EQUITY'])

        net_profit = data[net_profit_col] if net_profit_col else pd.Series([0], index=data.index)
        equity = data[equity_col] if equity_col else pd.Series([1], index=data.index)

        # Avoid division by zero
        roe = (net_profit / equity.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(roe.mean()) if len(roe) > 0 else 0.0,
            unit="%",
            description="Return on Equity",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=roe.tolist() if len(roe) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['net_profit', 'total_equity']

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


class ROAIndicator(BaseIndicator):
    """Return on Assets = Net Profit / Total Assets"""

    name = "ROA"
    description = "Return on Assets (Net Profit / Total Assets)"

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        net_profit_col = self._find_column(data, ['net_profit', 'NET_PROFIT', '净利润'])
        assets_col = self._find_column(data, ['total_assets', 'TOTAL_ASSETS', '资产总计', 'ASSET_BALANCE'])

        net_profit = data[net_profit_col] if net_profit_col else pd.Series([0], index=data.index)
        assets = data[assets_col] if assets_col else pd.Series([1], index=data.index)

        roa = (net_profit / assets.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(roa.mean()) if len(roa) > 0 else 0.0,
            unit="%",
            description="Return on Assets",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=roa.tolist() if len(roa) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['net_profit', 'total_assets']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class GrossMarginIndicator(BaseIndicator):
    """Gross Margin = (Revenue - COGS) / Revenue"""

    name = "gross_margin"
    description = "Gross Margin ((Revenue - COGS) / Revenue)"

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        revenue_col = self._find_column(data, ['revenue', 'REVENUE', '营业收入', 'OPERATING_REVENUE'])
        cogs_col = self._find_column(data, ['cost_of_sales', 'COST_OF_SALES', '营业成本', 'OPERATING_COST'])

        revenue = data[revenue_col] if revenue_col else pd.Series([0], index=data.index)
        cogs = data[cogs_col] if cogs_col else pd.Series([0], index=data.index)

        gross_profit = revenue - cogs
        gross_margin = (gross_profit / revenue.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(gross_margin.mean()) if len(gross_margin) > 0 else 0.0,
            unit="%",
            description="Gross Margin",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=gross_margin.tolist() if len(gross_margin) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['revenue', 'cost_of_sales']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class NetProfitMarginIndicator(BaseIndicator):
    """Net Profit Margin = Net Profit / Revenue"""

    name = "net_profit_margin"
    description = "Net Profit Margin (Net Profit / Revenue)"

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        net_profit_col = self._find_column(data, ['net_profit', 'NET_PROFIT', '净利润'])
        revenue_col = self._find_column(data, ['revenue', 'REVENUE', '营业收入'])

        net_profit = data[net_profit_col] if net_profit_col else pd.Series([0], index=data.index)
        revenue = data[revenue_col] if revenue_col else pd.Series([1], index=data.index)

        npm = (net_profit / revenue.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(npm.mean()) if len(npm) > 0 else 0.0,
            unit="%",
            description="Net Profit Margin",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=npm.tolist() if len(npm) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['net_profit', 'revenue']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class CurrentRatioIndicator(BaseIndicator):
    """Current Ratio = Current Assets / Current Liabilities"""

    name = "current_ratio"
    description = "Current Ratio (Current Assets / Current Liabilities)"

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        current_assets_col = self._find_column(data, ['current_assets', 'CURRENT_ASSETS', '流动资产', 'CURRENT_ASSET_BALANCE'])
        current_liab_col = self._find_column(data, ['current_liabilities', 'CURRENT_LIAB', '流动负债', 'CURRENT_LIAB_BALANCE'])

        current_assets = data[current_assets_col] if current_assets_col else pd.Series([0], index=data.index)
        current_liab = data[current_liab_col] if current_liab_col else pd.Series([1], index=data.index)

        cr = current_assets / current_liab.replace(0, 1)

        return IndicatorResult(
            value=float(cr.mean()) if len(cr) > 0 else 0.0,
            unit="ratio",
            description="Current Ratio",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=cr.tolist() if len(cr) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['current_assets', 'current_liabilities']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
