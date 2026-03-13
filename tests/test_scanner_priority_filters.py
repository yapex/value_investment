"""测试优先级过滤器和缓存优化

按照 TDD 流程测试常用指标独立缓存和分类执行逻辑。
"""
import pandas as pd
import pytest

from value_investment.scanner.priority_filters import (
    PRIORITY_FILTERS,
    get_priority_fields,
    is_priority_filter,
    classify_conditions,
    generate_cache_key,
    generate_non_priority_cache_key,
    compute_context_hash,
)
from value_investment.scanner.pipeline import FilterBuilder


class TestPriorityFiltersConfig:
    """测试常用指标配置"""
    
    def test_priority_filters_has_required_types(self):
        """测试 PRIORITY_FILTERS 包含所有支持的过滤类型"""
        assert 'consecutive_years' in PRIORITY_FILTERS
        assert 'latest_year' in PRIORITY_FILTERS
        assert 'majority_years' in PRIORITY_FILTERS
    
    def test_roe_is_priority_in_all_types(self):
        """测试 ROE 在所有过滤类型中都是常用指标"""
        assert 'roe' in PRIORITY_FILTERS['consecutive_years']
        assert 'roe' in PRIORITY_FILTERS['latest_year']
        assert 'roe' in PRIORITY_FILTERS['majority_years']
    
    def test_gross_profit_margin_is_priority(self):
        """测试毛利率是常用指标"""
        assert 'gross_profit_margin' in PRIORITY_FILTERS['consecutive_years']
        assert 'gross_profit_margin' in PRIORITY_FILTERS['latest_year']
    
    def test_roic_is_priority(self):
        """测试 ROIC 是常用指标"""
        assert 'roic' in PRIORITY_FILTERS['consecutive_years']
        assert 'roic' in PRIORITY_FILTERS['latest_year']
    
    def test_pe_ratio_is_priority_in_latest_year(self):
        """测试市盈率在最近一年过滤中是常用指标"""
        assert 'pe_ratio' in PRIORITY_FILTERS['latest_year']


class TestGetPriorityFields:
    """测试获取常用指标集合"""
    
    def test_get_consecutive_years_priority_fields(self):
        """测试获取连续年份过滤的常用指标"""
        fields = get_priority_fields('consecutive_years')
        assert 'roe' in fields
        assert 'gross_profit_margin' in fields
    
    def test_get_latest_year_priority_fields(self):
        """测试获取最近一年过滤的常用指标"""
        fields = get_priority_fields('latest_year')
        assert 'roe' in fields
        assert 'pe_ratio' in fields
    
    def test_get_unknown_type_returns_empty(self):
        """测试未知类型返回空集合"""
        fields = get_priority_fields('unknown_type')
        assert fields == set()


class TestIsPriorityFilter:
    """测试常用指标判断"""
    
    def test_roe_is_priority(self):
        """测试 ROE 被识别为常用指标"""
        assert is_priority_filter('consecutive_years', 'roe') is True
        assert is_priority_filter('latest_year', 'roe') is True
    
    def test_pe_ratio_is_priority_in_latest_year(self):
        """测试市盈率在最近一年过滤中是常用指标"""
        assert is_priority_filter('latest_year', 'pe_ratio') is True
        # 但在连续年份中不是（如果配置中没有）
        # 根据当前配置，pe_ratio 只在 latest_year 中
        assert is_priority_filter('consecutive_years', 'pe_ratio') is False
    
    def test_custom_field_is_not_priority(self):
        """测试自定义字段不是常用指标"""
        assert is_priority_filter('consecutive_years', 'custom_field') is False
    
    def test_case_insensitive(self):
        """测试字段名比较不区分大小写"""
        assert is_priority_filter('consecutive_years', 'ROE') is True
        assert is_priority_filter('latest_year', 'Roe') is True


class TestClassifyConditions:
    """测试条件分类"""
    
    def test_classify_mixed_conditions(self):
        """测试混合条件分类"""
        conditions = [
            {'type': 'consecutive_years', 'params': {'field': 'roe', 'min_value': 15}},
            {'type': 'latest_year', 'params': {'field': 'pe_ratio', 'max_value': 20}},
            {'type': 'consecutive_years', 'params': {'field': 'custom_field', 'min_value': 10}},
        ]
        
        result = classify_conditions(conditions)
        
        assert len(result['priority']) == 2
        assert len(result['non_priority']) == 1
        assert result['priority'][0]['params']['field'] == 'roe'
        assert result['priority'][1]['params']['field'] == 'pe_ratio'
        assert result['non_priority'][0]['params']['field'] == 'custom_field'
    
    def test_classify_all_priority(self):
        """测试全部是常用指标"""
        conditions = [
            {'type': 'consecutive_years', 'params': {'field': 'roe', 'min_value': 15}},
            {'type': 'latest_year', 'params': {'field': 'gross_profit_margin', 'min_value': 30}},
        ]
        
        result = classify_conditions(conditions)
        
        assert len(result['priority']) == 2
        assert len(result['non_priority']) == 0
    
    def test_classify_all_non_priority(self):
        """测试全部是非常用指标"""
        conditions = [
            {'type': 'consecutive_years', 'params': {'field': 'custom1', 'min_value': 10}},
            {'type': 'latest_year', 'params': {'field': 'custom2', 'max_value': 20}},
        ]
        
        result = classify_conditions(conditions)
        
        assert len(result['priority']) == 0
        assert len(result['non_priority']) == 2
    
    def test_classify_empty_conditions(self):
        """测试空条件列表"""
        result = classify_conditions([])
        
        assert result['priority'] == []
        assert result['non_priority'] == []


