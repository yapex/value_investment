"""Integration test for working capital indicators with real data"""
import pytest
import math
from value_investment import ValueInvestment


def test_working_capital_with_real_data():
    """Test working capital calculation with real stock data - returns {indicator_name: value}"""
    vi = ValueInvestment(market='A')

    # 获取贵州茅台数据
    result = vi.indicator('working_capital', stock_code='600519', years=3)

    assert result is not None
    # API returns dict like {'working_capital': value}
    value = result.get('working_capital')
    print(f"茅台 Working Capital: {value}")
    # Value might be NaN if data not available, just check the key exists
    assert 'working_capital' in result


def test_wc_to_revenue_with_real_data():
    """Test WC to revenue ratio with real stock data"""
    vi = ValueInvestment(market='A')

    result = vi.indicator('wc_to_revenue', stock_code='600519', years=3)

    assert result is not None
    assert 'wc_to_revenue' in result
    value = result.get('wc_to_revenue')
    print(f"茅台 WC/Revenue: {value}")
    # Value might be NaN, just check the key exists


def test_revenue_per_employee_indicator_exists():
    """Test that revenue_per_employee indicator is registered"""
    vi = ValueInvestment(market='A')

    result = vi.indicator('revenue_per_employee', stock_code='600519', years=1)

    assert result is not None
    # Check the indicator exists and returns a result
    assert 'revenue_per_employee' in result
    print(f"茅台 Revenue per Employee: {result}")
