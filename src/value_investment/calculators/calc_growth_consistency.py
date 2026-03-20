"""Growth Consistency Calculator

Growth Consistency = Years with Positive Growth / Total Years

Measures the consistency of revenue growth over time.
- Close to 1.0: Very consistent positive growth
- Close to 0.0: Irregular growth or frequent declines

Formula: count(YoY > threshold) / total_years
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "growth_consistency"

# 依赖字段
required_fields = ["revenue_yoy"]

# 阈值：大于此值视为正增长（百分比形式，如 0.02 表示 2%）
POSITIVE_GROWTH_THRESHOLD = 0.0

# 时间窗口（年）
WINDOW_YEARS = 5


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate growth consistency

    Args:
        results: {field: {year: value}}
            - revenue_yoy: Revenue year-over-year growth rate by year (as decimal)

    Returns:
        {year: consistency ratio or None if insufficient data}
    """
    revenue_yoy = results.get("revenue_yoy", {})

    if len(revenue_yoy) < WINDOW_YEARS:
        return {}

    sorted_years = sorted(revenue_yoy.keys())
    consistencies = {}

    for i in range(WINDOW_YEARS - 1, len(sorted_years)):
        end_year = sorted_years[i]

        # Get window of values
        window_years = sorted_years[i - WINDOW_YEARS + 1 : i + 1]
        valid_years = 0
        positive_years = 0

        for y in window_years:
            val = revenue_yoy.get(y)
            if val is not None:
                valid_years += 1
                if val > POSITIVE_GROWTH_THRESHOLD:
                    positive_years += 1

        # Only calculate if all years have data
        if valid_years == WINDOW_YEARS:
            consistencies[end_year] = positive_years / WINDOW_YEARS
        elif valid_years > 0:
            # Partial window - use available data
            consistencies[end_year] = positive_years / valid_years

    return consistencies
