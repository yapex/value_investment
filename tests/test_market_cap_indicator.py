"""Test MarketCapIndicator"""
import pytest
from value_investment.indicators.market_cap import MarketCapIndicator


def test_indicator_has_name():
    """MarketCapIndicator should have name 'market_cap'"""
    indicator = MarketCapIndicator()
    assert indicator.name == "market_cap"


def test_indicator_has_description():
    """MarketCapIndicator should have description"""
    indicator = MarketCapIndicator()
    assert indicator.description is not None
    assert len(indicator.description) > 0
