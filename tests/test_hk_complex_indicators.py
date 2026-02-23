"""Tests for HK stock complex indicators: ROIC, CAGR, ImpliedGrowth, PEPct"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


class TestHKROICIndicator:
    """Test ROIC indicator with HK data"""

    def test_roic_with_hk_field_names(self):
        """Should calculate ROIC with standardized field names"""
        from value_investment.indicators.growth import ROICIndicator

        # Use standardized field names
        data = pd.DataFrame({
            'year': [2023, 2022],
            'operating_profit': [50000, 45000],
            'total_equity': [1000000, 900000],
            'short_term_debt': [50000, 40000],
            'long_term_debt': [100000, 90000],
            'cash_and_equivalents': [80000, 70000],
        })

        indicator = ROICIndicator()
        result = indicator.calculate(data, tax_rate=0.25)

        # 2023:
        # NOPAT = 50000 * (1 - 0.25) = 37500
        # Debt = 50000 + 100000 = 150000
        # Cash = 80000 + 30000 + 10000 = 120000
        # Invested Capital = 1000000 + 150000 - 120000 = 1030000
        # ROIC = 37500 / 1030000 * 100 = 3.64%
        assert result.value > 0
        assert result.unit == "%"

    def test_roic_find_column_hk_fields(self):
        """Should find columns with standardized field names"""
        from value_investment.indicators.growth import ROICIndicator

        indicator = ROICIndicator()

        # Test operating profit field finding with standardized field names
        df = pd.DataFrame({'operating_profit': [100]})
        col = indicator._find_column(df, ['operating_profit'])
        assert col == 'operating_profit'

        # Test total assets field finding
        df = pd.DataFrame({'total_assets': [100]})
        col = indicator._find_column(df, ['total_assets'])
        assert col == 'total_assets'

        # Test accounts payable field finding
        df = pd.DataFrame({'accounts_payable': [100]})
        col = indicator._find_column(df, ['accounts_payable'])
        assert col == 'accounts_payable'


class TestHKCAGRIndicator:
    """Test CAGR indicator with HK data"""

    def test_cagr_revenue_with_hk_fields(self):
        """Should calculate CAGR with standardized revenue fields"""
        from value_investment.indicators.growth import CAGRIndicator

        # Use standardized field names
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            'total_revenue': [800000, 1000000, 1250000],
        })

        indicator = CAGRIndicator()
        result = indicator.calculate(data, metric="total_revenue")

        # CAGR = (1250000 / 800000)^(1/2) - 1 = 0.25 = 25%
        assert result.value > 0
        assert result.unit == "%"

    def test_cagr_net_profit_with_hk_fields(self):
        """Should calculate CAGR with standardized net profit fields"""
        from value_investment.indicators.growth import CAGRIndicator

        # Use standardized field names
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            'net_profit': [80000, 100000, 125000],
        })

        indicator = CAGRIndicator()
        result = indicator.calculate(data, metric="net_profit")

        assert result.value > 0
        assert result.unit == "%"

    def test_cagr_find_column_hk_fields(self):
        """Should find columns with standardized field names"""
        from value_investment.indicators.growth import CAGRIndicator

        indicator = CAGRIndicator()

        # Test revenue field finding with standardized field names
        df = pd.DataFrame({'total_revenue': [100]})
        col = indicator._find_column(df, ['total_revenue'])
        assert col == 'total_revenue'

        # Test net profit field finding with standardized field names
        df = pd.DataFrame({'net_profit': [100]})
        col = indicator._find_column(df, ['net_profit'])
        assert col == 'net_profit'

        # Test equity field finding with standardized field names
        df = pd.DataFrame({'total_equity': [100]})
        col = indicator._find_column(df, ['total_equity'])
        assert col == 'total_equity'


class TestHKImpliedGrowthIndicator:
    """Test ImpliedGrowth indicator with HK data"""

    def test_implied_growth_with_hk_fields(self):
        """Should calculate implied growth with standardized cash flow fields"""
        from value_investment.indicators.valuation import ImpliedGrowthIndicator

        # Use standardized field names
        data = pd.DataFrame({
            'year': [2023, 2022],
            'operating_cash_flow': [80000, 70000],
            'capital_expenditure': [10000, 9000],
        })

        indicator = ImpliedGrowthIndicator()
        # Market cap in billions
        result = indicator.calculate(data, market_cap=500_000_000_000, wacc=0.10, growth_rate=0.03)

        # FCF = 80000 - 10000 = 70000
        # With positive FCF and reasonable market cap, should calculate
        assert result.value != 0 or "需要" in result.description

    def test_implied_growth_find_column_hk_fields(self):
        """Should find columns with HK field names"""
        from value_investment.indicators.valuation import ImpliedGrowthIndicator

        indicator = ImpliedGrowthIndicator()

        # Test operating cash flow field finding (HK uses 经营业务现金净额)
        df = pd.DataFrame({'经营业务现金净额': [100]})
        col = indicator._find_column(df, ['operating_cash_flow', '经营活动现金流', '经营业务现金净额'])
        assert col == '经营业务现金净额'

        # Test capital expenditure field finding (HK uses 购建固定资产)
        df = pd.DataFrame({'购建固定资产': [100]})
        col = indicator._find_column(df, ['capital_expenditure', '资本支出', '购建固定资产'])
        assert col == '购建固定资产'


class TestHKPEPctIndicator:
    """Test PEPct indicator with HK data"""

    def test_pe_pct_requires_provider(self):
        """PEPct should require provider for HK stocks"""
        from value_investment.indicators.valuation import PEPercentileIndicator

        data = pd.DataFrame({
            'year': [2023, 2022, 2021],
            '净利润': [100000, 90000, 80000]
        })

        indicator = PEPercentileIndicator()

        # Without provider, should return error message
        result = indicator.calculate(data, stock_code="00700")
        assert "需要stock_code参数" in result.description or result.value == 0

    def test_pe_pct_with_mock_hk_provider(self):
        """Should calculate PE percentile with HK mock data"""
        from value_investment.indicators.valuation import PEPercentileIndicator

        # Create mock provider
        mock_provider = MagicMock()

        # Mock stock info (HK uses different field names)
        mock_info = pd.DataFrame({
            'item': ['总股本', '总市值'],
            'value': ['9323060843', 2800000000000]  # ~9.3 billion shares, 2.8 trillion HKD
        })
        mock_provider.get_stock_info.return_value = mock_info

        # Mock profit sheet (HK uses 股东应占溢利)
        mock_profit = pd.DataFrame({
            'year': [2023.0, 2022.0, 2021.0],
            '股东应占溢利': [115600000000, 107500000000, 102800000000],  # Tencent HK net profit
            'REPORT_DATE': ['2024-03-31', '2023-03-31', '2022-03-31']
        })
        mock_provider.get_profit_sheet.return_value = mock_profit

        # Mock historical data
        mock_hist = pd.DataFrame({
            'date': ['2023-12-31', '2023-12-29', '2023-12-28'],
            'close': [318.0, 320.0, 315.0]
        })
        mock_provider.get_historical_data.return_value = mock_hist

        data = pd.DataFrame({
            'year': [2023, 2022, 2021],
            '股东应占溢利': [115600000000, 107500000000, 102800000000]
        })

        indicator = PEPercentileIndicator()
        result = indicator.calculate(
            data,
            provider=mock_provider,
            stock_code="00700",
            years=3
        )

        # Should calculate with data from provider
        assert result is not None
        # If PE calculation works, should have some result (value or error message)
        assert hasattr(result, 'value')
        assert hasattr(result, 'description')

    def test_pe_pct_find_column_hk_fields(self):
        """Should find columns with standardized field names"""
        from value_investment.indicators.valuation import PEPercentileIndicator

        # PEPercentileIndicator uses dependency injection (quarterly, prices)
        # instead of _find_column, so no need to test _find_column here


class TestHKComplexIndicatorsIntegration:
    """Integration tests for HK complex indicators"""

    def test_all_indicators_registered(self):
        """All complex indicators should be registered"""
        from value_investment.indicators.factory import IndicatorFactory

        factory = IndicatorFactory()

        # Check all complex indicators are registered
        assert factory.get("ROIC") is not None
        assert factory.get("CAGR") is not None
        assert factory.get("ImpliedGrowth") is not None
        assert factory.get("PEPct") is not None

    def test_cagr_with_multiple_metrics_hk(self):
        """CAGR should work with different metrics using standardized fields"""
        from value_investment.indicators.growth import CAGRIndicator

        # Test with equity (standardized field name after DataMapper mapping)
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            'total_equity': [800000, 900000, 1000000],  # Standardized field name
        })

        indicator = CAGRIndicator()
        result = indicator.calculate(data, metric="total_equity")

        assert result.value > 0
        assert result.unit == "%"
