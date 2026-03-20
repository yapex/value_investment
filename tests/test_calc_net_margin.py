"""Tests for Net Margin Calculator"""
import pytest
from value_investment.calculators.calc_net_margin import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestNetMargin:
    """Test cases for net_margin calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert set(required_fields) == {"net_profit", "total_revenue"}

    def test_basic_calculation(self):
        """Test basic net margin calculation"""
        results = {
            "net_profit": {2023: 100000000, 2022: 80000000},
            "total_revenue": {2023: 500000000, 2022: 400000000},
        }
        output = calculate(results)

        # 2023: 100000000 / 500000000 = 0.2 (20%)
        assert output[2023] == pytest.approx(0.2, rel=1e-9)
        # 2022: 80000000 / 400000000 = 0.2 (20%)
        assert output[2022] == pytest.approx(0.2, rel=1e-9)

    def test_different_margins(self):
        """Test with different profit margins"""
        results = {
            "net_profit": {2023: 150000000, 2022: 60000000},
            "total_revenue": {2023: 500000000, 2022: 400000000},
        }
        output = calculate(results)

        # 2023: 150M / 500M = 0.3 (30%)
        assert output[2023] == pytest.approx(0.3, rel=1e-9)
        # 2022: 60M / 400M = 0.15 (15%)
        assert output[2022] == pytest.approx(0.15, rel=1e-9)

    def test_zero_revenue_returns_none(self):
        """Test that zero revenue returns None"""
        results = {
            "net_profit": {2023: 100000000},
            "total_revenue": {2023: 0},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_missing_revenue_returns_none(self):
        """Test that missing revenue returns None"""
        results = {
            "net_profit": {2023: 100000000},
            "total_revenue": {},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "net_margin"
