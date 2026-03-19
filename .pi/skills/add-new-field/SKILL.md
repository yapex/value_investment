---
name: add-new-field
description: Add new financial fields to value_investment project. Use when adding new fields to CustomFields, creating new Calculator, or mapping fields from data providers.
---

# Add New Field

## Golden Rule

> **先验证数据源，再写代码**  
> 字段映射必须通过实际 API 调用验证，绝不能凭猜测。

## Workflow

### Phase 1: 验证数据源（必须先做）

```bash
# 1. 查询 Tushare 字段（A股）
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
import tushare as ts
ts.set_token(os.getenv('TUSHARE_TOKEN'))
api = ts.pro_api()

# 获取完整字段列表
df = api.balancesheet(ts_code='000002.SZ', start_date='20230101', end_date='20231231')
for col in df.columns:
    print(col)
"

# 2. 验证目标字段有数据
uv run python -c "
import os, tushare as ts
from dotenv import load_dotenv
load_dotenv()
ts.set_token(os.getenv('TUSHARE_TOKEN'))
api = ts.pro_api()

# 测试特定字段
df = api.balancesheet(ts_code='000002.SZ', start_date='20230101', end_date='20231231',
    fields='end_date,goodwill,intan_assets,lt_eqt_invest,cip')
print(df.to_string())
"
```

### Phase 2: TDD 流程

- [ ] **Write test first** - 创建测试用例验证字段
- [ ] **Run test** - 确认失败
- [ ] **Write code** - 实现字段定义和映射
- [ ] **Run test** - 确认通过
- [ ] **Verify data** - 确认 API 实际返回数据

### Phase 3: 修改文件

| 文件 | 修改内容 |
|------|---------|
| `src/value_investment/domain/fields.py` | 添加到 `CustomFields`（**不是 IFRSFields**） |
| `src/value_investment/providers/a_share.py` | `SUPPORTED_FIELDS` + `FIELD_MAPPINGS` |
| `src/value_investment/handlers/a_share.py` | `A_SHARE_STATEMENT_FIELDS` + `_get_balance_fields()` |
| `tests/` | 添加字段相关测试 |

## Common Tushare Field Names

| 概念 | Tushare 字段 | 备注 |
|------|-------------|------|
| 无形资产 | `intan_assets` | 不是 `intang_assets` |
| 在建工程 | `cip` | construction in progress |
| 长期股权投资 | `lt_eqt_invest` | long-term equity investment |
| 商誉 | `goodwill` | 直接可用 |
| 固定资产 | `fix_assets` | |
| 应收账款 | `accounts_receiv` | |
| 应付账款 | `accounts_pay` | |

## Validation Checklist

- [ ] `uv run python -m pytest tests/` 全部通过
- [ ] 字段在 `ALL_FIELDS` 中
- [ ] `FIELD_MAPPINGS` 映射正确（通过实际 API 验证）
- [ ] Handler 的 `_get_*_fields()` 方法包含该字段

## Common Mistakes

❌ **Wrong**: 凭记忆猜测 Tushare 字段名  
✅ **Right**: 先用 API 查询完整字段列表

❌ **Wrong**: 直接添加字段到 IFRSFields（已冻结）  
✅ **Right**: 添加到 CustomFields

❌ **Wrong**: 只跑单元测试，不验证数据可用性  
✅ **Right**: 单元测试 + 实际 API 调用验证
