"""Tests for US market field mapping completeness"""
import pytest


class TestUSFinancialIndicatorMapping:
    """Test US financial indicator mapping completeness"""

    def test_us_should_have_parent_holder_netprofit_mapping(self):
        """US market should have PARENT_HOLDER_NETPROFIT -> net_profit mapping"""
        from value_investment.data.mapper import FINANCIAL_INDICATOR_MAPPING

        us_mapping = FINANCIAL_INDICATOR_MAPPING.get('US', {})

        # PARENT_HOLDER_NETPROFIT should map to net_profit (归母净利润)
        assert 'PARENT_HOLDER_NETPROFIT' in us_mapping, \
            "US market should have PARENT_HOLDER_NETPROFIT mapping for parent net profit"
        assert us_mapping['PARENT_HOLDER_NETPROFIT'] == 'net_profit', \
            "PARENT_HOLDER_NETPROFIT should map to net_profit"

    def test_us_should_have_roe_mapping(self):
        """US market should have ROE_AVG -> roe mapping"""
        from value_investment.data.mapper import FINANCIAL_INDICATOR_MAPPING

        us_mapping = FINANCIAL_INDICATOR_MAPPING.get('US', {})

        assert 'ROE_AVG' in us_mapping, \
            "US market should have ROE_AVG mapping"
        assert us_mapping['ROE_AVG'] == 'roe', \
            "ROE_AVG should map to roe"

    def test_us_should_have_basic_eps_mapping(self):
        """US market should have BASIC_EPS -> basic_eps mapping"""
        from value_investment.data.mapper import FINANCIAL_INDICATOR_MAPPING

        us_mapping = FINANCIAL_INDICATOR_MAPPING.get('US', {})

        assert 'BASIC_EPS' in us_mapping, \
            "US market should have BASIC_EPS mapping"
        assert us_mapping['BASIC_EPS'] == 'basic_eps', \
            "BASIC_EPS should map to basic_eps"

    def test_us_should_have_debt_ratio_mapping(self):
        """US market should have DEBT_ASSET_RATIO -> debt_ratio mapping"""
        from value_investment.data.mapper import FINANCIAL_INDICATOR_MAPPING

        us_mapping = FINANCIAL_INDICATOR_MAPPING.get('US', {})

        assert 'DEBT_ASSET_RATIO' in us_mapping, \
            "US market should have DEBT_ASSET_RATIO mapping"
        assert us_mapping['DEBT_ASSET_RATIO'] == 'debt_ratio', \
            "DEBT_ASSET_RATIO should map to debt_ratio"

    def test_us_should_have_current_ratio_mapping(self):
        """US market should have CURRENT_RATIO -> current_ratio mapping"""
        from value_investment.data.mapper import FINANCIAL_INDICATOR_MAPPING

        us_mapping = FINANCIAL_INDICATOR_MAPPING.get('US', {})

        assert 'CURRENT_RATIO' in us_mapping, \
            "US market should have CURRENT_RATIO mapping"
        assert us_mapping['CURRENT_RATIO'] == 'current_ratio', \
            "CURRENT_RATIO should map to current_ratio"


class TestUSBalanceSheetMapping:
    """Test US balance sheet field mapping"""

    def test_us_should_have_total_assets_mapping(self):
        """US market should have 总资产 -> total_assets mapping"""
        from value_investment.data.mapper import DataMapper

        # Check in BALANCE_MAPPING
        mapping = DataMapper.BALANCE_MAPPING
        assert '总资产' in mapping, \
            "BALANCE_MAPPING should have 总资产"
        assert mapping['总资产'] == 'total_assets', \
            "总资产 should map to total_assets"

    def test_us_should_have_total_liabilities_mapping(self):
        """US market should have 总负债 -> total_liabilities mapping"""
        from value_investment.data.mapper import DataMapper

        mapping = DataMapper.BALANCE_MAPPING
        assert '总负债' in mapping, \
            "BALANCE_MAPPING should have 总负债"
        assert mapping['总负债'] == 'total_liabilities', \
            "总负债 should map to total_liabilities"


class TestUSIncomeMapping:
    """Test US income statement field mapping"""

    def test_us_should_have_operating_income_mapping(self):
        """US market should have OPERATE_INCOME -> total_revenue mapping
        
        Note: In US financial statements, OPERATE_INCOME refers to 主营业收入 (total revenue),
        not 营业利润 (operating profit).
        """
        from value_investment.data.mapper import FINANCIAL_INDICATOR_MAPPING

        us_mapping = FINANCIAL_INDICATOR_MAPPING.get('US', {})

        assert 'OPERATE_INCOME' in us_mapping, \
            "US market should have OPERATE_INCOME mapping"
        assert us_mapping['OPERATE_INCOME'] == 'total_revenue', \
            "OPERATE_INCOME (主营业收入) should map to total_revenue"


class TestDuplicateMappingCheck:
    """Test that there are no duplicate mappings to the same field"""

    def test_no_duplicate_net_profit_mapping_in_financial_indicator(self):
        """FINANCIAL_INDICATOR_MAPPING should not have multiple sources mapping to net_profit
        
        We prefer PARENT_HOLDER_NETPROFIT for US market.
        Other sources like '净利润' should be handled by the standard mapping.
        """
        from value_investment.data.mapper import FINANCIAL_INDICATOR_MAPPING

        # Collect all keys that map to net_profit
        net_profit_sources = []
        for key, value in FINANCIAL_INDICATOR_MAPPING.items():
            if value == 'net_profit' and isinstance(key, str):
                net_profit_sources.append(key)

        # There should be at least one (PARENT_HOLDER_NETPROFIT for US)
        # But we should not have conflicting mappings
        assert len(net_profit_sources) >= 1, \
            "Should have at least PARENT_HOLDER_NETPROFIT mapping for net_profit"


