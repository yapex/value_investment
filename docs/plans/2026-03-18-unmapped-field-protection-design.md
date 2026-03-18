# 未映射字段保护机制设计

## 问题背景

当前系统中，Provider 返回的 DataFrame 可能包含未映射的原始字段，这些字段可能被下游代码（指标计算层）直接访问，导致：
1. 字段命名不一致（不同市场/数据源使用不同名称）
2. 难以追踪哪些字段是"官方支持"的
3. 数据质量无法保证

## 设计目标

通过系统架构层面的硬规则，确保：
- **核心计算框架只能使用经过映射的字段**
- 不依赖开发者自觉，而是通过运行时机制强制保证

## 核心策略

**默认拒绝（Default Deny）**：Provider 返回的 DataFrame 只包含已映射的字段，未映射字段不进入后续流程。

## 实现方案

### 1. DataMapper.map_to_standard() 改造

```python
def map_to_standard(
    df: pd.DataFrame, 
    mapping: dict[str, str], 
    market: str
) -> pd.DataFrame:
    """映射字段名，只保留已映射的字段
    
    Args:
        df: 原始 DataFrame
        mapping: {原生字段名: 标准字段名}
        market: 当前市场（用于判断字段是否应该存在）
    
    Returns:
        只包含已映射字段的新 DataFrame
    """
    # 高效方案：dict comprehension + .values 提取独立数组
    result = {
        standard_col: df[native_col].values
        for native_col, standard_col in mapping.items()
        if native_col in df.columns
    }
    
    # 检查缺失字段（只对当前市场应该存在的字段发出警告）
    missing_native = []
    for native_col, standard_col in mapping.items():
        if native_col not in df.columns:
            if is_field_expected_for_market(standard_col, market):
                missing_native.append(native_col)
    
    if missing_native:
        logger.warning(
            f"[{market}] 原始数据缺少映射字段: {missing_native}，"
            f"这些字段将被忽略"
        )
    
    return pd.DataFrame(result) if result else pd.DataFrame()
```

**关键点**：
- 使用 dict comprehension + `.values` 高效构建新 DataFrame（比 copy 快 50%）
- `.values` 返回独立数组，自然断开与原数据的联系
- 只复制映射表中定义的字段
- 警告逻辑考虑市场差异（某些字段只适用于特定市场）

### 2. 指标计算层辅助函数

```python
class MappedFieldMissingError(Exception):
    """字段已注册但数据中不存在"""
    pass

class UnmappedFieldError(Exception):
    """字段未在映射表中注册"""
    pass

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

### 3. 市场字段适用性检查

```python
def is_field_expected_for_market(standard_field: str, market: str) -> bool:
    """检查字段是否应该存在于指定市场
    
    Args:
        standard_field: 标准字段名
        market: 市场名称（"A股", "港股", "美股"）
    
    Returns:
        True 如果该字段在当前市场有定义
    """
    if standard_field not in CORE_FIELD_MAPPING:
        return False
    return market in CORE_FIELD_MAPPING[standard_field]
```

## 异常处理策略

| 层级 | 场景 | 处理方式 | 原因 |
|------|------|---------|------|
| Provider | 原始数据缺少映射字段（当前市场适用） | 警告 + 继续 | 数据源可能不完整，但不影响其他字段使用 |
| Provider | 原始数据缺少映射字段（当前市场不适用） | 不警告 | 字段本来就不适用于该市场 |
| 指标计算 | 访问已注册但缺失的字段 | 抛 `MappedFieldMissingError` | 需要检查 Provider 或映射配置 |
| 指标计算 | 访问未注册的字段 | 抛 `UnmappedFieldError` | 需要先添加映射 |

## 数据流

```
Provider 获取原始数据（可能包含未映射字段）
        ↓
map_to_standard(market=当前市场)
  ├── 检查原始字段 vs 映射表
  ├── 只对当前市场适用的字段发出警告
  └── 只复制已映射字段 → 返回新 DataFrame
        ↓
API 层（只包含已映射字段）
        ↓
指标计算层
  └── require_field() 访问字段
        ├── 字段存在 → 正常返回
        └── 字段不存在 → 明确的异常信息
```

## 保障机制

1. **运行时拦截**：未映射字段不存在于 DataFrame，访问时必然失败
2. **明确的异常**：区分"未注册"和"已注册但缺失"两种情况，便于排查
3. **智能警告**：只对当前市场适用的字段发出警告，减少噪音
4. **测试覆盖**：TDD 确保所有代码路径被验证
5. **缓存友好**：copy 开销只发生一次，后续使用缓存数据

## 影响范围

### 需要修改的文件

1. `src/value_investment/data/mapper.py`
   - 改造 `map_to_standard()` 方法
   - 添加 `is_field_expected_for_market()` 函数
   - 添加 `MappedFieldMissingError`、`UnmappedFieldError` 异常类

2. `src/value_investment/indicators/` 目录
   - 添加 `require_field()` 辅助函数
   - 可选：逐步迁移指标计算代码使用 `require_field()`

### 向后兼容

- 现有代码直接访问 `df['field']` 仍然可以工作
- 如果字段存在，行为不变
- 如果字段不存在，`KeyError` 仍然会抛出
- 使用 `require_field()` 可以获得更明确的错误信息

## 后续优化（可选）

1. **静态类型提示**：为 `require_field()` 添加重载，支持 IDE 自动补全
2. **字段注册表 API**：提供查询接口，方便开发者查看所有可用字段
3. **迁移工具**：扫描代码中直接访问字段的模式，提示使用 `require_field()`
