"""Tests for CAPEX to Revenue Ratio Calculator"""
import pytest
from value_investment.calculators.calc_capex_to_revenue_ratio import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestCapexToRevenueRatio:
    """Test cases for capex_to_revenue_ratio calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert required_fields == ["capital_expenditure", "total_revenue"]

    def test_basic_calculation(self):
        """Test basic CAPEX to revenue ratio calculation"""
        results = {
            "capital_expenditure": {2023: 300, 2022: 250},
            "total_revenue": {2023: 1000, 2022: 800},
        }
        output = calculate(results)
        
        # 300 / 1000 = 0.3
        assert output[2023] == pytest.approx(0.3, rel=1e-9)
        # 250 / 800 = 0.3125
        assert output[2022] == pytest.approx(0.3125, rel=1e-9)

    def test_missing_revenue_returns_none(self):
        """Test that missing revenue returns None"""
        results = {
            "capital_expenditure": {2023: 300},
            "total_revenue": {},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_zero_revenue_returns_none(self):
        """Test that zero revenue returns None (avoids division by zero)"""
        results = {
            "capital_expenditure": {2023: 300},
            "total_revenue": {2023: 0},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_zero_capex(self):
        """Test when CAPEX is zero"""
        results = {
            "capital_expenditure": {2023: 0},
            "total_revenue": {2023: 1000},
        }
        output = calculate(results)
        
        # 0 / 1000 = 0
        assert output[2023] == pytest.approx(0.0, rel=1e-9)

    def test_capital_intensive_company(self):
        """Test for capital-intensive company (>0.3 is considered high)"""
        results = {
            "capital_expenditure": {2023: 500},
            "total_revenue": {2023: 1000},
        }
        output = calculate(results)
        
        # 500 / 1000 = 0.5
        assert output[2023] == pytest.approx(0.5, rel=1e-9)
        assert output[2023] > 0.3  # Capital intensive threshold

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "capex_to_revenue_ratio"
