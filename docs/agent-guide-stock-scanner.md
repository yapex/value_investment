# Agent 股票 Scanner 操作指南

本指南教你如何使用 `value_investment` 库的 Scanner 功能来筛选股票。

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

## 常用过滤模式

### 1. 连续 N 年满足条件

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

### 2. 最近一年满足条件

**场景**: 最近一年毛利率 >= 30%

```python
result = filters.latest_year(
    financials,
    field='gross_profit_margin',
    min_value=30
)
```

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
```

## 数据处理特性

### 1. 自动去重

系统自动处理 Tushare 数据中的重复记录：
- 优先使用 `update_flag=1`（后期更新过的数据）
- 如果没有更新数据，则使用原始数据

### 2. 字段映射

使用标准字段名，系统自动转换为 Tushare 原始字段：

| 标准字段名 | Tushare 字段 |
|-----------|-------------|
| `roe` | `roe` |
| `gross_profit_margin` | `grossprofit_margin` |
| `net_profit_margin` | `netprofit_margin` |
| `debt_ratio` | `debt_to_assets` |
| `current_ratio` | `current_ratio` |

### 3. 缓存策略

| 数据类型 | 缓存时间 |
|---------|---------|
| 股票列表 | 1 年 |
| 财务数据 | 到次年 6 月底 |

## 性能提示

1. **首次扫描较慢**: 全市场 5000+ 只股票，首次获取数据约需 25-30 分钟（受 Tushare 速率限制）
2. **缓存机制**: 数据会自动缓存，后续扫描从缓存读取，速度极快
3. **分批处理**: 可以先用小批量（如前 100 只）测试筛选逻辑
4. **字段选择**: 只获取需要的字段，减少数据传输

## 可用字段参考

常用财务指标（标准字段名）：

| 标准字段名 | 说明 | 单位 |
|-----------|------|-----|
| `roe` | 净资产收益率 | % |
| `gross_profit_margin` | 销售毛利率 | % |
| `net_profit_margin` | 销售净利率 | % |
| `debt_ratio` | 资产负债率 | % |
| `current_ratio` | 流动比率 | ratio |
| `quick_ratio` | 速动比率 | ratio |
| `roa` | 总资产收益率 | % |
| `roic` | 投入资本回报率 | % |

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
