"""Test for Debt Due Within 1 Year Ratio Calculator

Formula: (short_term_borrowings + non_current_liabilities_due_1y + bonds_payable) / total_liabilities * 100
"""
import pytest
from value_investment.calculators.calc_debt_due_within_1y_ratio import calculate, required_fields, OUTPUT_FIELD


class TestDebtDueWithin1YRatio:
    """Test debt due within 1 year ratio calculation"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert "short_term_borrowings" in required_fields
        assert "non_current_liabilities_due_1y" in required_fields
        assert "bond_payable" in required_fields
        assert "total_liabilities" in required_fields

    def test_basic_calculation(self):
        """Test basic calculation with complete data"""
        results = {
            "short_term_borrowings": {2023: 100.0, 2022: 80.0},
            "non_current_liabilities_due_1y": {2023: 50.0, 2022: 40.0},
            "bond_payable": {2023: 30.0, 2022: 20.0},
            "total_liabilities": {2023: 500.0, 2022: 400.0},
        }

        ratios = calculate(results)

        # 2023: (100 + 50 + 30) / 500 = 180 / 500 = 0.36
        assert ratios.get(2023) == pytest.approx(0.36, rel=1e-6)
        # 2022: (80 + 40 + 20) / 400 = 140 / 400 = 0.35
        assert ratios.get(2022) == pytest.approx(0.35, rel=1e-6)

    def test_zero_total_liabilities(self):
        """Test handling of zero total liabilities"""
        results = {
            "short_term_borrowings": {2023: 100.0},
            "non_current_liabilities_due_1y": {2023: 50.0},
            "bond_payable": {2023: 30.0},
            "total_liabilities": {2023: 0.0},  # Zero division
        }

        ratios = calculate(results)
        assert 2023 not in ratios  # Should skip when total_liabilities is 0

    def test_missing_fields(self):
        """Test handling of missing fields"""
        # Only have short_term_borrowings
        results = {
            "short_term_borrowings": {2023: 100.0},
        }

        ratios = calculate(results)
        assert len(ratios) == 0  # Should not produce any results

    def test_large_values(self):
        """Test with large values (billions)"""
        results = {
            "short_term_borrowings": {2023: 41.33e8},  # 41.33亿
            "non_current_liabilities_due_1y": {2023: 639.22e8},  # 639.22亿
            "bond_payable": {2023: 688.16e8},  # 688.16亿
            "total_liabilities": {2023: 13521.33e8},  # 13521.33亿
        }

        ratios = calculate(results)
        # (41.33 + 639.22 + 688.16) / 13521.33 = 0.1012
        assert ratios.get(2023) == pytest.approx(0.1012, rel=1e-3)

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD constant is defined"""
        assert OUTPUT_FIELD == "debt_due_within_1y_ratio"
