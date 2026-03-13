"""Tests for data years filtering in scanner

验证扫描时数据年数检查逻辑：
1. 当要求 N 年数据时，不足 N 年的股票应该被排除
2. filter_by_data_years 函数正确工作
3. FilterBuilder 自动应用年数检查
"""

import pytest
import pandas as pd
from datetime import datetime

from value_investment.scanner.filters import (
    filter_by_data_years,
    consecutive_years,
    majority_years,
    latest_year,
)
from value_investment.scanner.pipeline import FilterBuilder


class TestFilterByDataYears:
    """Tests for filter_by_data_years function"""

    def test_filter_by_data_years_basic(self):
        """Test basic filtering by data years"""
        # 创建测试数据
        df = pd.DataFrame({
            'stock_code': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B'],
            'end_date': [
                '2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31', '2020-12-31',  # A: 5 年
                '2024-12-31', '2023-12-31', '2022-12-31',  # B: 3 年
            ],
            'roe': [15, 16, 17, 18, 19, 20, 21, 22],
        })
        
        # 要求 5 年数据
        result = filter_by_data_years(df, required_years=5)
        
        # 只有 A 股票有 5 年数据
        assert len(result['stock_code'].unique()) == 1
        assert result['stock_code'].iloc[0] == 'A'

    def test_filter_by_data_years_with_field(self):
        """Test filtering by data years for specific field"""
        df = pd.DataFrame({
            'stock_code': ['A', 'A', 'A', 'B', 'B', 'B'],
            'end_date': ['2024-12-31', '2023-12-31', '2022-12-31'] * 2,
            'roe': [15, 16, None, 20, 21, 22],  # A 的 2022 年 ROE 缺失
        })
        
        # 要求 ROE 字段有 3 年数据
        result = filter_by_data_years(df, required_years=3, field='roe')
        
        # A 只有 2 年 ROE 数据，B 有 3 年
        assert len(result['stock_code'].unique()) == 1
        assert result['stock_code'].iloc[0] == 'B'

    def test_filter_by_data_years_empty(self):
        """Test filtering with empty DataFrame"""
        df = pd.DataFrame()
        result = filter_by_data_years(df, required_years=5)
        assert result.empty

    def test_filter_by_data_years_no_match(self):
        """Test filtering when no stocks meet requirement"""
        df = pd.DataFrame({
            'stock_code': ['A', 'A', 'B', 'B'],
            'end_date': ['2024-12-31', '2023-12-31'] * 2,
            'roe': [15, 16, 20, 21],
        })
        
        # 要求 5 年，但最多只有 2 年
        result = filter_by_data_years(df, required_years=5)
        
        assert result.empty

    def test_filter_by_data_years_all_pass(self):
        """Test filtering when all stocks meet requirement"""
        df = pd.DataFrame({
            'stock_code': ['A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B'],
            'end_date': ['2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31', '2020-12-31'] * 2,
            'roe': [15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
        })
        
        result = filter_by_data_years(df, required_years=5)
        
        # 所有股票都保留
        assert len(result['stock_code'].unique()) == 2


class TestFilterBuilderDataYears:
    """Tests for FilterBuilder automatic data years filtering"""

    def test_filter_builder_auto_filters_insufficient_data(self):
        """Test that FilterBuilder automatically filters stocks with insufficient data"""
        # 创建测试数据：A 有 5 年，B 只有 3 年
        df = pd.DataFrame({
            'stock_code': ['A'] * 5 + ['B'] * 3,
            'end_date': [
                '2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31', '2020-12-31',
                '2024-12-31', '2023-12-31', '2022-12-31',
            ],
            'roe': [15, 16, 17, 18, 19, 20, 21, 22],
        })
        
        # 构建连续 5 年 ROE>=15% 的过滤条件
        fb = FilterBuilder()
        fb.add_filter('consecutive_years', field='roe', min_value=15, years=5)
        
        result = fb.execute(df)
        
        # B 股票因为只有 3 年数据，应该被排除
        assert len(result['stock_code'].unique()) == 1
        assert result['stock_code'].iloc[0] == 'A'

    def test_filter_builder_majority_years_requires_full_data(self):
        """Test that majority_years also requires full data years"""
        df = pd.DataFrame({
            'stock_code': ['A'] * 5 + ['B'] * 4,
            'end_date': [
                '2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31', '2020-12-31',
                '2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31',
            ],
            'roe': [15, 16, 17, 18, 19, 20, 21, 22, 23],
        })
        
        # 5 年中至少 3 年 ROE>=15%
        fb = FilterBuilder()
        fb.add_filter('majority_years', field='roe', min_value=15, years=5, required_years=3)
        
        result = fb.execute(df)
        
        # B 股票因为只有 4 年数据（不足 5 年），应该被排除
        assert len(result['stock_code'].unique()) == 1
        assert result['stock_code'].iloc[0] == 'A'

    def test_filter_builder_latest_year_no_years_requirement(self):
        """Test that latest_year doesn't require multiple years"""
        df = pd.DataFrame({
            'stock_code': ['A', 'B'],
            'end_date': ['2024-12-31', '2024-12-31'],
            'roe': [15, 20],
        })
        
        # 最近一年 ROE>=15%
        fb = FilterBuilder()
        fb.add_filter('latest_year', field='roe', min_value=15)
        
        result = fb.execute(df)
        
        # 两个股票都满足（都只有 1 年数据，但 latest_year 不要求多年）
        assert len(result['stock_code'].unique()) == 2

    def test_filter_builder_multiple_filters_takes_max_years(self):
        """Test that multiple filters use the maximum years requirement"""
        df = pd.DataFrame({
            'stock_code': ['A'] * 5 + ['B'] * 4 + ['C'] * 3,
            'end_date': [
                '2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31', '2020-12-31',  # A: 5 年
                '2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31',  # B: 4 年
                '2024-12-31', '2023-12-31', '2022-12-31',  # C: 3 年
            ],
            'roe': [15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27],
            'gross_profit_margin': [30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 41, 42],
        })
        
        # 连续 5 年 ROE>=15% + 连续 3 年毛利率>=30%
        fb = FilterBuilder()
        fb.add_filter('consecutive_years', field='roe', min_value=15, years=5)
        fb.add_filter('consecutive_years', field='gross_profit_margin', min_value=30, years=3)
        
        result = fb.execute(df)
        
        # 应该取最大年数要求（5 年），所以只有 A 符合
        assert len(result['stock_code'].unique()) == 1
        assert result['stock_code'].iloc[0] == 'A'


class TestFiltersWithInsufficientData:
    """Tests for filters handling stocks with insufficient data"""

    def test_consecutive_years_excludes_insufficient_data(self):
        """Test that consecutive_years filter excludes stocks with insufficient data"""
        df = pd.DataFrame({
            'stock_code': ['GOOD'] * 5 + ['BAD'] * 3,
            'end_date': [
                '2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31', '2020-12-31',
                '2024-12-31', '2023-12-31', '2022-12-31',
            ],
            'roe': [20, 20, 20, 20, 20, 25, 25, 25],  # BAD 虽然 ROE 高，但数据不足
        })
        
        result = consecutive_years(df, field='roe', min_value=15, years=5)
        
        # BAD 被排除（数据不足 5 年）
        assert len(result['stock_code'].unique()) == 1
        assert result['stock_code'].iloc[0] == 'GOOD'

    def test_majority_years_excludes_insufficient_data(self):
        """Test that majority_years filter excludes stocks with insufficient data"""
        df = pd.DataFrame({
            'stock_code': ['GOOD'] * 5 + ['BAD'] * 2,
            'end_date': [
                '2024-12-31', '2023-12-31', '2022-12-31', '2021-12-31', '2020-12-31',
                '2024-12-31', '2023-12-31',
            ],
            'roe': [20, 10, 20, 10, 20, 25, 25],  # BAD 虽然 100% 满足，但数据不足
        })
        
        result = majority_years(df, field='roe', min_value=15, years=5, required_years=3)
        
        # BAD 被排除（数据不足 5 年）
        assert len(result['stock_code'].unique()) == 1
        assert result['stock_code'].iloc[0] == 'GOOD'
