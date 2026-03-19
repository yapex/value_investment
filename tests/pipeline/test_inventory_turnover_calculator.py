"""Tests for InventoryTurnover Calculator"""
from value_investment.calculator_plugin import registry


def test_inventory_turnover_required_fields():
    """Test InventoryTurnover declares required fields"""
    calc = registry.get_by_name("inventory_turnover")
    assert "operating_cost" in calc.required_fields
    assert "inventory" in calc.required_fields


def test_inventory_turnover_name():
    """Test InventoryTurnover name"""
    assert registry.get_by_name("inventory_turnover").name == "inventory_turnover"


def test_inventory_turnover_calculate():
    """Test inventory turnover calculation"""
    calc = registry.get_by_name("inventory_turnover")
    results = {
        "operating_cost": {2024: 1000, 2023: 900, 2022: 800},
        "inventory": {2024: 200, 2023: 180, 2022: 160},
    }
    it = calc.calculate(results)

    # 2024: 1000 / ((200+180)/2) = 1000/190 = 5.263...
    assert abs(it[2024] - 5.263) < 0.001


def test_inventory_turnover_missing_data():
    """Test inventory turnover with missing data"""
    calc = registry.get_by_name("inventory_turnover")
    results = {
        "operating_cost": {2024: 1000},
        # inventory missing - can't calculate without inventory
    }
    it = calc.calculate(results)

    # Should handle missing data gracefully - returns empty dict when inventory missing
    assert it == {} or 2024 not in it
