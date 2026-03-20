---
name: add-new-field
description: "⚠️ REQUIRED: Before adding ANY field to value_investment project, you MUST read this skill first. Applies when adding new fields to CustomFields, creating new Calculator, or mapping fields from data providers. This is NOT optional."
---

# Add New Field

> **先验证数据源，再写代码**  
> 字段映射必须通过实际 API 调用验证

## 命名规范

| 原则 | 说明 |
|------|------|
| snake_case | 全小写，下划线分隔 |
| 简短明确 | 方便阅读，不过度详细 |
| 自主命名 | 以我们为主，不参考 provider |
| **无重复** | 先检查 ALL_FIELDS，不添加意义相同的字段 |

## 流程

### Phase 0: 检查重复

```bash
uv run python -c "
from value_investment.domain.fields import ALL_FIELDS
# 检查关键词
keywords = ['net_debt', 'debt', 'equity']
for f in sorted(ALL_FIELDS):
    if any(kw in f for kw in keywords):
        print(f)
"
```

### Phase 1: 验证数据源

**验证用股票（排除金融类）：**
- 600519 贵州茅台、000002 万科A、601012 隆基绿能、600276 恒瑞医药

```bash
# 查询字段列表
uv run python -c "
import tushare as ts, os
api = ts.pro_api(os.getenv('TUSHARE_TOKEN'))
df = api.balancesheet(ts_code='000002.SZ', start_date='20230101', end_date='20231231')
print(df.columns.tolist())
"

# 多股票交叉验证（必须 3 只以上）
uv run python -c "
import tushare as ts, os
api = ts.pro_api(os.getenv('TUSHARE_TOKEN'))
for code in ['600519', '000002', '601012']:
    ts_code = code + ('.SH' if code.startswith('6') else '.SZ')
    df = api.fina_indicator(ts_code=ts_code, fields='end_date,字段名')
    print(df.head(1))
"
```

### Phase 2: TDD + 添加字段

**文件修改：**
| 文件 | 修改 |
|------|------|
| `src/value_investment/domain/fields.py` | 添加到 `CustomFields`（❌ 不是 IFRSFields，已冻结） |
| `src/value_investment/providers/a_share.py` | `SUPPORTED_FIELDS` + `FIELD_MAPPINGS` |
| `src/value_investment/handlers/a_share.py` | `A_SHARE_STATEMENT_FIELDS` |

### Phase 3: 验证

```bash
# Dry run
uv run python -c "
from value_investment.pipeline.validator import validate_pipeline
report = validate_pipeline(['新字段'], '600519', 'A股', dry_run=True)
print(f'Blocking errors: {len(report.inconsistencies)}')
"

# 全量测试
uv run python -m pytest tests/ -q
```

## 常见错误

| ❌ 错误 | ✅ 正确 |
|--------|--------|
| 直接添加字段，不检查重复 | 先检查 ALL_FIELDS |
| 猜测 Tushare 字段名 | 先用 API 查询 |
| 添加到 IFRSFields | 添加到 CustomFields |
| 只验证单只股票 | 交叉验证 3+ 只 |
| 用金融股验证 | 用制造/消费/医药股 |
