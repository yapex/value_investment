"""Test for Revenue CAGR 10-Year Calculator

Formula: CAGR = (end_value / start_value) ^ (1 / 10) - 1
"""
import pytest
from value_investment.calculators.calc_revenue_cagr_10y import calculate, required_fields, OUTPUT_FIELD


class TestRevenueCAGR10Y:
    """Test revenue CAGR 10-year calculation"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert "total_revenue" in required_fields

    def test_basic_calculation(self):
        """Test basic CAGR calculation with 10+ years of data"""
        # Revenue: 1000 -> 3000 over 10 years (2015-2024)
        # CAGR = (3000/1100)^(1/10) - 1 ≈ 0.1057
        results = {
            "total_revenue": {
                2024: 3000.0,
                2023: 2700.0,
                2022: 2400.0,
                2021: 2100.0,
                2020: 1800.0,
                2019: 1700.0,
                2018: 1500.0,
                2017: 1350.0,
                2016: 1200.0,
                2015: 1100.0,
                2014: 1000.0,
            },
        }

        cagr = calculate(results)

        # Should calculate CAGR for 2024 (using 2015-2024, 10 years)
        # (3000/1100)^(1/10) - 1 = 0.1057
        assert 2024 in cagr
        assert cagr[2024] == pytest.approx(0.1057, rel=1e-2)

    def test_output_field(self):
        """Test OUTPUT_FIELD constant is defined"""
        assert OUTPUT_FIELD == "revenue_cagr_10y"

    def test_insufficient_data(self):
        """Test handling of insufficient data (less than 10 years)"""
        results = {
            "total_revenue": {
                2024: 300.0,
                2023: 270.0,
                2022: 240.0,
            },
        }

        cagr = calculate(results)
        assert len(cagr) == 0

    def test_zero_value_in_window(self):
        """Test with zero value in window (should skip)"""
        results = {
            "total_revenue": {
                2024: 3000.0,
                2023: 2700.0,
                2022: 2400.0,
                2021: 2100.0,
                2020: 1800.0,
                2019: 1700.0,
                2018: 0.0,  # Invalid
                2017: 1350.0,
                2016: 1200.0,
                2015: 1100.0,
                2014: 1000.0,
            },
        }
        cagr = calculate(results)
        # Should skip windows containing zero
        assert 2024 not in cagr or cagr.get(2024) is None

    def test_none_value_handling(self):
        """Test handling of None values"""
        results = {
            "total_revenue": {
                2024: 3000.0,
                2023: None,
                2022: 2400.0,
                2021: 2100.0,
                2020: 1800.0,
                2019: 1700.0,
                2018: 1500.0,
                2017: 1350.0,
                2016: 1200.0,
                2015: 1100.0,
                2014: 1000.0,
            },
        }
        cagr = calculate(results)
        assert 2024 not in cagr
