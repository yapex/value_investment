"""Test for Goodwill to Net Assets Ratio Calculator"""
import pytest
from value_investment.calculators.calc_goodwill_to_net_assets_ratio import calculate, required_fields, OUTPUT_FIELD


class TestGoodwillToNetAssetsRatio:
    """Test goodwill to net assets ratio calculation"""

    def test_required_fields(self):
        assert "goodwill" in required_fields
        assert "total_equity" in required_fields

    def test_output_field(self):
        assert OUTPUT_FIELD == "goodwill_to_net_assets_ratio"

    def test_basic_ratio_calculation(self):
        results = {
            "goodwill": {
                2022: 700.0,
                2021: 600.0,
                2020: 500.0,
            },
            "total_equity": {
                2022: 6000.0,
                2021: 5500.0,
                2020: 5000.0,
            }
        }
        ratios = calculate(results)
        
        assert 2022 in ratios
        assert ratios[2022] == pytest.approx(700.0 / 6000.0)

    def test_missing_goodwill(self):
        results = {
            "goodwill": {},
            "total_equity": {2022: 6000.0}
        }
        ratios = calculate(results)
        assert len(ratios) == 0

    def test_zero_equity(self):
        results = {
            "goodwill": {2022: 700.0},
            "total_equity": {2022: 0.0}
        }
        ratios = calculate(results)
        assert 2022 not in ratios
