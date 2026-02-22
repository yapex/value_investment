import pytest
from value_investment.indicators.base import IIndicator
from value_investment.indicators.simple import ROEIndicator

def test_indicator_implements_protocol():
    """ROEIndicator should satisfy IIndicator Protocol"""
    # Check class has required Protocol methods
    indicator = ROEIndicator()

    assert hasattr(indicator, 'calculate')
    assert hasattr(indicator, 'get_required_fields')
    assert hasattr(indicator, 'name')
    assert hasattr(indicator, 'needs')
