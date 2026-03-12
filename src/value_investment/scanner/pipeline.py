"""Scanner Pipeline - 过滤器构建器

支持外部配置过滤条件，方便 Agent 动态构建筛选逻辑。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pandas as pd

from value_investment.scanner import filters

if TYPE_CHECKING:
    from value_investment.scanner.scanner import Scanner


class FilterBuilder:
    """过滤器构建器
    
    用于构建要应用的过滤条件，可外部配置后传入 Scanner。
    
    Example:
        >>> fb = FilterBuilder()
        >>> fb.add_filter('latest_year', field='roe', min_value=15)
        >>> fb.add_filter('consecutive_years', field='gross_profit_margin', min_value=30, years=5)
        >>> 
        >>> scanner = Scanner(market='A')
        >>> result = scanner.scan(stocks, fields=['roe'], filters=fb)
    """
    
    # 支持的过滤器类型
    SUPPORTED_FILTERS = {
        'latest_year': filters.latest_year,
        'consecutive_years': filters.consecutive_years,
        'majority_years': filters.majority_years,
    }
    
    def __init__(self):
        self._filters: list[Dict[str, Any]] = []
    
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
            filter_type = item.get('type')
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
    
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行所有过滤条件
        
        Args:
            df: 输入的财务数据 DataFrame
            
        Returns:
            过滤后的 DataFrame
        """
        result = df
        
        for filter_config in self._filters:
            filter_type = filter_config['type']
            params = filter_config['params']
            
            filter_func = self.SUPPORTED_FILTERS[filter_type]
            result = filter_func(result, **params)
        
        return result
    
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
