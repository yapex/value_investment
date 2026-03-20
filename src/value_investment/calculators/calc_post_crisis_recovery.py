"""Post Crisis Recovery Speed Calculator

Recovery Speed = Years to recover to pre-crisis level after crisis

Measures how quickly a company recovers to its pre-crisis revenue level
after experiencing a decline.

Returns the number of years needed to exceed the pre-crisis peak,
or None if still in crisis.
"""
from typing import Any

# 依赖字段
required_fields = ["total_revenue"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate post crisis recovery speed

    Args:
        results: {field: {year: value}}
            - total_revenue: Total revenue by year

    Returns:
        {year: recovery years or None if not recovered}
    """
    revenue = results.get("total_revenue", {})

    if len(revenue) < 4:
        return {}

    sorted_years = sorted(revenue.keys())
    recoveries = {}

    for i in range(3, len(sorted_years)):
        current_year = sorted_years[i]
        current_rev = revenue.get(current_year)

        if current_rev is None:
            continue

        # Find pre-crisis peak (highest revenue in previous 3 years)
        pre_years = sorted_years[max(0, i - 3) : i]
        pre_peak = None
        for y in pre_years:
            val = revenue.get(y)
            if val is not None:
                if pre_peak is None or val > pre_peak:
                    pre_peak = val

        # If current is below pre-crisis peak, we're in crisis
        if pre_peak is not None and current_rev < pre_peak:
            # Count years to recover
            recovery_years = 1
            for j in range(i + 1, len(sorted_years)):
                future_rev = revenue.get(sorted_years[j])
                if future_rev is not None and future_rev > pre_peak:
                    recoveries[current_year] = recovery_years
                    break
                recovery_years += 1
            else:
                # Still in crisis, return None
                recoveries[current_year] = None
        else:
            # Already recovered or no crisis
            recoveries[current_year] = 0.0

    return recoveries
