# Scanner 使用指南

Scanner 用于批量获取全市场股票数据并进行筛选，适合构建选股策略。

## CLI 命令

```bash
v-invest scan --filter "<过滤条件>" [选项]
```

### 选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `-f, --filter` | 过滤条件文本（必填） | - |
| `-m, --market` | 市场类型 | `A` |
| `--fields` | 获取的字段，用逗号分隔 | `roe` |
| `-y, --years` | 获取年数 | `5` |
| `-l, --limit` | 扫描股票数量限制（0=全部） | `100` |
| `-o, --output` | 输出文件路径（CSV） | - |
| `--no-cache` | 强制重新扫描，不使用缓存 | - |

### 使用示例

```bash
# 基本筛选：连续 5 年 ROE ≥ 15%
v-invest scan --filter "ROE 连续 5 年 ≥15%"

# 多条件 AND：ROE 连续 5 年 ≥15% 且 毛利率 ≥30%
v-invest scan --filter "ROE 连续 5 年 ≥15% 且 毛利率 连续 5 年 ≥30%"

# 多数年份：5 年中至少 4 年 ROE ≥15%
v-invest scan --filter "ROE 5 年至少 4 年 ≥15%"

# 带平均值：5 年中至少 4 年 ROE ≥15%，且平均值 ≥15%
v-invest scan --filter "ROE 5 年至少 4 年 ≥15%, 平均≥15%"

# 最近一年
v-invest scan --filter "ROE 最近 1 年 ≥20%"

# ≤ 运算符（负债率）
v-invest scan --filter "负债率 最近 1 年 ≤60%"

# 限制扫描数量
v-invest scan --filter "ROE 连续 5 年 ≥15%" --limit 50

# 输出到文件
v-invest scan --filter "ROE 连续 5 年 ≥15%" -o result.csv

# 港股市场
v-invest scan --filter "ROE 连续 5 年 ≥15%" -m HK

# 缓存机制：首次扫描自动缓存结果，再次运行相同条件直接返回缓存
v-invest scan --filter "ROIC 5 年至少 4 年 ≥15%, 平均≥15%" -m A --fields roic -y 5 -l 0

# 强制重新扫描（不使用缓存）
v-invest scan --filter "ROE 连续 5 年 ≥15%" --no-cache

# 查看已缓存的扫描结果
v-invest scan-list
v-invest scan-list -m A    # 查看 A 股市场缓存
v-invest scan-list -m HK    # 查看港股市场缓存
```

## Python API

```python
from value_investment import Scanner, parse_filter

# 初始化
scanner = Scanner(market='A')

# 获取股票列表
stocks = scanner.get_stock_list()
stock_codes = stocks['symbol'].tolist()

# 解析文本条件
fb = parse_filter("ROE 连续 5 年 ≥15% 且 毛利率 连续 5 年 ≥30%")

# 获取数据并过滤
result = scanner.scan(
    stocks=stock_codes,
    fields=['roe', 'gross_profit_margin'],
    filters=fb,
    years=5
)
```

## 文本格式规范

### 条件类型

| 类型 | 格式 | 示例 |
|------|------|------|
| 连续 N 年 | `{字段} 连续{N}年 {运算符}{数值}%` | `ROE 连续 5 年 ≥15%` |
| 最近 N 年 | `{字段} 最近{N}年 {运算符}{数值}%` | `ROE 最近 1 年 ≥20%` |
| 多数年份 | `{字段} {N}年至少{M}年 {运算符}{数值}%` | `ROE 5 年至少 4 年 ≥15%` |

### 运算符

- `≥` 大于等于
- `≤` 小于等于
- `>` 大于（转换为 ≥ + 0.001）
- `<` 小于（转换为 ≤ - 0.001）

### 多条件组合

用 `且` 或 `和` 连接多个条件（AND 逻辑）：

```
ROE 连续 5 年 ≥15% 且 毛利率 连续 5 年 ≥30%
```

### 平均值要求

在条件后加 `, 平均≥{数值}%`：

```
ROE 5 年至少 4 年 ≥15%, 平均≥15%
```

## 支持的字段

| 中文名 | 英文名 |
|--------|--------|
| ROE / 净资产收益率 | roe |
| 毛利率 | gross_profit_margin |
| 净利率 | net_profit_margin |
| 负债率 / 资产负债率 | debt_to_asset |
| 营业收入增长率 | revenue_growth |
| 总资产周转率 | asset_turnover |
| 存货周转率 | inventory_turnover |

## 过滤函数说明

Scanner 内部使用以下过滤函数：

- `consecutive_years`：连续 N 年满足条件
- `latest_year`：最近一年满足条件
- `majority_years`：N 年中至少 M 年满足条件，可选平均值

所有过滤器通过 `FilterBuilder` 组合，默认使用 AND 逻辑。

## 缓存机制

Scanner 使用缓存机制提高性能：

| 缓存类型 | 说明 |
|---------|------|
| 自动缓存 | 首次扫描时自动缓存结果，相同条件再次扫描直接返回 |
| `--no-cache` | 强制重新扫描，忽略缓存 |
| `scan-list` | 查看已缓存的扫描结果，可按市场筛选 |

缓存文件存储在 `.cache/scan/` 目录下。
