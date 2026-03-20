"""ROE Volatility Calculator

Formula: Volatility = StdDev / Mean (coefficient of variation)

Measures the stability of ROE over time.
Lower volatility indicates more consistent profitability.
"""
import statistics
from typing import Any

# 输出字段名
OUTPUT_FIELD = "roe_volatility"

# 依赖字段
required_fields = ["roe"]

# 时间窗口（年）
WINDOW_YEARS = 5


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate ROE volatility (coefficient of variation)

    Args:
        results: {field: {year: value}}
            - roe: ROE by year (as decimal, e.g., 0.15 for 15%)

    Returns:
        {year: volatility (std/mean) or None if insufficient data}
    """
    roe = results.get("roe", {})
    
    if len(roe) < WINDOW_YEARS:
        return {}
    
    # Sort years
    sorted_years = sorted(roe.keys())
    volatilities = {}
    
    for i in range(WINDOW_YEARS - 1, len(sorted_years)):
        end_year = sorted_years[i]
        
        # Get window of values
        window_years = sorted_years[i - WINDOW_YEARS + 1 : i + 1]
        window_values = []
        
        for y in window_years:
            val = roe.get(y)
            if val is None:
                window_values = []
                break
            window_values.append(val)
        
        # Skip if any value is missing or insufficient
        if len(window_values) < WINDOW_YEARS:
            continue
        
        mean_val = statistics.mean(window_values)
        
        # Skip if mean is zero (all zeros or negatives)
        if mean_val == 0:
            continue
        
        # Calculate coefficient of variation (std / mean)
        stdev = statistics.stdev(window_values)
        cv = stdev / abs(mean_val)
        
        volatilities[end_year] = cv
    
    return volatilities