class TestCacheKeyGeneration:
    """测试缓存键生成"""
    
    def test_generate_priority_cache_key(self):
        """测试常用指标缓存键生成"""
        key = generate_cache_key('consecutive_years', 'roe', 5, 15)
        assert key == 'filter_consecutive_years_roe_5_15_A'
    
    def test_generate_cache_key_with_market(self):
        """测试带市场标识的缓存键"""
        key_a = generate_cache_key('consecutive_years', 'roe', 5, 15, 'A')
        key_hk = generate_cache_key('consecutive_years', 'roe', 5, 15, 'HK')
        
        assert key_a == 'filter_consecutive_years_roe_5_15_A'
        assert key_hk == 'filter_consecutive_years_roe_5_15_HK'
        assert key_a != key_hk  # 不同市场缓存隔离
    
    def test_generate_non_priority_cache_key(self):
        """测试非常用指标缓存键生成"""
        key = generate_non_priority_cache_key(
            'consecutive_years', 'custom_field', 5, 10, 'abc123'
        )
        assert key == 'filter_nopriority_consecutive_years_custom_field_5_10_abc123_A'
    
    def test_compute_context_hash_stability(self):
        """测试上下文 hash 的稳定性"""
        conditions = [
            {'type': 'consecutive_years', 'params': {'field': 'roe', 'min_value': 15}},
        ]
        
        hash1 = compute_context_hash(conditions)
        hash2 = compute_context_hash(conditions)
        
        assert hash1 == hash2
        assert len(hash1) == 8  # 8 位十六进制
    
    def test_compute_context_hash_order_independent(self):
        """测试上下文 hash 与条件顺序无关"""
        conditions1 = [
            {'type': 'consecutive_years', 'params': {'field': 'roe', 'min_value': 15}},
            {'type': 'latest_year', 'params': {'field': 'pe_ratio', 'max_value': 20}},
        ]
        conditions2 = [
            {'type': 'latest_year', 'params': {'field': 'pe_ratio', 'max_value': 20}},
            {'type': 'consecutive_years', 'params': {'field': 'roe', 'min_value': 15}},
        ]
        
        hash1 = compute_context_hash(conditions1)
        hash2 = compute_context_hash(conditions2)
        
        assert hash1 == hash2  # 相同条件不同顺序应生成相同 hash


class TestFilterBuilderCacheIntegration:
    """测试 FilterBuilder 与缓存的集成"""
    
    def test_filter_builder_execute_with_empty_data(self):
        """测试 FilterBuilder 在空数据上的执行"""
        fb = FilterBuilder()
        fb.add_filter('latest_year', field='roe', min_value=15)
        
        df = pd.DataFrame()
        result = fb.execute(df)
        
        assert result.empty
    
    def test_filter_builder_basic_consecutive_years(self):
        """测试连续年份过滤基础功能"""
        # 创建测试数据（使用字符串格式的 end_date）
        df = pd.DataFrame({
            'stock_code': ['001', '001', '001', '001', '001',
                          '002', '002', '002', '002', '002'],
            'end_date': ['20201231', '20211231', '20221231', '20231231', '20241231',
                        '20201231', '20211231', '20221231', '20231231', '20241231'],
            'roe': [10, 12, 14, 16, 18,  # 001: 逐年增长
                   20, 20, 20, 20, 20],  # 002: 稳定 20
        })
        
        fb = FilterBuilder()
        fb.add_filter('consecutive_years', field='roe', min_value=15, years=3)
        
        result = fb.execute(df)
        
        # 只有 002 满足连续 3 年 ROE >= 15
        assert '002' in result['stock_code'].values
        assert '001' not in result['stock_code'].values


