# 字段映射重构计划

## 问题分析

### 当前架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           外部数据源                                      │
│              Tushare API / AKShare / YFinance                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Provider 层                                                            │
│  1. fetch data (原始字段: ts_code, end_date, total_revenue...)          │
│  2. 数据清理 (ann_date过滤, update_flag去重)                             │
│  3. _apply_mapping() ← 第一次映射                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ 缓存 (映射后数据)
┌─────────────────────────────────────────────────────────────────────────┐
│  API 层 (ValueInvestment)                                               │
│  DataMapper.map_xxx() ← 第二次映射（重复！）                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  计算框架 (Indicators)                                                   │
│  ROEIndicator, ROAIndicator, ...                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 问题

1. **双重映射**：Provider 层和 API 层都在做字段映射
2. **职责不清**：Provider 层的 `_apply_mapping()` 配置分散在 `defaults.py`
3. **维护困难**：两套映射配置（`defaults.py` 和 `mapper.py`）需要同步
4. **架构混乱**：映射应该在"进入计算框架之前"完成，而不是分散在多处

## 设计原则

1. **Provider 职责**：获取数据 → 数据清理 → **统一映射** → 返回标准字段
2. **统一映射**：Provider 使用 `DataMapper` 做完整映射，输出标准字段
3. **API 层简化**：API 层不再做映射，直接透传 Provider 返回的标准字段
4. **计算层解耦**：计算层只依赖标准字段名，不关心数据来源

## 目标架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           外部数据源                                      │
│              Tushare API / AKShare / YFinance                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Provider 层                                                            │
│  1. fetch data (原始字段)                                                │
│  2. 数据清理 (ann_date过滤, update_flag去重)                             │
│  3. DataMapper.map_to_standard(df, source) ← 唯一映射点                  │
│  4. 返回标准字段                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ 缓存 (标准字段)
┌─────────────────────────────────────────────────────────────────────────┐
│  API 层 (ValueInvestment)                                               │
│  直接透传 Provider 返回的标准字段，不再映射                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  计算框架 (Indicators)                                                   │
│  只依赖标准字段: stock_code, report_date, total_revenue...              │
└─────────────────────────────────────────────────────────────────────────┘
```

## 采用方案：Provider 做完整映射

### 方案对比

| 方案 | 映射位置 | 缓存内容 | 优点 | 缺点 |
|------|---------|---------|------|------|
| ~~A~~ | API 层 | 原始数据 | 更换 provider 不需清缓存 | API 层职责增加 |
| **B** | Provider 层 | 标准字段 | Provider 输出标准化，API 层简化 | 更换 provider 需清缓存 |
| ~~C~~ | 分散 | 混合 | 改动最小 | 职责模糊 |

### 选择方案 B 的理由

1. **职责清晰**：Provider 负责从原始数据到标准数据的完整转换
2. **调用方简化**：API 层、计算层无需关心数据源差异
3. **单一入口**：映射逻辑集中在 `DataMapper`，易于维护
4. **缓存代价可接受**：更换 provider 是低频操作，清缓存是合理代价

### 实现代码

```python
# Provider 层：使用 DataMapper 做完整映射
class TushareProvider:
    def get_income_statement(self, stock_code, end_year):
        # 1. 获取原始数据
        df = self._api.income(...)
        
        # 2. 数据清理
        df = self._filter_announced(df)   # 过滤已公告
        df = self._filter_latest(df)       # 过滤 update_flag
        
        # 3. 统一映射（使用 DataMapper，而非 _apply_mapping）
        df = DataMapper.map_to_standard(df, source="tushare", data_type="income")
        
        return df  # 返回标准字段：stock_code, report_date, total_revenue...

# API 层：不再映射
class ValueInvestment:
    def get_profit_sheet(self, symbol):
        df = self._provider.get_income_statement(symbol)
        return df  # 已经是标准字段，无需再映射
