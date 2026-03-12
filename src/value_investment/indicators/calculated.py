"""Calculated indicators for HK missing metrics

港股缺失的关键指标补充：
- total_assets_turnover (总资产周转率)
- equity_multiplier (权益乘数)
- asset_turnover (资产周转率)
- total_assets (总资产)
- total_equity (股东权益)
- gross_margin (毛利率)
- operating_cash_flow (经营现金流)
"""

import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class TotalAssetsTurnoverIndicator(BaseIndicator):
    """Total Assets Turnover = Total Revenue / Total Assets

    总资产周转率 = 营业收入 / 总资产
    反映企业资产运营效率，是杜邦分析三要素之一
    """

    name = "total_assets_turnover"
    description = "Total Assets Turnover (总资产周转率 = 营业收入 / 总资产)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        revenue_col = self._find_column(data, ['total_revenue', 'operating_income', 'revenue'])
        assets_col = self._find_column(data, ['total_assets', 'TOTAL_ASSETS'])

        revenue = data[revenue_col] if revenue_col else pd.Series(0, index=data.index)
        total_assets = data[assets_col] if assets_col else pd.Series([1], index=data.index)

        # Avoid division by zero
        turnover = revenue / total_assets.replace(0, 1)

        return IndicatorResult(
            value=float(turnover.mean()) if len(turnover) > 0 else 0.0,
            unit="次",
            description="Total Assets Turnover (总资产周转率)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=turnover.tolist() if len(turnover) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['total_revenue', 'total_assets']


class EquityMultiplierIndicator(BaseIndicator):
    """Equity Multiplier = Total Assets / Total Equity = 1 / (1 - Debt Ratio)

    权益乘数 = 总资产 / 股东权益 = 1 / (1 - 资产负债率)
    反映企业财务杠杆水平，是杜邦分析三要素之一

    对于港股，可以从debt_ratio计算：equity_multiplier = 1 / (1 - debt_ratio/100)
    """

    name = "equity_multiplier"
    description = "Equity Multiplier (权益乘数 = 总资产 / 股东权益)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 优先使用总资产和股东权益计算
        assets_col = self._find_column(data, ['total_assets', 'TOTAL_ASSETS'])
        equity_col = self._find_column(data, ['total_equity', 'TOTAL_EQUITY', 'shareholders_equity'])

        if assets_col and equity_col:
            total_assets = data[assets_col]
            total_equity = data[equity_col]
            # Ensure Series type and avoid division by zero
            if not isinstance(total_equity, pd.Series):
                total_equity = pd.Series([total_equity])
            if not isinstance(total_assets, pd.Series):
                total_assets = pd.Series([total_assets])
            total_equity = total_equity.replace(0, 1)
            multiplier = total_assets / total_equity
        else:
            # 如果没有总资产/股东权益，从负债率计算
            debt_col = self._find_column(data, ['debt_ratio', 'debt_ratio_total', '资产负债率'])
            if debt_col:
                debt_ratio = data[debt_col] / 100  # Convert percentage to ratio
                # equity_multiplier = 1 / (1 - debt_ratio)
                # Handle edge case: debt_ratio >= 1
                denominator = (1 - debt_ratio).replace(0, 0.001)  # Avoid division by zero
                multiplier = 1 / denominator
            else:
                multiplier = pd.Series(1.0, index=data.index)  # Default to 1 (no leverage)

        return IndicatorResult(
            value=float(multiplier.mean()) if len(multiplier) > 0 else 1.0,
            unit="倍",
            description="Equity Multiplier (权益乘数)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=multiplier.tolist() if len(multiplier) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['total_assets', 'total_equity', 'debt_ratio']


class AssetTurnoverIndicator(BaseIndicator):
    """Asset Turnover = Total Revenue / Total Assets (alias for total_assets_turnover)"""

    name = "asset_turnover"
    description = "Asset Turnover (资产周转率 = 营业收入 / 总资产)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Delegate to TotalAssetsTurnoverIndicator
        indicator = TotalAssetsTurnoverIndicator()
        result = indicator.calculate(data, **kwargs)
        result.description = "Asset Turnover (资产周转率)"
        return result

    def get_required_fields(self) -> list[str]:
        return ['total_revenue', 'total_assets']


class TotalAssetsIndicator(BaseIndicator):
    """Total Assets - Direct value from balance sheet"""

    name = "total_assets"
    description = "Total Assets (总资产)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        assets_col = self._find_column(data, ['total_assets', 'TOTAL_ASSETS', '总资产'])

        if assets_col:
            total_assets = data[assets_col]
            return IndicatorResult(
                value=float(total_assets.mean()) if len(total_assets) > 0 else 0.0,
                unit="元",
                description="Total Assets (总资产)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=total_assets.tolist() if len(total_assets) > 0 else []
            )
        else:
            return IndicatorResult(
                value=0.0,
                unit="元",
                description="Total Assets (总资产)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[]
            )

    def get_required_fields(self) -> list[str]:
        return ['total_assets']


class TotalEquityIndicator(BaseIndicator):
    """Total Equity - Direct value from balance sheet"""

    name = "total_equity"
    description = "Total Equity (股东权益)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        equity_col = self._find_column(data, ['total_equity', 'TOTAL_EQUITY', 'shareholders_equity', '净资产'])

        if equity_col:
            total_equity = data[equity_col]
            return IndicatorResult(
                value=float(total_equity.mean()) if len(total_equity) > 0 else 0.0,
                unit="元",
                description="Total Equity (股东权益)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=total_equity.tolist() if len(total_equity) > 0 else []
            )
        else:
            return IndicatorResult(
                value=0.0,
                unit="元",
                description="Total Equity (股东权益)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[]
            )

    def get_required_fields(self) -> list[str]:
        return ['total_equity']


class GrossMarginIndicator(BaseIndicator):
    """Gross Margin = Gross Profit / Revenue * 100

    毛利率 = 毛利润 / 营业收入 * 100
    对于港股，可以使用gross_profit_margin字段
    """

    name = "gross_margin"
    description = "Gross Margin (毛利率 = 毛利润 / 营业收入 * 100)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 优先使用已有的gross_profit_margin字段
        gpm_col = self._find_column(data, ['gross_profit_margin', '毛利率'])

        if gpm_col:
            margin = data[gpm_col]
            return IndicatorResult(
                value=float(margin.mean()) if len(margin) > 0 else 0.0,
                unit="%",
                description="Gross Margin (毛利率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=margin.tolist() if len(margin) > 0 else []
            )

        # 如果没有gross_profit_margin，从毛利润和营收计算
        gp_col = self._find_column(data, ['gross_profit', '毛利'])
        revenue_col = self._find_column(data, ['total_revenue', 'operating_income', 'revenue', '营业额'])

        if gp_col and revenue_col:
            gross_profit = data[gp_col]
            revenue = data[revenue_col].replace(0, 1)
            margin = (gross_profit / revenue) * 100

            return IndicatorResult(
                value=float(margin.mean()) if len(margin) > 0 else 0.0,
                unit="%",
                description="Gross Margin (毛利率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=margin.tolist() if len(margin) > 0 else []
            )
        else:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description="Gross Margin (毛利率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[]
            )

    def get_required_fields(self) -> list[str]:
        return ['gross_profit_margin', 'gross_profit', 'total_revenue']


class OperatingCashFlowIndicator(BaseIndicator):
    """Operating Cash Flow = Operating Cash Flow Per Share * Total Shares

    经营现金流 = 每股经营现金流 * 总股本
    对于港股，可以从operating_cash_flow_per_share计算
    """

    name = "operating_cash_flow"
    description = "Operating Cash Flow (经营现金流)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 优先使用直接的经营现金流字段（精确匹配，避免匹配到operating_cash_flow_per_share）
        ocf_col = None
        if 'operating_cash_flow' in data.columns:
            ocf_col = 'operating_cash_flow'
        elif '经营业务现金净额' in data.columns:
            ocf_col = '经营业务现金净额'

        if ocf_col:
            ocf = data[ocf_col]
            return IndicatorResult(
                value=float(ocf.mean()) if len(ocf) > 0 else 0.0,
                unit="元",
                description="Operating Cash Flow (经营现金流)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=ocf.tolist() if len(ocf) > 0 else []
            )

        # 如果没有直接的经营现金流，从每股经营现金流计算
        ocfps_col = self._find_column(data, ['operating_cash_flow_per_share', '每股经营现金流'])
        shares_col = self._find_column(data, ['total_shares', '已发行股本'])

        if ocfps_col and shares_col:
            ocf_per_share = data[ocfps_col]
            total_shares = data[shares_col]
            ocf = ocf_per_share * total_shares

            return IndicatorResult(
                value=float(ocf.mean()) if len(ocf) > 0 else 0.0,
                unit="元",
                description="Operating Cash Flow (经营现金流)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=ocf.tolist() if len(ocf) > 0 else []
            )
        else:
            return IndicatorResult(
                value=0.0,
                unit="元",
                description="Operating Cash Flow (经营现金流)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[]
            )

    def get_required_fields(self) -> list[str]:
        return ['operating_cash_flow', 'operating_cash_flow_per_share', 'total_shares']


class NetProfitMarginIndicator(BaseIndicator):
    """Net Profit Margin = Net Profit / Revenue * 100

    净利润率 = 净利润 / 营业收入 * 100
    """

    name = "net_profit_margin"
    description = "Net Profit Margin (净利润率 = 净利润 / 营业收入 * 100)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 优先使用已有的net_profit_margin字段
        npm_col = self._find_column(data, ['net_profit_margin', '销售净利率'])

        if npm_col:
            margin = data[npm_col]
            return IndicatorResult(
                value=float(margin.mean()) if len(margin) > 0 else 0.0,
                unit="%",
                description="Net Profit Margin (净利润率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=margin.tolist() if len(margin) > 0 else []
            )

        # 如果没有，从净利润和营收计算
        np_col = self._find_column(data, ['net_profit', '净利润'])
        revenue_col = self._find_column(data, ['total_revenue', 'operating_income', 'revenue', '营业额'])

        if np_col and revenue_col:
            net_profit = data[np_col]
            revenue = data[revenue_col].replace(0, 1)
            margin = (net_profit / revenue) * 100

            return IndicatorResult(
                value=float(margin.mean()) if len(margin) > 0 else 0.0,
                unit="%",
                description="Net Profit Margin (净利润率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=margin.tolist() if len(margin) > 0 else []
            )
        else:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description="Net Profit Margin (净利润率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[]
            )

    def get_required_fields(self) -> list[str]:
        return ['net_profit_margin', 'net_profit', 'total_revenue']


