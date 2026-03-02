"""Tests for efficiency indicators - expense ratio, fee rate, fixed asset turnover"""
import pytest
from value_investment.api import ValueInvestment


def test_indicator_factory_has_expense_ratio():
    """Test that expense_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "expense_ratio" in indicators, f"expense_ratio not in indicators: {indicators}"


def test_indicator_factory_has_fee_rate():
    """Test that fee_rate indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "fee_rate" in indicators, f"fee_rate not in indicators: {indicators}"


def test_indicator_factory_has_fixed_asset_turnover():
    """Test that fixed_asset_turnover indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "fixed_asset_turnover" in indicators, f"fixed_asset_turnover not in indicators: {indicators}"


def test_expense_ratio_calculation():
    """Test expense_ratio calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("expense_ratio", "600519")
    assert result is not None
    assert result.unit == "%"


def test_fee_rate_calculation():
    """Test fee_rate calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("fee_rate", "600519")
    assert result is not None
    assert result.unit == "%"


def test_fixed_asset_turnover_calculation():
    """Test fixed_asset_turnover calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("fixed_asset_turnover", "600519")
    assert result is not None
    assert result.unit == "ratio"


# Phase 2 indicators - 费用占毛利润比
def test_indicator_factory_has_fee_to_gross_profit_ratio():
    """Test that fee_to_gross_profit_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "fee_to_gross_profit_ratio" in indicators, f"fee_to_gross_profit_ratio not in indicators: {indicators}"


def test_fee_to_gross_profit_ratio_calculation():
    """Test fee_to_gross_profit_ratio calculation for A stock

    Formula: 三费 / 毛利润 = (销售费用+管理费用+财务费用) / (营业收入-营业成本)
    Thresholds: <50%优秀, >70%无关注价值
    """
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("fee_to_gross_profit_ratio", "600519")
    assert result is not None
    assert result.unit == "%"
    # Verify the calculation is reasonable (should be a positive percentage)
    assert result.value >= 0, f"Fee to gross profit ratio should be non-negative, got {result.value}"


def test_fee_to_gross_profit_ratio_with_zero_gross_profit():
    """Test fee_to_gross_profit_ratio handles zero gross profit (division by zero)"""
    import pandas as pd
    from value_investment.indicators.efficiency import FeeToGrossProfitRatioIndicator

    indicator = FeeToGrossProfitRatioIndicator()

    # Create test data with zero gross profit (operating_income == operating_cost)
    data = pd.DataFrame({
        'year': [2023],
        'operating_income': [100.0],
        'operating_cost': [100.0],  # Zero gross profit
        'sales_expense': [10.0],
        'management_expense': [5.0],
        'financial_expense': [2.0],
    })

    result = indicator.calculate(data)
    assert result is not None
    # Should handle division by zero gracefully
    assert result.value == 0.0 or result.value == float('inf') or result.value == 0


# Phase 2 indicators - 应收账款占比
def test_indicator_factory_has_accounts_receivable_ratio():
    """Test that accounts_receivable_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "accounts_receivable_ratio" in indicators, f"accounts_receivable_ratio not in indicators: {indicators}"


def test_accounts_receivable_ratio_calculation():
    """Test accounts_receivable_ratio calculation for A stock

    Formula: 应收账款 / 营业收入
    Threshold: >30%需警惕
    """
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("accounts_receivable_ratio", "600519")
    assert result is not None
    assert result.unit == "%"
    # Verify the calculation is reasonable (should be a positive percentage)
    assert result.value >= 0, f"Accounts receivable ratio should be non-negative, got {result.value}"


def test_accounts_receivable_ratio_with_zero_revenue():
    """Test accounts_receivable_ratio handles zero revenue (division by zero)"""
    import pandas as pd
    from value_investment.indicators.efficiency import AccountsReceivableRatioIndicator

    indicator = AccountsReceivableRatioIndicator()

    # Create test data with zero revenue
    data = pd.DataFrame({
        'year': [2023],
        'operating_income': [0.0],  # Zero revenue
        'accounts_receivable': [50.0],
    })

    result = indicator.calculate(data)
    assert result is not None
    # Should handle division by zero gracefully
    assert result.value == 0.0


