"""Tests for InventoryTurnover"""
import pytest
from value_investment.pipeline.calculators.inventory_turnover import InventoryTurnover
from value_investment.pipeline.fields import CustomFields, IFRSFields


def test_inventory_turnover_required_fields():
    """Test InventoryTurnover declares required fields"""
    calc = InventoryTurnover()
    assert IFRSFields.OPERATING_COST in calc.required_fields
    assert IFRSFields.INVENTORY in calc.required_fields


def test_inventory_turnover_name():
    """Test InventoryTurnover name"""
    assert InventoryTurnover.name == CustomFields.INVENTORY_TURNOVER


def test_inventory_turnover_calculate():
    """Test inventory turnover calculation"""
    calc = InventoryTurnover()
    results = {
        IFRSFields.OPERATING_COST: {2024: 1000, 2023: 900, 2022: 800},
        IFRSFields.INVENTORY: {2024: 200, 2023: 180, 2022: 160},
    }
    it = calc.calculate(results)

    # 2024: 1000 / ((200+180)/2) = 1000/190 = 5.263...
    assert abs(it[2024] - 5.263) < 0.001


def test_inventory_turnover_missing_data():
    """Test inventory turnover with missing data"""
    calc = InventoryTurnover()
    results = {
        IFRSFields.OPERATING_COST: {2024: 1000},
        # inventory missing - can't calculate without inventory
    }
    it = calc.calculate(results)

    # Should handle missing data gracefully - returns empty dict when inventory missing
    # because avg_inv = 0, division by zero is skipped
    assert it == {} or 2024 not in it