class ROEIndicator(BaseIndicator):
    """ROE = Net Profit / Total Equity * 100

    净资产收益率 = 净利润 / 股东权益 * 100
    """

    name = "roe"
    description = "ROE (净资产收益率 = 净利润 / 股东权益 * 100)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 优先使用已有的roe字段
        roe_col = self._find_column(data, ['roe', '股东权益回报率'])

        if roe_col:
            roe = data[roe_col]
            return IndicatorResult(
                value=float(roe.mean()) if len(roe) > 0 else 0.0,
                unit="%",
                description="ROE (净资产收益率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=roe.tolist() if len(roe) > 0 else []
            )

        # 如果没有，从净利润和股东权益计算
        np_col = self._find_column(data, ['net_profit', '净利润'])
        equity_col = self._find_column(data, ['total_equity', '净资产'])

        if np_col and equity_col:
            net_profit = data[np_col]
            total_equity = data[equity_col].replace(0, 1)
            roe = (net_profit / total_equity) * 100

            return IndicatorResult(
                value=float(roe.mean()) if len(roe) > 0 else 0.0,
                unit="%",
                description="ROE (净资产收益率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=roe.tolist() if len(roe) > 0 else []
            )
        else:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description="ROE (净资产收益率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[]
            )

    def get_required_fields(self) -> list[str]:
        return ['roe', 'net_profit', 'total_equity']


