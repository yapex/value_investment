"""Tests for CAPEX Stability Calculator"""
import pytest
from value_investment.calculators.calc_capex_stability import (
    calculate,
    required_fields,
)


class TestCapexStability:
    """Test CapexStability Calculator"""

    def test_required_fields(self):
        """Test required fields are correct"""
        assert "capital_expenditure" in required_fields
        assert "total_revenue" in required_fields

    def test_stable_capex_low_stability(self):
        """Test stable capex ratio results in low stability value (good)"""
        results = {
            "capital_expenditure": {
                2019: -300,
                2020: -310,
                2021: -305,
                2022: -308,
                2023: -312,
            },
            "total_revenue": {
                2019: 10000,
                2020: 11000,
                2021: 12000,
                2022: 13000,
                2023: 14000,
            },
        }
        output = calculate(results)
        # CAPEX/revenue ~3%, stable -> low CV
        assert output[2023] < 0.15

    def test_volatile_capex_high_stability(self):
        """Test volatile capex ratio results in high stability value (bad)"""
        results = {
            "capital_expenditure": {
                2019: -1000,
                2020: -200,
                2021: -800,
                2022: -300,
                2023: -900,
            },
            "total_revenue": {
                2019: 10000,
                2020: 11000,
                2021: 12000,
                2022: 13000,
                2023: 14000,
            },
        }
        output = calculate(results)
        # CAPEX/revenue: 10%, 1.8%, 6.7%, 2.3%, 6.4% -> high variation
        assert output[2023] > 0.5

    def test_insufficient_data_returns_empty(self):
        """Test empty dict when insufficient data"""
        results = {
            "capital_expenditure": {2021: -300, 2022: -310, 2023: -305},
            "total_revenue": {2021: 10000, 2022: 11000, 2023: 12000},
        }
        output = calculate(results)
        assert output == {}

    def test_zero_revenue_skipped_in_ratio(self):
        """Test zero revenue is skipped in ratio calculation"""
        results = {
            "capital_expenditure": {
                2018: -300,
                2019: -300,
                2020: -310,
                2021: -305,
                2022: -308,
                2023: -312,
            },
            "total_revenue": {
                2018: 10000,
                2019: 10000,
                2020: 0,
                2021: 12000,
                2022: 13000,
                2023: 14000,
            },
        }
        output = calculate(results)
        # 2020 ratio not calculated due to zero revenue, but 2023 should be in output
        assert 2023 in output

    def test_negative_capex_uses_absolute(self):
        """Test negative capex uses absolute value"""
        results = {
            "capital_expenditure": {
                2019: -300,
                2020: -310,
                2021: -305,
                2022: -308,
                2023: -312,
            },
            "total_revenue": {
                2019: 10000,
                2020: 11000,
                2021: 12000,
                2022: 13000,
                2023: 14000,
            },
        }
        output = calculate(results)
        # Should use absolute value, ratio ~3%
        assert 2023 in output
        assert output[2023] > 0.02
