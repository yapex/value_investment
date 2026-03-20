"""Cumulative Operating Cash Flow to Net Profit Ratio

累计经营现金流/累计净利润 = Σ(经营现金流) / Σ(净利润)

用于识别财务造假风险：
- 多年累计值比单年更难造假
- 阈值：累计值 > 0.7 为健康

Usage:
    v-invest query 600519 -r "cumulative_ocf_to_nprofit" -y 10
"""
from typing import Any

required_fields = ["operating_cash_flow", "net_profit"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """计算累计经营现金流/累计净利润

    Args:
        results: {字段名: {年份: 值}}

    Returns:
        {最后年份: 累计比值}
        例如：{2024: 1.08} 表示10年累计净现比为1.08
    """
    ocf = results.get("operating_cash_flow", {})
    net_profit = results.get("net_profit", {})

    if not ocf or not net_profit:
        return {}

    # 累计值
    cum_ocf = sum(v for v in ocf.values() if v is not None)
    cum_np = sum(v for v in net_profit.values() if v is not None)

    # 返回最后一个年份作为标识
    last_year = max(ocf.keys()) if ocf else None

    if last_year is None:
        return {}

    if cum_np == 0 or cum_np is None:
        return {last_year: None}

    ratio = cum_ocf / cum_np
    return {last_year: ratio}
