"""Tests for Core Business Ratio Calculator

Core Business Ratio = Main Business Income / Total Revenue
Measures how focused the company is on its core business.
"""
import pytest
from value_investment.calculators.calc_core_business_ratio import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestCoreBusinessRatio:
    """Test cases for core_business_ratio calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert required_fields == ["main_business_income", "total_revenue"]

    def test_basic_calculation(self):
        """Test basic core business ratio calculation"""
        results = {
            "main_business_income": {2023: 1000, 2022: 800},
            "total_revenue": {2023: 1100, 2022: 900},
        }
        output = calculate(results)
        
        # 1000/1100 = 0.909
        assert output[2023] == pytest.approx(0.90909, rel=1e-4)
        # 800/900 = 0.889
        assert output[2022] == pytest.approx(0.8889, rel=1e-4)

    def test_perfect_focus(self):
        """Test when all revenue is from core business"""
        results = {
            "main_business_income": {2023: 1000},
            "total_revenue": {2023: 1000},
        }
        output = calculate(results)
        
        # 1000/1000 = 1.0
        assert output[2023] == pytest.approx(1.0, rel=1e-9)

    def test_zero_revenue_skipped(self):
        """Test that zero total_revenue is skipped (avoids division by zero)"""
        results = {
            "main_business_income": {2023: 1000},
            "total_revenue": {2023: 0},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_missing_main_business(self):
        """Test that missing main_business_income skips the year"""
        results = {
            "main_business_income": {2023: 1000},
            "total_revenue": {2023: 1100, 2022: 900},
        }
        output = calculate(results)
        
        # 2023: main_business_income=1000, total=1100 -> 0.909
        assert output[2023] == pytest.approx(0.90909, rel=1e-4)
        # 2022: no main_business_income -> not in output
        assert 2022 not in output

    def test_missing_total_revenue(self):
        """Test that missing total_revenue skips the year"""
        results = {
            "main_business_income": {2023: 1000, 2022: 800},
            "total_revenue": {2023: 1100},
        }
        output = calculate(results)
        
        # 2023: has both -> 0.909
        assert output[2023] == pytest.approx(0.90909, rel=1e-4)
        # 2022: no total_revenue -> not in output
        assert 2022 not in output

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "core_business_ratio"
