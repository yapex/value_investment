"""Tests for Post Crisis Recovery Speed Calculator"""
import pytest
from value_investment.calculators.calc_post_crisis_recovery import (
    calculate,
    required_fields,
)


class TestPostCrisisRecovery:
    """Test PostCrisisRecovery Calculator"""

    def test_required_fields(self):
        """Test required fields are correct"""
        assert "total_revenue" in required_fields

    def test_quick_recovery(self):
        """Test quick recovery within 1 year"""
        results = {
            "total_revenue": {
                2018: 10000,
                2019: 10000,
                2020: 12000,
                2021: 15000,
                2022: 8000,  # Crisis
                2023: 16000,  # Recovery (exceeds peak)
            }
        }
        output = calculate(results)
        # 2022 crisis, 2023 recovered (1 year to recover)
        assert output[2022] == 1

    def test_slow_recovery(self):
        """Test slow recovery within 2 years"""
        results = {
            "total_revenue": {
                2018: 10000,
                2019: 10000,
                2020: 12000,
                2021: 15000,
                2022: 8000,  # Crisis
                2023: 12000,  # Still below peak
                2024: 16000,  # Recovery (exceeds peak)
            }
        }
        output = calculate(results)
        # 2022 crisis, 2024 recovered (2 years to recover)
        assert output[2022] == 2

    def test_no_recovery(self):
        """Test ongoing crisis (no recovery)"""
        results = {
            "total_revenue": {
                2018: 10000,
                2019: 10000,
                2020: 12000,
                2021: 15000,
                2022: 8000,  # Crisis
                2023: 9000,  # Still below peak
            }
        }
        output = calculate(results)
        # 2022 crisis, no recovery yet
        assert output[2022] is None

    def test_no_crisis_returns_zero(self):
        """Test no crisis returns 0"""
        results = {
            "total_revenue": {
                2018: 10000,
                2019: 10000,
                2020: 12000,
                2021: 15000,
                2022: 16000,  # Growing
                2023: 18000,
            }
        }
        output = calculate(results)
        # 2022 above all previous peaks
        assert output[2022] == 0.0

    def test_insufficient_data_returns_empty(self):
        """Test empty dict when insufficient data"""
        results = {"total_revenue": {2021: 10000, 2022: 12000}}
        output = calculate(results)
        assert output == {}

    def test_multiple_crisis_years(self):
        """Test multiple crisis years"""
        results = {
            "total_revenue": {
                2018: 10000,
                2019: 10000,
                2020: 12000,
                2021: 15000,
                2022: 8000,  # Crisis
                2023: 7000,  # Deep crisis
                2024: 16000,  # Recovery (exceeds peak)
            }
        }
        output = calculate(results)
        # 2022: 2 years to recover (2023 still below, 2024 recovered)
        assert output[2022] == 2
        # 2023: 1 year to recover (2024 recovered)
        assert output[2023] == 1
