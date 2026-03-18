"""Tests for ROIC Calculator"""
import pytest
from value_investment.pipeline.calculators.roic import ROICCalculator
from value_investment.pipeline.fields import IFRSFields, CustomFields


def test_roic_required_fields():
    """Test ROIC calculator declares required fields"""
    calc = ROICCalculator()
    assert calc.required_fields == {
        IFRSFields.OPERATING_PROFIT,
        IFRSFields.TOTAL_ASSETS,
        IFRSFields.CASH_AND_EQUIVALENTS,
        IFRSFields.CURRENT_LIABILITIES,
    }


def test_roic_name():
    """Test ROIC calculator name"""
    assert ROICCalculator.name == CustomFields.ROIC


def test_roic_calculate():
    """Test ROIC calculation"""
    calc = ROICCalculator()
    results = {
        IFRSFields.OPERATING_PROFIT: {2024: 100.0, 2023: 90.0},
        IFRSFields.TOTAL_ASSETS: {2024: 1000.0, 2023: 900.0},
        IFRSFields.CASH_AND_EQUIVALENTS: {2024: 200.0, 2023: 180.0},
        IFRSFields.CURRENT_LIABILITIES: {2024: 300.0, 2023: 280.0},
    }
    roic = calc.calculate(results)
    # ROIC = Operating Profit / (Total Assets - Cash - Current Liabilities)
    # 2024: 100 / (1000 - 200 - 300) = 100 / 500 = 0.2 = 20%
    # 2023: 90 / (900 - 180 - 280) = 90 / 440 = 0.2045... = 20.45%
    assert abs(roic[2024] - 0.2) < 0.001
    assert abs(roic[2023] - 0.2045) < 0.001
