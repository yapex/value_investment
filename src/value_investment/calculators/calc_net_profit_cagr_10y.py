"""Net Profit CAGR 10-Year Calculator

Formula: CAGR = (end_value / start_value) ^ (1 / 10) - 1

Measures the compound annual growth rate of net profit over 10 years.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "net_profit_cagr_10y"

# 依赖字段
required_fields = ["net_profit"]

# 时间窗口（年）
WINDOW_YEARS = 10


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate net profit CAGR over 10 years

    Args:
        results: {field: {year: value}}
            - net_profit: Net profit by year

    Returns:
        {year: CAGR or None if insufficient data or invalid values}
    """
    net_profit = results.get("net_profit", {})
    
    if len(net_profit) < WINDOW_YEARS:
        return {}
    
    # Sort years
    sorted_years = sorted(net_profit.keys())
    cagrs = {}
    
    for i in range(WINDOW_YEARS - 1, len(sorted_years)):
        end_year = sorted_years[i]
        start_year = sorted_years[i - WINDOW_YEARS + 1]
        
        # Check all years in the window have valid values
        window_valid = True
        for j in range(i - WINDOW_YEARS + 1, i + 1):
            year = sorted_years[j]
            val = net_profit.get(year)
            if val is None or val <= 0:  # Must be positive for CAGR
                window_valid = False
                break
        
        if not window_valid:
            continue
        
        end_value = net_profit.get(end_year)
        start_value = net_profit.get(start_year)
        
        if end_value is None or start_value is None or start_value <= 0:
            continue
        
        # CAGR = (end/start)^(1/n) - 1
        cagr = (end_value / start_value) ** (1.0 / WINDOW_YEARS) - 1
        cagrs[end_year] = cagr
    
    return cagrs
