"""Test for Long Term Investment Ratio Calculator"""
import pytest
from value_investment.calculators.calc_long_term_investment_ratio import calculate, required_fields, OUTPUT_FIELD


class TestLongTermInvestmentRatio:
    """Test long term investment ratio calculation"""

    def test_required_fields(self):
        assert "long_term_investment" in required_fields
        assert "total_assets" in required_fields

    def test_output_field(self):
        assert OUTPUT_FIELD == "long_term_investment_ratio"

    def test_basic_ratio_calculation(self):
        results = {
            "long_term_investment": {
                2022: 1000.0,
                2021: 900.0,
                2020: 800.0,
            },
            "total_assets": {
                2022: 12000.0,
                2021: 11000.0,
                2020: 10000.0,
            }
        }
        ratios = calculate(results)
        
        assert 2022 in ratios
        assert ratios[2022] == pytest.approx(1000.0 / 12000.0)

    def test_missing_lt_investment(self):
        results = {
            "long_term_investment": {},
            "total_assets": {2022: 12000.0}
        }
        ratios = calculate(results)
        assert len(ratios) == 0
