"""Tests for GrossProfitCalculator"""
import pytest
from value_investment.pipeline.calculators.gross_profit import GrossProfitCalculator
from value_investment.pipeline.fields import IFRSFields


def test_gross_profit_required_fields():
    """Test GrossProfitCalculator declares required fields"""
    calc = GrossProfitCalculator()
    assert IFRSFields.TOTAL_REVENUE in calc.required_fields
    assert IFRSFields.OPERATING_COST in calc.required_fields


def test_gross_profit_name():
    """Test GrossProfitCalculator name"""
    assert GrossProfitCalculator.name == IFRSFields.GROSS_PROFIT


def test_gross_profit_calculate():
    """Test gross profit calculation"""
    calc = GrossProfitCalculator()
    results = {
        IFRSFields.TOTAL_REVENUE: {2024: 1000.0, 2023: 900.0},
        IFRSFields.OPERATING_COST: {2024: 600.0, 2023: 540.0},
    }
    gp = calc.calculate(results)

    # gross_profit = total_revenue - operating_cost
    assert gp[2024] == 400.0
    assert gp[2023] == 360.0


def test_gross_profit_missing_data():
    """Test gross profit with missing data"""
    calc = GrossProfitCalculator()
    results = {
        IFRSFields.TOTAL_REVENUE: {2024: 1000.0},
        # operating_cost missing
    }
    gp = calc.calculate(results)

    # Should handle missing data gracefully
    assert 2024 in gp
    assert gp[2024] == 1000.0  # cost defaults to 0
