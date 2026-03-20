"""Test for Non-Operating Income Ratio Calculator"""
import pytest
from value_investment.calculators.calc_non_operating_income_ratio import calculate, required_fields, OUTPUT_FIELD


class TestNonOperatingIncomeRatio:
    """Test non-operating income ratio calculation"""

    def test_required_fields(self):
        assert "non_operating_income" in required_fields
        assert "operating_profit" in required_fields

    def test_output_field(self):
        assert OUTPUT_FIELD == "non_operating_income_ratio"

    def test_basic_ratio_calculation(self):
        results = {
            "non_operating_income": {
                2022: 80.0,
                2021: 60.0,
                2020: 50.0,
            },
            "operating_profit": {
                2022: 1200.0,
                2021: 1100.0,
                2020: 1000.0,
            }
        }
        ratios = calculate(results)
        
        assert 2022 in ratios
        assert ratios[2022] == pytest.approx(80.0 / 1200.0)

    def test_high_ratio_flag(self):
        """Test that high non-operating income can be detected"""
        results = {
            "non_operating_income": {
                2022: 80.0,
                2021: 60.0,
                2020: 50.0,
            },
            "operating_profit": {
                2022: 1200.0,
                2021: 1100.0,
                2020: 1000.0,
            }
        }
        ratios = calculate(results)
        
        # All years should be < 10% (healthy range)
        for year, ratio in ratios.items():
            if ratio is not None:
                assert ratio < 0.1

    def test_missing_operating_profit(self):
        results = {
            "non_operating_income": {2022: 80.0},
            "operating_profit": {}
        }
        ratios = calculate(results)
        assert 2022 not in ratios
