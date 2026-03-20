"""Test for Revenue CAGR 5-Year Calculator

Formula: CAGR = (end_value / start_value) ^ (1 / 5) - 1
"""
import pytest
from value_investment.calculators.calc_revenue_cagr_5y import calculate, required_fields, OUTPUT_FIELD


class TestRevenueCAGR5Y:
    """Test revenue CAGR 5-year calculation"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert "total_revenue" in required_fields

    def test_basic_calculation(self):
        """Test basic CAGR calculation with 5 years of data"""
        # Revenue: 100 -> 200 over 5 years
        # CAGR = (200/100)^(1/5) - 1 = 2^0.2 - 1 ≈ 0.1487
        results = {
            "total_revenue": {
                2023: 200.0,
                2022: 180.0,
                2021: 160.0,
                2020: 140.0,
                2019: 100.0,
            },
        }

        cagr = calculate(results)

        # Should calculate CAGR for 2023 (using 2019-2023)
        # (200/100)^(1/5) - 1 = 0.1487
        assert 2023 in cagr
        assert cagr[2023] == pytest.approx(0.1487, rel=1e-2)

    def test_negative_cagr(self):
        """Test CAGR with declining revenue"""
        # Revenue: 200 -> 100 over 5 years (declining)
        # CAGR = (100/200)^(1/5) - 1 = 0.5^0.2 - 1 ≈ -0.0746
        results = {
            "total_revenue": {
                2023: 100.0,
                2022: 120.0,
                2021: 140.0,
                2020: 160.0,
                2019: 200.0,
            },
        }

        cagr = calculate(results)
        # Should be negative
        assert 2023 in cagr
        assert cagr[2023] < 0

    def test_insufficient_data(self):
        """Test handling of insufficient data (less than 5 years)"""
        results = {
            "total_revenue": {
                2023: 200.0,
                2022: 180.0,
                2021: 160.0,
            },
        }

        cagr = calculate(results)
        assert len(cagr) == 0  # Should not produce any results

    def test_exact_5_years(self):
        """Test with exactly 5 years of data"""
        results = {
            "total_revenue": {
                2023: 161.0,
                2022: 151.0,
                2021: 141.0,
                2020: 131.0,
                2019: 121.0,
            },
        }

        cagr = calculate(results)
        # CAGR ≈ 7.4%
        assert 2023 in cagr
        assert cagr[2023] > 0

    def test_zero_start_value(self):
        """Test handling of zero start value"""
        results = {
            "total_revenue": {
                2023: 200.0,
                2022: 180.0,
                2021: 160.0,
                2020: 140.0,
                2019: 0.0,  # Zero start value
            },
        }

        cagr = calculate(results)
        # Should skip calculation when start value is 0 or None
        assert 2023 not in cagr or cagr[2023] is None

    def test_zero_end_value(self):
        """Test handling of zero end value"""
        results = {
            "total_revenue": {
                2023: 0.0,  # Zero end value
                2022: 180.0,
                2021: 160.0,
                2020: 140.0,
                2019: 100.0,
            },
        }

        cagr = calculate(results)
        # Should skip calculation when end value is 0 or None
        assert 2023 not in cagr or cagr[2023] is None

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD constant is defined"""
        assert OUTPUT_FIELD == "revenue_cagr_5y"

    def test_none_values(self):
        """Test handling of None values in data"""
        results = {
            "total_revenue": {
                2023: 200.0,
                2022: None,
                2021: 160.0,
                2020: 140.0,
                2019: 100.0,
            },
        }

        cagr = calculate(results)
        # Should skip when any value is None
        assert 2023 not in cagr or cagr[2023] is None
