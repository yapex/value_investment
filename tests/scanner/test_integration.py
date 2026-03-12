"""集成测试 - 验证 Scanner + filters 完整流程"""
import pandas as pd
from value_investment.scanner import filters


class TestIntegration:
    """集成测试类"""

    def test_consecutive_years_integration(self):
        """测试连续年份过滤集成"""
        df = pd.DataFrame({
            'stock_code': ['600519', '600519', '600519'],
            'end_date': ['2022-12-31', '2023-12-31', '2024-12-31'],
            'roe': [30.0, 31.0, 32.0],
        })
        df['end_date'] = pd.to_datetime(df['end_date'])

        result = filters.consecutive_years(df, field='roe', min_value=15, years=3)

        assert len(result) == 3
        assert result['stock_code'].nunique() == 1
