"""Tests for API get_indicator method"""
import pytest
from unittest.mock import Mock, patch


class TestAPIIndicator:
    """Test ValueInvestment API get_indicator method"""

    def test_get_indicator_method_exists(self):
        """API should have get_indicator method"""
        from value_investment.api import ValueInvestment

        api = ValueInvestment()
        assert hasattr(api, "get_indicator")
        assert callable(api.get_indicator)

    def test_get_indicator_returns_meta(self):
        """get_indicator should return indicator metadata"""
        from value_investment.api import ValueInvestment

        api = ValueInvestment()

        # Register test indicator
        from value_investment.indicators.registry import IndicatorRegistry, register_defaults
        register_defaults()

        result = api.get_indicator("revenue")
        assert result is not None
        assert result.name == "revenue"

    def test_get_indicator_unknown(self):
        """get_indicator should return None for unknown indicator"""
        from value_investment.api import ValueInvestment

        api = ValueInvestment()

        result = api.get_indicator("nonexistent_indicator")
        assert result is None
