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
