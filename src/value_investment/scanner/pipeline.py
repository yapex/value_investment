"""Scanner Pipeline - 过滤器构建器

支持外部配置过滤条件，方便 Agent 动态构建筛选逻辑。
支持常用指标独立缓存和优先执行优化。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING, cast

import pandas as pd

from value_investment.scanner import filters
from value_investment.scanner.priority_filters import (
    classify_conditions,
    generate_cache_key,
    generate_non_priority_cache_key,
    compute_context_hash,
    is_priority_filter,
)

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache
    from value_investment.scanner.scanner import Scanner


class FilterBuilder:
    """过滤器构建器

    用于构建要应用的过滤条件，可外部配置后传入 Scanner。
    支持常用指标独立缓存和优先执行优化。

    Example:
        >>> fb = FilterBuilder()
        >>> fb.add_filter('latest_year', field='roe', min_value=15)
        >>> fb.add_filter('consecutive_years', field='gross_profit_margin', min_value=30, years=5)
        >>>
        >>> scanner = Scanner(market='A')
        >>> result = scanner.scan(stocks, fields=['roe'], filters=fb)
    """

    # 支持的过滤器类型
    SUPPORTED_FILTERS: dict = {
        'latest_year': filters.latest_year,
        'consecutive_years': filters.consecutive_years,
        'majority_years': filters.majority_years,
    }

    def __init__(self, cache: Optional["SmartCache"] = None, market: str = 'A'):
        """初始化 FilterBuilder
        
        Args:
            cache: 缓存实例，用于存储过滤结果
            market: 市场标识（A/HK），用于缓存键生成
        """
        self._filters: list[Dict[str, Any]] = []
        self._cache = cache
        self._market = market

    def add_filter(
        self,
        filter_type: str,
        **kwargs: Any
    ) -> "FilterBuilder":
        """添加一个过滤条件

        Args:
            filter_type: 过滤器类型，可选值：
                - 'latest_year': 最近一年满足条件
                - 'consecutive_years': 连续 N 年满足条件
                - 'majority_years': N 年中至少 M 年满足条件
            **kwargs: 过滤器参数

        Returns:
            self

        Example:
            >>> fb.add_filter('latest_year', field='roe', min_value=15)
            >>> fb.add_filter('consecutive_years', field='gross_profit_margin', min_value=30, years=5)
        """
        if filter_type not in self.SUPPORTED_FILTERS:
            raise ValueError(
                f"Unknown filter type: {filter_type}. "
                f"Supported: {list(self.SUPPORTED_FILTERS.keys())}"
            )

        self._filters.append({
            'type': filter_type,
            'params': kwargs
        })

        return self

    def add_filters_from_config(self, config: List[Dict[str, Any]]) -> "FilterBuilder":
        """从配置列表批量添加过滤条件

        Args:
            config: 配置列表，每个元素包含 type 和 params

        Example:
            >>> config = [
            ...     {'type': 'latest_year', 'params': {'field': 'roe', 'min_value': 15}},
            ...     {'type': 'consecutive_years', 'params': {'field': 'gross_profit_margin', 'min_value': 30}}
            ... ]
            >>> fb.add_filters_from_config(config)
        """
        for item in config:
            filter_type = item.get('type', '')
            params = item.get('params', {})
            self.add_filter(filter_type, **params)

        return self

    def add_filters_from_json(self, json_str: str) -> "FilterBuilder":
        """从 JSON 字符串添加过滤条件

        Args:
            json_str: JSON 格式的过滤配置

        Example:
            >>> json_str = '[{"type": "latest_year", "params": {"field": "roe", "min_value": 15}}]'
            >>> fb.add_filters_from_json(json_str)
        """
        import json
        config = json.loads(json_str)
        return self.add_filters_from_config(config)

    def execute(self, df: pd.DataFrame, use_cache: bool = True) -> pd.DataFrame:
        """执行所有过滤条件
        
        在执行过滤前，会先检查数据年数要求，排除数据不足的股票。
        支持常用指标优先执行和独立缓存优化。
        
        Args:
            df: 输入的财务数据 DataFrame
            use_cache: 是否使用缓存，默认 True
            
        Returns:
            过滤后的 DataFrame
        """
        if df.empty:
            return df
        
        # 如果没有缓存实例，退化为普通执行
        if self._cache is None or not use_cache:
            return self._execute_without_cache(df)
        
        # 使用缓存优化执行
        return self._execute_with_cache(df)
    
    def _execute_without_cache(self, df: pd.DataFrame) -> pd.DataFrame:
        """无缓存执行（兼容旧逻辑）"""
        result = df.copy()
        
        # 第一步：收集所有过滤条件的年数要求
        required_years = 0
        for filter_config in self._filters:
            filter_type = filter_config['type']
            params = filter_config['params']
            years = params.get('years', 0)
            if years > required_years:
                required_years = years
        
        # 第二步：如果有年数要求，先过滤掉数据不足的股票
        if required_years > 0:
            result = filters.filter_by_data_years(result, required_years)
            
            # 如果过滤后没有数据，直接返回
            if result.empty:
                return result
        
        # 第三步：执行各个过滤条件
        for filter_config in self._filters:
            filter_type = filter_config['type']
            params = filter_config['params']
            
            filter_func = self.SUPPORTED_FILTERS[filter_type]
            result = filter_func(result, **params)
            
            # 如果中途没有数据了，提前返回
            if result.empty:
                return result
        
        return result
    
    def _execute_with_cache(self, df: pd.DataFrame) -> pd.DataFrame:
        """使用缓存优化执行
        
        执行策略：
        1. 分类条件：常用指标（priority）vs 非常用指标（non-priority）
        2. 优先执行常用指标，使用独立缓存（可跨场景复用）
        3. 在缩小的数据集上执行非常用指标，带上下文 hash 缓存
        """
        if df.empty:
            return df
        
        # 第一步：分类条件
        classified = classify_conditions(self._filters)
        priority_conditions = classified['priority']
        non_priority_conditions = classified['non_priority']
        
        result = df.copy()
        
        # 第二步：收集所有过滤条件的年数要求
        required_years = 0
        for filter_config in self._filters:
            filter_type = filter_config['type']
            params = filter_config['params']
            years = params.get('years', 0)
            if years > required_years:
                required_years = years
        
        # 第三步：如果有年数要求，先过滤掉数据不足的股票
        if required_years > 0:
            result = filters.filter_by_data_years(result, required_years)
            
            if result.empty:
                return result
        
        # 第四步：优先执行常用指标（独立缓存）
        if priority_conditions:
            result = self._execute_priority_filters(result, priority_conditions)
            
            if result.empty:
                return result
        
        # 第五步：执行非常用指标（带上下文 hash 缓存）
        if non_priority_conditions:
            # 计算前置条件的上下文 hash
            context_hash = compute_context_hash(priority_conditions)
            result = self._execute_non_priority_filters(
                result, non_priority_conditions, context_hash
            )
        
        return result
    
    def _execute_priority_filters(
        self, 
        df: pd.DataFrame, 
        conditions: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """执行常用指标过滤（独立缓存）"""
        result = df.copy()
        
        for condition in conditions:
            filter_type = condition['type']
            params = condition['params']
            field = params.get('field', '')
            years = params.get('years', 1)
            
            # 确定阈值（min_value 或 max_value）
            value = params.get('min_value') or params.get('max_value', 0)
            
            # 生成缓存键
            cache_key = generate_cache_key(
                filter_type, field, years, value, self._market
            )
            
            # 尝试从缓存获取
            cached_result = self._cache.get(cache_key)
            if cached_result is not None and isinstance(cached_result, pd.DataFrame):
                # 缓存命中：过滤出在缓存结果中的股票
                cached_codes = set(cached_result['stock_code'].unique())
                result = result[result['stock_code'].isin(list(cached_codes))]
                continue
            
            # 缓存未命中：执行过滤
            filter_func = self.SUPPORTED_FILTERS[filter_type]
            filtered = cast(pd.DataFrame, filter_func(result, **params))  # type: ignore[assignment]
            
            # 缓存结果（保存满足条件的股票代码）
            if not filtered.empty:
                codes_df = filtered[['stock_code']].drop_duplicates()
                self._cache.set(cache_key, codes_df, ttl=604800)  # 7 天 TTL
            
            result = filtered
            
            if result.empty:
                return result
        
        return result  # type: ignore[return-value]
    
    def _execute_non_priority_filters(
        self, 
        df: pd.DataFrame, 
        conditions: List[Dict[str, Any]],
        context_hash: str
    ) -> pd.DataFrame:
        """执行非常用指标过滤（带上下文 hash 缓存）"""
        result = df.copy()
        
        for condition in conditions:
            filter_type = condition['type']
            params = condition['params']
            field = params.get('field', '')
            years = params.get('years', 1)
            value = params.get('min_value') or params.get('max_value', 0)
            
            # 生成带上下文 hash 的缓存键
            cache_key = generate_non_priority_cache_key(
                filter_type, field, years, value, context_hash, self._market
            )
            
            # 尝试从缓存获取
            cached_result = self._cache.get(cache_key)
            if cached_result is not None and isinstance(cached_result, pd.DataFrame):
                cached_codes = set(cached_result['stock_code'].unique())
                result = result[result['stock_code'].isin(list(cached_codes))]
                continue
            
            # 缓存未命中：执行过滤
            filter_func = self.SUPPORTED_FILTERS[filter_type]
            filtered = cast(pd.DataFrame, filter_func(result, **params))  # type: ignore[assignment]
            
            # 缓存结果
            if not filtered.empty:
                codes_df = filtered[['stock_code']].drop_duplicates()
                self._cache.set(cache_key, codes_df, ttl=86400)  # 1 天 TTL
            
            result = filtered
            
            if result.empty:
                return result
        
        return result  # type: ignore[return-value]

    def __len__(self) -> int:
        """返回过滤条件数量"""
        return len(self._filters)

    def __repr__(self) -> str:
        return f"FilterBuilder(filters={self._filters})"

    def to_config(self) -> List[Dict[str, Any]]:
        """导出为配置列表（可用于序列化）"""
        return self._filters.copy()

    def to_json(self) -> str:
        """导出为 JSON 字符串"""
        import json
        return json.dumps(self._filters, ensure_ascii=False)


# 便捷函数
def create_filter_builder(config: List[Dict[str, Any]]) -> FilterBuilder:
    """从配置列表创建 FilterBuilder 的便捷函数

    Example:
        >>> config = [
        ...     {'type': 'latest_year', 'params': {'field': 'roe', 'min_value': 15}},
        ... ]
        >>> fb = create_filter_builder(config)
    """
    return FilterBuilder().add_filters_from_config(config)
