"""Tests for ROIC Calculator"""
import pytest
from value_investment.pipeline.calculators.roic import ROICCalculator


def test_roic_required_fields():
    """Test ROIC calculator declares required fields"""
    calc = ROICCalculator()
    assert "ebit" in calc.required_fields
    assert "total_assets" in calc.required_fields
    assert "cash" in calc.required_fields
    assert "current_liabilities" in calc.required_fields
    assert "roic" not in calc.required_fields  # 这是输出，不是输入


def test_roic_calculate():
    """Test ROIC calculation"""
    calc = ROICCalculator()
    results = {
        "ebit": {2024: 100.0, 2023: 90.0},
        "total_assets": {2024: 1000.0, 2023: 900.0},
        "cash": {2024: 200.0, 2023: 180.0},
        "current_liabilities": {2024: 300.0, 2023: 280.0},
    }
    roic = calc.calculate(results)
    # ROIC = EBIT / (Total Assets - Cash - Current Liabilities)
    # 2024: 100 / (1000 - 200 - 300) = 100 / 500 = 0.2 = 20%
    # 2023: 90 / (900 - 180 - 280) = 90 / 440 = 0.2045... = 20.45%
    assert abs(roic[2024] - 0.2) < 0.001
    assert abs(roic[2023] - 0.2045) < 0.001
