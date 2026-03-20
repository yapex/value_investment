"""Tests for Receivable Revenue Growth Gap Calculator

Gap = Accounts Receivable Growth Rate - Revenue YoY Growth Rate
Used to identify potential receivables accumulation risk.
"""
import pytest
from value_investment.calculators.calc_receivable_revenue_growth_gap import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestReceivableRevenueGrowthGap:
    """Test cases for receivable_revenue_growth_gap calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert required_fields == ["accounts_receivable", "revenue_yoy"]

    def test_basic_calculation(self):
        """Test basic growth gap calculation"""
        results = {
            "accounts_receivable": {2023: 120, 2022: 100},
            "revenue_yoy": {2023: 0.2},
        }
        output = calculate(results)
        
        # ar_growth = (120 - 100) / 100 = 0.2
        # gap = 0.2 - 0.2 = 0.0
        assert output[2023] == pytest.approx(0.0, rel=1e-9)

    def test_positive_gap_risk(self):
        """Test when AR grows faster than revenue (risk signal)"""
        results = {
            "accounts_receivable": {2023: 160, 2022: 100},
            "revenue_yoy": {2023: 0.1},
        }
        output = calculate(results)
        
        # ar_growth = (160 - 100) / 100 = 0.6
        # gap = 0.6 - 0.1 = 0.5
        assert output[2023] == pytest.approx(0.5, rel=1e-9)

    def test_negative_gap_healthy(self):
        """Test when AR grows slower than revenue (healthy signal)"""
        results = {
            "accounts_receivable": {2023: 108, 2022: 100},
            "revenue_yoy": {2023: 0.2},
        }
        output = calculate(results)
        
        # ar_growth = (108 - 100) / 100 = 0.08
        # gap = 0.08 - 0.2 = -0.12
        assert output[2023] == pytest.approx(-0.12, rel=1e-9)

    def test_missing_prev_ar_not_in_output(self):
        """Test that missing previous AR is skipped"""
        results = {
            "accounts_receivable": {2023: 120},
            "revenue_yoy": {2023: 0.2},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "receivable_revenue_growth_gap"