class ROAIndicator(BaseIndicator):
    """ROA = Net Profit / Total Assets * 100

    总资产收益率 = 净利润 / 总资产 * 100
    """

    name = "roa"
    description = "ROA (总资产收益率 = 净利润 / 总资产 * 100)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 优先使用已有的roa字段
        roa_col = self._find_column(data, ['roa', '总资产回报率'])

        if roa_col:
            roa = data[roa_col]
            return IndicatorResult(
                value=float(roa.mean()) if len(roa) > 0 else 0.0,
                unit="%",
                description="ROA (总资产收益率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=roa.tolist() if len(roa) > 0 else []
            )

        # 如果没有，从净利润和总资产计算
        np_col = self._find_column(data, ['net_profit', '净利润'])
        assets_col = self._find_column(data, ['total_assets', '总资产'])

        if np_col and assets_col:
            net_profit = data[np_col]
            total_assets = data[assets_col].replace(0, 1)
            roa = (net_profit / total_assets) * 100

            return IndicatorResult(
                value=float(roa.mean()) if len(roa) > 0 else 0.0,
                unit="%",
                description="ROA (总资产收益率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=roa.tolist() if len(roa) > 0 else []
            )
        else:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description="ROA (总资产收益率)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[]
            )

    def get_required_fields(self) -> list[str]:
        return ['roa', 'net_profit', 'total_assets']
