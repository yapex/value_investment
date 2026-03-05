"""Tests for unified core field mapping (TDD)"""
import pytest


class TestCoreFieldMapping:
    """Test unified core field mapping table"""

    def test_core_field_mapping_exists(self):
        """CORE_FIELD_MAPPING should exist and be a dict"""
        from value_investment.data.mapper import CORE_FIELD_MAPPING

        assert isinstance(CORE_FIELD_MAPPING, dict)
        assert len(CORE_FIELD_MAPPING) > 0

    def test_core_field_mapping_structure(self):
        """Each entry should have structure: standard_field -> {market: market_field}"""
        from value_investment.data.mapper import CORE_FIELD_MAPPING

        # Check key fields exist
        assert "total_revenue" in CORE_FIELD_MAPPING
        assert "net_profit" in CORE_FIELD_MAPPING
        assert "total_assets" in CORE_FIELD_MAPPING

        # Check structure
        revenue_map = CORE_FIELD_MAPPING["total_revenue"]
        assert isinstance(revenue_map, dict)
        assert "A股" in revenue_map
        assert "港股" in revenue_map
        assert "美股" in revenue_map

    def test_core_field_mapping_values(self):
        """Check specific field mappings"""
        from value_investment.data.mapper import CORE_FIELD_MAPPING

        # total_revenue
        assert CORE_FIELD_MAPPING["total_revenue"]["A股"] == "营业总收入"
        assert CORE_FIELD_MAPPING["total_revenue"]["港股"] == "收益"
        assert CORE_FIELD_MAPPING["total_revenue"]["美股"] == "totalRevenue"

        # net_profit
        assert CORE_FIELD_MAPPING["net_profit"]["A股"] == "净利润"
        assert CORE_FIELD_MAPPING["net_profit"]["港股"] == "期内溢利"
        assert CORE_FIELD_MAPPING["net_profit"]["美股"] == "netIncome"

        # total_assets
        assert CORE_FIELD_MAPPING["total_assets"]["A股"] == "资产总计"
        assert CORE_FIELD_MAPPING["total_assets"]["港股"] == "资产总值"
        assert CORE_FIELD_MAPPING["total_assets"]["美股"] == "totalAssets"


class TestGetMarketField:
    """Test forward lookup: standard field -> market field"""

    def test_get_market_field_a_stock(self):
        """Should return A股 field name"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_market_field("total_revenue", "A股") == "营业总收入"
        assert DataMapper.get_market_field("net_profit", "A股") == "净利润"
        assert DataMapper.get_market_field("total_assets", "A股") == "资产总计"

    def test_get_market_field_hk(self):
        """Should return 港股 field name"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_market_field("total_revenue", "港股") == "收益"
        assert DataMapper.get_market_field("net_profit", "港股") == "期内溢利"
        assert DataMapper.get_market_field("total_assets", "港股") == "资产总值"

    def test_get_market_field_us(self):
        """Should return 美股 field name"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_market_field("total_revenue", "美股") == "totalRevenue"
        assert DataMapper.get_market_field("net_profit", "美股") == "netIncome"
        assert DataMapper.get_market_field("total_assets", "美股") == "totalAssets"

    def test_get_market_field_unknown_field(self):
        """Should return None for unknown standard field"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_market_field("unknown_field", "A股") is None

    def test_get_market_field_unknown_market(self):
        """Should return None for unknown market"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_market_field("total_revenue", "日本") is None


class TestGetStandardField:
    """Test reverse lookup: market field -> standard field"""

    def test_get_standard_field_a_stock(self):
        """Should return standard field name from A股 field"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_standard_field("营业总收入", "A股") == "total_revenue"
        assert DataMapper.get_standard_field("净利润", "A股") == "net_profit"
        assert DataMapper.get_standard_field("资产总计", "A股") == "total_assets"

    def test_get_standard_field_hk(self):
        """Should return standard field name from 港股 field"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_standard_field("收益", "港股") == "total_revenue"
        assert DataMapper.get_standard_field("期内溢利", "港股") == "net_profit"
        assert DataMapper.get_standard_field("资产总值", "港股") == "total_assets"

    def test_get_standard_field_us(self):
        """Should return standard field name from 美股 field"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_standard_field("totalRevenue", "美股") == "total_revenue"
        assert DataMapper.get_standard_field("netIncome", "美股") == "net_profit"
        assert DataMapper.get_standard_field("totalAssets", "美股") == "total_assets"

    def test_get_standard_field_unknown_field(self):
        """Should return None for unknown market field"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_standard_field("unknown_field", "A股") is None

    def test_get_standard_field_unknown_market(self):
        """Should return None for unknown market"""
        from value_investment.data.mapper import DataMapper

        assert DataMapper.get_standard_field("营业总收入", "日本") is None


class TestListCoreFields:
    """Test listing all core standard fields"""

    def test_list_core_fields(self):
        """Should return list of all standard field names"""
        from value_investment.data.mapper import DataMapper

        fields = DataMapper.list_core_fields()

        assert isinstance(fields, list)
        assert len(fields) > 0
        assert "total_revenue" in fields
        assert "net_profit" in fields
        assert "total_assets" in fields

    def test_list_core_fields_sorted(self):
        """Should return sorted list"""
        from value_investment.data.mapper import DataMapper

        fields = DataMapper.list_core_fields()
        assert fields == sorted(fields)


class TestMappingCompleteness:
    """Test that all three markets have mappings for core fields"""

    def test_all_markets_have_mappings(self):
        """Each core field should have mappings for A股, 港股, 美股"""
        from value_investment.data.mapper import CORE_FIELD_MAPPING

        required_markets = {"A股", "港股", "美股"}
        core_fields = ["total_revenue", "net_profit", "total_assets", "total_equity"]

        for field in core_fields:
            assert field in CORE_FIELD_MAPPING, f"Missing core field: {field}"
            markets = set(CORE_FIELD_MAPPING[field].keys())
            assert required_markets.issubset(markets), f"{field} missing markets: {required_markets - markets}"
