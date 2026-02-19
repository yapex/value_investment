"""Simple financial indicators: ROE, ROA, Gross Margin, etc."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class ROEIndicator(BaseIndicator):
    """Return on Equity = Net Profit / Shareholder's Equity"""

    name = "ROE"
    description = "Return on Equity (Net Profit / Shareholder's Equity)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Map column names - akshare uses uppercase with underscores
        # 港股: 除税后溢利, 股东应占溢利, 总权益, 股东权益
        net_profit_col = self._find_column(data, [
            'net_profit', 'NET_PROFIT', '净利润', 'NET_PROFIT_ATTRIBUTABLE',
            '除税后溢利', '股东应占溢利', '经营溢利'
        ])
        equity_col = self._find_column(data, [
            'total_equity', 'TOTAL_EQUITY', '股东权益', 'HOLDERS_EQUITY',
            '总权益'
        ])

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
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 港股: 除税后溢利, 股东应占溢利, 总资产
        net_profit_col = self._find_column(data, [
            'net_profit', 'NET_PROFIT', '净利润', '除税后溢利', '股东应占溢利', '经营溢利'
        ])
        assets_col = self._find_column(data, [
            'total_assets', 'TOTAL_ASSETS', '资产总计', 'ASSET_BALANCE', '总资产'
        ])

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
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 港股: 营业额, 营运收入, 营运支出
        revenue_col = self._find_column(data, [
            'revenue', 'REVENUE', '营业收入', 'OPERATING_REVENUE',
            '营业额', '营运收入'
        ])
        cogs_col = self._find_column(data, [
            'cost_of_sales', 'COST_OF_SALES', '营业成本', 'OPERATING_COST',
            '营运支出'
        ])

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
    type = IndicatorType.CALCULATED

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
    type = IndicatorType.CALCULATED

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


class AssetTurnoverIndicator(BaseIndicator):
    """Asset Turnover = Operating Income / Total Assets"""

    name = "asset_turnover"
    description = "Asset Turnover (Operating Income / Total Assets)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        income_col = self._find_column(data, ['operating_income', 'OPERATING_INCOME', '营业收入'])
        assets_col = self._find_column(data, ['total_assets', 'TOTAL_ASSETS', '资产总计', 'ASSET_BALANCE'])

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
        cost_col = self._find_column(data, ['operating_cost', 'OPERATING_COST', '营业成本'])
        inv_col = self._find_column(data, ['inventory', 'INVENTORY', '存货'])

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


class QuickRatioIndicator(BaseIndicator):
    """Quick Ratio = (Current Assets - Inventory) / Current Liabilities"""

    name = "quick_ratio"
    description = "Quick Ratio ((Current Assets - Inventory) / Current Liabilities)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        current_assets_col = self._find_column(data, ['current_assets', 'CURRENT_ASSET_BALANCE', '流动资产'])
        inventory_col = self._find_column(data, ['inventory', 'INVENTORY', '存货'])
        current_liab_col = self._find_column(data, ['current_liabilities', 'CURRENT_LIAB_BALANCE', '流动负债'])

        current_assets = data[current_assets_col] if current_assets_col else pd.Series([0], index=data.index)
        inventory = data[inventory_col] if inventory_col else pd.Series([0], index=data.index)
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

    def get_required_fields(self) -> List[str]:
        return ['current_assets', 'inventory', 'current_liabilities']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
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
        liab_col = self._find_column(data, ['total_liabilities', 'TOTAL_LIABILITIES', '负债合计', 'LIAB_BALANCE'])
        assets_col = self._find_column(data, ['total_assets', 'TOTAL_ASSETS', '资产总计', 'ASSET_BALANCE'])

        liabilities = data[liab_col] if liab_col else pd.Series([0], index=data.index)
        assets = data[assets_col] if assets_col else pd.Series([1], index=data.index)

        dr = (liabilities / assets.replace(0, 1)) * 100

        return IndicatorResult(
            value=float(dr.mean()) if len(dr) > 0 else 0.0,
            unit="%",
            description="Debt Ratio",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=dr.tolist() if len(dr) > 0 else []
        )

    def get_required_fields(self) -> List[str]:
        return ['total_liabilities', 'total_assets']

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
        income_col = self._find_column(data, ['operating_income', 'OPERATING_INCOME', '营业收入'])
        ar_col = self._find_column(data, ['accounts_receivable', 'ACCOUNTS_RECEIVE', '应收账款'])

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
        cost_col = self._find_column(data, ['operating_cost', 'OPERATING_COST', '营业成本'])
        ap_col = self._find_column(data, ['accounts_payable', 'ACCOUNTS_PAYABLE', '应付账款'])

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


