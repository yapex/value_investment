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


def test_indicator_factory_has_latest_market_cap():
    """Test that latest_market_cap indicator is available"""
    vi = ValueInvestment(market="HK")
    indicators = vi.list_indicators()
    assert "latest_market_cap" in indicators, f"latest_market_cap not in indicators: {indicators}"


def test_latest_market_cap_calculation():
    """Test latest_market_cap calculation for HK stock"""
    vi = ValueInvestment(market="HK")
    # 使用 mock 数据测试计算逻辑
    result = vi.calculate_indicator("latest_market_cap", "00700")
    assert result is not None
    # 市值应该大于0
    assert result.value > 0, f"Expected positive market cap, got {result.value}"
    # 单位应该为空
    assert result.unit == ""
