import pytest
import re

def test_latest_market_cap_no_provider_kwarg():
    """LatestMarketCapIndicator should not use kwargs.get('provider') in code"""
    from value_investment.indicators.simple import LatestMarketCapIndicator
    import inspect

    indicator = LatestMarketCapIndicator()
    source = inspect.getsource(indicator.calculate)

    # Remove comments to avoid false positives
    source_no_comments = re.sub(r'#.*$', '', source, flags=re.MULTILINE)

    # Check for actual code pattern
    assert "kwargs.get('provider')" not in source_no_comments

def test_implied_growth_no_provider_kwarg():
    """ImpliedGrowthIndicator should not use kwargs.get('provider') in code"""
    from value_investment.indicators.complex import ImpliedGrowthIndicator
    import inspect

    indicator = ImpliedGrowthIndicator()
    source = inspect.getsource(indicator.calculate)

    # Remove comments to avoid false positives
    source_no_comments = re.sub(r'#.*$', '', source, flags=re.MULTILINE)

    # Check for actual code pattern
    assert "kwargs.get('provider')" not in source_no_comments

def test_pe_percentile_no_provider_kwarg():
    """PEPercentileIndicator should not use kwargs.get('provider') in code"""
    from value_investment.indicators.complex import PEPercentileIndicator
    import inspect

    indicator = PEPercentileIndicator()
    source = inspect.getsource(indicator.calculate)

    # Remove comments to avoid false positives
    source_no_comments = re.sub(r'#.*$', '', source, flags=re.MULTILINE)

    # Check for actual code pattern
    assert "kwargs.get('provider')" not in source_no_comments
