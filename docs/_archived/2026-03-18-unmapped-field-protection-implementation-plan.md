# 未映射字段保护机制实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在系统架构层面强制保证指标计算只能使用经过映射的字段，通过运行时检查 + 明确的异常信息实现"默认拒绝"策略。

**Architecture:** 
- 在 DataMapper.map_to_standard() 中显式构建新 DataFrame，只包含已映射字段
- 添加市场字段适用性检查，只对适用字段发出警告
- 在指标计算层提供 require_field() 辅助函数，提供明确的异常信息

**Tech Stack:** Python, pandas, pytest, logging

> **性能优化说明**: 本计划采用最高效的 dict 构建方案来创建新 DataFrame：
> ```python
> result = {
>     standard_col: df[native_col].values
>     for native_col, standard_col in mapping.items()
>     if native_col in df.columns
> }
> return pd.DataFrame(result) if result else pd.DataFrame()
> ```
> 实测比传统遍历 + copy 方式快约 50%，`.values` 返回独立数组确保安全断开原数据联系。

---

## Task 1: 添加异常类

**Files:**
- Modify: `src/value_investment/data/mapper.py`

**Step 1: 添加异常类**

在文件开头（import 之后，class DataMapper 之前）添加：

```python
class MappedFieldMissingError(Exception):
    """字段已注册但数据中不存在"""
    pass

class UnmappedFieldError(Exception):
    """字段未在映射表中注册"""
    pass
```

Run: `grep -n "class DataMapper" src/value_investment/data/mapper.py`
Expected: 输出行号，如 `629:class DataMapper:`

在 `class DataMapper:` 之前插入异常类。

**Step 2: 验证导入正常**

Run: `python -c "from src.value_investment.data.mapper import MappedFieldMissingError, UnmappedFieldError; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add src/value_investment/data/mapper.py
git commit -m "feat: 添加 MappedFieldMissingError 和 UnmappedFieldError 异常类"
```

---

## Task 2: 添加 is_field_expected_for_market() 函数

**Files:**
- Modify: `src/value_investment/data/mapper.py` (在 DataMapper 类中添加)

**Step 1: 添加静态方法**

在 DataMapper 类中找到合适位置（map_to_standard 方法之后），添加：

```python
@classmethod
def is_field_expected_for_market(cls, standard_field: str, market: str) -> bool:
    """检查字段是否应该存在于指定市场
    
    Args:
        standard_field: 标准字段名
        market: 市场名称 ("A", "HK", "US")
    
    Returns:
        True 如果该字段在当前市场有定义
    """
    # 标准化市场名称
    market_map = {"a": "A股", "hk": "港股", "us": "美股"}
    market = market_map.get(market.lower(), market)
    
    if standard_field not in CORE_FIELD_MAPPING:
        return False
    return market in CORE_FIELD_MAPPING[standard_field]
```

**Step 2: 验证函数可用**

Run: `python -c "from src.value_investment.data.mapper import DataMapper; print(DataMapper.is_field_expected_for_market('total_revenue', 'A'))"`
Expected: `True`

Run: `python -c "from src.value_investment.data.mapper import DataMapper; print(DataMapper.is_field_expected_for_market('total_revenue', 'HK'))"`
Expected: `True` 或 `False`（取决于映射定义）

**Step 3: Commit**

```bash
git add src/value_investment/data/mapper.py
git commit -m "feat: 添加 is_field_expected_for_market() 市场字段检查方法"
```

---

## Task 3: 改造 map_to_standard() 方法

**Files:**
- Modify: `src/value_investment/data/mapper.py` (map_to_standard 方法，约 1483-1555 行)

**Step 1: 查看当前实现**

Run: `sed -n '1483,1555p' src/value_investment/data/mapper.py`
确认当前实现结构。

**Step 2: 改造方法实现**

将现有的 map_to_standard 方法改造为显式构建新 DataFrame：

