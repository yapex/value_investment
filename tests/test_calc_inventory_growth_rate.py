"""Tests for Inventory Growth Rate Calculator"""
import pytest
from value_investment.calculators.calc_inventory_growth_rate import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestInventoryGrowthRate:
    """Test cases for inventory_growth_rate calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert required_fields == ["inventory"]

    def test_basic_calculation(self):
        """Test basic inventory growth rate calculation"""
        results = {
            "inventory": {2023: 100, 2022: 80, 2021: 50},
        }
        output = calculate(results)
        
        # (100 - 80) / 80 = 0.25
        assert output[2023] == pytest.approx(0.25, rel=1e-9)
        # (80 - 50) / 50 = 0.6
        assert output[2022] == pytest.approx(0.6, rel=1e-9)

    def test_first_year_no_prev_returns_none(self):
        """Test that first year with no previous data returns None"""
        results = {
            "inventory": {2023: 100},
        }
        output = calculate(results)
        
        # No previous year data, should be None
        assert 2023 not in output

    def test_zero_prev_inventory_not_in_output(self):
        """Test that zero previous inventory is skipped (avoids division by zero)"""
        results = {
            "inventory": {2023: 100, 2022: 0},
        }
        output = calculate(results)
        
        # prev is 0, skip to avoid division by zero
        assert 2023 not in output

    def test_negative_growth_rate(self):
        """Test when inventory decreases (negative growth)"""
        results = {
            "inventory": {2023: 80, 2022: 100},
        }
        output = calculate(results)
        
        # (80 - 100) / 100 = -0.2
        assert output[2023] == pytest.approx(-0.2, rel=1e-9)

    def test_zero_inventory_stays_zero(self):
        """Test when current inventory is zero"""
        results = {
            "inventory": {2023: 0, 2022: 100},
        }
        output = calculate(results)
        
        # (0 - 100) / 100 = -1.0
        assert output[2023] == pytest.approx(-1.0, rel=1e-9)

    def test_missing_prev_year_returns_none(self):
        """Test that missing previous year returns None"""
        results = {
            "inventory": {2023: 100, 2022: 80, 2020: 50},
        }
        output = calculate(results)
        
        # 2023 has prev (2022) -> 0.25
        assert output[2023] == pytest.approx(0.25, rel=1e-9)
        # 2022 has prev (2021=missing) -> not in output
        assert 2022 not in output
        # 2020 has no output (only one year)
        assert 2020 not in output

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "inventory_growth_rate"