# Phase 2 indicators - 生产资产占比
def test_indicator_factory_has_production_asset_ratio():
    """Test that production_asset_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "production_asset_ratio" in indicators, f"production_asset_ratio not in indicators: {indicators}"


def test_production_asset_ratio_calculation():
    """Test production_asset_ratio calculation for A stock

    Formula: (固定资产 + 在建工程 + 工程物资) / 总资产
    Note: 土地 is part of intangible_assets and typically not separated in data
    """
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("production_asset_ratio", "600519")
    assert result is not None
    assert result.unit == "%"
    # Verify the calculation is reasonable (should be a positive percentage between 0-100)
    assert 0 <= result.value <= 100, f"Production asset ratio should be between 0-100%, got {result.value}"


def test_production_asset_ratio_with_zero_total_assets():
    """Test production_asset_ratio handles zero total assets (division by zero)"""
    import pandas as pd
    from value_investment.indicators.efficiency import ProductionAssetRatioIndicator

    indicator = ProductionAssetRatioIndicator()

    # Create test data with zero total assets
    data = pd.DataFrame({
        'year': [2023],
        'total_assets': [0.0],
        'fixed_assets': [100.0],
        'construction_in_progress': [50.0],
    })

    result = indicator.calculate(data)
    assert result is not None
    # Should handle division by zero gracefully
    assert result.value == 0.0


# Phase 2 indicators - 税前利润/生产资产
def test_indicator_factory_has_return_on_production_assets():
    """Test that return_on_production_assets indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "return_on_production_assets" in indicators, f"return_on_production_assets not in indicators: {indicators}"


def test_return_on_production_assets_calculation():
    """Test return_on_production_assets calculation for A stock

    Formula: 利润总额 / 生产资产
    Where 生产资产 = 固定资产 + 在建工程 + 工程物资

    From 手把手教你读财报: 用"税前利润总额÷生产资产"，得出的比值如果显著高于
    社会平均资本回报率（银行借款标准利率的两倍左右），则属于优秀公司
    """
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("return_on_production_assets", "600519")
    assert result is not None
    assert result.unit == "%"


def test_return_on_production_assets_with_zero_production_assets():
    """Test return_on_production_assets handles zero production assets (division by zero)"""
    import pandas as pd
    from value_investment.indicators.efficiency import ReturnOnProductionAssetsIndicator

    indicator = ReturnOnProductionAssetsIndicator()

    # Create test data with zero production assets
    data = pd.DataFrame({
        'year': [2023],
        'total_profit': [100.0],
        'fixed_assets': [0.0],
        'construction_in_progress': [0.0],
    })

    result = indicator.calculate(data)
    assert result is not None
    # Should handle division by zero gracefully
    assert result.value == 0.0


# Phase 2 indicators - 应收类科目占比
def test_indicator_factory_has_receivables_to_assets_ratio():
    """Test that receivables_to_assets_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "receivables_to_assets_ratio" in indicators, f"receivables_to_assets_ratio not in indicators: {indicators}"


def test_receivables_to_assets_ratio_calculation():
    """Test receivables_to_assets_ratio calculation for A stock

    Formula: (应收账款 + 应收票据 + 其他应收款) / 总资产
    Note: 银票 (bank acceptances) is typically not available separately

    From 手把手教你读财报: 所有带"应收"两个字的科目总和，减去银票金额，
    看其占总资产比例是否过大，一般超过三成已经算严重，过半显然有问题
    """
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("receivables_to_assets_ratio", "600519")
    assert result is not None
    assert result.unit == "%"
    # Verify the calculation is reasonable (should be a positive percentage between 0-100)
    assert 0 <= result.value <= 100, f"Receivables to assets ratio should be between 0-100%, got {result.value}"


def test_receivables_to_assets_ratio_with_zero_total_assets():
    """Test receivables_to_assets_ratio handles zero total assets (division by zero)"""
    import pandas as pd
    from value_investment.indicators.efficiency import ReceivablesToAssetsRatioIndicator

    indicator = ReceivablesToAssetsRatioIndicator()

    # Create test data with zero total assets
    data = pd.DataFrame({
        'year': [2023],
        'total_assets': [0.0],
        'accounts_receivable': [50.0],
        'notes_receivable': [20.0],
        'other_receivables': [10.0],
    })

    result = indicator.calculate(data)
    assert result is not None
    # Should handle division by zero gracefully
    assert result.value == 0.0
