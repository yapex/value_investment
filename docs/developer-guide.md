# 开发者指南

面向 Agent 的精简开发手册。

> 详细架构说明请参考 [Pipeline 架构详解](./pipeline-architecture.md)。

---

## 架构概览

```
用户请求 (fields)
    ↓
PipelineAPI.get_data()
    ↓
MessageBus → 9 Handler 并行处理 (市场 × 数据类型)
    ↓
Calculator 计算派生字段
    ↓
返回 {field: {year: value}}
```

**9 Handler 矩阵**:

| 市场 | 财务报表 | 财务指标 | 市值数据 |
|-----|---------|---------|---------|
| A股 | AStatement | AIndicator | AMarket |
| 港股 | HKStatement | HKIndicator | HKMarket |
| 美股 | USStatement | USIndicator | USMarket |

---

## 目录结构

```
src/value_investment/
├── pipeline/           # Pipeline 核心
│   ├── api.py          # PipelineAPI（入口）
│   ├── bus.py          # MessageBus
│   ├── validator.py    # 依赖验证
│   └── handlers/       # 9 Handler
├── calculators/        # 内置计算器 (Package 方式)
├── domain/
│   └── fields.py       # IFRSFields（标准字段）
└── handlers/           # 兼容层 Handler (旧)
    ├── a_share.py
    ├── hk_share.py
    └── us_share.py
```

---

## 添加字段

### 原始字段（从数据源获取）

1. **定义字段**: `domain/fields.py`
   ```python
   class IFRSFields:
       NEW_FIELD = "new_field"
   ```

2. **添加映射**: 找到对应 Handler 的 `_field_mapping` 方法，添加数据源字段映射

3. **Handler 支持**: 在 Handler 的字段集合中添加
   ```python
   class AStockStatementHandler:
       FIELDS = {...， IFRSFields.NEW_FIELD}
   ```

### 派生字段（Calculator 计算）

1. **创建计算器**:
   ```python
   # calculators/calc_xxx.py
   
   name = "my_metric"
   required_fields = ["field_a", "field_b"]
   
   def calculate(results):
       a = results.get("field_a", {})
       b = results.get("field_b", {})
       return {
           year: a.get(year, 0) / b.get(year, 1)
           for year in a
       }
   ```

2. **验证**:
   ```bash
   uv run python -m pytest tests/pipeline/test_validator.py -v
   ```

---

## 测试

```bash
# 全部测试
uv run python -m pytest tests/ -v

# 单元测试
uv run python -m pytest tests/pipeline/ -v

# 指定测试
uv run python -m pytest tests/test_xxx.py -v
```

---

## CLI 命令

```bash
# 查询数据
v-invest query 600519 --requires roe,roic --years 10

# 验证配置（dry run）
v-invest validate 600519 --requires implied_growth

# 列出字段
v-invest fields --prefix ro

# 清除缓存
v-invest cache-clear
```

---

## 常用操作

| 操作 | 命令 |
|------|------|
| 添加 Calculator | 创建 `calculators/calc_xxx.py` |
| 添加字段映射 | 修改 Handler 的 `_field_mapping` |
| 验证依赖链 | `pytest tests/pipeline/test_validator.py` |
| 调试数据流 | 使用 `v-invest validate` 检查配置 |

---

## 相关文档

- [Pipeline 架构详解](./pipeline-architecture.md) - 详细架构说明
- [IFRS 标准字段](./ifrs_standard_fields.md) - 字段定义
