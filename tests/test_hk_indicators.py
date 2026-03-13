"""Tests for HK stock financial indicator calculation"""

import pytest
import pandas as pd

from value_investment.indicators.hk import calculate_hk_roe, calculate_hk_roic, merge_hk_financial_data


class TestHKROICCalculation:
    """Tests for HK stock ROIC calculation from three statements

    ROIC = NOPAT / 投入资本
    - NOPAT = 股东应占溢利 + 融资成本
    - 投入资本 = 股东权益 + 短期贷款 + 长期贷款
    """

    def test_calculate_hk_roic_basic(self):
        """Test basic ROIC calculation"""
        # 模拟利润表数据
        income_data = pd.DataFrame({
            'year': [2024, 2023],
            '股东应占溢利': [1000, 900],  # 净利润
            '融资成本': [100, 80],        # 财务费用/融资成本
        })

        # 模拟资产负债表数据
        balance_data = pd.DataFrame({
            'year': [2024, 2023],
            '股东权益': [10000, 9000],
            '短期贷款': [2000, 1800],
            '长期贷款': [3000, 2700],
        })

        result = calculate_hk_roic(income_data, balance_data)

        assert len(result) == 2
        assert 'year' in result.columns
        assert 'roic' in result.columns

        # ROIC = (净利润 + 融资成本) / (股东权益 + 短期贷款 + 长期贷款)
        # 2024: (1000 + 100) / (10000 + 2000 + 3000) = 1100 / 15000 = 7.33%
        # 2023: (900 + 80) / (9000 + 1800 + 2700) = 980 / 13500 = 7.26%
        expected_roic = [7.333333, 7.259259]
        assert abs(result['roic'].iloc[0] - expected_roic[0]) < 0.01
        assert abs(result['roic'].iloc[1] - expected_roic[1]) < 0.01

    def test_calculate_hk_roic_without_debt(self):
        """Test ROIC calculation when there's no debt (only equity)"""
        income_data = pd.DataFrame({
            'year': [2024],
            '股东应占溢利': [1000],
            '融资成本': [0],
        })

        balance_data = pd.DataFrame({
            'year': [2024],
            '股东权益': [10000],
            '短期贷款': [0],
            '长期贷款': [0],
        })

        result = calculate_hk_roic(income_data, balance_data)

        # ROIC = (1000 + 0) / (10000 + 0 + 0) = 10%
        expected_roic = [10.0]
        assert abs(result['roic'].iloc[0] - expected_roic[0]) < 0.01

    def test_calculate_hk_roic_with_zero_capital(self):
        """Test ROIC calculation handles zero invested capital"""
        income_data = pd.DataFrame({
            'year': [2024],
            '股东应占溢利': [1000],
            '融资成本': [100],
        })

        balance_data = pd.DataFrame({
            'year': [2024],
            '股东权益': [0],
            '短期贷款': [0],
            '长期贷款': [0],
        })

        result = calculate_hk_roic(income_data, balance_data)

        # Should return NaN when invested capital is 0
        assert pd.isna(result.iloc[0]['roic'])

    def test_calculate_hk_roic_with_missing_debt_columns(self):
        """Test ROIC calculation when debt columns are missing"""
        income_data = pd.DataFrame({
            'year': [2024],
            '股东应占溢利': [1000],
            '融资成本': [100],
        })

        # 只有股东权益，没有贷款字段
        balance_data = pd.DataFrame({
            'year': [2024],
            '股东权益': [10000],
        })

        result = calculate_hk_roic(income_data, balance_data)

        # Should handle missing columns gracefully
        # ROIC = (1000 + 100) / 10000 = 11%
        expected_roic = [11.0]
        assert abs(result['roic'].iloc[0] - expected_roic[0]) < 0.01


class TestHKROECalculation:
    """Tests for HK stock ROE calculation from three statements"""

    def test_calculate_hk_roe_basic(self):
        """Test basic ROE calculation"""
        # 模拟利润表数据
        income_data = pd.DataFrame({
            'year': [2024, 2023, 2022],
            '股东应占溢利': [1000, 900, 800],  # 净利润
        })

        # 模拟资产负债表数据
        balance_data = pd.DataFrame({
            'year': [2024, 2023, 2022],
            '股东权益': [10000, 9000, 8000],
        })

        result = calculate_hk_roe(income_data, balance_data)

        assert len(result) == 3
        assert 'year' in result.columns
        assert 'roe' in result.columns

        # ROE = 净利润 / 股东权益
        expected_roe = [10.0, 10.0, 10.0]  # 1000/10000=10%, 900/9000=10%, 800/8000=10%
        assert result['roe'].tolist() == expected_roe

    def test_calculate_hk_roe_with_zero_equity(self):
        """Test ROE calculation handles zero equity"""
        income_data = pd.DataFrame({
            'year': [2024],
            '股东应占溢利': [1000],
        })

        balance_data = pd.DataFrame({
            'year': [2024],
            '股东权益': [0],  # 零权益
        })

        result = calculate_hk_roe(income_data, balance_data)

        # 应该返回 NaN 而不是 infinity
        assert pd.isna(result.iloc[0]['roe'])

    def test_merge_hk_financial_data(self):
        """Test merging three statements into one DataFrame"""
        balance = pd.DataFrame({
            'year': [2024, 2023],
            '股东权益': [10000, 9000],
            '总资产': [50000, 45000],
        })

        income = pd.DataFrame({
            'year': [2024, 2023],
            '股东应占溢利': [1000, 900],
            '营业额': [20000, 18000],
        })

        cashflow = pd.DataFrame({
            'year': [2024, 2023],
            '经营产生现金': [1500, 1300],
        })

        result = merge_hk_financial_data(balance, income, cashflow)

        assert len(result) == 2
        assert '股东权益' in result.columns
        assert '股东应占溢利' in result.columns
        assert '经营产生现金' in result.columns