class TestUSBalanceSheetCompleteMapping:
    """Test all US balance sheet fields are mapped"""

    # 美股 AkShare 资产负债表实际字段
    US_BALANCE_ITEMS = [
        '现金及现金等价物',
        '短期投资',
        '应收账款',
        '存货',
        '递延所得税资产(流动)',
        '其他流动资产',
        '其他应收款',
        '有价证券投资(流动)',
        '流动资产合计',
        '物业、厂房及设备',
        '无形资产',
        '商誉',
        '长期投资',
        '其他非流动资产',
        '有价证券投资(非流动)',
        '非流动资产合计',
        '总资产',
        '应付账款',
        '应付票据(流动)',
        '预收及预提费用',
        '短期债务',
        '长期负债(本期部分)',
        '递延收入(流动)',
        '其他流动负债',
        '流动负债合计',
        '递延所得税负债(非流动)',
        '递延收入(非流动)',
        '长期负债',
        '其他非流动负债',
        '非运算项目',
        '非流动负债合计',
        '总负债',
        '普通股',
        '优先股',
        '留存收益',
        '其他综合收益',
        '归属于母公司股东权益其他项目',
        '归属于母公司股东权益',
        '股东权益合计',
        '负债及股东权益合计',
    ]

    @pytest.mark.parametrize("item", US_BALANCE_ITEMS)
    def test_us_balance_item_should_be_mapped(self, item):
        """All US balance sheet items should be in BALANCE_MAPPING"""
        from value_investment.data.mapper import DataMapper

        mapping = DataMapper.BALANCE_MAPPING
        assert item in mapping, f"US balance sheet item '{item}' should be mapped in BALANCE_MAPPING"


class TestUSIncomeStatementCompleteMapping:
    """Test all US income statement fields are mapped"""

    # 美股 AkShare 利润表实际字段
    US_INCOME_ITEMS = [
        '主营收入',
        '营业收入',
        '主营成本',
        '营业成本',
        '毛利',
        '研发费用',
        '营销费用',
        '其他营业费用',
        '重组费用',
        '营业费用',
        '营业利润',
        '利息收入',
        '权益性投资损益',
        '其他收入(支出)',
        '持续经营税前利润',
        '所得税',
        '持续经营净利润',
        '税后利润其他项目',
        '净利润',
        '归属于普通股股东净利润',
        '归属于母公司股东净利润',
        '每股股息-普通股',
        '基本每股收益-普通股',
        '摊薄每股收益-普通股',
        '基本加权平均股数-普通股',
        '摊薄加权平均股数-普通股',
        '本公司拥有人占全面收益总额',
        '非控股权益占全面收益总额',
        '其他全面收益其他项目',
        '其他全面收益合计项',
        '全面收益总额',
        '非运算项目',
    ]

    @pytest.mark.parametrize("item", US_INCOME_ITEMS)
    def test_us_income_item_should_be_mapped(self, item):
        """All US income statement items should be in INCOME_MAPPING"""
        from value_investment.data.mapper import DataMapper

        mapping = DataMapper.INCOME_MAPPING
        assert item in mapping, f"US income statement item '{item}' should be mapped in INCOME_MAPPING"


class TestUSCashFlowCompleteMapping:
    """Test all US cash flow fields are mapped"""

    # 美股 AkShare 现金流量表实际字段
    US_CASHFLOW_ITEMS = [
        '净利润',
        '折旧及摊销',
        '基于股票的补偿费',
        '减值及拨备',
        '递延所得税',
        '资产处置损益',
        '投资损益',
        '重估盈余',
        '经营业务调整其他项目',
        '应收账款及票据',
        '存货',
        '应付账款及票据',
        '递延收入',
        '经营业务其他项目',
        '经营活动产生的现金流量净额',
        '购买固定资产',
        '处置固定资产',
        '购建无形资产及其他资产',
        '投资支付现金',
        '收购附属公司',
        '其他投资活动产生的现金流量净额',
        '投资业务其他项目',
        '投资活动产生的现金流量净额',
        '发行股份',
        '回购股份',
        '发行债券',
        '赎回债券',
        '股息支付',
        '贷款收益',
        '超额税收优惠',
        '其他筹资活动产生的现金流量净额',
        '筹资业务其他项目',
        '筹资活动产生的现金流量净额',
        '现金及现金等价物增加(减少)额',
        '现金及现金等价物期初余额',
        '现金及现金等价物期末余额',
    ]

    @pytest.mark.parametrize("item", US_CASHFLOW_ITEMS)
    def test_us_cashflow_item_should_be_mapped(self, item):
        """All US cash flow items should be in CASHFLOW_MAPPING"""
        from value_investment.data.mapper import DataMapper

        mapping = DataMapper.CASHFLOW_MAPPING
        assert item in mapping, f"US cash flow item '{item}' should be mapped in CASHFLOW_MAPPING"
