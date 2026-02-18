"""Complex financial indicators: ROIC, DCF, CAGR."""
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

        # Get data fields - use flexible column matching
        # HK: 经营溢利, A股: 营业利润
        operating_income_col = self._find_column(data, [
            'operating_profit', 'OPERATING_PROFIT', '营业利润', 'OPERATE_PROFIT', '经营溢利'
        ])
        operating_income = data[operating_income_col] if operating_income_col else pd.Series([0], index=data.index)

        # Try to get actual tax rate from data if not provided
        # HK: 税项, A股: 所得税费用 / 除税前溢利, 除税前利润
        if tax_rate is None:
            tax_expense_col = self._find_column(data, ['税项', 'TAX_EXPENSE', '所得税费用', 'income_tax'])
            pretax_income_col = self._find_column(data, ['除税前溢利', '除税前利润', 'pretax_income', 'profit_before_tax'])

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

        # 1. Get Total Equity (权益总额/总权益)
        # HK: 总权益, A股: 股东权益/归属于母公司所有者权益
        equity_col = self._find_column(data, [
            'total_equity', 'TOTAL_EQUITY', '总权益', '股东权益', 'EQUITY_BALANCE', '归属于母公司所有者权益'
        ])
        total_equity = data[equity_col].fillna(0) if equity_col is not None else pd.Series([0], index=data.index)

        # 2. Get Interest-bearing Debt (有息负债)
        # HK: 短期贷款 + 长期贷款, A股: 短期借款 + 长期借款
        debt = pd.Series(0, index=data.index)

        # Short-term debt
        short_debt_col = self._find_column(data, [
            'short_term_loan', 'SHORT_TERM_LOAN', '短期借款', '短期贷款'
        ])
        if short_debt_col is not None:
            debt = debt + data[short_debt_col].fillna(0)

        # Long-term debt
        long_debt_col = self._find_column(data, [
            'long_term_loan', 'LONG_TERM_LOAN', '长期借款', '长期贷款'
        ])
        if long_debt_col is not None:
            debt = debt + data[long_debt_col].fillna(0)

        # Bonds payable (应付债券)
        bonds_col = self._find_column(data, ['应付债券', 'BONDS_PAYABLE'])
        if bonds_col is not None:
            debt = debt + data[bonds_col].fillna(0)

        # Notes payable (应付票据) - HK uses both 流动 and 非流动
        for notes_field in ['应付票据', '应付票据(非流动)']:
            if notes_field in data.columns:
                debt = debt + data[notes_field].fillna(0)

        # 3. Get Cash and Deposits (现金及存款)
        cash = pd.Series(0, index=data.index)

        # Cash and cash equivalents
        cash_col = self._find_column(data, [
            'cash_equivalents', 'CASH_EQUIVALENTS', '现金及等价物', '货币资金'
        ])
        if cash_col is not None:
            cash = cash + data[cash_col].fillna(0)

        # Short-term deposits (短期存款)
        short_deposit_col = self._find_column(data, ['短期存款', 'SHORT_TERM_DEPOSIT'])
        if short_deposit_col is not None:
            cash = cash + data[short_deposit_col].fillna(0)

        # Long-term deposits (中长期存款)
        long_deposit_col = self._find_column(data, ['中长期存款', 'LONG_TERM_DEPOSIT'])
        if long_deposit_col is not None:
            cash = cash + data[long_deposit_col].fillna(0)

        # Term deposits (定期存款)
        term_deposit_col = self._find_column(data, ['定期存款', 'TERM_DEPOSIT'])
        if term_deposit_col is not None:
            cash = cash + data[term_deposit_col].fillna(0)

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
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        metric = kwargs.get("metric", "revenue")

        # Define column mappings for each metric
        # HK fields: 营业额/营运收入, 股东应占溢利, 总资产, 股东权益
        metric_columns = {
            "revenue": ['operating_income', 'OPERATING_INCOME', '营业收入', 'total_revenue', 'TOTAL_REVENUE', '营业额', '营运收入'],
            "net_profit": ['net_profit', 'NET_PROFIT', '净利润', 'parent_net_profit', 'PARENT_NET_PROFIT', '股东应占溢利'],
            "total_assets": ['total_assets', 'TOTAL_ASSETS', '资产总计', 'ASSET_BALANCE', '总资产'],
            "total_equity": ['total_equity', 'TOTAL_EQUITY', '股东权益', 'EQUITY_BALANCE', '股东权益']
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
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get parameters
        growth_rate = kwargs.get("growth_rate", 0.03)  # Terminal growth
        wacc = kwargs.get("wacc", 0.10)  # Weighted Average Cost of Capital
        market_cap = kwargs.get("market_cap", None)  # Required for implied growth

        # Calculate FCF = Operating Cash Flow - Capital Expenditure
        # HK: 经营业务现金净额, A股: 经营活动现金流
        op_cash_flow_col = self._find_column(data, [
            'operating_cash_flow', 'OPERATING_CASH_FLOW', '经营活动现金流', '经营业务现金净额'
        ])
        # HK: 购建固定资产, A股: 资本支出
        capex_col = self._find_column(data, [
            'capital_expenditure', 'CAPITAL_EXPENDITURE', '资本支出', '购建固定资产'
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


class PEPercentileIndicator(BaseIndicator):
    """
    PE历史百分位指标

    计算当前PE在历史PE序列中的百分位，用于判断估值高低。
    使用年度净利润和年末股价计算PE。
    """

    name = "PEPct"
    description = "PE历史百分位"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """计算PE历史百分位

        需要通过provider获取额外数据：历史股价、当前市值、股本
        """
        # 从kwargs获取provider和数据
        provider = kwargs.get('provider')
        stock_code = kwargs.get('stock_code')
        years = kwargs.get('years', 10)

        if not provider or not stock_code:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description="PE历史百分位 (需要stock_code参数)",
                years=[],
                values=[]
            )

        try:
            # 1. 获取个股信息（获取总股本和当前市值）
            info = provider.get_stock_info(stock_code)
            total_shares = None
            current_market_cap = None

            if 'item' in info.columns:
                for _, row in info.iterrows():
                    item = str(row['item'])
                    if '总股本' in item:
                        total_shares = float(row['value'])
                    elif '总市值' in item:
                        current_market_cap = float(row['value'])

            if not total_shares or not current_market_cap:
                return IndicatorResult(
                    value=0.0,
                    unit="%",
                    description="PE历史百分位 (无法获取股本/市值数据)",
                    years=[],
                    values=[]
                )

            # 2. 获取年度净利润数据
            from datetime import datetime
            current_year = datetime.now().year

            # 使用provider获取利润表数据
            profit_sheet = provider.get_profit_sheet(stock_code, current_year)

            if profit_sheet.empty:
                return IndicatorResult(
                    value=0.0,
                    unit="%",
                    description="PE历史百分位 (无利润表数据)",
                    years=[],
                    values=[]
                )

            # 提取净利润列（优先使用扣非归母净利润，更合理）
            net_profit_col = self._find_column(profit_sheet, [
                'DEDUCT_PARENT_NETPROFIT', '扣非归母净利润',  # 扣非归母净利润
                'PARENT_NETPROFIT', '归母净利润',  # 归母净利润
                'NETPROFIT', 'net_profit', '净利润',  # 净利润
            ])

            if not net_profit_col:
                return IndicatorResult(
                    value=0.0,
                    unit="%",
                    description="PE历史百分位 (无净利润数据)",
                    years=[],
                    values=[]
                )

            # 3. 提取年份和净利润
            if 'year' not in profit_sheet.columns:
                if 'REPORT_DATE' in profit_sheet.columns:
                    profit_sheet['year'] = pd.to_datetime(profit_sheet['REPORT_DATE']).dt.year
                elif 'REPORT_DATE_NAME' in profit_sheet.columns:
                    profit_sheet['year'] = profit_sheet['REPORT_DATE_NAME'].astype(str).str.extract(r'(\d{4})')[0].astype(float)

            # 过滤出年报数据（年份匹配）
            profit_sheet = profit_sheet[profit_sheet['year'].notna()].copy()
            profit_sheet = profit_sheet.sort_values('year', ascending=False)

            # 只取最近N年的数据
            profit_sheet = profit_sheet.head(years)

            # 4. 获取每年的年末股价，计算PE
            pe_list = []
            valid_years = []

            for _, row in profit_sheet.iterrows():
                year = int(row['year'])
                net_profit = row[net_profit_col]

                # 跳过无效净利润
                if pd.isna(net_profit) or net_profit <= 0:
                    continue

                # 获取该年最后一天的股价（不复权，用于计算历史PE）
                try:
                    year_end = f"{year}1231"
                    # 使用不复权价格(adjust="")计算历史PE，避免后复权高估市值
                    hist = provider.get_historical_data(stock_code, year_end, adjust="")
                    if hist.empty:
                        hist = provider.get_historical_data(stock_code, f"{year}1231", adjust="")
                        if hist.empty:
                            continue

                    # 获取最后一天的收盘价 (支持中文"收盘"和英文"close")
                    close_col = '收盘' if '收盘' in hist.columns else 'close'
                    last_price = hist[close_col].iloc[-1]
                    if pd.isna(last_price) or last_price <= 0:
                        continue

                    # 计算市值 = 股价 × 总股本
                    market_cap = last_price * total_shares

                    # 计算PE = 市值 / 净利润
                    pe = market_cap / net_profit
                    if pe > 0 and pe < 1000:  # 过滤异常值
                        pe_list.append(pe)
                        valid_years.append(year)
                except Exception:
                    continue

            if len(pe_list) < 3:
                return IndicatorResult(
                    value=0.0,
                    unit="%",
                    description=f"PE历史百分位 (数据不足，仅{len(pe_list)}年)",
                    years=valid_years,
                    values=pe_list
                )

            # 5. 计算当前PE
            # 当前市值已经获取，用当前市值 / 最近年度净利润
            latest_year = valid_years[0]
            latest_net_profit = profit_sheet[profit_sheet['year'] == latest_year][net_profit_col].iloc[0]
            current_pe = current_market_cap / latest_net_profit if latest_net_profit > 0 else 0

            # 6. 计算百分位
            percentile = sum(1 for pe in pe_list if pe < current_pe) / len(pe_list) * 100

            # 计算历史PE范围
            pe_min = min(pe_list)
            pe_max = max(pe_list)
            pe_median = sorted(pe_list)[len(pe_list) // 2]

            # 返回结果
            return IndicatorResult(
                value=percentile,
                unit="%",
                description=f"PE历史百分位 (当前PE: {current_pe:.1f}x, 历史范围: {pe_min:.1f}x ~ {pe_max:.1f}x)",
                years=valid_years,
                values=pe_list  # 存储历史PE序列用于展示
            )

        except Exception as e:
            return IndicatorResult(
                value=0.0,
                unit="%",
                description=f"PE历史百分位 (计算错误: {str(e)})",
                years=[],
                values=[]
            )

    def get_required_fields(self) -> List[str]:
        return ['net_profit']

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
