"""港股财务指标计算模块

从三表数据计算财务指标
"""

import pandas as pd
import numpy as np


def merge_hk_financial_data(
    balance: pd.DataFrame,
    income: pd.DataFrame,
    cashflow: pd.DataFrame
) -> pd.DataFrame:
    """合并港股三表数据

    Args:
        balance: 资产负债表 DataFrame
        income: 利润表 DataFrame
        cashflow: 现金流量表 DataFrame

    Returns:
        合并后的 DataFrame，包含所有三表字段
    """
    if balance is None or balance.empty:
        raise ValueError("资产负债表不能为空")

    result = balance.copy()

    if income is not None and not income.empty:
        income_cols = [c for c in income.columns if c != 'year']
        result = result.merge(
            income[['year'] + income_cols],
            on='year',
            how='left'
        )

    if cashflow is not None and not cashflow.empty:
        cashflow_cols = [c for c in cashflow.columns if c != 'year']
        result = result.merge(
            cashflow[['year'] + cashflow_cols],
            on='year',
            how='left'
        )

    return result


def calculate_hk_roe(income: pd.DataFrame, balance: pd.DataFrame) -> pd.DataFrame:
    """计算港股 ROE

    ROE = 股东应占溢利 / 股东权益

    Args:
        income: 利润表 DataFrame，需包含 'year' 和 '股东应占溢利' 列
        balance: 资产负债表 DataFrame，需包含 'year' 和 '股东权益' 列

    Returns:
        包含 year 和 roe 列的 DataFrame
    """
    if income is None or income.empty:
        return pd.DataFrame({'year': [], 'roe': []})

    if balance is None or balance.empty:
        return pd.DataFrame({'year': income['year'], 'roe': [np.nan] * len(income)})

    # 合并数据
    merged = income[['year', '股东应占溢利']].merge(
        balance[['year', '股东权益']],
        on='year',
        how='inner'
    )

    if merged.empty:
        return pd.DataFrame({'year': [], 'roe': []})

    # 计算 ROE = 净利润 / 股东权益 * 100 (百分比)
    # 使用向量化操作
    roe = np.where(
        (merged['股东权益'] != 0) & (merged['股东权益'].notna()),
        merged['股东应占溢利'] / merged['股东权益'] * 100,
        np.nan
    )

    result = pd.DataFrame({
        'year': merged['year'],
        'roe': roe
    })

    return result


def calculate_hk_roic(income: pd.DataFrame, balance: pd.DataFrame) -> pd.DataFrame:
    """计算港股 ROIC

    ROIC = NOPAT / 投入资本
    - NOPAT = 股东应占溢利 + 融资成本（简化处理，忽略税后调整）
    - 投入资本 = 股东权益 + 短期贷款 + 长期贷款

    Args:
        income: 利润表 DataFrame，需包含 'year', '股东应占溢利', '融资成本' 列
        balance: 资产负债表 DataFrame，需包含 'year', '股东权益', '短期贷款', '长期贷款' 列

    Returns:
        包含 year 和 roic 列的 DataFrame
    """
    if income is None or income.empty:
        return pd.DataFrame({'year': [], 'roic': []})

    if balance is None or balance.empty:
        return pd.DataFrame({'year': income['year'], 'roic': [np.nan] * len(income)})

    # 提取需要的列
    income_cols = ['year', '股东应占溢利']
    if '融资成本' in income.columns:
        income_cols.append('融资成本')

    balance_cols = ['year', '股东权益']
    for col in ['短期贷款', '长期贷款']:
        if col in balance.columns:
            balance_cols.append(col)

    # 合并数据
    merged = income[income_cols].merge(
        balance[balance_cols],
        on='year',
        how='inner'
    )

    if merged.empty:
        return pd.DataFrame({'year': [], 'roic': []})

    # 计算 NOPAT（股东应占溢利 + 融资成本）
    nopat = merged['股东应占溢利'].copy()
    if '融资成本' in merged.columns:
        nopat = nopat + merged['融资成本'].fillna(0)

    # 计算投入资本（股东权益 + 短期贷款 + 长期贷款）
    invested_capital = merged['股东权益'].copy()
    for col in ['短期贷款', '长期贷款']:
        if col in merged.columns:
            invested_capital = invested_capital + merged[col].fillna(0)

    # 计算 ROIC = NOPAT / 投入资本 × 100
    roic = np.where(
        (invested_capital != 0) & (invested_capital.notna()),
        nopat / invested_capital * 100,
        np.nan
    )

    result = pd.DataFrame({
        'year': merged['year'],
        'roic': roic
    })

    return result


def calculate_hk_gross_profit_margin(income: pd.DataFrame) -> pd.DataFrame:
    """计算港股毛利率

    毛利率 = 毛利 / 营业收入

    Args:
        income: 利润表 DataFrame

    Returns:
        包含 year 和 gross_profit_margin 列的 DataFrame
    """
    if income is None or income.empty:
        return pd.DataFrame({'year': [], 'gross_profit_margin': []})

    revenue_col = '营业额'

    if revenue_col not in income.columns:
        return pd.DataFrame({'year': income['year'], 'gross_profit_margin': [np.nan] * len(income)})

    if 'gross_profit' in income.columns:
        gpm = np.where(
            (income[revenue_col] != 0) & (income[revenue_col].notna()),
            income['gross_profit'] / income[revenue_col] * 100,
            np.nan
        )
        return pd.DataFrame({
            'year': income['year'],
            'gross_profit_margin': gpm
        })
    elif '营运支出' in income.columns:
        gross_profit = income[revenue_col] - income['营运支出']
        gpm = np.where(
            (income[revenue_col] != 0) & (income[revenue_col].notna()),
            gross_profit / income[revenue_col] * 100,
            np.nan
        )
        return pd.DataFrame({
            'year': income['year'],
            'gross_profit_margin': gpm
        })

    return pd.DataFrame({'year': income['year'], 'gross_profit_margin': [np.nan] * len(income)})


def calculate_hk_net_profit_margin(income: pd.DataFrame) -> pd.DataFrame:
    """计算港股净利率

    净利率 = 股东应占溢利 / 营业收入

    Args:
        income: 利润表 DataFrame

    Returns:
        包含 year 和 net_profit_margin 列的 DataFrame
    """
    if income is None or income.empty:
        return pd.DataFrame({'year': [], 'net_profit_margin': []})

    revenue_col = '营业额'
    profit_col = '股东应占溢利'

    if revenue_col not in income.columns or profit_col not in income.columns:
        return pd.DataFrame({'year': income['year'], 'net_profit_margin': [np.nan] * len(income)})

    npm = np.where(
        (income[revenue_col] != 0) & (income[revenue_col].notna()),
        income[profit_col] / income[revenue_col] * 100,
        np.nan
    )

    return pd.DataFrame({
        'year': income['year'],
        'net_profit_margin': npm
    })
