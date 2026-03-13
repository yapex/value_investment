"""优先级过滤器配置 - 常用指标独立缓存优化

定义常用指标列表和分类逻辑，支持缓存复用和优先执行。
"""
from __future__ import annotations

from typing import Any, Dict, List, Set


# 常用指标配置
# 这些指标在多个过滤条件中频繁使用，支持独立缓存和跨场景复用
PRIORITY_FILTERS: Dict[str, Set[str]] = {
    # 连续 N 年满足条件的指标
    'consecutive_years': {
        'roe',              # 净资产收益率
        'gross_profit_margin',  # 毛利率
        'roic',             # 投入资本回报率
        'net_profit_margin',    # 净利率
    },
    # 最近一年满足条件的指标
    'latest_year': {
        'roe',
        'pe_ratio',         # 市盈率
        'gross_profit_margin',
        'roic',
    },
    # N 年中至少 M 年满足条件的指标
    'majority_years': {
        'roe',
        'gross_profit_margin',
        'roic',
    },
}


def get_priority_fields(filter_type: str) -> Set[str]:
    """获取指定过滤类型的常用指标集合
    
    Args:
        filter_type: 过滤类型，如 'consecutive_years', 'latest_year'
    
    Returns:
        常用指标集合
    """
    return PRIORITY_FILTERS.get(filter_type, set())


def is_priority_filter(filter_type: str, field: str) -> bool:
    """判断是否为常用指标过滤条件
    
    Args:
        filter_type: 过滤类型
        field: 指标字段名
    
    Returns:
        是否为常用指标
    """
    priority_fields = get_priority_fields(filter_type)
    return field.lower() in priority_fields


def classify_conditions(conditions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """将过滤条件分类为常用指标和非常用指标
    
    Args:
        conditions: 过滤条件列表，每个元素包含 type 和 params
    
    Returns:
        分类后的字典，包含 'priority' 和 'non_priority' 两个键
    
    Example:
        >>> conditions = [
        ...     {'type': 'consecutive_years', 'params': {'field': 'roe', 'min_value': 15}},
        ...     {'type': 'latest_year', 'params': {'field': 'pe_ratio', 'max_value': 20}},
        ...     {'type': 'consecutive_years', 'params': {'field': 'custom_field', 'min_value': 10}},
        ... ]
        >>> result = classify_conditions(conditions)
        >>> len(result['priority'])  # 2 (roe 和 pe_ratio)
        >>> len(result['non_priority'])  # 1 (custom_field)
    """
    priority = []
    non_priority = []
    
    for condition in conditions:
        filter_type = condition.get('type', '')
        params = condition.get('params', {})
        field = params.get('field', '')
        
        if is_priority_filter(filter_type, field):
            priority.append(condition)
        else:
            non_priority.append(condition)
    
    return {
        'priority': priority,
        'non_priority': non_priority,
    }


def generate_cache_key(
    filter_type: str,
    field: str,
    years: int,
    value: Any,
    market: str = 'A'
) -> str:
    """为常用指标生成独立的缓存键
    
    缓存键格式：filter_{type}_{field}_{years}_{value}
    
    Args:
        filter_type: 过滤类型
        field: 指标字段名
        years: 年数要求
        value: 阈值（min_value 或 max_value）
        market: 市场标识
    
    Returns:
        缓存键字符串
    
    Example:
        >>> generate_cache_key('consecutive_years', 'roe', 5, 15)
        'filter_consecutive_years_roe_5_15'
        >>> generate_cache_key('latest_year', 'pe_ratio', 1, 20)
        'filter_latest_year_pe_ratio_1_20'
    """
    return f"filter_{filter_type}_{field}_{years}_{value}_{market}"


def generate_non_priority_cache_key(
    filter_type: str,
    field: str,
    years: int,
    value: Any,
    context_hash: str,
    market: str = 'A'
) -> str:
    """为非常用指标生成带上下文 hash 的缓存键
    
    避免缓存污染，确保相同指标在不同上下文中有独立的缓存。
    
    Args:
        filter_type: 过滤类型
        field: 指标字段名
        years: 年数要求
        value: 阈值
        context_hash: 上下文 hash（基于前置过滤条件生成）
        market: 市场标识
    
    Returns:
        缓存键字符串
    
    Example:
        >>> generate_non_priority_cache_key('consecutive_years', 'custom_field', 5, 10, 'abc123')
        'filter_nopriority_consecutive_years_custom_field_5_10_abc123'
    """
    return f"filter_nopriority_{filter_type}_{field}_{years}_{value}_{context_hash}_{market}"


def compute_context_hash(conditions: List[Dict[str, Any]]) -> str:
    """计算过滤条件上下文的 hash
    
    用于非常用指标缓存键，确保不同上下文有不同的缓存。
    
    Args:
        conditions: 前置过滤条件列表
    
    Returns:
        8 位十六进制 hash 字符串
    """
    import hashlib
    
    # 将条件序列化为稳定字符串
    import json
    # 排序确保相同条件生成相同 hash
    sorted_conditions = sorted(
        conditions,
        key=lambda x: (x.get('type', ''), str(x.get('params', {})))
    )
    context_str = json.dumps(sorted_conditions, sort_keys=True)
    
    # 生成 hash
    hash_obj = hashlib.md5(context_str.encode('utf-8'))
    return hash_obj.hexdigest()[:8]
