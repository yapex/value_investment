"""Tests for Inventory Revenue Growth Gap Calculator

Gap = Inventory Growth Rate - Revenue YoY Growth Rate
Used to identify potential inventory accumulation risk.
"""
import pytest
from value_investment.calculators.calc_inventory_revenue_growth_gap import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestInventoryRevenueGrowthGap:
    """Test cases for inventory_revenue_growth_gap calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert required_fields == ["inventory", "revenue_yoy"]

    def test_basic_calculation(self):
        """Test basic growth gap calculation"""
        results = {
            "inventory": {2023: 110, 2022: 100},
            "revenue_yoy": {2023: 0.1, 2022: 0.2},
        }
        output = calculate(results)
        
        # inventory_growth = (110 - 100) / 100 = 0.1
        # gap = 0.1 - 0.1 = 0.0
        assert output[2023] == pytest.approx(0.0, rel=1e-9)
        # inventory_growth = (100 - 99) / 99 = ~0.01 (99 is not in data)
        # Actually prev year (2021) not in data, so 2022 won't have output
        assert 2022 not in output

    def test_positive_gap_risk(self):
        """Test when inventory grows faster than revenue (risk signal)"""
        results = {
            "inventory": {2023: 150, 2022: 100},
            "revenue_yoy": {2023: 0.1},  # revenue only grew 10%
        }
        output = calculate(results)
        
        # inv_growth = (150 - 100) / 100 = 0.5
        # gap = 0.5 - 0.1 = 0.4
        assert output[2023] == pytest.approx(0.4, rel=1e-9)

    def test_negative_gap_healthy(self):
        """Test when inventory grows slower than revenue (healthy signal)"""
        results = {
            "inventory": {2023: 105, 2022: 100},
            "revenue_yoy": {2023: 0.2},  # revenue grew 20%
        }
        output = calculate(results)
        
        # inv_growth = (105 - 100) / 100 = 0.05
        # gap = 0.05 - 0.2 = -0.15
        assert output[2023] == pytest.approx(-0.15, rel=1e-9)

    def test_missing_prev_inventory_not_in_output(self):
        """Test that missing previous inventory is skipped"""
        results = {
            "inventory": {2023: 110},
            "revenue_yoy": {2023: 0.1},
        }
        output = calculate(results)
        
        # No prev inventory -> no inventory_growth -> skip
        assert 2023 not in output

    def test_missing_revenue_yoy_not_in_output(self):
        """Test that missing revenue_yoy is skipped"""
        results = {
            "inventory": {2023: 110, 2022: 100},
            "revenue_yoy": {},  # No revenue_yoy data
        }
        output = calculate(results)
        
        # revenue_yoy missing -> skip
        assert 2023 not in output

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "inventory_revenue_growth_gap"
