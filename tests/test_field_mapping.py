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


class TestDataMapperHKSpecific:
    """Test DataMapper for 港股 fields - Task 8: 港股特有指标"""

    def test_hk_dividend_yield_mapping(self):
        """港股 'hk_dividend_yield_ttm' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("hk_dividend_yield_ttm", "港股")
        assert result == "hk_dividend_yield_ttm"

    def test_hk_dividend_payout_ratio_mapping(self):
        """港股 'hk_dividend_payout_ratio' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("hk_dividend_payout_ratio", "港股")
        assert result == "hk_dividend_payout_ratio"

    def test_hk_dividend_per_share_mapping(self):
        """港股 'hk_dividend_per_share' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("hk_dividend_per_share", "港股")
        assert result == "hk_dividend_per_share"

    def test_hk_market_cap_mapping(self):
        """港股 'hk_market_cap' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("hk_market_cap", "港股")
        assert result == "hk_market_cap"

    def test_hk_legal_shares_mapping(self):
        """港股 'hk_legal_shares' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("hk_legal_shares", "港股")
        assert result == "hk_legal_shares"

    def test_hk_total_revenue_growth_qoq_mapping(self):
        """港股 'hk_total_revenue_growth_qoq' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("hk_total_revenue_growth_qoq", "港股")
        assert result == "hk_total_revenue_growth_qoq"

    def test_hk_net_profit_growth_qoq_mapping(self):
        """港股 'hk_net_profit_growth_qoq' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("hk_net_profit_growth_qoq", "港股")
        assert result == "hk_net_profit_growth_qoq"

    def test_hk_total_shares_mapping(self):
        """港股 'total_shares' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("total_shares", "港股")
        assert result == "total_shares"
    """Test DataMapper for 港股 fields - Task 7: 估值指标"""

    def test_hk_pe_ratio_mapping(self):
        """港股 'pe_ratio' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("pe_ratio", "港股")
        assert result == "pe_ratio"

    def test_hk_pb_ratio_mapping(self):
        """港股 'pb_ratio' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("pb_ratio", "港股")
        assert result == "pb_ratio"
    """Test DataMapper for 港股 fields - Task 6: 营运能力指标"""

    def test_hk_current_ratio_mapping(self):
        """港股 'current_ratio' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("current_ratio", "港股")
        assert result == "current_ratio"

    def test_hk_quick_ratio_mapping(self):
        """港股 'quick_ratio' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("quick_ratio", "港股")
        assert result == "quick_ratio"

    def test_hk_cash_ratio_mapping(self):
        """港股 'cash_ratio' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("cash_ratio", "港股")
        assert result == "cash_ratio"

    def test_hk_debt_ratio_mapping(self):
        """港股 'debt_ratio' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("debt_ratio", "港股")
        assert result == "debt_ratio"
    """Test DataMapper for 港股 fields - Task 5: 每股指标"""

    def test_hk_basic_eps_mapping(self):
        """港股 'basic_eps' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("basic_eps", "港股")
        assert result == "basic_eps"

    def test_hk_book_value_per_share_mapping(self):
        """港股 'book_value_per_share' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("book_value_per_share", "港股")
        assert result == "book_value_per_share"

    def test_hk_operating_cash_flow_per_share_mapping(self):
        """港股 'operating_cash_flow_per_share' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("operating_cash_flow_per_share", "港股")
        assert result == "operating_cash_flow_per_share"
    """Test DataMapper for 港股 fields - Task 4: 关键比率字段"""

    def test_hk_roe_mapping(self):
        """港股 'roe' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("roe", "港股")
        assert result == "roe"

    def test_hk_roa_mapping(self):
        """港股 'roa' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("roa", "港股")
        assert result == "roa"

    def test_hk_net_profit_margin_mapping(self):
        """港股 'net_profit_margin' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("net_profit_margin", "港股")
        assert result == "net_profit_margin"
    """Test DataMapper for 港股 fields - Task 3: 现金流量表核心字段"""

    def test_hk_operating_cash_flow_mapping(self):
        """港股 '经营业务现金净额' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("经营业务现金净额", "港股")
        assert result == "operating_cash_flow"

    def test_hk_investing_cash_flow_mapping(self):
        """港股 '投资业务现金净额' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("投资业务现金净额", "港股")
        assert result == "investing_cash_flow"

    def test_hk_financing_cash_flow_mapping(self):
        """港股 '融资业务现金净额' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("融资业务现金净额", "港股")
        assert result == "financing_cash_flow"

    def test_hk_standard_cashflow_fields_passthrough(self):
        """港股返回标准字段名时应保持不变"""
        from value_investment.data.mapper import DataMapper
        
        # 港股 API 返回标准字段名
        standard_fields = ["operating_cash_flow", "investing_cash_flow", "financing_cash_flow"]
        for field in standard_fields:
            result = DataMapper.get_standard_field(field, "港股")
            assert result == field, f"港股字段 {field} 应该透传"
    """Test DataMapper for 港股 fields - Task 2: 资产负债表核心字段"""

    def test_hk_total_assets_mapping(self):
        """港股 '资产总值' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("资产总值", "港股")
        assert result == "total_assets"

    def test_hk_total_equity_mapping(self):
        """港股 '权益总额' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("权益总额", "港股")
        assert result == "total_equity"

    def test_hk_total_liabilities_mapping(self):
        """港股 '总负债' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("总负债", "港股")
        assert result == "total_liabilities"

    def test_hk_current_assets_mapping(self):
        """港股 '流动资产合计' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("流动资产合计", "港股")
        assert result == "current_assets"

    def test_hk_current_liabilities_mapping(self):
        """港股 '流动负债合计' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("流动负债合计", "港股")
        assert result == "current_liabilities"

    def test_hk_cash_equivalents_mapping(self):
        """港股 '现金及等价物' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("现金及等价物", "港股")
        assert result == "cash_and_equivalents"

    def test_hk_standard_balance_fields_passthrough(self):
        """港股返回标准字段名时应保持不变"""
        from value_investment.data.mapper import DataMapper
        
        # 港股 API 返回标准字段名
        standard_fields = ["total_assets", "total_equity", "total_liabilities"]
        for field in standard_fields:
            result = DataMapper.get_standard_field(field, "港股")
            assert result == field, f"港股字段 {field} 应该透传"
    """Test DataMapper for 港股 fields - Task 1: 利润表核心字段"""

    def test_hk_revenue_mapping_from_chinese(self):
        """港股 '收益' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        # 港股可能返回中文 "收益"
        result = DataMapper.get_standard_field("收益", "港股")
        assert result == "total_revenue"

    def test_hk_net_profit_mapping_from_chinese(self):
        """港股 '期内溢利' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        # 港股可能返回中文 "期内溢利"
        result = DataMapper.get_standard_field("期内溢利", "港股")
        assert result == "net_profit"

    def test_hk_operating_profit_mapping_from_chinese(self):
        """港股 '营业溢利' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("营业溢利", "港股")
        assert result == "operating_profit"

    def test_hk_gross_profit_mapping(self):
        """港股 '毛利' 字段应能转换为标准字段名"""
        from value_investment.data.mapper import DataMapper
        
        result = DataMapper.get_standard_field("毛利", "港股")
        assert result == "gross_profit"

    def test_hk_standard_field_passthrough(self):
        """港股返回标准字段名时应保持不变"""
        from value_investment.data.mapper import DataMapper
        
        # 港股 API 返回标准字段名 (如 total_revenue) 时，应该直接返回
        # 这是一个透传场景
        standard_fields = ["total_revenue", "net_profit", "roe", "roa"]
        for field in standard_fields:
            result = DataMapper.get_standard_field(field, "港股")
            # 如果没有映射，应该返回原值或者需要添加映射
            # 当前返回 None，我们期望能添加映射后返回标准字段名
            assert result is not None, f"港股字段 {field} 应该有映射"


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
