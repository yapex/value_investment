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

### 连续 N 年满足条件

**场景**: 连续 5 年 ROE >= 15%

```python
from value_investment.scanner import filters

result = filters.consecutive_years(
    financials,
    field='roe',
    min_value=15,
    years=5
)

# 查看结果
print(f"符合条件：{result['stock_code'].nunique()} 只")
print(result[['stock_code', 'end_date', 'roe']].head(10))
```

## 完整示例

```python
from value_investment import Scanner, filters

# 初始化
scanner = Scanner(market="A")

# 获取股票列表（取前 100 只测试）
stocks = scanner.get_stock_list()
test_stocks = stocks['symbol'].head(100).tolist()
print(f"测试股票：{len(test_stocks)} 只")

# 获取财务数据
financials = scanner.get_financial_data(
    stocks=test_stocks,
    fields=['roe'],
    years=5
)
print(f"获取到 {financials['stock_code'].nunique()} 只股票的数据")

# 筛选：连续 5 年 ROE >= 15%
result = filters.consecutive_years(
    financials,
    field='roe',
    min_value=15,
    years=5
)

# 显示结果
print(f"\n符合条件：{result['stock_code'].nunique()} 只")

if not result.empty:
    # 合并股票名称
    result_named = result.merge(
        stocks[['symbol', 'name']],
        left_on='stock_code',
        right_on='symbol'
    )
    print("\n符合条件的股票:")
    for code in result_named['stock_code'].unique():
        name = result_named[result_named['stock_code'] == code]['name'].iloc[0]
        roe_values = result_named[result_named['stock_code'] == code]['roe'].tolist()
        print(f"  - {code} ({name}): ROE = {roe_values}")
```

## 性能提示

1. **首次扫描较慢**: 全市场 5000+ 只股票，首次获取数据约需 25-30 分钟（受 Tushare 速率限制）
2. **缓存机制**: 数据会自动缓存，后续扫描从缓存读取，速度极快
3. **分批处理**: 可以先用小批量（如前 100 只）测试筛选逻辑
4. **字段选择**: 只获取需要的字段，减少数据传输

## 可用字段参考

常用财务指标字段：
- `roe` - 净资产收益率 (%)
- `gross_margin` - 毛利率 (%)
- `net_margin` - 净利率 (%)
- `debt_ratio` - 资产负债率 (%)
- `current_ratio` - 流动比率
- `roe_diluted` - 摊薄 ROE
- `roa` - 总资产收益率
- `eps` - 每股收益

完整字段列表请参考 Tushare `fina_indicator` 接口文档。

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
```python
# 检查数据覆盖情况
print(f"获取到 {financials['stock_code'].nunique()} 只股票的数据")
```
