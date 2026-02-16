"""Tests for IndicatorRegistry"""
import pytest


class TestIndicatorRegistry:
    """Test IndicatorRegistry class"""

    def test_registry_singleton(self):
        """Should get singleton instance"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry1 = IndicatorRegistry.get_instance()
        registry2 = IndicatorRegistry.get_instance()
        assert registry1 is registry2

    def test_register_indicator(self):
        """Should register an indicator"""
        from value_investment.indicators.registry import IndicatorRegistry
        from value_investment.indicators.base import IndicatorMeta, IndicatorType

        registry = IndicatorRegistry.get_instance()
        meta = IndicatorMeta(
            name="test_indicator",
            display_name="测试指标",
            type=IndicatorType.RAW,
            field_names=["field1"],
            description="测试用指标",
        )
        registry.register(meta)

        retrieved = registry.get("test_indicator")
        assert retrieved is not None
        assert retrieved.name == "test_indicator"

    def test_get_nonexistent_indicator(self):
        """Should return None for nonexistent indicator"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        assert registry.get("nonexistent") is None

    def test_list_indicators(self):
        """Should list all registered indicators"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        indicators = registry.list_all()
        assert isinstance(indicators, list)

    def test_filter_by_type(self):
        """Should filter indicators by type"""
        from value_investment.indicators.registry import IndicatorRegistry
        from value_investment.indicators.base import IndicatorType

        registry = IndicatorRegistry.get_instance()
        raw_indicators = registry.list_by_type(IndicatorType.RAW)
        assert isinstance(raw_indicators, list)

    def test_filter_by_market(self):
        """Should filter indicators by market"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        abc_indicators = registry.list_by_market("A股")
        assert isinstance(abc_indicators, list)
