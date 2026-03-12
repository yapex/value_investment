"""股票筛选过滤函数

提供常用的财务指标过滤模式，支持 DataFrame 输入输出。
"""
import pandas as pd


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

    return df[df['stock_code'].isin(results)].copy()
