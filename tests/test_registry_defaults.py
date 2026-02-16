"""Tests for default indicator registration"""
import pytest


class TestRegisterDefaults:
    """Test default indicator registration"""

    def test_register_defaults_creates_indicators(self):
        """Should register default raw financial indicators"""
        from value_investment.indicators.registry import IndicatorRegistry
        from value_investment.indicators.base import IndicatorType

        # Clear existing
        registry = IndicatorRegistry.get_instance()
        registry.clear()

        # Register defaults
        from value_investment.indicators.registry import register_defaults
        register_defaults()

        # Verify some indicators registered
        revenue = registry.get("revenue")
        assert revenue is not None
        assert revenue.type == IndicatorType.RAW

    def test_default_indicators_have_market_fields(self):
        """Default indicators should have market-specific field mappings"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        revenue = registry.get("revenue")

        if revenue:
            assert "A股" in revenue.market_fields
            assert "港股" in revenue.market_fields
            assert "美股" in revenue.market_fields

    def test_list_raw_indicators(self):
        """Should list all RAW type indicators"""
        from value_investment.indicators.registry import IndicatorRegistry
        from value_investment.indicators.base import IndicatorType

        registry = IndicatorRegistry.get_instance()
        raw_indicators = registry.list_by_type(IndicatorType.RAW)
        assert len(raw_indicators) > 0
