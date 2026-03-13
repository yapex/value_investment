"""股票筛选过滤函数

提供常用的财务指标过滤模式，支持 DataFrame 输入输出。
"""
from __future__ import annotations

from typing import Optional
import pandas as pd


def filter_by_data_years(
    df: pd.DataFrame,
    required_years: int,
    field: Optional[str] = None
) -> pd.DataFrame:
    """过滤出数据年数满足要求的股票
    
    当扫描条件明确要求 N 年数据时（如"连续 5 年 ROE≥15%"），
    直接排除数据不足 N 年的股票。
    
    Args:
        df: 财务数据 DataFrame，必须包含 stock_code, end_date 列
        required_years: 要求的最少年数
        field: 可选，指定字段名。如果指定，只检查该字段有数据的年数
        
    Returns:
        过滤后的 DataFrame，只包含数据年数 >= required_years 的股票
        
    Example:
        >>> # 过滤出至少有 5 年数据的股票
        >>> df = filters.filter_by_data_years(financials, required_years=5)
        >>>
        >>> # 过滤出 ROE 字段至少有 5 年数据的股票
        >>> df = filters.filter_by_data_years(financials, required_years=5, field='roe')
    """
    if df.empty:
        return df
    
    df = df.copy()
    df['end_date'] = pd.to_datetime(df['end_date'])
    
    valid_codes = []
    
    for code, group in df.groupby('stock_code'):
        if field is not None:
            # 检查指定字段有数据且不为 NaN 的年数
            field_data = group[group[field].notna()]
            year_count = len(field_data['end_date'].dt.year.unique())
        else:
            # 检查总数据年数
            year_count = len(group['end_date'].dt.year.unique())
        
        if year_count >= required_years:
            valid_codes.append(code)
    
    result = df[df['stock_code'].isin(valid_codes)].copy()
    return result


def consecutive_years(
    df: pd.DataFrame,
    field: str,
    min_value: float,
    years: int = 5
) -> pd.DataFrame:
    """连续 N 年满足条件的股票

    筛选出最近 N 年中，指定字段每年都 >= min_value 的股票。

    Args:
        df: 财务数据 DataFrame，必须包含 stock_code, end_date 和 field 列
        field: 要检查的字段名（如 'roe', 'gross_margin'）
        min_value: 最小值阈值
        years: 考察年数

    Returns:
        符合条件的股票数据 DataFrame

    Example:
        >>> # 连续 5 年 ROE >= 15%
        >>> from value_investment.scanner import filters
        >>> result = filters.consecutive_years(financials, field='roe', min_value=15, years=5)
    """
    df = df.copy()
    df['end_date'] = pd.to_datetime(df['end_date'])

    results = []

    for code, group in df.groupby('stock_code'):
        recent = group.nlargest(years, 'end_date')

        if len(recent) < years:
            continue

        values = recent[field].astype(float)

        if (values >= min_value).all():
            results.append(code)

    result = df[df['stock_code'].isin(results)].copy()
    return result  # type: ignore[no-any-return]


def latest_year(
    df: pd.DataFrame,
    field: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> pd.DataFrame:
    """最近一年满足条件的股票

    Args:
        df: 财务数据 DataFrame
        field: 要检查的字段名
        min_value: 最小值（可选）
        max_value: 最大值（可选）

    Returns:
        符合条件的股票数据 DataFrame

    Example:
        >>> # 最近一年 ROE >= 15%
        >>> result = filters.latest_year(financials, field='roe', min_value=15)
        >>>
        >>> # 最近一年负债率 <= 60%
        >>> result = filters.latest_year(financials, field='debt_ratio', max_value=60)
    """
    df = df.copy()
    df['end_date'] = pd.to_datetime(df['end_date'])

    valid_codes = []

    for code, group in df.groupby('stock_code'):
        latest = group.nlargest(1, 'end_date')
        value = float(latest[[field]].iloc[0, 0])

        meets_min = (min_value is None) or (value >= min_value)
        meets_max = (max_value is None) or (value <= max_value)

        if meets_min and meets_max:
            valid_codes.append(code)

    mask = df['stock_code'].isin(valid_codes)
    result = df.loc[mask].copy()
    return result


def majority_years(
    df: pd.DataFrame,
    field: str,
    min_value: float,
    years: int = 5,
    required_years: Optional[int] = None,
    min_avg: Optional[float] = None
) -> pd.DataFrame:
    """多数年份满足条件的股票

    筛选出最近 N 年中，至少 M 年满足条件的股票。可选：同时要求平均值 >= 某值。

    Args:
        df: 财务数据 DataFrame，必须包含 stock_code, end_date 和 field 列
        field: 要检查的字段名（如 'roe', 'gross_margin'）
        min_value: 最小值阈值
        years: 考察年数，默认 5 年
        required_years: 满足条件的年数，默认取 floor(years/2) + 1（多数）
        min_avg: 可选，平均值最小值

    Returns:
        符合条件的股票数据 DataFrame

    Example:
        >>> # 5 年中至少 3 年 ROE >= 15%
        >>> result = filters.majority_years(financials, field='roe', min_value=15, years=5, required_years=3)
        >>>
        >>> # 5 年中至少 3 年 ROE >= 15%，且平均值 >= 15%
        >>> result = filters.majority_years(financials, field='roe', min_value=15, years=5, required_years=3, min_avg=15)
    """
    df = df.copy()
    df['end_date'] = pd.to_datetime(df['end_date'])

    # 默认：多数年份（超过一半）
    if required_years is None:
        required_years = years // 2 + 1

    results = []

    for code, group in df.groupby('stock_code'):
        recent = group.nlargest(years, 'end_date')

        if len(recent) < years:
            continue

        values = recent[field].astype(float)

        # 检查满足条件的年数
        years_met = (values >= min_value).sum()

        if years_met < required_years:
            continue

        # 检查平均值（如果指定）
        if min_avg is not None:
            avg_value = values.mean()
            if avg_value < min_avg:
                continue

        results.append(code)

    mask = df['stock_code'].isin(results)
    result = df.loc[mask].copy()
    return result  # type: ignore[no-any-return]