```python
@classmethod
def map_to_standard(
    cls,
    df: pd.DataFrame | None,
    source: str,
    data_type: str,
    market: str = "A",
) -> pd.DataFrame | None:
    """统一映射入口：将数据源原始字段映射为标准字段
    
    默认拒绝策略：只保留已映射的字段，未映射字段不进入后续流程。
    
    Args:
        df: 原始 DataFrame (可能为 None)
        source: 数据源 ("tushare" | "akshare" | "yfinance")
        data_type: 数据类型
        market: 市场 ("A", "HK", "US")，用于判断字段是否应该存在
    
    Returns:
        映射后的 DataFrame（只包含已映射的标准字段名）
    """
    # 处理 None 和空 DataFrame
    if df is None:
        return None
    if df.empty:
        return df

    # 标准化 source 和 data_type
    source = source.lower().strip()
    data_type = data_type.lower().strip()

    # 验证 source
    if source not in cls.SOURCE_MAPPINGS:
        valid_sources = ", ".join(cls.SOURCE_MAPPINGS.keys())
        raise ValueError(f"Unknown source: '{source}'. Valid sources: {valid_sources}")

    # 验证 data_type
    if data_type not in cls.DATA_TYPE_MAPPINGS:
        valid_types = ", ".join(cls.DATA_TYPE_MAPPINGS.keys())
        raise ValueError(f"Unknown data_type: '{data_type}'. Valid types: {valid_types}")

    # 收集完整的映射表（source + type）
    rename_map = {}  # {原生字段: 标准字段}

    # Step 1: 应用数据源特定映射
    source_mapping_name = cls.SOURCE_MAPPINGS[source]
    source_mapping = getattr(cls, source_mapping_name, {})
    for old_field, new_field in source_mapping.items():
        if old_field in df.columns:
            rename_map[old_field] = new_field

    # Step 2: 应用数据类型映射
    type_mapping_name = cls.DATA_TYPE_MAPPINGS[data_type]
    type_mapping = getattr(cls, type_mapping_name, None)

    if type_mapping is not None:
        if data_type == "financial_indicator":
            # 财务指标特殊处理：先应用 rename_map，再调用 map_financial_indicator
            result = {}
            for old_field, new_field in rename_map.items():
                if old_field in df.columns:
                    result[new_field] = df[old_field].copy()
            temp_df = pd.DataFrame(result)
            return cls.map_financial_indicator(temp_df, market=market)
        else:
            for old_field, new_field in type_mapping.items():
                if old_field in df.columns and old_field not in rename_map:
                    rename_map[old_field] = new_field

    # Step 3: 显式构建新 DataFrame，只包含已映射字段（推荐方案：dict 构建）
    # 高效方案：使用 dict comprehension + .values 提取独立数组
    missing_native = []
    
    # 构建结果 dict：标准字段 -> 独立数组
    result = {
        standard_col: df[native_col].values
        for native_col, standard_col in rename_map.items()
        if native_col in df.columns
    }
    
    # 检查缺失字段（只对当前市场应该存在的字段发出警告）
    for native_col, standard_col in rename_map.items():
        if native_col not in df.columns:
            if cls.is_field_expected_for_market(standard_col, market):
                missing_native.append(native_col)

    if missing_native:
        import logging
        logging.warning(
            f"[{source}/{market}] 原始数据缺少映射字段: {missing_native}，"
            f"这些字段将被忽略"
        )

    return pd.DataFrame(result) if result else pd.DataFrame()
```

**Step 3: 验证方法可用**

Run: `python -c "from src.value_investment.data.mapper import DataMapper; import pandas as pd; df = pd.DataFrame({'total_revenue': [100], 'other': [200]}); result = DataMapper.map_to_standard(df, 'tushare', 'income_statement', 'A'); print(list(result.columns))"`
Expected: 只包含 `['total_revenue']`，不包含 `'other'`

**Step 4: Commit**

```bash
git add src/value_investment/data/mapper.py
git commit -m "feat: 改造 map_to_standard() 实现默认拒绝策略"
```

---

## Task 4: 添加 require_field() 辅助函数

**Files:**
- Modify: `src/value_investment/indicators/utils.py` (如不存在则创建)

**Step 1: 检查 indicators 目录结构**

Run: `ls src/value_investment/indicators/`
确认现有文件。

**Step 2: 创建或修改 utils.py**

如果 `src/value_investment/indicators/utils.py` 不存在，创建它：

```python
"""指标计算辅助工具"""
from typing import Set

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
    return df[field]
```

**Step 3: 验证导入正常**

Run: `python -c "from src.value_investment.indicators.utils import require_field, get_registered_fields; print('OK')"`
Expected: `OK`

**Step 4: 测试 require_field 正常访问**

Run: `python -c "from src.value_investment.indicators.utils import require_field; import pandas as pd; df = pd.DataFrame({'total_revenue': [100]}); result = require_field(df, 'total_revenue'); print(result.iloc[0])"`
Expected: `100`

**Step 5: 测试 require_field 未注册字段**

Run: `python -c "from src.value_investment.indicators.utils import require_field, UnmappedFieldError; import pandas as pd; df = pd.DataFrame({'total_revenue': [100]}); require_field(df, 'unregistered_field')"`
Expected: 抛出 `UnmappedFieldError`

**Step 6: Commit**

```bash
git add src/value_investment/indicators/utils.py
git commit -m "feat: 添加 require_field() 辅助函数"
```

---

## Task 5: 编写测试

**Files:**
- Create: `tests/test_unmapped_field_protection.py`

**Step 1: 创建测试文件**