class CfoToNetprofitIndicator(BaseIndicator):
    """CFO to Net Profit = Operating Cash Flow / Net Profit"""

    name = "cfo_to_netprofit"
    description = "Operating Cash Flow to Net Profit"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # HK: 经营业务现金净额, 股东应占溢利
        cfo_col = self._find_column(data, ['operating_cash_flow', 'OPERATE_NETCASH_BALANCE', '经营活动产生的现金流量净额', '经营业务现金净额'])
        np_col = self._find_column(data, ['net_profit', 'NET_PROFIT', '净利润', '股东应占溢利'])

        cfo = data[cfo_col] if cfo_col else pd.Series([0], index=data.index)
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
        fcf_col = self._find_column(data, ['free_cash_flow', 'FREE_CASH_FLOW', '自由现金流'])
        income_col = self._find_column(data, ['operating_income', 'OPERATING_INCOME', '营业收入'])

        fcf = data[fcf_col] if fcf_col else pd.Series([0], index=data.index)
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


class LatestMarketCapIndicator(BaseIndicator):
    """
    最新市值指标

    通过最新收盘价（不复权）* 股数计算当前市值。
    用于 ImpliedGrowth 等需要最新市值的指标。
    """

    name = "latest_market_cap"
    description = "最新市值 (最新收盘价 × 股数)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        provider = kwargs.get('provider')
        stock_code = kwargs.get('stock_code')

        if not provider or not stock_code:
            return IndicatorResult(
                value=0.0,
                unit="",
                description="最新市值 (需要provider和stock_code)",
                years=[],
                values=[]
            )

        try:
            # 1. 从财务指标获取股本
            finind = provider.get_financial_indicator(stock_code)
            if finind.empty:
                return IndicatorResult(
                    value=0.0,
                    unit="",
                    description="最新市值 (无法获取财务指标)",
                    years=[],
                    values=[]
                )

            # 获取股本 - 支持多市场字段
            total_shares = None
            shares_cols = ['已发行股本(股)', 'total_shares', '总股本']
            for col in shares_cols:
                if col in finind.columns:
                    total_shares = float(finind[col].iloc[0])
                    break

            if not total_shares or total_shares <= 0:
                return IndicatorResult(
                    value=0.0,
                    unit="",
                    description="最新市值 (无法获取股本)",
                    years=[],
                    values=[]
                )

            # 2. 获取最新收盘价（不复权）
            from datetime import datetime
            today = datetime.now().strftime("%Y%m%d")
            hist = provider.get_historical_data(stock_code, today, adjust="")

            if hist.empty:
                return IndicatorResult(
                    value=0.0,
                    unit="",
                    description="最新市值 (无法获取历史数据)",
                    years=[],
                    values=[]
                )

            # 获取最新收盘价
            close_col = '收盘' if '收盘' in hist.columns else 'close'
            latest_price = float(hist[close_col].iloc[-1])

            if latest_price <= 0:
                return IndicatorResult(
                    value=0.0,
                    unit="",
                    description="最新市值 (股价无效)",
                    years=[],
                    values=[]
                )

            # 3. 计算市值
            market_cap = latest_price * total_shares

            return IndicatorResult(
                value=market_cap,
                unit="",
                description=f"最新市值 (股价={latest_price:.2f}, 股本={total_shares/1e8:.2f}亿)",
                years=[],
                values=[]
            )

        except Exception as e:
            return IndicatorResult(
                value=0.0,
                unit="",
                description=f"最新市值 (计算错误: {str(e)})",
                years=[],
                values=[]
            )

    def get_required_fields(self) -> List[str]:
        return []

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
        # HK: 经营业务现金净额, 股东应占溢利
        cfo_col = self._find_column(data, ['NETCASH_OPERATE', 'OPERATE_NETCASH_BALANCE', 'operating_cash_flow', '经营活动产生的现金流量净额', '经营业务现金净额'])
        np_col = self._find_column(data, ['NETPROFIT', 'PARENT_NETPROFIT', 'net_profit', 'NET_PROFIT', '净利润', '股东应占溢利'])

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
