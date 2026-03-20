"""Cash to Profit Volatility Calculator

Formula: Volatility = StdDev / Mean (coefficient of variation)

Measures the stability of cash-to-profit ratio over time.
Lower volatility indicates consistent cash generation relative to accounting profit.
"""
import statistics
from typing import Any

# 依赖字段
required_fields = ["operating_cash_flow", "net_profit"]

# 时间窗口（年）
WINDOW_YEARS = 5


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate cash-to-profit volatility (coefficient of variation)

    Args:
        results: {field: {year: value}}
            - operating_cash_flow: OCF by year
            - net_profit: Net profit by year

    Returns:
        {year: volatility (std/mean) or None if insufficient data}
    """
    ocf = results.get("operating_cash_flow", {})
    net_profit = results.get("net_profit", {})

    # Calculate ratio for each year (including those with zero/missing net_profit)
    all_years = set(ocf.keys()) | set(net_profit.keys())
    ratios = {}
    for year in all_years:
        ocf_val = ocf.get(year)
        np_val = net_profit.get(year)
        
        if ocf_val is not None and np_val is not None and np_val != 0:
            ratios[year] = ocf_val / np_val

    if len(ratios) < WINDOW_YEARS:
        return {}

    sorted_years = sorted(ratios.keys())
    volatilities = {}

    for i in range(WINDOW_YEARS - 1, len(sorted_years)):
        end_year = sorted_years[i]

        # Get window of values
        window_years = sorted_years[i - WINDOW_YEARS + 1 : i + 1]
        window_values = []

        for y in window_years:
            val = ratios.get(y)
            if val is None:
                window_values = []
                break
            window_values.append(val)

        # Skip if any value is missing or insufficient
        if len(window_values) < WINDOW_YEARS:
            continue

        mean_val = statistics.mean(window_values)

        # Skip if mean is zero or very small
        if abs(mean_val) < 0.001:
            continue

        # Calculate coefficient of variation (std / mean)
        stdev = statistics.stdev(window_values)
        cv = stdev / abs(mean_val)

        volatilities[end_year] = cv

    return volatilities
