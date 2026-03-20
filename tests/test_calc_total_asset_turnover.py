"""Tests for Total Asset Turnover Calculator"""
import pytest
from value_investment.calculators.calc_total_asset_turnover import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestTotalAssetTurnover:
    """Test cases for total_asset_turnover calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert set(required_fields) == {"total_revenue", "total_assets"}

    def test_basic_calculation(self):
        """Test basic total asset turnover calculation"""
        results = {
            "total_revenue": {2023: 500000000, 2022: 400000000},
            "total_assets": {2023: 2000000000, 2022: 1800000000},
        }
        output = calculate(results)

        # 2023: 500M / ((2000M + 1800M) / 2) = 500M / 1900M = 0.263...
        assert output[2023] == pytest.approx(0.263, rel=1e-2)
        # 2022: 无上一年数据，无法计算平均，返回 None
        assert output[2022] is None

    def test_multi_year_calculation(self):
        """Test turnover with multiple years of data"""
        results = {
            "total_revenue": {2023: 600000000, 2022: 500000000, 2021: 400000000},
            "total_assets": {2023: 2500000000, 2022: 2000000000, 2021: 1800000000},
        }
        output = calculate(results)

        # 2023: 600M / ((2500M + 2000M) / 2) = 600M / 2250M = 0.267...
        assert output[2023] == pytest.approx(0.267, rel=1e-2)
        # 2022: 500M / ((2000M + 1800M) / 2) = 500M / 1900M = 0.263...
        assert output[2022] == pytest.approx(0.263, rel=1e-2)
        # 2021: 无上一年数据，无法计算平均，返回 None
        assert output[2021] is None

    def test_zero_assets_returns_none(self):
        """Test that zero assets returns None"""
        results = {
            "total_revenue": {2023: 500000000},
            "total_assets": {2023: 0},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_missing_assets_returns_none(self):
        """Test that missing assets returns None"""
        results = {
            "total_revenue": {2023: 500000000},
            "total_assets": {},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "total_asset_turnover"