class TestPriorityFilterExecution:
    """测试优先级过滤执行（集成测试）"""
    
    def test_priority_filters_execute_first(self):
        """测试常用指标优先执行"""
        from value_investment.data.cache import SmartCache
        import tempfile
        import os
        
        # 创建临时缓存目录
        with tempfile.TemporaryDirectory() as cache_dir:
            cache = SmartCache(cache_dir)
            
            # 创建 FilterBuilder 并设置缓存
            fb = FilterBuilder(cache=cache, market='A')
            fb.add_filter('consecutive_years', field='roe', min_value=15, years=3)
            fb.add_filter('latest_year', field='pe_ratio', max_value=20)
            
            # 创建测试数据（end_date 使用字符串格式）
            df = pd.DataFrame({
                'stock_code': ['001', '001', '001', '002', '002', '002'],
                'end_date': ['20221231', '20231231', '20241231', '20221231', '20231231', '20241231'],
                'roe': [10, 12, 14, 16, 18, 20],  # 只有 002 满足 ROE>=15
                'pe_ratio': [15, 15, 15, 25, 25, 25],  # 001 PE=15, 002 PE=25
            })
            
            result = fb.execute(df)
            
            # 001 满足 PE<=20 但不满足 ROE>=15
            # 002 满足 ROE>=15 但不满足 PE<=20
            # 所以结果应该为空
            assert result.empty
    
    def test_priority_cache_reuse(self):
        """测试常用指标缓存复用（相同数据集场景）"""
        from value_investment.data.cache import SmartCache
        import tempfile
        
        with tempfile.TemporaryDirectory() as cache_dir:
            cache = SmartCache(cache_dir)
            
            # 第一次执行：扫描 1000 只股票
            fb1 = FilterBuilder(cache=cache, market='A')
            fb1.add_filter('consecutive_years', field='roe', min_value=15, years=3)
            
            # 大数据集
            df1 = pd.DataFrame({
                'stock_code': ['001', '001', '001', '002', '002', '002', '003', '003', '003'],
                'end_date': ['20221231'] * 3 + ['20231231'] * 3 + ['20241231'] * 3,
                'roe': [10, 12, 14, 16, 18, 20, 20, 20, 20],  # 只有 002 和 003 满足
            })
            # 修正数据格式
            df1 = pd.DataFrame({
                'stock_code': ['001', '001', '001', '002', '002', '002', '003', '003', '003'],
                'end_date': ['20221231', '20231231', '20241231'] * 3,
                'roe': [10, 12, 14, 16, 18, 20, 20, 20, 20],
            })
            
            result1 = fb1.execute(df1)
            
            # 验证缓存已创建
            cache_keys = cache.list_keys()
            assert any('filter_consecutive_years_roe' in k for k in cache_keys)
            
            # 验证第一次结果
            assert set(result1['stock_code'].unique()) == {'002', '003'}
            
            # 第二次执行：使用相同条件，扫描相同数据集（缓存命中）
            fb2 = FilterBuilder(cache=cache, market='A')
            fb2.add_filter('consecutive_years', field='roe', min_value=15, years=3)
            fb2.add_filter('latest_year', field='roe', min_value=20)  # 额外条件：最新一年 ROE>=20
            
            # 相同数据集
            df2 = df1.copy()
            
            result2 = fb2.execute(df2)
            
            # 验证缓存复用：第一次过滤结果应该从缓存获取
            # 002 和 003 满足 ROE>=15（缓存命中）
            # 002 最新一年 ROE=20>=20，满足
            # 003 最新一年 ROE=20>=20，满足
            # 所以结果应该是 {'002', '003'}
            assert set(result2['stock_code'].unique()) == {'002', '003'}
    
    def test_non_priority_cache_with_context_hash(self):
        """测试非常用指标带上下文 hash 缓存"""
        from value_investment.data.cache import SmartCache
        import tempfile
        
        with tempfile.TemporaryDirectory() as cache_dir:
            cache = SmartCache(cache_dir)
            
            # 创建 FilterBuilder，包含常用和非常用指标
            fb = FilterBuilder(cache=cache, market='A')
            fb.add_filter('consecutive_years', field='roe', min_value=15, years=3)  # 常用
            fb.add_filter('consecutive_years', field='custom_field', min_value=10, years=3)  # 非常用
            
            df = pd.DataFrame({
                'stock_code': ['001', '001', '001', '002', '002', '002'],
                'end_date': ['20221231', '20231231', '20241231', '20221231', '20231231', '20241231'],
                'roe': [16, 18, 20, 10, 12, 14],
                'custom_field': [15, 15, 15, 5, 5, 5],  # 001 满足 custom_field>=10
            })
            
            result = fb.execute(df)
            
            # 001 满足 ROE>=15 且 custom_field>=10
            # 002 不满足 ROE>=15
            # 所以结果应该只有 001
            assert not result.empty
            assert set(result['stock_code'].unique()) == {'001'}
            
            # 验证缓存键包含上下文 hash
            cache_keys = cache.list_keys()
            nopriority_keys = [k for k in cache_keys if 'filter_nopriority' in k]
            assert len(nopriority_keys) > 0
            # 验证缓存键包含 8 位 hash
            for key in nopriority_keys:
                # 格式：filter_nopriority_{type}_{field}_{years}_{value}_{hash}_{market}
                parts = key.split('_')
                # hash 应该是倒数第二个部分（market 是最后一个）
                assert len(parts[-2]) == 8, f"Hash length should be 8, got {len(parts[-2])} in key {key}"
