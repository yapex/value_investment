# Agent 股票 Scanner 操作指南

本指南教你如何使用 `value_investment` 库的 Scanner 功能来筛选股票。

## 概述

Scanner 是用于批量获取和筛选股票数据的工具，特点：
- **统一字段**：使用标准字段名，内部自动转换为 Tushare 字段
- **自动去重**：优先使用最新修订的数据（update_flag=1）
- **智能缓存**：股票列表缓存 1 年，财务数据缓存到次年 6 月底
- **速率限制**：内置 RateLimiter，每分钟最多 200 次 API 调用

## 快速开始

### 1. 初始化 Scanner

```python
from value_investment import Scanner

scanner = Scanner(market="A")
```

### 2. 获取股票列表

```python
# 获取全市场 A 股列表
stocks = scanner.get_stock_list()
print(f"共 {len(stocks)} 只股票")

# 查看前几只
print(stocks[['symbol', 'name', 'industry']].head())
```

### 3. 获取财务数据

```python
# 获取前 100 只股票的 5 年 ROE 数据
test_stocks = stocks['symbol'].head(100).tolist()

financials = scanner.get_financial_data(
    stocks=test_stocks,
    fields=['roe'],
    years=5
)
```

## 股票代码格式

Scanner 接受两种格式的股票代码：

| 格式 | 示例 | 说明 |
|-----|------|-----|
| 6 位数字 | `600519` | 内部使用格式 |
| Tushare 格式 | `600519.SH` | 也支持 |

系统会自动转换：
- `0`/`3` 开头 → `.SZ`（深圳）
- `6` 开头 → `.SH`（上海）

## 财务数据时间逻辑

**年报数据年份**：
- 当前是 2026 年 1-3 月：使用 2024 年年报（2025 年报尚未发布）
- 当前是 2026 年 4-12 月：使用 2025 年年报

系统自动判断当前月份，选择最新可用的年报数据。

## 过滤函数

### 1. consecutive_years - 连续 N 年满足条件

**场景**: 连续 5 年 ROE >= 15%

```python
from value_investment.scanner import filters

result = filters.consecutive_years(
    financials,
    field='roe',
    min_value=15,
    years=5
)
```

### 2. latest_year - 最近一年满足条件

**场景**: 最近一年毛利率 >= 30%

```python
result = filters.latest_year(
    financials,
    field='gross_profit_margin',
    min_value=30
)
```

**支持的条件**：
- `min_value`: 最小值（可选）
- `max_value`: 最大值（可选）

```python
# 最近一年 ROE 在 15%-30% 之间
result = filters.latest_year(
    financials,
    field='roe',
    min_value=15,
    max_value=30
)
```

### 3. 组合过滤

可以多次调用过滤器进行组合筛选：

```python
# 第一步：筛选毛利率 > 30% 的股票
step1 = filters.latest_year(financials, field='gross_profit_margin', min_value=30)

# 第二步：从中筛选连续 5 年 ROE > 15%
result = filters.consecutive_years(step1, field='roe', min_value=15, years=5)
```

## 数据处理特性

### 1. 自动去重

系统自动处理 Tushare 数据中的重复记录：
- 优先使用 `update_flag=1`（后期修订过的数据）
- 如果没有修订数据，则使用原始数据

### 2. 字段映射

使用标准字段名，系统自动转换为 Tushare 原始字段：

| 标准字段名 | Tushare 字段 | 说明 |
|-----------|-------------|------|
| `roe` | `roe` | 净资产收益率 |
| `gross_profit_margin` | `grossprofit_margin` | 销售毛利率 |
| `net_profit_margin` | `netprofit_margin` | 销售净利率 |
| `debt_ratio` | `debt_to_assets` | 资产负债率 |
| `current_ratio` | `current_ratio` | 流动比率 |
| `quick_ratio` | `quick_ratio` | 速动比率 |
| `roa` | `roa` | 总资产收益率 |
| `roic` | `roic` | 投入资本回报率 |
| `book_value_per_share` | `bps` | 每股净资产 |
| `operating_cash_flow_per_share` | `ocfps` | 每股经营现金流 |

### 3. 缓存策略

| 数据类型 | 缓存时间 | 说明 |
|---------|---------|------|
| 股票列表 | 1 年 | 上市公司列表变化不频繁 |
| 财务数据 | 到次年 6 月底 | 年报通常在次年 4 月发布 |

### 4. 速率限制

内置 RateLimiter，每分钟最多 200 次 API 调用，防止超出 Tushare 限制。

## 完整示例

### 示例：筛选连续 5 年毛利率 > 30% 的股票

```python
from value_investment import Scanner, filters

# 初始化
scanner = Scanner(market="A")

# 获取股票列表
stocks = scanner.get_stock_list()

# 定义股票列表（100 家知名公司）
top_stocks = ['600519', '000858', '000568', ...]  # 省略...

# 获取财务数据（毛利率）
financials = scanner.get_financial_data(
    stocks=top_stocks,
    fields=['gross_profit_margin'],  # 使用标准字段名
    years=5
)

# 筛选：最近一年毛利率 > 30%
step1 = filters.latest_year(financials, field='gross_profit_margin', min_value=30)

# 筛选：连续 5 年毛利率 > 30%
result = filters.consecutive_years(step1, field='gross_profit_margin', min_value=30, years=5)

print(f"符合条件：{result['stock_code'].nunique()} 只")

# 查看每只股票的详细数据
for code in result['stock_code'].unique()[:5]:
    stock_data = result[result['stock_code'] == code].sort_values('end_date')
    name = stocks[stocks['symbol'] == code]['name'].iloc[0]
    margins = stock_data['gross_profit_margin'].tolist()
    years = stock_data['end_date'].dt.strftime('%Y').tolist()
    print(f"{code} ({name}): {dict(zip(years, margins))}")
```

## 性能提示

1. **首次扫描较慢**: 全市场 5000+ 只股票，首次获取数据约需 25-30 分钟（受 Tushare 速率限制）
2. **缓存机制**: 数据会自动缓存，后续扫描从缓存读取，速度极快
3. **分批处理**: 可以先用小批量（如前 100 只）测试筛选逻辑
4. **字段选择**: 只获取需要的字段，减少数据传输

## 故障排除

### 问题："TUSHARE_TOKEN not found"

**解决**: 设置环境变量
```bash
export TUSHARE_TOKEN="your_token_here"
```

### 问题：数据获取很慢

**解决**: 这是正常的，受 Tushare 速率限制（每分钟 200 次）。首次获取后会缓存，后续很快。

### 问题：某些股票没有数据

**解决**: 可能是新股或数据缺失，过滤时会自动跳过。

### 问题：筛选结果为空

**检查**：
1. 确认数据已成功获取：`print(financials['stock_code'].nunique())`
2. 确认字段名正确：使用标准字段名（如 `gross_profit_margin` 而不是 `gross_margin`）
3. 调整筛选条件

## 后续开发

当前已实现功能：
- ✅ 连续 N 年过滤
- ✅ 最近一年过滤
- ✅ 多数年份过滤 (majority_years)
- ✅ A 股市场支持

计划中功能：
- ⏳ 更多过滤函数（趋势、稳定性等）
- ⏳ 港股/美股市场支持
- ⏳ CLI 集成