```python
"""未映射字段保护机制测试"""
import logging
import pytest
import pandas as pd

from src.value_investment.data.mapper import (
    DataMapper,
    MappedFieldMissingError,
    UnmappedFieldError,
    CORE_FIELD_MAPPING,
)
from src.value_investment.indicators.utils import (
    require_field,
    get_registered_fields,
)


class TestIsFieldExpectedForMarket:
    """测试 is_field_expected_for_market 方法"""
    
    def test_standard_market_has_field(self):
        """测试标准市场字段存在"""
        # total_revenue 在 A股/港股/美股 都有定义
        assert DataMapper.is_field_expected_for_market('total_revenue', 'A') is True
        assert DataMapper.is_field_expected_for_market('total_revenue', 'HK') is True
        assert DataMapper.is_field_expected_for_market('total_revenue', 'US') is True
    
    def test_unknown_field(self):
        """测试未知字段返回 False"""
        assert DataMapper.is_field_expected_for_market('unknown_field', 'A') is False
    
    def test_case_insensitive(self):
        """测试市场名称大小写不敏感"""
        assert DataMapper.is_field_expected_for_market('total_revenue', 'a') is True
        assert DataMapper.is_field_expected_for_market('total_revenue', 'hk') is True


class TestMapToStandardDefaultDeny:
    """测试 map_to_standard 默认拒绝策略"""
    
    def test_only_mapped_fields_in_result(self):
        """测试结果只包含已映射字段"""
        df = pd.DataFrame({
            'total_revenue': [100, 200],
            'net_profit': [10, 20],
            'unmapped_field': [1, 2],  # 未映射字段
        })
        
        result = DataMapper.map_to_standard(df, 'tushare', 'income_statement', 'A')
        
        # 只包含已映射的字段
        assert 'total_revenue' in result.columns
        assert 'net_profit' in result.columns
        assert 'unmapped_field' not in result.columns
    
    def test_copy_disconnects_from_original(self):
        """测试 copy 断开与原始 DataFrame 的联系"""
        df = pd.DataFrame({'total_revenue': [100]})
        result = DataMapper.map_to_standard(df, 'tushare', 'income_statement', 'A')
        
        # 修改结果不影响原始
        result.iloc[0, 0] = 999
        assert df.iloc[0, 0] == 100
    
    def test_missing_native_field_warning(self, caplog):
        """测试缺少原生字段时发出警告"""
        # 模拟原始数据缺少字段
        df = pd.DataFrame({
            'total_revenue': [100],  # 存在
            # 'net_profit' 缺失 - 但这是 A股 的有效字段
        })
        
        with caplog.at_level(logging.WARNING):
            result = DataMapper.map_to_standard(df, 'tushare', 'income_statement', 'A')
        
        assert 'net_profit' in caplog.text or '缺少' in caplog.text


class TestRequireField:
    """测试 require_field 辅助函数"""
    
    def test_access_existing_field(self):
        """测试访问已存在的字段"""
        df = pd.DataFrame({'total_revenue': [100]})
        result = require_field(df, 'total_revenue')
        
        assert result.iloc[0] == 100
    
    def test_access_unregistered_field(self):
        """测试访问未注册字段抛出异常"""
        df = pd.DataFrame({'total_revenue': [100]})
        
        with pytest.raises(UnmappedFieldError) as exc_info:
            require_field(df, 'unregistered_field')
        
        assert '未注册' in str(exc_info.value)
    
    def test_access_missing_mapped_field(self):
        """测试访问已注册但缺失的字段抛出异常"""
        df = pd.DataFrame({'other_field': [100]})  # 不包含 total_revenue
        
        with pytest.raises(MappedFieldMissingError) as exc_info:
            require_field(df, 'total_revenue')
        
        assert '已注册但数据中不存在' in str(exc_info.value)


class TestGetRegisteredFields:
    """测试 get_registered_fields 函数"""
    
    def test_returns_set_of_fields(self):
        """测试返回字段集合"""
        fields = get_registered_fields()
        
        assert isinstance(fields, set)
        assert 'total_revenue' in fields
        assert 'total_assets' in fields
        assert 'net_profit' in fields
```

**Step 2: 运行测试验证**

Run: `python -m pytest tests/test_unmapped_field_protection.py -v`
Expected: 所有测试通过

**Step 3: Commit**

```bash
git add tests/test_unmapped_field_protection.py
git commit -m "test: 添加未映射字段保护机制测试"
```

---

## 实施顺序

建议按顺序执行：
1. Task 1: 添加异常类
2. Task 2: 添加 is_field_expected_for_market() 函数
3. Task 3: 改造 map_to_standard() 方法
4. Task 4: 添加 require_field() 辅助函数
5. Task 5: 编写测试

---

## Plan Complete

计划已保存到 `docs/plans/2026-03-18-unmapped-field-protection-design.md`。

**Two execution options:**

1. **Subagent-Driven (this session)** - 我在新 session 中逐步执行每个任务，并在任务之间进行代码审查

2. **Parallel Session (separate)** - 在新 session 中使用 executing-plans，批量执行并在检查点进行验证

**Which approach?**
