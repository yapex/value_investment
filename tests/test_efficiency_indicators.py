"""Tests for efficiency indicators - expense ratio, fee rate, fixed asset turnover"""
import pytest
from value_investment.api import ValueInvestment


def test_indicator_factory_has_expense_ratio():
    """Test that expense_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "expense_ratio" in indicators, f"expense_ratio not in indicators: {indicators}"


def test_indicator_factory_has_fee_rate():
    """Test that fee_rate indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "fee_rate" in indicators, f"fee_rate not in indicators: {indicators}"


def test_indicator_factory_has_fixed_asset_turnover():
    """Test that fixed_asset_turnover indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "fixed_asset_turnover" in indicators, f"fixed_asset_turnover not in indicators: {indicators}"


def test_expense_ratio_calculation():
    """Test expense_ratio calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("expense_ratio", "600519")
    assert result is not None
    assert result.unit == "%"


def test_fee_rate_calculation():
    """Test fee_rate calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("fee_rate", "600519")
    assert result is not None
    assert result.unit == "%"


def test_fixed_asset_turnover_calculation():
    """Test fixed_asset_turnover calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("fixed_asset_turnover", "600519")
    assert result is not None
    assert result.unit == "ratio"
