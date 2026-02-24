"""Valuation indicators: Latest Market Cap, Implied Growth, PE Percentile."""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class LatestMarketCapIndicator(BaseIndicator):
    """
    最新市值指标

    通过最新收盘价（不复权）* 股数计算当前市值。
    用于 ImpliedGrowth 等需要最新市值的指标。
    """

    name = "latest_market_cap"
    needs = ['financial_indicator', 'prices']
    description = "最新市值 (最新收盘价 × 股数)"
    type = IndicatorType.CALCULATED
    # 港币兑换人民币汇率 (约0.88)
    HKD_TO_CNY = 0.88

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Use injected dependencies instead of kwargs.get('provider')
        financial_indicator = kwargs.get('financial_indicator')  # Injected from registry
        prices = kwargs.get('prices')  # Injected from registry
        stock_code = kwargs.get('stock_code')

        # Check if dependencies are valid (use .empty for DataFrame check)
        if (financial_indicator is None or financial_indicator.empty or
            prices is None or prices.empty or
            not stock_code):
            return IndicatorResult(
                value=0.0,
                unit="",
                description="最新市值 (需要financial_indicator和prices依赖)",
                years=[],
                values=[]
            )

        try:
            # 判断市场类型：5位代码=港股，6位代码=A股，美股=字母
            is_hk = len(stock_code) == 5
            is_us = stock_code.isalpha()  # 美股代码是纯字母

            # 1. 从财务指标获取市值（优先使用）
            finind = financial_indicator
            if not finind.empty:
                market_cap = None

                if is_hk:
                    # 港股：优先使用内部标准字段 (hk_market_cap)
                    if 'hk_market_cap' in finind.columns:
                        market_cap_hkd = float(finind['hk_market_cap'].iloc[0])
                        if market_cap_hkd and market_cap_hkd > 0:
                            market_cap = market_cap_hkd * self.HKD_TO_CNY
                    elif 'market_cap_hkd' in finind.columns:
                        market_cap_hkd = float(finind['market_cap_hkd'].iloc[0])
                        if market_cap_hkd and market_cap_hkd > 0:
                            market_cap = market_cap_hkd * self.HKD_TO_CNY
                    elif '总市值(港元)' in finind.columns:
                        market_cap_hkd = float(finind['总市值(港元)'].iloc[0])
                        if market_cap_hkd and market_cap_hkd > 0:
                            market_cap = market_cap_hkd * self.HKD_TO_CNY
                elif is_us:
                    # 美股：优先使用内部标准字段 (us_market_cap)
                    if 'us_market_cap' in finind.columns:
                        market_cap = float(finind['us_market_cap'].iloc[0])
                    elif 'market_cap_usd' in finind.columns:
                        market_cap = float(finind['market_cap_usd'].iloc[0])
                    elif '总市值(美元)' in finind.columns:
                        market_cap = float(finind['总市值(美元)'].iloc[0])
                else:
                    # A股：优先使用内部标准字段 (a_market_cap)
                    if 'a_market_cap' in finind.columns:
                        market_cap = float(finind['a_market_cap'].iloc[0])
                    elif 'market_cap_cny' in finind.columns:
                        market_cap = float(finind['market_cap_cny'].iloc[0])
                    elif '总市值(元)' in finind.columns:
                        market_cap = float(finind['总市值(元)'].iloc[0])

                if market_cap and market_cap > 0:
                    return IndicatorResult(
                        value=market_cap,
                        unit="",
                        description=f"最新市值 (从财务指标获取, {'港股' if is_hk else 'A股'})",
                        years=[],
                        values=[]
                    )

            # 如果没有总市值字段，则尝试计算
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

            # 如果财务指标中没有股本，尝试从 stock_info 获取（美股）
            if (not total_shares or total_shares <= 0) and is_us:
                # 美股：使用 actual_issue_total_shares_num * 10000 转换为股
                try:
                    from value_investment.api import ValueInvestment
                    vi = ValueInvestment(market='US')
                    info = vi.get_stock_info(stock_code)
                    if info is not None and not info.empty:
                        for item, value in zip(info['item'], info['value']):
                            if 'actual_issue_total_shares_num' in item:
                                total_shares = float(value) * 10000  # 转换为股
                                break
                except Exception:
                    pass

            if not total_shares or total_shares <= 0:
                return IndicatorResult(
                    value=0.0,
                    unit="",
                    description="最新市值 (无法获取股本)",
                    years=[],
                    values=[]
                )

            # 2. 使用注入的价格数据获取最新收盘价
            hist = prices

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
    needs = ['financial_indicator', 'prices']
    description = "市场隐含增长率 (基于DCF模型)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # Get parameters
        growth_rate = kwargs.get("growth_rate", 0.03)  # Terminal growth
        wacc = kwargs.get("wacc", 0.10)  # Weighted Average Cost of Capital
        market_cap = kwargs.get("market_cap", None)  # Required for implied growth

        # Use injected dependencies instead of kwargs.get('provider')
        financial_indicator = kwargs.get('financial_indicator')  # Injected from registry
        prices = kwargs.get('prices')  # Injected from registry
        stock_code = kwargs.get('stock_code')

        # Auto-fetch latest market cap if not provided
        if not market_cap or market_cap <= 0:
            finind_valid = financial_indicator is not None and not financial_indicator.empty
            prices_valid = prices is not None and not prices.empty
            if finind_valid and prices_valid and stock_code:
                try:
                    # 使用 LatestMarketCapIndicator 获取市值
                    from value_investment.indicators.valuation import LatestMarketCapIndicator
                    mc_indicator = LatestMarketCapIndicator()
                    mc_result = mc_indicator.calculate(pd.DataFrame(), financial_indicator=financial_indicator, prices=prices, stock_code=stock_code)
                    if mc_result and mc_result.value > 0:
                        market_cap = mc_result.value
                except Exception:
                    pass

        # Calculate FCF = Operating Cash Flow - Capital Expenditure (standardized field names)
        op_cash_flow_col = self._find_column(data, ['operating_cash_flow'])
        capex_col = self._find_column(data, ['capital_expenditure'])

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
    needs = ['quarterly', 'prices', 'stock_info']
    description = "PE历史百分位"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        """计算PE历史百分位（支持PE-TTM）"""
        # Get injected dependencies
        quarterly = kwargs.get('quarterly')  # Injected from registry
        prices = kwargs.get('prices')  # Injected from registry
        stock_info = kwargs.get('stock_info')  # Injected from registry
        stock_code = kwargs.get('stock_code')
        years = kwargs.get('years', 10)

        # Check if required dependencies are provided (use .empty for DataFrame check)
        if (quarterly is None or (hasattr(quarterly, 'empty') and quarterly.empty) or
            prices is None or (hasattr(prices, 'empty') and prices.empty) or
            stock_info is None or (hasattr(stock_info, 'empty') and stock_info.empty) or
            not stock_code):
            return IndicatorResult(
                value=0.0,
                unit="",
                description="PEPct (需要quarterly, prices和stock_info依赖)",
                years=[],
                values=[]
            )

        try:
            # 1. 尝试使用PE-TTM计算（A股）
            ttm_result = self._calculate_pe_ttm_percentile_with_data(quarterly, prices, stock_info, stock_code, years)
            if ttm_result:
                return ttm_result

            # 2. 回退到原有年度PE计算
            return self._calculate_annual_pe_percentile_with_data(quarterly, prices, stock_info, stock_code, years)

        except Exception as e:
            return IndicatorResult(
                value=0.0,
                unit="",
                description=f"PEPct (计算错误: {str(e)})",
                years=[],
                values=[]
            )

    # New methods that use injected data instead of provider
    def _calculate_pe_ttm_percentile_with_data(self, quarterly_data, prices_data, stock_info, stock_code: str, years: int):
        """使用PE-TTM计算百分位（使用注入的数据）"""
        from datetime import datetime
        import pandas as pd

        if quarterly_data.empty or prices_data.empty:
            return None

        # 检测是否为港股（港股有 date_type_code 字段，且没有 operating_income 字段）
        # 美股有 date_type_code 和 operating_income 字段
        # A股没有 date_type_code 字段
        has_date_type_code = 'date_type_code' in quarterly_data.columns
        has_operating_income = 'operating_income' in quarterly_data.columns

        is_hk = has_date_type_code and not has_operating_income

        if is_hk:
            return self._calculate_hk_pe_ttm_percentile_with_data(quarterly_data, prices_data, stock_code, years)

        # A股或美股处理逻辑 - 提取净利润列
        # 优先使用内部标准字段名，其次兼容原始字段名
        # 美股使用 parent_net_profit
        net_profit_col = None
        for col in ['net_profit', 'parent_net_profit']:
            if col in quarterly_data.columns:
                net_profit_col = col
                break

        if not net_profit_col:
            return None

        # 提取报告期和净利润
        report_col = None
        for col in ['report_date']:
            if col in quarterly_data.columns:
                report_col = col
                break

        if not report_col:
            return None

        data = quarterly_data.copy()
        data['_quarter_date'] = pd.to_datetime(data[report_col], errors='coerce')
        data = data.dropna(subset=['_quarter_date', net_profit_col])
        data = data.sort_values('_quarter_date')

        # 过滤近年数据
        current_year = datetime.now().year
        cutoff_year = current_year - years
        data = data[data['_quarter_date'].dt.year > cutoff_year]

        if len(data) < 4:
            return None

        # 计算TTM
        ttm_list = []
        ttm_dates = []

        for i in range(3, len(data)):
            ttm = 0.0
            valid = True
            for j in range(4):
                profit = data[net_profit_col].iloc[i - j]
                if pd.isna(profit) or profit <= 0:
                    valid = False
                    break
                ttm += profit

            if valid and ttm > 0:
                quarter_date = data['_quarter_date'].iloc[i]
                ttm_list.append(ttm)
                ttm_dates.append(quarter_date)

        if len(ttm_list) < 4:
            return None

        # 获取股本数据（从stock_info依赖）
        total_shares = None

        if stock_info is not None and not (hasattr(stock_info, 'empty') and stock_info.empty):
            try:
                for item_col in ['item', 'Item']:
                    if item_col in stock_info.columns:
                        for _, row in stock_info.iterrows():
                            item = str(row.get(item_col, ''))
                            value = row.get('value', 0)
                            # A股: 总股本
                            if '总股本' in item:
                                total_shares = float(value)
                                break
                            # 美股: actual_issue_total_shares_num (实际发行股本数)
                            # 苹果的 actual_issue_total_shares_num = 4600000 表示约 46 亿股
                            if 'actual_issue_total_shares_num' in item:
                                total_shares = float(value) * 10000  # 转换为股
                                break
            except Exception:
                pass

        if not total_shares or total_shares <= 0:
            return None

        # 准备prices_data用于查找历史价格
        # 确保有date列
        prices = prices_data.copy()
        if 'date' not in prices.columns:
            if '日期' in prices.columns:
                prices['date'] = pd.to_datetime(prices['日期'])
            elif 'REPORT_DATE' in prices.columns:
                prices['date'] = pd.to_datetime(prices['REPORT_DATE'])
        prices = prices.sort_values('date')

        # 确定收盘价列名
        close_col = '收盘' if '收盘' in prices.columns else 'close'

        # 计算各季度末的PE-TTM（从prices_data中查找对应日期的价格）
        pe_ttm_list = []
        valid_dates = []

        for ttm, quarter_date in zip(ttm_list, ttm_dates):
            try:
                # 找到该季度末或之前最近的价格
                price_mask = prices['date'] <= quarter_date
                if not price_mask.any():
                    continue

                end_price = float(prices.loc[price_mask, close_col].iloc[-1])

                if end_price <= 0:
                    continue

                market_cap = end_price * total_shares
                pe_ttm = market_cap / ttm

                if 0 < pe_ttm < 500:
                    pe_ttm_list.append(pe_ttm)
                    valid_dates.append(quarter_date.year + quarter_date.month / 12)
            except Exception:
                continue

        if len(pe_ttm_list) < 4:
            return None

        # 获取当前PE-TTM（使用最新价格和最新TTM计算）
        current_pe = None
        try:
            latest_price = float(prices[close_col].iloc[-1])
            market_cap = latest_price * total_shares
            current_pe = market_cap / ttm_list[-1]
        except Exception:
            pass

        if not current_pe or current_pe <= 0:
            return None

        # 计算百分位
        rank = sum(1 for pe in pe_ttm_list if pe < current_pe)
        percentile = (rank + 0.5) / len(pe_ttm_list) * 100
        percentile = max(0, min(100, percentile))

        pe_min = min(pe_ttm_list)
        pe_max = max(pe_ttm_list)

        year_labels = [f"{int(d)}Q{int((d % 1) * 4 + 1)}" for d in valid_dates]

        return IndicatorResult(
            value=percentile,
            unit="%",
            description=f"PE-TTM百分位: {percentile:.1f}% (当前PE-TTM={current_pe:.1f}x, 历史范围={pe_min:.1f}x~{pe_max:.1f}x, {len(pe_ttm_list)}个季度)",
            years=year_labels,
            values=pe_ttm_list
        )

    def _calculate_annual_pe_percentile_with_data(self, quarterly_data, prices_data, stock_info, stock_code: str, years: int):
        """使用年度PE计算百分位（使用注入的数据）

        注：由于PE-TTM方法已实现，此方法作为后备。目前依赖注入的prices数据暂不支持此方法。
        """
        # 返回None以触发调用方使用PE-TTM方法的结果
        return None

    def _calculate_pe_ttm_percentile(self, provider, stock_code: str, years: int):
        """使用PE-TTM计算百分位（支持A股和港股）"""
        from datetime import datetime
        import pandas as pd

        # 1. 获取季度净利润数据
        quarterly_data = provider.get_quarterly_indicator(stock_code)
        if quarterly_data.empty:
            return None

        # 检测是否为港股（港股有 date_type_code 字段，且没有 operating_income 字段）
        # 美股有 date_type_code 和 operating_income 字段
        # A股没有 date_type_code 字段
        has_date_type_code = 'date_type_code' in quarterly_data.columns
        has_operating_income = 'operating_income' in quarterly_data.columns

        is_hk = has_date_type_code and not has_operating_income

        if is_hk:
            return self._calculate_hk_pe_ttm_percentile(quarterly_data, provider, stock_code, years)

        # A股或美股处理逻辑（两者都使用标准字段）
        # 检查是否有净利润字段（优先使用内部标准字段）
        net_profit_col = None
        for col in ['net_profit']:
            if col in quarterly_data.columns:
                net_profit_col = col
                break

        if not net_profit_col:
            return None

        # 2. 提取报告期和净利润
        report_col = None
        for col in ['report_date']:
            if col in quarterly_data.columns:
                report_col = col
                break

        if not report_col:
            return None

        quarterly_data = quarterly_data.copy()
        quarterly_data['_quarter_date'] = pd.to_datetime(quarterly_data[report_col], errors='coerce')
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
        for col in ['total_shares']:
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
            from value_investment.indicators.valuation import LatestMarketCapIndicator
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

    def _calculate_hk_pe_ttm_percentile_with_data(self, quarterly_data, prices_data, stock_code: str, years: int):
        """使用港股半年报数据计算PE-TTM百分位（使用注入的数据）"""
        from datetime import datetime
        import pandas as pd

        if quarterly_data.empty or prices_data.empty:
            return None

        # 港股字段映射 - 优先使用内部标准字段
        net_profit_col = None
        for col in ['parent_net_profit']:
            if col in quarterly_data.columns:
                net_profit_col = col
                break
        if not net_profit_col:
            return None

        # 处理数据 - 优先使用内部标准字段
        data = quarterly_data.copy()
        report_col = 'report_date' if 'report_date' in data.columns else 'REPORT_DATE'
        data['_report_date'] = pd.to_datetime(data[report_col], errors='coerce')
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
            return None

        # 获取股本 - 从prices_data中无法获取，需要依赖stock_info
        # 这里暂时返回None，后续可以通过扩展依赖来解决
        return None

    def _calculate_hk_pe_ttm_percentile(self, quarterly_data, provider, stock_code: str, years: int):
        """使用港股半年报数据计算PE-TTM百分位"""
        from datetime import datetime
        import pandas as pd

        # 港股字段映射 - 优先使用内部标准字段
        net_profit_col = None
        for col in ['parent_net_profit']:
            if col in quarterly_data.columns:
                net_profit_col = col
                break
        if not net_profit_col:
            return None

        # 处理数据 - 优先使用内部标准字段
        data = quarterly_data.copy()
        report_col = 'report_date' if 'report_date' in data.columns else 'REPORT_DATE'
        data['_report_date'] = pd.to_datetime(data[report_col], errors='coerce')
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
            from value_investment.indicators.valuation import LatestMarketCapIndicator
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
        from value_investment.indicators.valuation import LatestMarketCapIndicator
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

        # 优先使用内部标准市值字段 (带市场前缀)
        for cap_col in ['a_market_cap', 'hk_market_cap', 'us_market_cap', 'market_cap_cny', 'market_cap_hkd', '总市值(元)', '总市值(港元)']:
            if cap_col in finind.columns:
                current_market_cap_field = float(finind[cap_col].iloc[0])
                if current_market_cap_field and current_market_cap_field > 0:
                    break

        # 尝试获取股本（优先从财务指标，A股和港股都可能有）
        for col in ['total_shares', '已发行股本(股)', '总股本']:
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

        # 提取净利润列 - 优先使用内部标准字段
        net_profit_col = None
        priority_cols = ['parent_net_profit', 'profit_after_tax', 'net_profit', '股东应占溢利', '除税后溢利', '净利润', 'NETPROFIT']
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
