"""Test for Other Receivables Ratio Calculator"""
import pytest
from value_investment.calculators.calc_other_receivables_ratio import calculate, required_fields, OUTPUT_FIELD


class TestOtherReceivablesRatio:
    """Test other receivables ratio calculation"""

    def test_required_fields(self):
        assert "other_receivables" in required_fields
        assert "total_assets" in required_fields

    def test_output_field(self):
        assert OUTPUT_FIELD == "other_receivables_ratio"

    def test_basic_ratio_calculation(self):
        results = {
            "other_receivables": {
                2022: 150.0,
                2021: 120.0,
                2020: 100.0,
            },
            "total_assets": {
                2022: 12000.0,
                2021: 11000.0,
                2020: 10000.0,
            }
        }
        ratios = calculate(results)
        
        assert 2022 in ratios
        assert ratios[2022] == pytest.approx(150.0 / 12000.0)

    def test_missing_total_assets(self):
        results = {
            "other_receivables": {2022: 150.0},
            "total_assets": {}
        }
        ratios = calculate(results)
        assert 2022 not in ratios

    def test_zero_total_assets(self):
        results = {
            "other_receivables": {2022: 150.0},
            "total_assets": {2022: 0.0}
        }
        ratios = calculate(results)
        assert 2022 not in ratios
