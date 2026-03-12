"""filters 过滤函数测试"""
import pandas as pd
from value_investment.scanner import filters


class TestConsecutiveYears:
    """连续年份过滤测试"""

    def test_consecutive_years_basic(self):
        """测试基本连续年份过滤"""
        df = pd.DataFrame({
            'stock_code': ['A', 'A', 'A', 'B', 'B', 'B'],
            'end_date': ['2022-12-31', '2023-12-31', '2024-12-31',
                        '2022-12-31', '2023-12-31', '2024-12-31'],
            'roe': [16.0, 17.0, 18.0, 10.0, 11.0, 12.0],
        })
        df['end_date'] = pd.to_datetime(df['end_date'])

        result = filters.consecutive_years(df, field='roe', min_value=15, years=3)

        assert result['stock_code'].nunique() == 1
        assert result.iloc[0]['stock_code'] == 'A'

    def test_consecutive_years_not_enough(self):
        """测试数据不足的年份"""
        df = pd.DataFrame({
            'stock_code': ['A', 'A'],
            'end_date': ['2023-12-31', '2024-12-31'],
            'roe': [16.0, 17.0],
        })
        df['end_date'] = pd.to_datetime(df['end_date'])

        result = filters.consecutive_years(df, field='roe', min_value=15, years=3)

        assert len(result) == 0


class TestMajorityYears:
    """多数年份过滤测试 - N 年中至少 M 年满足条件"""

    def test_majority_years_basic(self):
        """测试基本多数年份过滤：5 年中至少 3 年满足"""
        df = pd.DataFrame({
            'stock_code': ['A'] * 5 + ['B'] * 5,
            'end_date': ['2020-12-31', '2021-12-31', '2022-12-31', '2023-12-31', '2024-12-31'] * 2,
            'roe': [20.0, 16.0, 14.0, 18.0, 19.0,   # A: 4年满足
                    10.0, 11.0, 12.0, 13.0, 14.0],  # B: 0年满足
        })
        df['end_date'] = pd.to_datetime(df['end_date'])

        result = filters.majority_years(df, field='roe', min_value=15, years=5, required_years=3)

        assert result['stock_code'].nunique() == 1
        assert 'A' in result['stock_code'].values
        assert 'B' not in result['stock_code'].values

    def test_majority_years_boundary(self):
        """测试边界：刚好满足要求的年数"""
        df = pd.DataFrame({
            'stock_code': ['A'] * 5 + ['B'] * 5,
            'end_date': ['2020-12-31', '2021-12-31', '2022-12-31', '2023-12-31', '2024-12-31'] * 2,
            'roe': [15.0, 15.0, 15.0, 10.0, 10.0,   # A: 3年满足（刚好）
                    15.0, 15.0, 15.0, 10.0, 10.0],  # B: 3年满足（刚好）
        })
        df['end_date'] = pd.to_datetime(df['end_date'])

        result = filters.majority_years(df, field='roe', min_value=15, years=5, required_years=3)

        assert result['stock_code'].nunique() == 2

    def test_majority_years_with_avg(self):
        """测试带平均值条件的多数年份过滤"""
        df = pd.DataFrame({
            'stock_code': ['A'] * 5 + ['B'] * 5,
            'end_date': ['2020-12-31', '2021-12-31', '2022-12-31', '2023-12-31', '2024-12-31'] * 2,
            'roe': [20.0, 20.0, 5.0, 5.0, 5.0,     # A: 2年满足，平均10（不满足平均15）
                    15.0, 15.0, 15.0, 15.0, 15.0], # B: 5年满足，平均15（满足）
        })
        df['end_date'] = pd.to_datetime(df['end_date'])

        result = filters.majority_years(
            df, field='roe', min_value=15, years=5, required_years=3, min_avg=15
        )

        assert 'A' not in result['stock_code'].values
        assert 'B' in result['stock_code'].values

    def test_majority_years_not_enough_data(self):
        """测试数据不足的情况"""
        df = pd.DataFrame({
            'stock_code': ['A'] * 3,
            'end_date': ['2022-12-31', '2023-12-31', '2024-12-31'],
            'roe': [16.0, 17.0, 18.0],
        })
        df['end_date'] = pd.to_datetime(df['end_date'])

        # 需要 5 年数据，但只有 3 年
        result = filters.majority_years(df, field='roe', min_value=15, years=5, required_years=3)

        assert len(result) == 0
