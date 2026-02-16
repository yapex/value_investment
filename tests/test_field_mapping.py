"""Tests for field mapping"""
import pytest


class TestFieldMapping:
    """Test field mapping functionality"""

    def test_get_mapped_field_abc(self):
        """Should return A股 field name"""
        from value_investment.indicators.mapping import get_mapped_field

        assert get_mapped_field("revenue", "A股") == "营业总收入"
        assert get_mapped_field("net_profit", "A股") == "净利润"

    def test_get_mapped_field_hk(self):
        """Should return 港股 field name"""
        from value_investment.indicators.mapping import get_mapped_field

        assert get_mapped_field("revenue", "港股") == "收益"
        assert get_mapped_field("net_profit", "港股") == "期内溢利"

    def test_get_mapped_field_us(self):
        """Should return 美股 field name"""
        from value_investment.indicators.mapping import get_mapped_field

        assert get_mapped_field("revenue", "美股") == "totalRevenue"
        assert get_mapped_field("net_profit", "美股") == "netIncome"

    def test_get_mapped_field_unknown(self):
        """Should return None for unknown indicator"""
        from value_investment.indicators.mapping import get_mapped_field

        assert get_mapped_field("unknown_indicator", "A股") is None


class TestMarketConfig:
    """Test MarketConfig"""

    def test_market_config_creation(self):
        """Should create MarketConfig with required fields"""
        from value_investment.indicators.mapping import MarketConfig

        config = MarketConfig(
            market="A股",
            indicator_prefix="akshare",
            year_field="报告日期",
            data_source="akshare_financial",
        )

        assert config.market == "A股"
        assert config.year_field == "报告日期"

    def test_get_field_mapping(self):
        """Should get field mapping for market"""
        from value_investment.indicators.mapping import MarketConfig

        config = MarketConfig(
            market="A股",
            indicator_prefix="akshare",
            year_field="报告日期",
            data_source="akshare_financial",
        )

        fields = config.get_field_mapping("revenue")
        assert fields is not None
        assert "A股" in fields
