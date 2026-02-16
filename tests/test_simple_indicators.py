"""Test for simple indicators"""
import pytest
from value_investment.api import ValueInvestment


def test_indicator_factory_has_roe():
    """Test that ROE indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "ROE" in indicators, f"ROE not in indicators: {indicators}"


def test_indicator_factory_has_gross_margin():
    """Test that gross margin indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "gross_margin" in indicators, f"gross_margin not in indicators: {indicators}"


def test_indicator_factory_has_roa():
    """Test that ROA indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "ROA" in indicators, f"ROA not in indicators: {indicators}"
