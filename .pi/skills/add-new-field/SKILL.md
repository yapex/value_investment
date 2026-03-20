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

#### 验证用股票代码（按行业分类）

```python
# A 股验证用股票（排除金融类，选取各行业代表性企业）
A_SHARE_VALIDATION_STOCKS = [
    "600519",  # 白酒 - 贵州茅台
    "000002",  # 房地产 - 万科A
    "000858",  # 白酒 - 五粮液
    "601012",  # 光伏 - 隆基绿能
    "600276",  # 医药 - 恒瑞医药
    "002475",  # 电子 - 立讯精密
]
```

#### 验证步骤

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

# 2. 多股票交叉验证（必须！）
# ❌ 禁止只验证单只股票就下结论
# ✅ 必须验证至少 3 只不同行业的股票
# ❌ 金融类股票（银行/保险/券商）报表结构不同，可能缺失某些字段
uv run python -c "
import os, tushare as ts
from dotenv import load_dotenv
load_dotenv()
ts.set_token(os.getenv('TUSHARE_TOKEN'))
api = ts.pro_api()

stocks = ['600519', '000002', '601318', '000858', '600036']
fields = 'end_date,cash_ratio,interestdebt,ebitda'

for code in stocks:
    ts_code = code + ('.SZ' if code.startswith(('0','3')) else '.SH')
    df = api.fina_indicator(ts_code=ts_code, start_date='20220101', end_date='20241231', fields=fields)
    df = df[df['end_date'].str.endswith('1231')]
    df = df.drop_duplicates(subset='end_date', keep='first')
    if not df.empty:
        row = df.iloc[0]
        print(f'{code}: cash_ratio={row.get(\"cash_ratio\")}, interestdebt={row.get(\"interestdebt\")}, ebitda={row.get(\"ebitda\")}')

# 判断规则：
# - 所有股票都有数据 → 字段有效，可添加映射
# - 部分股票有数据 → 字段有效，映射仍需添加（数据因行业而异）
# - 所有股票都无数据 → 字段无效，暂不添加映射
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

### Phase 4: 完整验证（修改完成后必须执行）

#### 4.1 Dry Run Pipeline 验证

```bash
# 验证新字段能被 pipeline 正确识别
uv run python -c "
from value_investment.pipeline.validator import validate_pipeline

new_fields = ['cash_ratio','ocf_to_debt','interest_bearing_debt','ebitda']
ok_count = 0
for f in new_fields:
    report = validate_pipeline([f], '600519', 'A股', dry_run=True)
    status = report.field_statuses[f]
    if status.available:
        ok_count += 1
    print('%s %s' % ('✓' if status.available else 'X', f))

print()
report = validate_pipeline([new_fields[0]], '600519', 'A股', dry_run=True)
print('Blocking errors: %d' % len(report.inconsistencies))
for i in report.inconsistencies:
    print('  ', i)
print()
print('结果: %d/%d 通过' % (ok_count, len(new_fields)))
"
```

**通过标准：**
- 8/8 字段 `available=True`
- 0 个 blocking errors（如果有，先排查是否是自己引入的问题）

#### 4.2 检查 fields.py 中无 calculator 的孤立字段

```bash
# ❌ 禁止：添加了字段到 CustomFields 但无 calculator 使用且 handler 也没有
# ✅ 必须：要么有 calculator 消费，要么有 handler 提供
uv run python -c "
import os, glob

calc_files = glob.glob('calculators/*.py')
# 从 fields.py 读取 CustomFields 的字段（手动检查或用下方的 registry）
# 检查是否有字段在 CustomFields 中但无 calculator 依赖也无 handler 提供
"
```

**操作规则：**
- 有 calculator 依赖 → 保留
- 无 calculator 依赖 → 检查 handler 是否提供，若也无则**从 fields.py 移除**

#### 4.3 全量测试

```bash
uv run python -m pytest tests/ -q
```

全部通过后方可提交。

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

- [ ] **数据源验证** — 通过 Tushare API 多股票交叉验证，确认字段有数据
- [ ] **Dry Run** — `validate_pipeline([field], '600519', 'A股', dry_run=True)` 通过，0 blocking errors
- [ ] **字段注册** — 字段在 `ALL_FIELDS` 中，在 handler 常量或 calculator 的 `required_fields` 中
- [ ] **无孤立字段** — `fields.py` 中每个 CustomFields 字段都有 calculator 依赖或 handler 提供
- [ ] **映射正确** — `FIELD_MAPPINGS` 映射通过实际 API 验证
- [ ] **全量测试** — `uv run python -m pytest tests/` 全部通过

## Common Mistakes

❌ **Wrong**: 凭记忆猜测 Tushare 字段名  
✅ **Right**: 先用 API 查询完整字段列表

❌ **Wrong**: 直接添加字段到 IFRSFields（已冻结）  
✅ **Right**: 添加到 CustomFields

❌ **Wrong**: 只跑单元测试，不验证数据可用性  
✅ **Right**: 单元测试 + 实际 API 调用验证

❌ **Wrong**: 只验证单只股票就判定字段无数据  
✅ **Right**: 交叉验证 3 只以上不同行业股票，避免因特定行业报表结构差异误判

❌ **Wrong**: 用金融类股票（银行/保险/券商）验证字段  
✅ **Right**: 金融类报表结构特殊，部分字段（如带息债务、EBITDA）可能为空。验证应选取制造业、消费、医药等代表企业