```

## 实施步骤

### Phase 1: 扩展 DataMapper（2-3h）

**目标**：添加 `map_to_standard(df, source, data_type)` 方法

```python
class DataMapper:
    # 数据源配置
    TUSHARE_MAPPINGS = {
        "balance": {"ts_code": "stock_code", "end_date": "report_date", ...},
        "income": {"ts_code": "stock_code", "end_date": "report_date", ...},
        "cashflow": {...},
    }
    AKSHARE_MAPPINGS = {...}
    YFINANCE_MAPPINGS = {...}
    
    @classmethod
    def map_to_standard(cls, df, source, data_type):
        """统一映射入口
        
        Args:
            df: 原始 DataFrame
            source: 数据源 ("tushare" | "akshare" | "yfinance")
            data_type: 数据类型 ("balance" | "income" | "cashflow" | "market")
        
        Returns:
            映射后的 DataFrame（标准字段名）
        """
        mappings = cls._get_mappings(source, data_type)
        return df.rename(columns=mappings)
```

**测试用例**：
- `test_map_to_standard_tushare_balance` - Tushare 资产负债表映射
- `test_map_to_standard_tushare_income` - Tushare 利润表映射
- `test_map_to_standard_akshare_balance` - AKShare 资产负债表映射
- `test_map_to_standard_yfinance_balance` - YFinance 资产负债表映射

### Phase 2: 修改 Provider（1-2h）

**目标**：Provider 使用 `DataMapper.map_to_standard()` 替代 `_apply_mapping()`

**文件变更**：

| 文件 | 变更 |
|------|------|
| `data/providers/tushare_provider.py` | `_apply_mapping()` → `DataMapper.map_to_standard()` |
| `data/providers/akshare_provider.py` | 同上 |
| `data/providers/yfinance_provider.py` | 同上 |
| `data/providers/base_provider.py` | `_apply_mapping()` 标记为 deprecated |
| `core/defaults.py` | `field_mappings` 标记为 deprecated |

### Phase 3: 简化 API 层（1-2h）

**目标**：移除 API 层的重复映射

**文件变更**：

| 文件 | 变更 |
|------|------|
| `api.py` | 移除 `DataMapper.map_balance_sheet()` 等调用 |

**变更前**：
```python
def get_balance_sheet(self, symbol, ...):
    df = self._provider.get_balance_sheet(symbol, ...)
    df = DataMapper.map_balance_sheet(df)  # 移除这行
    return df
```

**变更后**：
```python
def get_balance_sheet(self, symbol, ...):
    df = self._provider.get_balance_sheet(symbol, ...)
    return df  # 已经是标准字段
```

### Phase 4: 清理废弃代码（1h）

**目标**：移除不再使用的代码

- 移除 `base_provider._apply_mapping()`
- 移除 `defaults.field_mappings`
- 移除 `api.py` 中的 `map_fields` 参数

### Phase 5: 测试（2h）

1. **单元测试**：`DataMapper.map_to_standard()` 各数据源
2. **集成测试**：Provider → API → Indicator 完整流程
3. **回归测试**：确保现有功能不受影响

## 文件变更清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `data/mapper.py` | 新增方法 | `map_to_standard(df, source, data_type)` |
| `data/providers/tushare_provider.py` | 修改 | 使用 `DataMapper.map_to_standard()` |
| `data/providers/akshare_provider.py` | 修改 | 同上 |
| `data/providers/yfinance_provider.py` | 修改 | 同上 |
| `data/providers/base_provider.py` | 废弃 | `_apply_mapping()` 标记 deprecated |
| `api.py` | 简化 | 移除 `DataMapper.map_xxx()` 调用 |
| `core/defaults.py` | 废弃 | `field_mappings` 标记 deprecated |

## 时间估算

| Phase | 时间 | 说明 |
|-------|------|------|
| Phase 1 | 2-3h | 扩展 DataMapper |
| Phase 2 | 1-2h | 修改 Provider |
| Phase 3 | 1-2h | 简化 API 层 |
| Phase 4 | 1h | 清理废弃代码 |
| Phase 5 | 2h | 测试 |

**总计：7-10 小时**

## 风险与对策

| 风险 | 对策 |
|------|------|
| 缓存失效 | 重构后需要清缓存，在 Release Note 中说明 |
| 字段遗漏 | 编写完整的映射测试，覆盖所有字段 |
| 回归问题 | 运行完整测试套件，确保现有功能正常 |

## 决策记录

- [x] 2026-03-18: 确认采用方案 B（Provider 做完整映射）
- [x] 2026-03-18: 缓存策略：缓存标准字段数据
- [x] 2026-03-18: 缓存年数：默认 10 年（已完成）
- [ ] 是否需要向后兼容（保留 `map_fields` 参数）
