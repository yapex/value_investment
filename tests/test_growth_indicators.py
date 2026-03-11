"""Test Growth Indicators - TDD Style"""
import pytest
import pandas as pd


class TestRevenueGrowthIndicator:
    """营业收入增长率测试"""

    def test_calculates_year_over_year_growth_correctly(self):
        """
        营业收入增长率 = (本期营业收入 - 上期营业收入) / 上期营业收入 * 100
        
        数据 (按年份升序):
        - 2021: 100
        - 2022: 120  -> 增长率 = (120-100)/100 * 100 = 20%
        - 2023: 150  -> 增长率 = (150-120)/120 * 100 = 25%
        
        平均增长率 = (20 + 25) / 2 = 22.5%
        """
        from value_investment.indicators.growth import RevenueGrowthIndicator
        
        indicator = RevenueGrowthIndicator()
        
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            'operating_income': [100.0, 120.0, 150.0],
        })
        
        result = indicator.calculate(data)
        
        assert result.unit == '%'
        assert len(result.values) == 2  # 3年数据只有2个增长率
        assert result.value == pytest.approx(22.5, 0.1)

    def test_handles_single_year_gracefully(self):
        """单年数据无法计算增长率，应返回空"""
        from value_investment.indicators.growth import RevenueGrowthIndicator
        
        indicator = RevenueGrowthIndicator()
        
        data = pd.DataFrame({
            'year': [2023],
            'operating_income': [100.0],
        })
        
        result = indicator.calculate(data)
        
        assert len(result.values) == 0
        assert result.value == 0.0

    def test_skips_growth_when_previous_is_zero(self):
        """上期为零时跳过增长率计算（避免除零）"""
        from value_investment.indicators.growth import RevenueGrowthIndicator
        
        indicator = RevenueGrowthIndicator()
        
        data = pd.DataFrame({
            'year': [2022, 2023],
            'operating_income': [0.0, 100.0],
        })
        
        result = indicator.calculate(data)
        
        # 上期为0，无法计算增长率，应跳过
        assert len(result.values) == 0

    def test_works_with_descending_year_order(self):
        """数据按年份降序排列时也能正确计算"""
        from value_investment.indicators.growth import RevenueGrowthIndicator
        
        indicator = RevenueGrowthIndicator()
        
        # 注意：年份是降序的
        data = pd.DataFrame({
            'year': [2023, 2022, 2021],
            'operating_income': [150.0, 120.0, 100.0],
        })
        
        result = indicator.calculate(data)
        
        # 结果应该一样：20% 和 25%，平均 22.5%
        assert result.value == pytest.approx(22.5, 0.1)


class TestOperatingProfitGrowthIndicator:
    """营业利润增长率测试"""

    def test_calculates_operating_profit_growth(self):
        """
        营业利润增长率 = (本期营业利润 - 上期营业利润) / 上期营业利润 * 100
        """
        from value_investment.indicators.growth import OperatingProfitGrowthIndicator
        
        indicator = OperatingProfitGrowthIndicator()
        
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            'operating_profit': [50.0, 60.0, 75.0],
        })
        
        result = indicator.calculate(data)
        
        # 2022: (60-50)/50 * 100 = 20%
        # 2023: (75-60)/60 * 100 = 25%
        # mean = 22.5%
        assert result.unit == '%'
        assert result.value == pytest.approx(22.5, 0.1)


class TestTotalAssetGrowthIndicator:
    """总资产增长率测试"""

    def test_calculates_total_asset_growth(self):
        """总资产增长率"""
        from value_investment.indicators.growth import TotalAssetGrowthIndicator
        
        indicator = TotalAssetGrowthIndicator()
        
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            'total_assets': [1000.0, 1200.0, 1500.0],
        })
        
        result = indicator.calculate(data)
        
        # 2022: 20%, 2023: 25%, mean: 22.5%
        assert result.value == pytest.approx(22.5, 0.1)


class TestNetAssetGrowthIndicator:
    """净资产增长率测试"""

    def test_calculates_net_asset_growth(self):
        """净资产(股东权益)增长率"""
        from value_investment.indicators.growth import NetAssetGrowthIndicator
        
        indicator = NetAssetGrowthIndicator()
        
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            'total_equity': [600.0, 700.0, 800.0],
        })
        
        result = indicator.calculate(data)
        
        # 2022: (700-600)/600 * 100 = 16.67%
        # 2023: (800-700)/700 * 100 = 14.29%
        # mean = 15.48%
        assert result.value == pytest.approx(15.48, 0.1)


class TestOperatingProfitMarginIndicator:
    """营业利润率测试"""

    def test_calculates_operating_profit_margin(self):
        """
        营业利润率 = 营业利润 / 营业收入 * 100
        """
        from value_investment.indicators.profitability import OperatingProfitMarginIndicator
        
        indicator = OperatingProfitMarginIndicator()
        
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            'operating_profit': [20.0, 30.0, 40.0],
            'operating_income': [100.0, 100.0, 100.0],
        })
        
        result = indicator.calculate(data)
        
        # 2021: 20%, 2022: 30%, 2023: 40%, mean: 30%
        assert result.unit == '%'
        assert result.value == pytest.approx(30.0, 0.1)

    def test_handles_zero_revenue_gracefully(self):
        """营业收入为零时避免除零错误"""
        from value_investment.indicators.profitability import OperatingProfitMarginIndicator
        
        indicator = OperatingProfitMarginIndicator()
        
        data = pd.DataFrame({
            'year': [2023],
            'operating_profit': [10.0],
            'operating_income': [0.0],
        })
        
        result = indicator.calculate(data)
        
        # 不应该抛出异常，应该返回合理值
        assert result is not None
