"""Test for simple indicators"""
import pytest
from value_investment.api import ValueInvestment


def test_indicator_factory_has_roe():
    """Test that ROE indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "ROE" in indicators, f"ROE not in indicators: {indicators}"


def test_indicator_factory_has_gross_margin():
    """Test that gross margin indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "gross_margin" in indicators, f"gross_margin not in indicators: {indicators}"


def test_indicator_factory_has_roa():
    """Test that ROA indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "ROA" in indicators, f"ROA not in indicators: {indicators}"


def test_indicator_factory_has_latest_market_cap():
    """Test that latest_market_cap indicator is available"""
    vi = ValueInvestment(market="HK")
    indicators = vi.list_indicators()
    assert "latest_market_cap" in indicators, f"latest_market_cap not in indicators: {indicators}"


def test_latest_market_cap_calculation():
    """Test latest_market_cap calculation for HK stock"""
    vi = ValueInvestment(market="HK")
    # 使用 mock 数据测试计算逻辑
    result = vi.calculate_indicator("latest_market_cap", "00700")
    assert result is not None
    # 市值应该大于0
    assert result.value > 0, f"Expected positive market cap, got {result.value}"
    # 单位应该为空
    assert result.unit == ""


# ========== Additional Simple Indicators Tests ==========

def test_indicator_factory_has_net_profit_margin():
    """Test that net_profit_margin indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "net_profit_margin" in indicators, f"net_profit_margin not in indicators: {indicators}"


def test_indicator_factory_has_current_ratio():
    """Test that current_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "current_ratio" in indicators, f"current_ratio not in indicators: {indicators}"


def test_indicator_factory_has_asset_turnover():
    """Test that asset_turnover indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "asset_turnover" in indicators, f"asset_turnover not in indicators: {indicators}"


def test_indicator_factory_has_inventory_turnover():
    """Test that inventory_turnover indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "inventory_turnover" in indicators, f"inventory_turnover not in indicators: {indicators}"


def test_indicator_factory_has_quick_ratio():
    """Test that quick_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "quick_ratio" in indicators, f"quick_ratio not in indicators: {indicators}"


def test_indicator_factory_has_debt_ratio():
    """Test that debt_ratio indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "debt_ratio" in indicators, f"debt_ratio not in indicators: {indicators}"


def test_indicator_factory_has_receivable_turnover():
    """Test that receivable_turnover indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "receivable_turnover" in indicators, f"receivable_turnover not in indicators: {indicators}"


def test_indicator_factory_has_payable_turnover():
    """Test that payable_turnover indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "payable_turnover" in indicators, f"payable_turnover not in indicators: {indicators}"


def test_indicator_factory_has_cfo_to_netprofit():
    """Test that cfo_to_netprofit indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "cfo_to_netprofit" in indicators, f"cfo_to_netprofit not in indicators: {indicators}"


def test_indicator_factory_has_fcf_to_revenue():
    """Test that fcf_to_revenue indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "fcf_to_revenue" in indicators, f"fcf_to_revenue not in indicators: {indicators}"


def test_indicator_factory_has_cfo_to_netprofit_sum():
    """Test that cfo_to_netprofit_sum indicator is available"""
    vi = ValueInvestment(market="A")
    indicators = vi.list_indicators()
    assert "cfo_to_netprofit_sum" in indicators, f"cfo_to_netprofit_sum not in indicators: {indicators}"


def test_net_profit_margin_calculation():
    """Test net_profit_margin calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("net_profit_margin", "600519")
    assert result is not None
    assert result.unit == "%"


def test_current_ratio_calculation():
    """Test current_ratio calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("current_ratio", "600519")
    assert result is not None
    assert result.unit == "ratio"


def test_asset_turnover_calculation():
    """Test asset_turnover calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("asset_turnover", "600519")
    assert result is not None
    assert result.unit == "ratio"


def test_inventory_turnover_calculation():
    """Test inventory_turnover calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("inventory_turnover", "600519")
    assert result is not None
    assert result.unit == "ratio"


def test_quick_ratio_calculation():
    """Test quick_ratio calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("quick_ratio", "600519")
    assert result is not None
    assert result.unit == "ratio"


def test_debt_ratio_calculation():
    """Test debt_ratio calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("debt_ratio", "600519")
    assert result is not None
    assert result.unit == "%"


def test_receivable_turnover_calculation():
    """Test receivable_turnover calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("receivable_turnover", "600519")
    assert result is not None
    assert result.unit == "ratio"


def test_payable_turnover_calculation():
    """Test payable_turnover calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("payable_turnover", "600519")
    assert result is not None
    assert result.unit == "ratio"


def test_cfo_to_netprofit_calculation():
    """Test cfo_to_netprofit calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("cfo_to_netprofit", "600519")
    assert result is not None
    assert result.unit == "%"


def test_fcf_to_revenue_calculation():
    """Test fcf_to_revenue calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("fcf_to_revenue", "600519")
    assert result is not None
    assert result.unit == "%"


def test_cfo_to_netprofit_sum_calculation():
    """Test cfo_to_netprofit_sum calculation for A stock"""
    vi = ValueInvestment(market="A")
    result = vi.calculate_indicator("cfo_to_netprofit_sum", "600519")
    assert result is not None
    assert result.unit == "%"
