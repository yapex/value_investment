"""指标计算辅助工具"""
from typing import Set, cast

import pandas as pd

from src.value_investment.data.mapper import (
    CORE_FIELD_MAPPING,
    MappedFieldMissingError,
    UnmappedFieldError,
)


def get_registered_fields() -> Set[str]:
    """获取所有已注册的标准字段名"""
    return set(CORE_FIELD_MAPPING.keys())


def require_field(df: pd.DataFrame, field: str) -> pd.Series:
    """安全访问字段，提供明确的错误信息
    
    Args:
        df: DataFrame（应该只包含已映射字段）
        field: 标准字段名
    
    Returns:
        字段对应的 Series
    
    Raises:
        MappedFieldMissingError: 字段已注册但数据中不存在
        UnmappedFieldError: 字段未注册
    """
    if field not in df.columns:
        registered = get_registered_fields()
        if field in registered:
            raise MappedFieldMissingError(
                f"'{field}' 已注册但数据中不存在\n"
                f"可能原因：\n"
                f"  1) Provider 未获取该字段\n"
                f"  2) 原始字段名与映射不匹配"
            )
        else:
            raise UnmappedFieldError(
                f"'{field}' 未注册\n"
                f"请先在 CORE_FIELD_MAPPING 或 field_mappings 中添加映射"
            )
    return cast(pd.Series, df[field])
