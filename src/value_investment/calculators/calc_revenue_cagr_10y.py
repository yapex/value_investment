"""Revenue CAGR 10-Year Calculator

Formula: CAGR = (end_value / start_value) ^ (1 / 10) - 1

Measures the compound annual growth rate of total revenue over 10 years.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "revenue_cagr_10y"

# 依赖字段
required_fields = ["total_revenue"]

# 时间窗口（年）
WINDOW_YEARS = 10


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate revenue CAGR over 10 years

    Args:
        results: {field: {year: value}}
            - total_revenue: Total revenue by year

    Returns:
        {year: CAGR or None if insufficient data or invalid values}
    """
    revenue = results.get("total_revenue", {})
    
    if len(revenue) < WINDOW_YEARS:
        return {}
    
    # Sort years
    sorted_years = sorted(revenue.keys())
    cagrs = {}
    
    for i in range(WINDOW_YEARS - 1, len(sorted_years)):
        end_year = sorted_years[i]
        start_year = sorted_years[i - WINDOW_YEARS + 1]
        
        # Check all years in the window have valid values
        window_valid = True
        for j in range(i - WINDOW_YEARS + 1, i + 1):
            year = sorted_years[j]
            val = revenue.get(year)
            if val is None or val <= 0:  # Must be positive for CAGR
                window_valid = False
                break
        
        if not window_valid:
            continue
        
        end_value = revenue.get(end_year)
        start_value = revenue.get(start_year)
        
        if end_value is None or start_value is None or start_value <= 0:
            continue
        
        # CAGR = (end/start)^(1/n) - 1
        cagr = (end_value / start_value) ** (1.0 / WINDOW_YEARS) - 1
        cagrs[end_year] = cagr
    
    return cagrs
