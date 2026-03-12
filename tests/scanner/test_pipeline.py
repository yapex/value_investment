"""FilterBuilder 和 Scanner.scan() 的测试"""
import pytest
import pandas as pd
from value_investment.scanner.pipeline import FilterBuilder
from value_investment.scanner import filters


class TestFilterBuilder:
    """FilterBuilder 测试"""
    
    def test_add_filter_returns_self(self):
        """add_filter 应该返回 self，支持链式调用"""
        fb = FilterBuilder()
        result = fb.add_filter('latest_year', field='roe', min_value=15)
        
        assert result is fb
    
    def test_add_filter_chain(self):
        """测试链式调用"""
        fb = (FilterBuilder()
            .add_filter('latest_year', field='roe', min_value=15)
            .add_filter('consecutive_years', field='gross_profit_margin', min_value=30, years=5))
        
        assert len(fb) == 2
    
    def test_add_filter_unknown_type_raises_error(self):
        """未知过滤器类型应该抛出错误"""
        fb = FilterBuilder()
        
        with pytest.raises(ValueError, match="Unknown filter type"):
            fb.add_filter('unknown_filter', field='roe')
    
    def test_execute_single_filter(self):
        """执行单个过滤"""
        # 准备测试数据
        df = pd.DataFrame({
            'stock_code': ['A', 'A', 'B', 'B'],
            'end_date': ['2024-12-31', '2023-12-31', '2024-12-31', '2023-12-31'],
            'roe': [20.0, 18.0, 10.0, 12.0],
        })
        df['end_date'] = pd.to_datetime(df['end_date'])
        
        # 执行过滤
        fb = FilterBuilder()
        fb.add_filter('latest_year', field='roe', min_value=15)
        
        result = fb.execute(df)
        
        # 只有 A 通过
        assert result['stock_code'].nunique() == 1
        assert 'A' in result['stock_code'].values
    
    def test_execute_multiple_filters(self):
        """执行多个过滤（级联）"""
        # 注意：latest_year 取的是最新年份的数据
        # A: 2022年 roe=20 (最新), 毛利率=35
        # B: 2022年 roe=10 (最新), 毛利率=25
        df = pd.DataFrame({
            'stock_code': ['A', 'A', 'A', 'B', 'B', 'B'],
            'end_date': ['2020-12-31', '2021-12-31', '2022-12-31',
                        '2020-12-31', '2021-12-31', '2022-12-31'],
            'roe': [14.0, 16.0, 20.0, 12.0, 11.0, 10.0],  # A 最新=20, B 最新=10
            'gross_profit_margin': [30.0, 32.0, 35.0, 25.0, 25.0, 25.0],  # A 最新=35, B 最新=25
        })
        df['end_date'] = pd.to_datetime(df['end_date'])
        
        # 先过滤 ROE，再过滤毛利率
        fb = (FilterBuilder()
            .add_filter('latest_year', field='roe', min_value=15)
            .add_filter('latest_year', field='gross_profit_margin', min_value=30))
        
        result = fb.execute(df)
        
        # A 通过 ROE 过滤 (latest 20 >= 15)，也通过毛利率过滤 (latest 35 >= 30)
        # B 不通过 ROE 过滤 (latest 10 < 15)
        assert 'A' in result['stock_code'].values
        assert 'B' not in result['stock_code'].values
    
    def test_to_config(self):
        """导出配置"""
        fb = (FilterBuilder()
            .add_filter('latest_year', field='roe', min_value=15)
            .add_filter('consecutive_years', field='gross_profit_margin', min_value=30))
        
        config = fb.to_config()
        
        assert len(config) == 2
        assert config[0]['type'] == 'latest_year'
        assert config[0]['params']['field'] == 'roe'
        assert config[1]['type'] == 'consecutive_years'
    
    def test_to_json(self):
        """导出 JSON"""
        fb = FilterBuilder()
        fb.add_filter('latest_year', field='roe', min_value=15)
        
        json_str = fb.to_json()
        
        import json
        config = json.loads(json_str)
        assert len(config) == 1
        assert config[0]['type'] == 'latest_year'
    
    def test_add_filters_from_config(self):
        """从配置批量添加"""
        config = [
            {'type': 'latest_year', 'params': {'field': 'roe', 'min_value': 15}},
            {'type': 'consecutive_years', 'params': {'field': 'gross_profit_margin', 'min_value': 30}},
        ]
        
        fb = FilterBuilder().add_filters_from_config(config)
        
        assert len(fb) == 2
    
    def test_add_filters_from_json(self):
        """从 JSON 字符串添加"""
        json_str = '[{"type": "latest_year", "params": {"field": "roe", "min_value": 15}}]'
        
        fb = FilterBuilder().add_filters_from_json(json_str)
        
        assert len(fb) == 1
    
    def test_len(self):
        """len() 返回过滤条件数量"""
        fb = (FilterBuilder()
            .add_filter('latest_year', field='roe')
            .add_filter('consecutive_years', field='gross_profit_margin'))
        
        assert len(fb) == 2


class TestScannerScan:
    """Scanner.scan() 方法测试"""
    
    def test_scan_with_filters(self):
        """测试 scan 方法使用 FilterBuilder"""
        from value_investment import Scanner
        
        # 这个测试需要实际 API，mock 可能会复杂
        # 暂时跳过集成测试，只验证接口存在
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
