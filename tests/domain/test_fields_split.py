"""Tests for fields split: SourceFields vs IndicatorFields"""
import pytest


def test_source_fields_contains_original_data():
    """SourceFields 应包含原始数据字段"""
    from value_investment.domain.fields import get_source_fields

    source = get_source_fields()
    # 这些是原始资产负债表/利润表科目
    assert "goodwill" in source
    assert "short_term_borrowings" in source
    assert "net_debt" in source
    assert "interest_expense" in source
    assert "non_current_liabilities_due_1y" in source


def test_indicator_fields_contains_calculated_metrics():
    """IndicatorFields 应包含衍生指标"""
    from value_investment.domain.fields import get_indicator_fields

    indicators = get_indicator_fields()
    assert "roe" in indicators
    assert "net_margin" in indicators
    assert "revenue_cagr_5y" in indicators


def test_indicator_fields_count_matches_calculators():
    """IndicatorFields 数量应等于 Calculator 数量"""
    from value_investment.domain.fields import get_indicator_fields
    from value_investment.calculator_plugin import registry

    indicators = get_indicator_fields()
    assert len(indicators) == len(registry.get_all())


def test_no_overlap_between_source_and_indicators():
    """衍生指标不应出现在 SourceFields"""
    from value_investment.domain.fields import get_source_fields, get_indicator_fields

    source = get_source_fields()
    indicators = get_indicator_fields()
    overlap = source & indicators
    assert len(overlap) == 0, f"Overlap found: {overlap}"


def test_all_fields_union():
    """ALL_FIELDS = SourceFields | IndicatorFields"""
    from value_investment.domain.fields import get_source_fields, get_indicator_fields, ALL_FIELDS

    source = get_source_fields()
    indicators = get_indicator_fields()
    assert ALL_FIELDS == source | indicators


def test_custom_fields_is_alias_of_source_fields():
    """向后兼容：CustomFields 应是 SourceFields 的别名"""
    from value_investment.domain.fields import SourceFields, CustomFields

    assert SourceFields is CustomFields
