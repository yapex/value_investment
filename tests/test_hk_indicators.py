"""Tests for HK stock financial indicators"""
import pytest
import pandas as pd


class TestHKFinancialIndicators:
    """Test HK stock financial indicators registration"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup registry with defaults"""
        from value_investment.indicators.registry import IndicatorRegistry, register_defaults

        registry = IndicatorRegistry.get_instance()
        registry.clear()
        register_defaults()

    def test_hk_market_indicators_list(self):
        """Should list indicators available for HK market"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        hk_indicators = registry.list_by_market("港股")

        # Print for debugging
        hk_names = [ind.name for ind in hk_indicators]
        print(f"HK indicators: {hk_names}")

        assert isinstance(hk_indicators, list)
        # Should have more than basic indicators
        assert len(hk_indicators) > 0

    def test_hk_has_gross_margin(self):
        """HK market should have gross margin indicator"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        gross_margin = registry.get("gross_margin")

        assert gross_margin is not None, "gross_margin should be registered"

    def test_hk_has_debt_ratio(self):
        """HK market should have debt ratio indicator"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        debt_ratio = registry.get("debt_ratio")

        assert debt_ratio is not None, "debt_ratio should be registered"

    def test_hk_has_current_ratio(self):
        """HK market should have current ratio indicator"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        current_ratio = registry.get("current_ratio")

        assert current_ratio is not None, "current_ratio should be registered"

    def test_hk_has_quick_ratio(self):
        """HK market should have quick ratio indicator"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        quick_ratio = registry.get("quick_ratio")

        assert quick_ratio is not None, "quick_ratio should be registered"

    def test_hk_has_inventory_turnover(self):
        """HK market should have inventory turnover indicator"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        inventory_turnover = registry.get("inventory_turnover")

        assert inventory_turnover is not None, "inventory_turnover should be registered"

    def test_hk_has_receivable_turnover(self):
        """HK market should have receivable turnover indicator"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        receivable_turnover = registry.get("receivable_turnover")

        assert receivable_turnover is not None, "receivable_turnover should be registered"

    def test_hk_has_asset_turnover(self):
        """HK market should have asset turnover indicator"""
        from value_investment.indicators.registry import IndicatorRegistry

        registry = IndicatorRegistry.get_instance()
        asset_turnover = registry.get("asset_turnover")

        assert asset_turnover is not None, "asset_turnover should be registered"


class TestHKIndicatorsCalculation:
    """Test HK stock indicators calculation with mock data"""

    def test_gross_margin_calculation(self):
        """Should calculate gross margin correctly"""
        from value_investment.indicators.simple import GrossMarginIndicator

        # Create mock data
        data = pd.DataFrame({
            'year': [2023, 2022, 2021],
            'revenue': [1000000, 900000, 800000],
            'cost_of_sales': [600000, 540000, 480000]
        })

        indicator = GrossMarginIndicator()
        result = indicator.calculate(data)

        # Gross margin = (revenue - cost) / revenue * 100
        # (1000000 - 600000) / 1000000 * 100 = 40%
        assert result.value == pytest.approx(40.0, rel=0.1)
        assert result.unit == "%"

    def test_current_ratio_calculation(self):
        """Should calculate current ratio correctly"""
        from value_investment.indicators.simple import CurrentRatioIndicator

        data = pd.DataFrame({
            'year': [2023, 2022],
            'current_assets': [500000, 400000],
            'current_liabilities': [250000, 200000]
        })

        indicator = CurrentRatioIndicator()
        result = indicator.calculate(data)

        # Current ratio = current assets / current liabilities
        # 500000 / 250000 = 2.0
        assert result.value == pytest.approx(2.0, rel=0.1)

    def test_quick_ratio_calculation(self):
        """Should calculate quick ratio correctly"""
        from value_investment.indicators.simple import QuickRatioIndicator

        data = pd.DataFrame({
            'year': [2023, 2022],
            'current_assets': [500000, 400000],
            'inventory': [100000, 80000],
            'current_liabilities': [250000, 200000]
        })

        indicator = QuickRatioIndicator()
        result = indicator.calculate(data)

        # Quick ratio = (current assets - inventory) / current liabilities
        # (500000 - 100000) / 250000 = 1.6
        assert result.value == pytest.approx(1.6, rel=0.1)

    def test_debt_ratio_calculation(self):
        """Should calculate debt ratio correctly"""
        from value_investment.indicators.simple import DebtRatioIndicator

        data = pd.DataFrame({
            'year': [2023, 2022],
            'total_liabilities': [400000, 350000],
            'total_assets': [1000000, 900000]
        })

        indicator = DebtRatioIndicator()
        result = indicator.calculate(data)

        # Debt ratio = liabilities / assets * 100
        # 400000 / 1000000 * 100 = 40%
        assert result.value == pytest.approx(40.0, rel=0.1)

    def test_inventory_turnover_calculation(self):
        """Should calculate inventory turnover correctly"""
        from value_investment.indicators.simple import InventoryTurnoverIndicator

        data = pd.DataFrame({
            'year': [2023, 2022],
            'operating_cost': [600000, 540000],
            'inventory': [100000, 90000]
        })

        indicator = InventoryTurnoverIndicator()
        result = indicator.calculate(data)

        # Inventory turnover = cost / inventory
        # 600000 / 100000 = 6.0
        assert result.value == pytest.approx(6.0, rel=0.1)

    def test_receivable_turnover_calculation(self):
        """Should calculate receivable turnover correctly"""
        from value_investment.indicators.simple import ReceivableTurnoverIndicator

        data = pd.DataFrame({
            'year': [2023, 2022],
            'operating_income': [1000000, 900000],
            'accounts_receivable': [200000, 180000]
        })

        indicator = ReceivableTurnoverIndicator()
        result = indicator.calculate(data)

        # Receivable turnover = income / receivable
        # 1000000 / 200000 = 5.0
        assert result.value == pytest.approx(5.0, rel=0.1)

    def test_asset_turnover_calculation(self):
        """Should calculate asset turnover correctly"""
        from value_investment.indicators.simple import AssetTurnoverIndicator

        data = pd.DataFrame({
            'year': [2023, 2022],
            'operating_income': [1000000, 900000],
            'total_assets': [2000000, 1800000]
        })

        indicator = AssetTurnoverIndicator()
        result = indicator.calculate(data)

        # Asset turnover = income / assets
        # 1000000 / 2000000 = 0.5
        assert result.value == pytest.approx(0.5, rel=0.1)
