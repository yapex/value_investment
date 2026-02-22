import pytest
from value_investment.indicators.simple import LatestMarketCapIndicator
from value_investment.indicators.complex import ImpliedGrowthIndicator, PEPercentileIndicator

def test_latest_market_cap_has_needs():
    indicator = LatestMarketCapIndicator()
    assert hasattr(indicator, 'needs'), "LatestMarketCapIndicator must have 'needs' attribute"
    # Should include financial_indicator for HK market cap
    assert 'financial_indicator' in indicator.needs

def test_implied_growth_has_needs():
    indicator = ImpliedGrowthIndicator()
    assert hasattr(indicator, 'needs'), "ImpliedGrowthIndicator must have 'needs' attribute"
    assert 'financial_indicator' in indicator.needs

def test_pe_percentile_has_needs():
    indicator = PEPercentileIndicator()
    assert hasattr(indicator, 'needs'), "PEPercentileIndicator must have 'needs' attribute"
    assert 'quarterly' in indicator.needs
