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
            "revenue": ['OPERATE_INCOME', 'TOTAL_OPERATE_INCOME', 'operating_income', 'OPERATING_INCOME', '营业收入', 'total_revenue', 'TOTAL_REVENUE', '营业额', '营运收入'],
            "net_profit": ['NETPROFIT', 'PARENT_NET_PROFIT', 'net_profit', 'NET_PROFIT', '净利润', 'parent_net_profit', '股东应占溢利'],
            "total_assets": ['TOTAL_ASSETS', 'total_assets', 'TOTAL_ASSETS', '资产总计', 'ASSET_BALANCE', '总资产'],
            "total_equity": ['TOTAL_EQUITY', 'total_equity', 'EQUITY_BALANCE', '股东权益', 'PARENT_EQUITY']
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

        # Auto-fetch latest market cap if not provided
        if not market_cap or market_cap <= 0:
            provider = kwargs.get('provider')
            stock_code = kwargs.get('stock_code')
            if provider and stock_code:
                try:
                    # 使用 LatestMarketCapIndicator 获取市值
                    from value_investment.indicators.simple import LatestMarketCapIndicator
                    mc_indicator = LatestMarketCapIndicator()
                    mc_result = mc_indicator.calculate(pd.DataFrame(), provider=provider, stock_code=stock_code)
                    if mc_result and mc_result.value > 0:
                        market_cap = mc_result.value
                except Exception:
                    pass

        # Calculate FCF = Operating Cash Flow - Capital Expenditure
        # HK: 经营业务现金净额, A股: 经营活动现金流
        op_cash_flow_col = self._find_column(data, [
            'NETCASH_OPERATE', 'operating_cash_flow', 'OPERATING_CASH_FLOW', '经营活动现金流', '经营业务现金净额'
        ])
        # HK: 购建固定资产, A股: 资本支出
        capex_col = self._find_column(data, [
            'CONSTRUCT_LONG_ASSET', 'capital_expenditure', 'CAPITAL_EXPENDITURE', '资本支出', '购建固定资产'
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
    PE历史百分位

    计算当前PE在历史PE序列中的百分位。
    通过历年末股价 × 当时股本 / 当时净利润计算历史PE。
    """

    name = "PEPct"
    description = "PE历史百分位"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """计算PE历史百分位（支持PE-TTM）"""
        provider = kwargs.get('provider')
        stock_code = kwargs.get('stock_code')
        years = kwargs.get('years', 10)

        if not provider or not stock_code:
            return IndicatorResult(
                value=0.0,
                unit="",
                description="PEPct (需要stock_code参数)",
                years=[],
                values=[]
            )

        try:
            # 1. 尝试使用PE-TTM计算（A股）
            ttm_result = self._calculate_pe_ttm_percentile(provider, stock_code, years)
            if ttm_result:
                return ttm_result

            # 2. 回退到原有年度PE计算
            return self._calculate_annual_pe_percentile(provider, stock_code, years)

        except Exception as e:
            return IndicatorResult(
                value=0.0,
                unit="",
                description=f"PEPct (计算错误: {str(e)})",
                years=[],
                values=[]
            )

    def _calculate_pe_ttm_percentile(self, provider, stock_code: str, years: int):
        """使用PE-TTM计算百分位（支持A股和港股）"""
        from datetime import datetime
        import pandas as pd

        # 1. 获取季度净利润数据
        quarterly_data = provider.get_quarterly_indicator(stock_code)
        if quarterly_data.empty:
            return None

        # 检测是否为港股（港股有 DATE_TYPE_CODE 字段）
        is_hk = 'DATE_TYPE_CODE' in quarterly_data.columns

        if is_hk:
            return self._calculate_hk_pe_ttm_percentile(quarterly_data, provider, stock_code, years)

        # A股处理逻辑
        # 检查是否有净利润字段
        net_profit_col = None
        for col in ['净利润', 'NETPROFIT']:
            if col in quarterly_data.columns:
                net_profit_col = col
                break

        if not net_profit_col:
            return None

        # 2. 提取报告期和净利润
        if '报告期' not in quarterly_data.columns:
            return None

        quarterly_data = quarterly_data.copy()
        quarterly_data['_quarter_date'] = pd.to_datetime(quarterly_data['报告期'], errors='coerce')
        quarterly_data = quarterly_data.dropna(subset=['_quarter_date', net_profit_col])
        quarterly_data = quarterly_data.sort_values('_quarter_date')

        # 过滤近年数据（保留过去N年）
        current_year = datetime.now().year
        cutoff_year = current_year - years
        quarterly_data = quarterly_data[quarterly_data['_quarter_date'].dt.year > cutoff_year]

        if len(quarterly_data) < 4:
            return None

        # 3. 计算滚动12个月净利润（TTM）
        # TTM = 当季 + 之前3个季度
        ttm_list = []
        ttm_dates = []

        for i in range(3, len(quarterly_data)):
            ttm = 0.0
            valid = True
            # 累加最近4个季度
            for j in range(4):
                profit = quarterly_data[net_profit_col].iloc[i - j]
                if pd.isna(profit) or profit <= 0:
                    valid = False
                    break
                ttm += profit

            if valid and ttm > 0:
                # 获取该季度末的日期
                quarter_date = quarterly_data['_quarter_date'].iloc[i]
                ttm_list.append(ttm)
                ttm_dates.append(quarter_date)

        if len(ttm_list) < 4:
            return None

        # 4. 获取股本数据
        finind = provider.get_financial_indicator(stock_code)
        total_shares = None

        # 优先从财务指标获取股本
        for col in ['已发行股本(股)', 'total_shares', '总股本']:
            if col in finind.columns:
                total_shares = float(finind[col].iloc[0])
                break

        # 如果没有，尝试从stock info获取
        if not total_shares or total_shares <= 0:
            try:
                stock_info = provider.get_stock_info(stock_code)
                if not stock_info.empty:
                    for item_col in ['item', 'Item']:
                        if item_col in stock_info.columns:
                            for _, row in stock_info.iterrows():
                                item = str(row.get(item_col, ''))
                                if '总股本' in item:
                                    total_shares = float(row.get('value', 0))
                                    break
                            if total_shares and total_shares > 0:
                                break
            except Exception:
                pass

        if not total_shares or total_shares <= 0:
            return None

        # 5. 计算各季度末的PE-TTM
        pe_ttm_list = []
        valid_dates = []

        for i, (ttm, quarter_date) in enumerate(zip(ttm_list, ttm_dates)):
            try:
                # 获取该季度末的日期（使用季度最后一天）
                if quarter_date.month == 3:
                    date_str = f"{quarter_date.year}0331"
                elif quarter_date.month == 6:
                    date_str = f"{quarter_date.year}0630"
                elif quarter_date.month == 9:
                    date_str = f"{quarter_date.year}0930"
                else:  # 12月
                    date_str = f"{quarter_date.year}1231"

                hist = provider.get_historical_data(stock_code, date_str, adjust="")
                if hist.empty:
                    continue

                close_col = '收盘' if '收盘' in hist.columns else 'close'
                end_price = float(hist[close_col].iloc[-1])

                if end_price <= 0:
                    continue

                # 计算市值和PE-TTM
                market_cap = end_price * total_shares
                pe_ttm = market_cap / ttm

                if 0 < pe_ttm < 500:
                    pe_ttm_list.append(pe_ttm)
                    valid_dates.append(quarter_date.year + quarter_date.month / 12)
            except Exception:
                continue

        if len(pe_ttm_list) < 4:
            return None

        # 6. 获取当前PE-TTM
        current_pe = None
        if '市盈率' in finind.columns:
            current_pe = float(finind['市盈率'].iloc[0])

        if not current_pe or current_pe <= 0:
            # 使用最新市值计算当前PE-TTM
            from value_investment.indicators.simple import LatestMarketCapIndicator
            mc_indicator = LatestMarketCapIndicator()
            mc_result = mc_indicator.calculate(pd.DataFrame(), provider=provider, stock_code=stock_code)
            if mc_result and mc_result.value > 0:
                # 使用最新TTM
                current_pe = mc_result.value / ttm_list[-1]

        if not current_pe or current_pe <= 0:
            return None

        # 7. 计算百分位
        rank = sum(1 for pe in pe_ttm_list if pe < current_pe)
        percentile = (rank + 0.5) / len(pe_ttm_list) * 100
        percentile = max(0, min(100, percentile))

        pe_min = min(pe_ttm_list)
        pe_max = max(pe_ttm_list)

        # 整理年份输出
        year_labels = [f"{int(d)}Q{int((d % 1) * 4 + 1)}" for d in valid_dates]

        return IndicatorResult(
            value=percentile,
            unit="%",
            description=f"PE-TTM百分位: {percentile:.1f}% (当前PE-TTM={current_pe:.1f}x, 历史范围={pe_min:.1f}x~{pe_max:.1f}x, {len(pe_ttm_list)}个季度)",
            years=year_labels,
            values=pe_ttm_list
        )

    def _calculate_hk_pe_ttm_percentile(self, quarterly_data, provider, stock_code: str, years: int):
        """使用港股半年报数据计算PE-TTM百分位"""
        from datetime import datetime
        import pandas as pd

        # 港股字段映射
        net_profit_col = 'HOLDER_PROFIT'  # 股东应占溢利
        if net_profit_col not in quarterly_data.columns:
            return None

        # 处理数据
        data = quarterly_data.copy()
        data['_report_date'] = pd.to_datetime(data['REPORT_DATE'], errors='coerce')
        data = data.dropna(subset=['_report_date', net_profit_col])
        data = data.sort_values('_report_date')

        # 过滤近年数据
        current_year = datetime.now().year
        cutoff_year = current_year - years
        data = data[data['_report_date'].dt.year > cutoff_year]

        if len(data) < 4:
            return None

        # 提取净利润和日期
        data['_profit'] = pd.to_numeric(data[net_profit_col], errors='coerce')

        # 构建TTM数据：使用半年报 + 去年的半年报
        # TTM = 当前半年报 + (去年年报 - 去年半年报)
        ttm_list = []
        ttm_dates = []

        # 按年份组织数据
        data['_year'] = data['_report_date'].dt.year
        data['_month'] = data['_report_date'].dt.month

        # 创建年份-报告类型到利润的映射
        year_data = {}
        for _, row in data.iterrows():
            year = row['_year']
            dtype = row['DATE_TYPE_CODE']
            profit = row['_profit']
            if pd.isna(profit) or profit <= 0:
                continue
            if year not in year_data:
                year_data[year] = {}
            year_data[year][dtype] = profit

        # 计算TTM
        years_sorted = sorted(year_data.keys())
        for i, year in enumerate(years_sorted):
            if year not in year_data:
                continue
            # 需要有本年半年报(002)和去年年报(001)
            if '002' not in year_data[year]:
                continue
            if i == 0:
                continue  # 去年没有数据，无法计算TTM
            prev_year = years_sorted[i - 1]
            if '001' not in year_data.get(prev_year, {}):
                continue

            # TTM = 本年半年报 + (去年年报 - 去年半年报)
            h1_current = year_data[year]['002']
            annual_prev = year_data[prev_year]['001']
            h1_prev = year_data.get(prev_year, {}).get('002', 0)

            if h1_current > 0 and annual_prev > 0:
                ttm = h1_current + (annual_prev - h1_prev)
                if ttm > 0:
                    # 使用半年报日期
                    for _, row in data.iterrows():
                        if row['_year'] == year and row['DATE_TYPE_CODE'] == '002':
                            ttm_list.append(ttm)
                            ttm_dates.append(row['_report_date'])
                            break

        if len(ttm_list) < 3:
            # 如果TTM数据不足，回退到使用年报数据
            return None

        # 获取股本
        total_shares = None
        try:
            stock_info = provider.get_stock_info(stock_code)
            if not stock_info.empty:
                for item_col in ['item', 'Item']:
                    if item_col in stock_info.columns:
                        for _, row in stock_info.iterrows():
                            item = str(row.get(item_col, ''))
                            if '总股本' in item:
                                total_shares = float(row.get('value', 0))
                                break
                        if total_shares and total_shares > 0:
                            break
        except Exception:
            pass

        if not total_shares or total_shares <= 0:
            return None

        # 计算各时点的PE-TTM
        pe_ttm_list = []
        valid_dates = []

        for ttm, quarter_date in zip(ttm_list, ttm_dates):
            try:
                # 使用半年末的日期
                if quarter_date.month == 6:
                    date_str = f"{quarter_date.year}0630"
                else:
                    date_str = f"{quarter_date.year}1231"

                hist = provider.get_historical_data(stock_code, date_str, adjust="")
                if hist.empty:
                    continue

                close_col = '收盘' if '收盘' in hist.columns else 'close'
                end_price = float(hist[close_col].iloc[-1])

                if end_price <= 0:
                    continue

                # 计算市值和PE-TTM
                market_cap = end_price * total_shares
                pe_ttm = market_cap / ttm

                if 0 < pe_ttm < 500:
                    pe_ttm_list.append(pe_ttm)
                    valid_dates.append(quarter_date.year + quarter_date.month / 12)
            except Exception:
                continue

        if len(pe_ttm_list) < 3:
            return None

        # 获取当前PE-TTM
        finind = provider.get_financial_indicator(stock_code)
        current_pe = None
        if '市盈率' in finind.columns:
            current_pe = float(finind['市盈率'].iloc[0])

        if not current_pe or current_pe <= 0:
            # 使用最新市值和最新TTM计算
            from value_investment.indicators.simple import LatestMarketCapIndicator
            mc_indicator = LatestMarketCapIndicator()
            mc_result = mc_indicator.calculate(pd.DataFrame(), provider=provider, stock_code=stock_code)
            if mc_result and mc_result.value > 0 and ttm_list:
                current_pe = mc_result.value / ttm_list[-1]

        if not current_pe or current_pe <= 0:
            return None

        # 计算百分位
        rank = sum(1 for pe in pe_ttm_list if pe < current_pe)
        percentile = (rank + 0.5) / len(pe_ttm_list) * 100
        percentile = max(0, min(100, percentile))

        pe_min = min(pe_ttm_list)
        pe_max = max(pe_ttm_list)

        # 整理年份输出
        year_labels = [f"{int(d)}H" for d in valid_dates]

        return IndicatorResult(
            value=percentile,
            unit="%",
            description=f"PE-TTM百分位: {percentile:.1f}% (当前PE-TTM={current_pe:.1f}x, 历史范围={pe_min:.1f}x~{pe_max:.1f}x, {len(pe_ttm_list)}个半年)",
            years=year_labels,
            values=pe_ttm_list
        )

    def _calculate_annual_pe_percentile(self, provider, stock_code: str, years: int):
        """使用年度PE计算百分位（原有逻辑）"""
        # 1. 获取最新市值（用于当前PE计算）
        from value_investment.indicators.simple import LatestMarketCapIndicator
        mc_indicator = LatestMarketCapIndicator()
        mc_result = mc_indicator.calculate(pd.DataFrame(), provider=provider, stock_code=stock_code)

        if not mc_result or mc_result.value <= 0:
            return IndicatorResult(
                value=0.0,
                unit="",
                description="PEPct (无法获取市值)",
                years=[],
                values=[]
            )

        current_market_cap = mc_result.value

        # 2. 获取财务指标（获取当前PE和股本）
        finind = provider.get_financial_indicator(stock_code)
        if finind.empty:
            return IndicatorResult(
                value=0.0,
                unit="",
                description="PEPct (无财务指标数据)",
                years=[],
                values=[]
            )

        # 获取当前PE
        pe_col = None
        for col in finind.columns:
            if '市盈率' in col:
                pe_col = col
                break

        if not pe_col:
            return IndicatorResult(
                value=0.0,
                unit="",
                description="PEPct (无PE数据)",
                years=[],
                values=[]
            )

        current_pe = float(finind[pe_col].iloc[0])

        # 获取股本或市值
        total_shares = None
        current_market_cap_field = None

        # 优先使用总市值字段（A股用元，港股用港元）
        for cap_col in ['总市值(元)', '总市值(港元)']:
            if cap_col in finind.columns:
                current_market_cap_field = float(finind[cap_col].iloc[0])
                if current_market_cap_field and current_market_cap_field > 0:
                    break

        # 尝试获取股本（优先从财务指标，A股和港股都可能有）
        for col in ['已发行股本(股)', 'total_shares', '总股本']:
            if col in finind.columns:
                total_shares = float(finind[col].iloc[0])
                if total_shares and total_shares > 0:
                    break

        # 如果还是没有股本，尝试从stock info获取
        if not total_shares or total_shares <= 0:
            try:
                stock_info = provider.get_stock_info(stock_code)
                if not stock_info.empty:
                    # 查找总股本字段
                    for item_col in ['item', 'Item']:
                        if item_col in stock_info.columns:
                            for _, row in stock_info.iterrows():
                                item = str(row.get(item_col, ''))
                                if '总股本' in item:
                                    total_shares = float(row.get('value', 0))
                                    break
                            if total_shares and total_shares > 0:
                                break
            except Exception:
                pass

        if not total_shares or total_shares <= 0:
            return IndicatorResult(
                value=0.0,
                unit="",
                description="PEPct (无股本/市值数据)",
                years=[],
                values=[]
            )

        # 3. 获取利润表历年数据
        from datetime import datetime
        current_year = datetime.now().year
        profit_sheet = provider.get_profit_sheet(stock_code, current_year + 1)

        if profit_sheet.empty:
            return IndicatorResult(
                value=current_pe,
                unit="x",
                description=f"当前PE: {current_pe:.1f}x (历史百分位数据不足)",
                years=[],
                values=[]
            )

        # 提取净利润列 - 优先使用股东应占溢利/除税后溢利
        net_profit_col = None
        priority_cols = ['股东应占溢利', '除税后溢利', '净利润', 'NETPROFIT', 'net_profit']
        for col in profit_sheet.columns:
            if col in priority_cols:
                net_profit_col = col
                break
        # 如果没有优先列，再匹配其他包含"溢利"的列
        if not net_profit_col:
            for col in profit_sheet.columns:
                if '溢利' in col:
                    net_profit_col = col
                    break

        if not net_profit_col:
            return IndicatorResult(
                value=current_pe,
                unit="x",
                description=f"当前PE: {current_pe:.1f}x (无净利润数据)",
                years=[],
                values=[]
            )

        # 获取最近N年的年报数据
        # 从REPORT_DATE列提取年份（A股格式）
        if 'REPORT_DATE' in profit_sheet.columns:
            profit_sheet = profit_sheet.copy()
            profit_sheet['_year'] = pd.to_datetime(profit_sheet['REPORT_DATE'], errors='coerce').dt.year
            profit_sheet = profit_sheet.dropna(subset=['_year'])
            profit_sheet = profit_sheet.sort_values('_year', ascending=False)
        elif 'year' in profit_sheet.columns:
            profit_sheet = profit_sheet.sort_values('year', ascending=False)
        profit_sheet = profit_sheet.head(years)

        # 4. 计算历史PE
        pe_list = []
        valid_years = []

        for _, row in profit_sheet.iterrows():
            # 优先使用_year列，否则用year列
            year = row.get('_year') or row.get('year')
            if year is None or pd.isna(year):
                continue

            year = int(year)
            net_profit = row.get(net_profit_col)

            if pd.isna(net_profit) or net_profit <= 0:
                continue

            # 获取该年年末股价
            try:
                year_end = f"{int(year)}1231"
                hist = provider.get_historical_data(stock_code, year_end, adjust="")

                if hist.empty:
                    continue

                close_col = '收盘' if '收盘' in hist.columns else 'close'
                last_price = float(hist[close_col].iloc[-1])

                if last_price <= 0:
                    continue

                # 计算当时市值：有市值字段用市值，否则用股价×股本
                if current_market_cap_field and total_shares:
                    # 使用当前市值比例估算历史市值
                    year_market_cap = last_price * total_shares
                elif total_shares:
                    year_market_cap = last_price * total_shares
                else:
                    continue

                # 计算当时PE
                year_pe = year_market_cap / net_profit

                if 0 < year_pe < 500:
                    pe_list.append(year_pe)
                    valid_years.append(year)
            except Exception:
                continue

        if len(pe_list) < 3:
            return IndicatorResult(
                value=current_pe,
                unit="x",
                description=f"当前PE: {current_pe:.1f}x (历史数据仅{len(pe_list)}年)",
                years=valid_years,
                values=pe_list
            )

        # 5. 计算百分位（使用排名公式，避免0%和100%）
        # 公式: (小于当前值的个数 + 0.5) / 总数 * 100
        # 这样最低PE显示5%，最高PE显示95%
        rank = sum(1 for pe in pe_list if pe < current_pe)
        percentile = (rank + 0.5) / len(pe_list) * 100
        percentile = max(0, min(100, percentile))  # 限制范围

        pe_min = min(pe_list)
        pe_max = max(pe_list)

        return IndicatorResult(
            value=percentile,
            unit="%",
            description=f"PE百分位: {percentile:.1f}% (当前PE={current_pe:.1f}x, 历史范围={pe_min:.1f}x~{pe_max:.1f}x)",
            years=valid_years,
            values=pe_list
        )

    def get_required_fields(self) -> List[str]:
        return []
