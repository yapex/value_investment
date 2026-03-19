"""Tests for ImpliedGrowth Calculator"""
from value_investment.calculator_plugin import registry


class TestImpliedGrowth:
    def setup_method(self):
        self.calc = registry.get_by_name("implied_growth")

    def test_required_fields(self):
        """包含 FCF 和市值相关字段"""
        assert "operating_cash_flow" in self.calc.required_fields
        assert "market_cap" in self.calc.required_fields

    def test_name(self):
        """字段名为 implied_growth"""
        assert self.calc.name == "implied_growth"

    def test_calculate_basic(self):
        """基本计算：给定市值反推增长率"""
        results = {
            "operating_cash_flow": {2024: 100e8, 2023: 90e8},
            "capital_expenditure": {2024: 20e8, 2023: 18e8},
            "market_cap": {2024: 5000e8},  # 5000亿市值
        }

        calculated = self.calc.calculate(results)

        assert 2024 in calculated
        # 市值5000亿，年FCF约80亿，WACC=10%，永续=3%
        # 隐含增长率应该在合理范围内（5%~15%）
        assert 0.05 < calculated[2024] < 0.20

    def test_calculate_with_free_cash_flow(self):
        """使用 free_cash_flow 字段"""
        results = {
            "operating_cash_flow": {2024: 100e8},
            "free_cash_flow": {2024: 80e8},
            "market_cap": {2024: 4000e8},
        }

        calculated = self.calc.calculate(results)

        assert 2024 in calculated

    def test_missing_operating_cash_flow(self):
        """缺少 operating_cash_flow 返回空"""
        results = {
            "market_cap": {2024: 5000e8},
        }

        calculated = self.calc.calculate(results)

        assert calculated == {}

    def test_missing_market_cap(self):
        """缺少 market_cap 返回空"""
        results = {
            "operating_cash_flow": {2024: 100e8},
        }

        calculated = self.calc.calculate(results)

        assert calculated == {}

    def test_invalid_fcf(self):
        """FCF 为负返回空"""
        results = {
            "operating_cash_flow": {2024: -10e8},
            "capital_expenditure": {2024: 20e8},
            "market_cap": {2024: 5000e8},
        }

        calculated = self.calc.calculate(results)

        assert calculated == {}

    def test_zero_market_cap(self):
        """市值为零返回空"""
        results = {
            "operating_cash_flow": {2024: 100e8},
            "capital_expenditure": {2024: 20e8},
            "market_cap": {2024: 0},
        }

        calculated = self.calc.calculate(results)

        assert calculated == {}
