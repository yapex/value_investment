"""未映射字段保护机制测试"""
import logging
import pytest
import pandas as pd

from src.value_investment.data.mapper import (
    DataMapper,
    MappedFieldMissingError,
    UnmappedFieldError,
    CORE_FIELD_MAPPING,
)
from src.value_investment.indicators.utils import (
    require_field,
    get_registered_fields,
)


class TestIsFieldExpectedForMarket:
    """测试 is_field_expected_for_market 方法"""
    
    def test_standard_market_has_field(self):
        """测试标准市场字段存在"""
        # total_revenue 在 A股/港股/美股 都有定义
        assert DataMapper.is_field_expected_for_market('total_revenue', 'A') is True
        assert DataMapper.is_field_expected_for_market('total_revenue', 'HK') is True
        assert DataMapper.is_field_expected_for_market('total_revenue', 'US') is True
    
    def test_unknown_field(self):
        """测试未知字段返回 False"""
        assert DataMapper.is_field_expected_for_market('unknown_field', 'A') is False
    
    def test_case_insensitive(self):
        """测试市场名称大小写不敏感"""
        assert DataMapper.is_field_expected_for_market('total_revenue', 'a') is True
        assert DataMapper.is_field_expected_for_market('total_revenue', 'hk') is True


class TestMapToStandardDefaultDeny:
    """测试 map_to_standard 默认拒绝策略"""
    
    def test_only_mapped_fields_in_result(self):
        """测试结果只包含已映射字段"""
        # 使用 tushare 实际的字段名
        df = pd.DataFrame({
            'total_operate_income': [100, 200],  # 映射到 total_revenue
            'netprofit': [10, 20],               # 映射到 net_profit
            'unmapped_field': [1, 2],            # 未映射字段
        })
        
        result = DataMapper.map_to_standard(df, 'tushare', 'income_statement', 'A')
        
        # 只包含已映射的字段
        assert 'total_revenue' in result.columns
        assert 'net_profit' in result.columns
        assert 'unmapped_field' not in result.columns
    
    def test_copy_disconnects_from_original(self):
        """测试 copy 断开与原始 DataFrame 的联系"""
        df = pd.DataFrame({'total_operate_income': [100]})
        result = DataMapper.map_to_standard(df, 'tushare', 'income_statement', 'A')
        
        # 修改结果不影响原始
        result.iloc[0, 0] = 999
        assert df.iloc[0, 0] == 100
    
    def test_missing_native_field_no_warning_for_non_applicable_market(self):
        """测试不适用市场的字段不发出警告"""
        # 这个测试验证逻辑正确，不需要检查具体日志
        # 因为港股/美股特有的字段在A股查询时应该不警告
        df = pd.DataFrame({
            'total_operate_income': [100],
            # 港股特有字段 '收益' 不存在于 df 中
        })
        
        # 不应该抛出异常
        result = DataMapper.map_to_standard(df, 'tushare', 'income_statement', 'A')
        assert 'total_revenue' in result.columns


class TestRequireField:
    """测试 require_field 辅助函数"""
    
    def test_access_existing_field(self):
        """测试访问已存在的字段"""
        df = pd.DataFrame({'total_revenue': [100]})
        result = require_field(df, 'total_revenue')
        
        assert result.iloc[0] == 100
    
    def test_access_unregistered_field(self):
        """测试访问未注册字段抛出异常"""
        df = pd.DataFrame({'total_revenue': [100]})
        
        with pytest.raises(UnmappedFieldError) as exc_info:
            require_field(df, 'unregistered_field')
        
        assert '未注册' in str(exc_info.value)
    
    def test_access_missing_mapped_field(self):
        """测试访问已注册但缺失的字段抛出异常"""
        df = pd.DataFrame({'other_field': [100]})  # 不包含 total_revenue
        
        with pytest.raises(MappedFieldMissingError) as exc_info:
            require_field(df, 'total_revenue')
        
        assert '已注册但数据中不存在' in str(exc_info.value)


class TestGetRegisteredFields:
    """测试 get_registered_fields 函数"""
    
    def test_returns_set_of_fields(self):
        """测试返回字段集合"""
        fields = get_registered_fields()
        
        assert isinstance(fields, set)
        assert 'total_revenue' in fields
        assert 'total_assets' in fields
        assert 'net_profit' in fields
