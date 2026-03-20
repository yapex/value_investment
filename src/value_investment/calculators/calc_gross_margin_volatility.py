"""Gross Margin Volatility Calculator

Formula: Volatility = StdDev / Mean (coefficient of variation)

Measures the stability of gross margin over time.
Lower volatility indicates more consistent pricing power and cost control.
"""
import statistics
from typing import Any

# 输出字段名
OUTPUT_FIELD = "gross_margin_volatility"

# 依赖字段
required_fields = ["gross_margin"]

# 时间窗口（年）
WINDOW_YEARS = 5


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate gross margin volatility (coefficient of variation)

    Args:
        results: {field: {year: value}}
            - gross_margin: Gross margin by year (as decimal, e.g., 0.30 for 30%)

    Returns:
        {year: volatility (std/mean) or None if insufficient data}
    """
    gross_margin = results.get("gross_margin", {})

    if len(gross_margin) < WINDOW_YEARS:
        return {}

    sorted_years = sorted(gross_margin.keys())
    volatilities = {}

    for i in range(WINDOW_YEARS - 1, len(sorted_years)):
        end_year = sorted_years[i]

        # Get window of values
        window_years = sorted_years[i - WINDOW_YEARS + 1 : i + 1]
        window_values = []

        for y in window_years:
            val = gross_margin.get(y)
            if val is None:
                window_values = []
                break
            window_values.append(val)

        # Skip if any value is missing or insufficient
        if len(window_values) < WINDOW_YEARS:
            continue

        mean_val = statistics.mean(window_values)

        # Skip if mean is zero or very small (avoid division issues)
        if abs(mean_val) < 0.001:
            continue

        # Calculate coefficient of variation (std / mean)
        stdev = statistics.stdev(window_values)
        cv = stdev / abs(mean_val)

        volatilities[end_year] = cv

    return volatilities
