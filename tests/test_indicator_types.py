"""Tests for indicator types and metadata"""
import pytest
from dataclasses import dataclass


class TestIndicatorType:
    """Test IndicatorType enum"""

    def test_indicator_type_has_raw(self):
        """Should have RAW type for raw financial data"""
        from value_investment.indicators.base import IndicatorType
        assert hasattr(IndicatorType, "RAW")

    def test_indicator_type_has_calculated(self):
        """Should have CALCULATED type for calculated indicators"""
        from value_investment.indicators.base import IndicatorType
        assert hasattr(IndicatorType, "CALCULATED")


class TestIndicatorMeta:
    """Test IndicatorMeta dataclass"""

    def test_indicator_meta_creation(self):
        """Should create IndicatorMeta with required fields"""
        from value_investment.indicators.base import IndicatorMeta

        meta = IndicatorMeta(
            name="roe",
            display_name="净资产收益率",
            type="RAW",
            field_names=["净资产收益率"],
            description="净利润/平均净资产",
        )

        assert meta.name == "roe"
        assert meta.display_name == "净资产收益率"
        assert meta.type == "RAW"
        assert "净资产收益率" in meta.field_names

    def test_indicator_meta_fields(self):
        """IndicatorMeta should have market-specific field mapping"""
        from value_investment.indicators.base import IndicatorMeta

        meta = IndicatorMeta(
            name="revenue",
            display_name="营业收入",
            type="RAW",
            field_names=["营业总收入"],
            market_fields={
                "A股": "营业总收入",
                "港股": "收益",
                "美股": "totalRevenue",
            },
            description="企业营业收入",
        )

        assert meta.market_fields["A股"] == "营业总收入"
        assert meta.market_fields["港股"] == "收益"
