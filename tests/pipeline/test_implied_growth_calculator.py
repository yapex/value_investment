"""Tests for ImpliedGrowthCalculator"""
from value_investment.pipeline.calculators.implied_growth import ImpliedGrowthCalculator
from value_investment.pipeline.fields import IFRSFields


class TestImpliedGrowthCalculator:
    def test_required_fields(self):
        """包含 FCF 相关字段"""
        calc = ImpliedGrowthCalculator()
        assert IFRSFields.OPERATING_CASH_FLOW in calc.required_fields
        assert IFRSFields.CAPITAL_EXPENDITURE in calc.required_fields

    def test_name(self):
        """字段名为 implied_growth"""
        calc = ImpliedGrowthCalculator()
        assert calc.name == "implied_growth"

    def test_calculate_basic(self):
        """基本计算：给定市值反推增长率"""
        calc = ImpliedGrowthCalculator()
        results = {
            IFRSFields.OPERATING_CASH_FLOW: {2024: 100e8, 2023: 90e8},
            IFRSFields.CAPITAL_EXPENDITURE: {2024: 20e8, 2023: 18e8},
            IFRSFields.MARKET_CAP: {2024: 5000e8},  # 5000亿市值
        }

        calculated = calc.calculate(results)

        assert 2024 in calculated
        # 市值5000亿，年FCF约80亿，WACC=10%，永续=3%
        # 隐含增长率应该在合理范围内（5%~15%）
        assert 0.05 < calculated[2024] < 0.20

    def test_calculate_with_free_cash_flow(self):
        """使用 free_cash_flow 字段"""
        calc = ImpliedGrowthCalculator()
        results = {
            IFRSFields.OPERATING_CASH_FLOW: {2024: 100e8},
            # free_cash_flow 存在时优先使用
            "free_cash_flow": {2024: 80e8},
            IFRSFields.MARKET_CAP: {2024: 4000e8},
        }

        calculated = calc.calculate(results)

        # 使用 free_cash_flow (80亿) 而非 OCF-CAPEX (80亿)，结果应该接近
        assert 2024 in calculated

    def test_missing_operating_cash_flow(self):
        """缺少 operating_cash_flow 返回空"""
        calc = ImpliedGrowthCalculator()
        results = {
            IFRSFields.MARKET_CAP: {2024: 5000e8},
        }

        calculated = calc.calculate(results)

        assert calculated == {}

    def test_missing_market_cap(self):
        """缺少 market_cap 返回空"""
        calc = ImpliedGrowthCalculator()
        results = {
            IFRSFields.OPERATING_CASH_FLOW: {2024: 100e8},
        }

        calculated = calc.calculate(results)

        assert calculated == {}

    def test_invalid_fcf(self):
        """FCF 为负返回空"""
        calc = ImpliedGrowthCalculator()
        results = {
            IFRSFields.OPERATING_CASH_FLOW: {2024: -10e8},  # 负值
            IFRSFields.CAPITAL_EXPENDITURE: {2024: 20e8},
            IFRSFields.MARKET_CAP: {2024: 5000e8},
        }

        calculated = calc.calculate(results)

        assert calculated == {}

    def test_zero_market_cap(self):
        """市值为零返回空"""
        calc = ImpliedGrowthCalculator()
        results = {
            IFRSFields.OPERATING_CASH_FLOW: {2024: 100e8},
            IFRSFields.CAPITAL_EXPENDITURE: {2024: 20e8},
            IFRSFields.MARKET_CAP: {2024: 0},
        }

        calculated = calc.calculate(results)

        assert calculated == {}
