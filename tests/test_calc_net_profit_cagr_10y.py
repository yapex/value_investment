"""Test for Net Profit CAGR 10-Year Calculator

Formula: CAGR = (end_value / start_value) ^ (1 / 10) - 1
"""
import pytest
from value_investment.calculators.calc_net_profit_cagr_10y import calculate, required_fields, OUTPUT_FIELD


class TestNetProfitCAGR10Y:
    """Test net profit CAGR 10-year calculation"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert "net_profit" in required_fields

    def test_basic_calculation(self):
        """Test basic CAGR calculation with 10+ years of data"""
        # Net profit: 200 -> 600 over 10 years (2015-2024)
        # CAGR = (600/220)^(1/10) - 1 ≈ 0.1057
        results = {
            "net_profit": {
                2024: 600.0,
                2023: 540.0,
                2022: 480.0,
                2021: 420.0,
                2020: 380.0,
                2019: 350.0,
                2018: 320.0,
                2017: 280.0,
                2016: 250.0,
                2015: 220.0,
                2014: 200.0,
            },
        }

        cagr = calculate(results)

        # Should calculate CAGR for 2024 (using 2015-2024, 10 years)
        assert 2024 in cagr
        assert cagr[2024] == pytest.approx(0.1057, rel=1e-2)

    def test_output_field(self):
        """Test OUTPUT_FIELD constant is defined"""
        assert OUTPUT_FIELD == "net_profit_cagr_10y"

    def test_insufficient_data(self):
        """Test with insufficient data (less than 10 years)"""
        results = {
            "net_profit": {
                2024: 600.0,
                2023: 540.0,
                2022: 480.0,
            },
        }
        cagr = calculate(results)
        assert len(cagr) == 0

    def test_negative_profit_handling(self):
        """Test handling of negative profit"""
        results = {
            "net_profit": {
                2024: 600.0,
                2023: 540.0,
                2022: 480.0,
                2021: 420.0,
                2020: 380.0,
                2019: 350.0,
                2018: 320.0,
                2017: 280.0,
                2016: 250.0,
                2015: -50.0,  # Negative
                2014: 200.0,
            },
        }
        cagr = calculate(results)
        # Should skip windows containing negative or zero values
        assert 2024 not in cagr
