"""测试CLI hist命令对600519的兼容性"""
import pytest
from value_investment.api import ValueInvestment


def test_hist_command_with_600519():
    """测试hist命令能否正确获取600519的历史数据
    
    这个测试是为了重现问题: pandas 3.0.0 移除了 fillna() 的 method 参数,
    导致 tushare 的 pro_bar() 调用失败。
    """
    vi = ValueInvestment(market="A")
    
    # 获取600519最近1年的历史数据
    df = vi.get_historical_data("600519", end_date="20241231", start_date="20240101")
    
    # 验证返回的数据
    assert df is not None, "应该返回数据"
    assert not df.empty, "数据不应为空"
    assert len(df) > 0, "应该有历史记录"
    
    # 验证必要的列存在
    # 注意：daily接口返回volume而不是vol
    required_columns = ["trade_date", "open", "high", "low", "close"]
    for col in required_columns:
        # 允许字段名不同（映射后的字段名）
        assert col in df.columns or col.upper() in df.columns, f"缺少列: {col}"

    # 验证成交量列存在（可能是vol或volume）
    assert "vol" in df.columns or "volume" in df.columns, "应该有成交量列"


def test_balance_sheet_has_column_names():
    """测试资产负债表输出是否有列名"""
    vi = ValueInvestment(market="A")
    
    # 获取600519的资产负债表
    df = vi.get_balance_sheet("600519", end_year=2024)
    
    # 验证返回的数据
    assert df is not None, "应该返回数据"
    assert not df.empty, "数据不应为空"
    
    # 验证有列名（不是空的）
    assert len(df.columns) > 0, "应该有列名"
    assert all(df.columns.notna()), "列名不应为空"
    
    # 验证关键列存在
    assert "report_date" in df.columns or "ann_date" in df.columns, "应该有日期列"


def test_income_statement_has_column_names():
    """测试利润表输出是否有列名"""
    vi = ValueInvestment(market="A")
    
    # 获取600519的利润表
    df = vi.get_profit_sheet("600519", end_year=2024)
    
    # 验证返回的数据
    assert df is not None, "应该返回数据"
    assert not df.empty, "数据不应为空"
    
    # 验证有列名
    assert len(df.columns) > 0, "应该有列名"


def test_cashflow_has_column_names():
    """测试现金流量表输出是否有列名"""
    vi = ValueInvestment(market="A")
    
    # 获取600519的现金流量表
    df = vi.get_cashflow_sheet("600519", end_year=2024)
    
    # 验证返回的数据
    assert df is not None, "应该返回数据"
    assert not df.empty, "数据不应为空"
    
    # 验证有列名
    assert len(df.columns) > 0, "应该有列名"
