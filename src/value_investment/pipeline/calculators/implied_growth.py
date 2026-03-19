"""Implied Growth Rate Calculator based on DCF model"""
from typing import Any

from value_investment.pipeline.calculators import calculator
from value_investment.pipeline.fields import IFRSFields


@calculator
class ImpliedGrowth:
    """Implied Growth Rate Calculator

    基于 DCF 模型，用当前市值反推隐含的年增长率。
    假设 FCF 按固定增长率 g 增长，WACC 和永续增长率固定，
    求解使 DCF 估值等于市值的 g 值。

    Formula:
    - DCF = Σ(FCF_t / (1+WACC)^t) + TV / (1+WACC)^n
    - TV = FCF_n * (1+g) / (WACC - g_terminal)
    - 求解 g 使 DCF = market_cap

    Parameters:
    - WACC: 加权平均资本成本 (默认 10%)
    - g_terminal: 永续增长率 (默认 3%)
    - n_years: 预测期 (默认 10 年)
    """

    name = "implied_growth"

    # capital_expenditure 是可选的 - 如果没有，将使用 operating_cash_flow 作为 FCF 近似
    required_fields = {
        IFRSFields.OPERATING_CASH_FLOW,
        IFRSFields.MARKET_CAP,
    }

    def __init__(
        self,
        wacc: float = 0.10,
        g_terminal: float = 0.03,
        n_years: int = 10,
    ):
        self.wacc = wacc
        self.g_terminal = g_terminal
        self.n_years = n_years

    def calculate(
        self,
        results: dict[str, dict[int, Any]],
    ) -> dict[int, float]:
        """计算隐含增长率

        Args:
            results: {field: {year: value}}
                必须包含:
                - operating_cash_flow 或 free_cash_flow
                - capital_expenditure (若无 free_cash_flow)
                - market_cap

        Returns:
            {year: implied_growth_rate}
        """
        # 获取 FCF
        fcf_data = self._get_fcf(results)
        if not fcf_data:
            return {}

        # 获取市值
        market_cap_data = results.get(IFRSFields.MARKET_CAP, {})
        if not market_cap_data:
            return {}

        # 计算每年对应的隐含增长率
        implied_growth = {}
        for year, fcf in fcf_data.items():
            if fcf <= 0:
                continue

            market_cap = market_cap_data.get(year)
            if not market_cap or market_cap <= 0:
                continue

            g = self._calculate_implied_growth(fcf, market_cap)
            if g is not None:
                implied_growth[year] = g

        return implied_growth

    def _get_fcf(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """获取自由现金流数据

        优先使用 free_cash_flow，否则用 operating_cash_flow - capital_expenditure。
        如果没有 capital_expenditure，则直接使用 operating_cash_flow（近似自由现金流）。
        """
        # 优先使用 free_cash_flow
        if "free_cash_flow" in results:
            fcf_data = results["free_cash_flow"]
            # 确保都是正数
            return {year: val for year, val in fcf_data.items() if val > 0}

        # 使用 OCF - CAPEX
        ocf_data = results.get(IFRSFields.OPERATING_CASH_FLOW, {})
        capex_data = results.get(IFRSFields.CAPITAL_EXPENDITURE, {})

        # 如果没有 capex 数据，直接使用 OCF 作为 FCF 的近似
        if not capex_data:
            return {year: val for year, val in ocf_data.items() if val > 0}

        fcf_data = {}
        for year in ocf_data:
            ocf = ocf_data.get(year, 0)
            capex = capex_data.get(year, 0)
            fcf = ocf - capex
            if fcf > 0:
                fcf_data[year] = fcf

        return fcf_data

    def _calculate_implied_growth(
        self,
        current_fcf: float,
        market_cap: float,
    ) -> float | None:
        """计算隐含增长率

        使用二分搜索求解：
        找到增长率 g 使 DCF(g) = market_cap

        Args:
            current_fcf: 当前自由现金流
            market_cap: 市值

        Returns:
            隐含增长率 (如 0.12 表示 12%)
        """
        wacc = self.wacc
        g_terminal = self.g_terminal
        n_years = self.n_years

        def dcf_value(g: float) -> float:
            """计算给定增长率 g 的 DCF 值"""
            if g >= wacc:
                return float("inf")
            if g <= -0.1:
                return 0.0

            # 预测未来 n 年 FCF
            projected_fcf = [
                current_fcf * ((1 + g) ** i) for i in range(1, n_years + 1)
            ]

            # 终值
            tv = (projected_fcf[-1] * (1 + g_terminal)) / (wacc - g_terminal)

            # 折现
            pv = sum(
                fc / ((1 + wacc) ** i) for i, fc in enumerate(projected_fcf, 1)
            )
            pv += tv / ((1 + wacc) ** n_years)

            return pv

        # 二分搜索 [-5%, 30%]
        low, high = -0.05, 0.30
        tolerance = 0.0001  # 0.01% 精度

        for _ in range(100):  # 最多 100 次迭代
            mid = (low + high) / 2
            pv = dcf_value(mid)

            if abs(pv - market_cap) / market_cap < tolerance:
                return mid

            if pv > market_cap:
                # 需要更低的增长率来降低估值
                high = mid
            else:
                # 需要更高的增长率来提高估值
                low = mid

        return (low + high) / 2
