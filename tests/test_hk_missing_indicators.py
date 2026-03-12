"""Tests for HK missing financial indicators - TDD approach

港股缺失的关键指标：
- total_assets_turnover (总资产周转率)
- equity_multiplier (权益乘数)
- asset_turnover (资产周转率，与total_assets_turnover相同)
- total_assets (总资产)
- total_equity (股东权益)
- gross_margin (毛利率，港股有gross_profit_margin需要统一)
- operating_cash_flow (经营现金流，港股有operating_cash_flow_per_share)

港股可用替代指标：
- debt_ratio_total (可用于计算equity_multiplier=1/(1-debt_ratio))
- gross_profit_margin (需要统一为gross_margin)
- operating_cash_flow_per_share (可用于计算operating_cash_flow)

测试数据（腾讯00700）：
- ROE=15.53%，ROA=8.64%，净利润率=30.63%，负债率=40.83%，毛利率=53.52%
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch

# Ensure registry is initialized
from value_investment.indicators.registry import register_defaults, IndicatorRegistry
register_defaults()


class TestHKMissingIndicators:
    """Test HK missing financial indicators"""

    def test_hk_total_assets_turnover_calculation(self):
        """Should calculate total_assets_turnover from revenue and total_assets"""
        # Given: 模拟港股财务数据
        financial_data = pd.DataFrame({
            'year': [2024],
            'total_revenue': [557395000000],  # 腾讯2024年营收
            'total_assets': [1.6e12],  # 约1.6万亿总资产
        })

        # When: 计算总资产周转率
        from value_investment.indicators.calculated import TotalAssetsTurnoverIndicator
        indicator = TotalAssetsTurnoverIndicator()
        result = indicator.calculate(financial_data)

        # Then: 验证计算结果
        expected_turnover = 557395000000 / 1.6e12
        assert abs(result.value - expected_turnover) < 0.01
        assert result.unit == "次"

    def test_hk_equity_multiplier_from_debt_ratio(self):
        """Should calculate equity_multiplier from debt_ratio"""
        # Given: 模拟港股财务数据（腾讯负债率约40.83%）
        financial_data = pd.DataFrame({
            'year': [2024],
            'debt_ratio': [40.83],  # 负债率百分比
        })

        # When: 计算权益乘数
        from value_investment.indicators.calculated import EquityMultiplierIndicator
        indicator = EquityMultiplierIndicator()
        result = indicator.calculate(financial_data)

        # Then: 验证计算结果 equity_multiplier = 1 / (1 - debt_ratio/100)
        expected_em = 1 / (1 - 40.83 / 100)
        assert abs(result.value - expected_em) < 0.01
        assert result.unit == "倍"

    def test_hk_gross_margin_alias(self):
        """Should use gross_profit_margin as gross_margin for HK stocks"""
        # Given: 港股财务指标数据
        from value_investment.indicators.calculated import GrossMarginIndicator

        # When: 使用港股数据计算毛利率
        financial_data = pd.DataFrame({
            'year': [2024],
            'gross_profit_margin': [53.52],  # 港股直接提供的毛利率
        })

        indicator = GrossMarginIndicator()
        result = indicator.calculate(financial_data)

        # Then: 验证结果
        assert result.value == 53.52
        assert result.unit == "%"

    def test_hk_operating_cash_flow_calculation(self):
        """Should calculate operating_cash_flow from per_share data"""
        # Given: 模拟港股财务数据
        financial_data = pd.DataFrame({
            'year': [2024],
            'operating_cash_flow_per_share': [25.8469],  # 每股经营现金流
            'total_shares': [9.10636e9],  # 总股本
        })

        # When: 计算经营现金流
        from value_investment.indicators.calculated import OperatingCashFlowIndicator
        indicator = OperatingCashFlowIndicator()
        result = indicator.calculate(financial_data)

        # Then: 验证计算结果 (允许10%误差)
        expected_ocf = 25.8469 * 9.10636e9
        assert abs(result.value - expected_ocf) < expected_ocf * 0.1
        assert result.unit == "元"

    def test_hk_total_assets_from_balance_sheet(self):
        """Should get total_assets from HK balance sheet"""
        # Given: 模拟港股资产负债表数据
        financial_data = pd.DataFrame({
            'year': [2024],
            'total_assets': [1.6e12],  # 总资产
        })

        # When: 获取总资产
        from value_investment.indicators.calculated import TotalAssetsIndicator
        indicator = TotalAssetsIndicator()
        result = indicator.calculate(financial_data)

        # Then: 验证结果
        assert result.value == 1.6e12
        assert result.unit == "元"

    def test_hk_total_equity_from_balance_sheet(self):
        """Should get total_equity from HK balance sheet"""
        # Given: 模拟港股资产负债表数据
        financial_data = pd.DataFrame({
            'year': [2024],
            'total_equity': [9.5e11],  # 股东权益
        })

        # When: 获取股东权益
        from value_investment.indicators.calculated import TotalEquityIndicator
        indicator = TotalEquityIndicator()
        result = indicator.calculate(financial_data)

        # Then: 验证结果
        assert result.value == 9.5e11
        assert result.unit == "元"


class TestHKIndicatorRegistry:
    """Test HK indicators in registry"""

    def test_hk_total_assets_turnover_in_factory(self):
        """Should have total_assets_turnover indicator in factory"""
        from value_investment.indicators.factory import IndicatorFactory
        factory = IndicatorFactory()

        indicator = factory.get('total_assets_turnover')
        assert indicator is not None
        assert indicator.name == 'total_assets_turnover'

    def test_hk_equity_multiplier_in_factory(self):
        """Should have equity_multiplier indicator in factory"""
        from value_investment.indicators.factory import IndicatorFactory
        factory = IndicatorFactory()

        indicator = factory.get('equity_multiplier')
        assert indicator is not None
        assert indicator.name == 'equity_multiplier'

    def test_hk_gross_margin_in_factory(self):
        """Should have gross_margin indicator in factory"""
        from value_investment.indicators.factory import IndicatorFactory
        factory = IndicatorFactory()

        indicator = factory.get('gross_margin')
        assert indicator is not None
        assert indicator.name == 'gross_margin'


class TestHKDuPontAnalysis:
    """Test DuPont analysis completeness for HK stocks"""

    def test_hk_dupont_three_factors_available(self):
        """Should have all three DuPont factors for HK"""
        # Given: 腾讯财务数据
        financial_data = pd.DataFrame({
            'year': [2024],
            'net_profit_margin': [30.63],  # 净利润率
            'total_revenue': [557395000000],
            'total_assets': [1.6e12],
            'debt_ratio': [40.83],
        })

        # When: 计算杜邦三要素
        from value_investment.indicators.calculated import (
            NetProfitMarginIndicator,
            TotalAssetsTurnoverIndicator,
            EquityMultiplierIndicator,
        )

        npm = NetProfitMarginIndicator().calculate(financial_data)
        turnover = TotalAssetsTurnoverIndicator().calculate(financial_data)
        em = EquityMultiplierIndicator().calculate(financial_data)

        # Then: 验证ROE = NPM × Turnover × EM
        calculated_roe = npm.value / 100 * turnover.value * em.value * 100  # 转换为百分比
        expected_roe = 30.63 / 100 * (557395000000 / 1.6e12) * (1 / (1 - 40.83 / 100)) * 100
        assert abs(calculated_roe - expected_roe) < 1.0  # 允许1%误差

    def test_hk_dupont_roe_verification(self):
        """Should verify ROE calculation matches reported value"""
        # Given: 腾讯实际数据
        financial_data = pd.DataFrame({
            'year': [2024],
            'net_profit': [166582000000],
            'total_equity': [9.5e11],  # 估算
        })

        # When: 计算ROE
        from value_investment.indicators.calculated import ROEIndicator
        roe = ROEIndicator().calculate(financial_data)

        # Then: 验证ROE约等于15.53%
        expected_roe = 166582000000 / 9.5e11 * 100
        assert abs(roe.value - expected_roe) < 2.0  # 允许2%误差
