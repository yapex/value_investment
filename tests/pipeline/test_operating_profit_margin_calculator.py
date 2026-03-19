"""Tests for OperatingProfitMargin"""
from value_investment.domain.calculators.operating_profit_margin import OperatingProfitMargin
from value_investment.domain.fields import CustomFields


class TestOperatingProfitMargin:
    def test_required_fields(self):
        """包含必要的依赖字段"""
        calc = OperatingProfitMargin()
        assert "operating_profit" in calc.required_fields
        assert "total_revenue" in calc.required_fields

    def test_name(self):
        """字段名为 operating_profit_margin"""
        calc = OperatingProfitMargin()
        assert calc.name == CustomFields.OPERATING_PROFIT_MARGIN

    def test_calculate_basic(self):
        """基本计算：营业利润/营业收入"""
        calc = OperatingProfitMargin()
        results = {
            "operating_profit": {2024: 50e8, 2023: 45e8},
            "total_revenue": {2024: 500e8, 2023: 450e8},
        }

        calculated = calc.calculate(results)

        assert 2024 in calculated
        assert 2023 in calculated
        # 50/500 = 10%, 45/450 = 10%
        assert calculated[2024] == 10.0
        assert calculated[2023] == 10.0

    def test_calculate_different_margins(self):
        """不同年份不同利润率"""
        calc = OperatingProfitMargin()
        results = {
            "operating_profit": {2024: 100e8, 2023: 50e8},
            "total_revenue": {2024: 500e8, 2023: 400e8},
        }

        calculated = calc.calculate(results)

        # 2024: 100/500 = 20%
        # 2023: 50/400 = 12.5%
        assert calculated[2024] == 20.0
        assert calculated[2023] == 12.5

    def test_zero_revenue(self):
        """营收为零时不计算"""
        calc = OperatingProfitMargin()
        results = {
            "operating_profit": {2024: 50e8},
            "total_revenue": {2024: 0},
        }

        calculated = calc.calculate(results)

        # 营收为零，不应该有结果
        assert 2024 not in calculated

    def test_missing_operating_profit(self):
        """缺少营业利润返回空"""
        calc = OperatingProfitMargin()
        results = {
            "total_revenue": {2024: 500e8},
        }

        calculated = calc.calculate(results)

        assert calculated == {}

    def test_missing_revenue(self):
        """缺少营业收入返回空"""
        calc = OperatingProfitMargin()
        results = {
            "operating_profit": {2024: 50e8},
        }

        calculated = calc.calculate(results)

        assert calculated == {}
