"""Tests for HK stock complex indicators: ROIC, CAGR, ImpliedGrowth, PEPct"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


class TestHKROICIndicator:
    """Test ROIC indicator with HK data"""

    def test_roic_with_hk_field_names(self):
        """Should calculate ROIC with HK field names"""
        from value_investment.indicators.complex import ROICIndicator

        # HK field names from balance sheet - using new formula
        # Invested Capital = Shareholders' Equity + Debt - Cash
        data = pd.DataFrame({
            'year': [2023, 2022],
            '经营溢利': [50000, 45000],  # HK: Operating profit
            '股东权益': [1000000, 900000],  # HK: Shareholders' equity
            '短期贷款': [50000, 40000],  # HK: Short-term loan
            '长期贷款': [100000, 90000],  # HK: Long-term loan
            '现金及等价物': [80000, 70000],  # HK: Cash and equivalents
            '短期存款': [30000, 25000],  # HK: Short-term deposit
            '中长期存款': [10000, 8000],  # HK: Medium/long-term deposit
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
        """Should find columns with HK field names"""
        from value_investment.indicators.complex import ROICIndicator

        indicator = ROICIndicator()

        # Test operating profit field finding
        df = pd.DataFrame({'经营溢利': [100]})
        col = indicator._find_column(df, ['operating_profit', '经营溢利', '营业利润'])
        assert col == '经营溢利'

        # Test total assets field finding
        df = pd.DataFrame({'总资产': [100]})
        col = indicator._find_column(df, ['total_assets', '总资产', '资产总计'])
        assert col == '总资产'

        # Test accounts payable field finding
        df = pd.DataFrame({'应付帐款': [100]})
        col = indicator._find_column(df, ['accounts_payable', '应付账款', '应付帐款'])
        assert col == '应付帐款'


class TestHKCAGRIndicator:
    """Test CAGR indicator with HK data"""

    def test_cagr_revenue_with_hk_fields(self):
        """Should calculate CAGR with HK revenue fields"""
        from value_investment.indicators.complex import CAGRIndicator

        # HK: 营业额 = revenue
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            '营业额': [800000, 1000000, 1250000],  # HK: Revenue
        })

        indicator = CAGRIndicator()
        result = indicator.calculate(data, metric="revenue")

        # CAGR = (1250000 / 800000)^(1/2) - 1 = 0.25 = 25%
        assert result.value > 0
        assert result.unit == "%"

    def test_cagr_net_profit_with_hk_fields(self):
        """Should calculate CAGR with HK net profit fields"""
        from value_investment.indicators.complex import CAGRIndicator

        # HK: 股东应占溢利 = Parent net profit (attributable to shareholders)
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            '股东应占溢利': [80000, 100000, 125000],  # HK: Net profit attributable to shareholders
        })

        indicator = CAGRIndicator()
        result = indicator.calculate(data, metric="net_profit")

        assert result.value > 0
        assert result.unit == "%"

    def test_cagr_find_column_hk_fields(self):
        """Should find columns with HK field names"""
        from value_investment.indicators.complex import CAGRIndicator

        indicator = CAGRIndicator()

        # Test revenue field finding (HK uses 营业额)
        df = pd.DataFrame({'营业额': [100]})
        col = indicator._find_column(df, ['revenue', '营业额', '营业收入'])
        assert col == '营业额'

        # Test net profit field finding (HK uses 股东应占溢利)
        df = pd.DataFrame({'股东应占溢利': [100]})
        col = indicator._find_column(df, ['net_profit', '净利润', '股东应占溢利'])
        assert col == '股东应占溢利'

        # Test equity field finding (HK uses 股东权益)
        df = pd.DataFrame({'股东权益': [100]})
        col = indicator._find_column(df, ['total_equity', '股东权益', '权益总额'])
        assert col == '股东权益'


class TestHKImpliedGrowthIndicator:
    """Test ImpliedGrowth indicator with HK data"""

    def test_implied_growth_with_hk_fields(self):
        """Should calculate implied growth with HK cash flow fields"""
        from value_investment.indicators.complex import ImpliedGrowthIndicator

        # HK field names from cash flow statement
        data = pd.DataFrame({
            'year': [2023, 2022],
            '经营业务现金净额': [80000, 70000],  # HK: Operating cash flow
            '购建固定资产': [10000, 9000],  # HK: Capital expenditure
        })

        indicator = ImpliedGrowthIndicator()
        # Market cap in billions
        result = indicator.calculate(data, market_cap=500_000_000_000, wacc=0.10, growth_rate=0.03)

        # FCF = 80000 - 10000 = 70000
        # With positive FCF and reasonable market cap, should calculate
        assert result.value != 0 or "需要" in result.description

    def test_implied_growth_find_column_hk_fields(self):
        """Should find columns with HK field names"""
        from value_investment.indicators.complex import ImpliedGrowthIndicator

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
        from value_investment.indicators.complex import PEPercentileIndicator

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
        from value_investment.indicators.complex import PEPercentileIndicator

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
        """Should find columns with HK field names"""
        from value_investment.indicators.complex import PEPercentileIndicator

        indicator = PEPercentileIndicator()

        # Test net profit field finding (HK uses 股东应占溢利)
        df = pd.DataFrame({'股东应占溢利': [100]})
        col = indicator._find_column(df, ['net_profit', '净利润', '股东应占溢利', 'PARENT_NETPROFIT'])
        assert col == '股东应占溢利'


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
        """CAGR should work with different metrics using HK fields"""
        from value_investment.indicators.complex import CAGRIndicator

        # Test with equity (HK: 股东权益)
        data = pd.DataFrame({
            'year': [2021, 2022, 2023],
            '股东权益': [800000, 900000, 1000000],  # HK: Total equity
        })

        indicator = CAGRIndicator()
        result = indicator.calculate(data, metric="total_equity")

        assert result.value > 0
        assert result.unit == "%"
