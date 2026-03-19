"""Tests for GrossProfit Calculator"""
from value_investment.calculator_plugin import registry


def test_gross_profit_required_fields():
    """Test GrossProfit declares required fields"""
    calc = registry.get_by_name("gross_profit")
    assert "total_revenue" in calc.required_fields
    assert "operating_cost" in calc.required_fields


def test_gross_profit_name():
    """Test GrossProfit name"""
    assert registry.get_by_name("gross_profit").name == "gross_profit"


def test_gross_profit_calculate():
    """Test gross profit calculation"""
    calc = registry.get_by_name("gross_profit")
    results = {
        "total_revenue": {2024: 1000.0, 2023: 900.0},
        "operating_cost": {2024: 600.0, 2023: 540.0},
    }
    gp = calc.calculate(results)

    # gross_profit = total_revenue - operating_cost
    assert gp[2024] == 400.0
    assert gp[2023] == 360.0


def test_gross_profit_missing_data():
    """Test gross profit with missing data"""
    calc = registry.get_by_name("gross_profit")
    results = {
        "total_revenue": {2024: 1000.0},
        # operating_cost missing
    }
    gp = calc.calculate(results)

    # Should handle missing data gracefully
    assert 2024 in gp
    assert gp[2024] == 1000.0  # cost defaults to 0
