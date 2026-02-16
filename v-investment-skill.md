# Value Investment Skill

A股/港股/美股基本面分析，基于akshare数据。

## 快速使用

```bash
# CLI
uv run python -m value_investment.cli info 600519
uv run python -m value_investment.cli hist 600519 --end 20241231
uv run python -m value_investment.cli financial 600519 --end 2024
uv run python -m value_investment.cli analyze 600519
uv run python -m value_investment.cli indicator ImpliedGrowth -s 600519
```

```python
# Python
from value_investment import ValueInvestment

vi = ValueInvestment(market="A")
vi.get_stock_info("600519")
vi.get_historical_data("600519", "20200101", "20241231")
vi.get_financial_data("600519", 2024)  # 获取到2024年的所有数据
vi.analyze("600519", years=5)
```

---

## CLI 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `info <code>` | 个股信息 | `info 600519` |
| `hist <code>` | 历史行情 | `hist 600519 --end 20241231` |
| `financial <code>` | 财务数据 | `financial 600519 --end 2024` |
| `indicator <name> -s <code>` | 计算指标 | `indicator ImpliedGrowth -s 600519` |
| `analyze <code>` | 完整分析 | `analyze 600519` |
| `list` | 指标列表 | `list` |

### 市场代码格式

- A股: 6位数字 (600519)
- 港股: 5位数字 (00700)
- 美股: 字母 (AAPL)

---

## Python API

### 核心方法

| 方法 | 说明 |
|------|------|
| `get_stock_info(code)` | 个股基本信息 |
| `get_historical_data(code, start, end)` | 历史行情(默认后复权) |
| `get_financial_data(code, end_year)` | 三大表合并(获取到end_year的所有历史数据) |
| `calculate_indicator(name, code, years)` | 计算指标 |
| `get_indicator(name)` | 获取指标元数据 |
| `list_indicators()` | 列出所有指标 |
| `analyze(code, years)` | 完整分析 |

### 指标类型

- **RAW**: 原始财务数据 (revenue, net_profit, total_assets)
- **SIMPLE**: 简单计算 (ROE, ROA, gross_margin, net_profit_margin, current_ratio, etc.)
- **COMPLEX**: 复杂计算 (ROIC, CAGR, ImpliedGrowth)

### 常用指标

`ROE` `ROA` `ROIC` `gross_margin` `net_profit_margin` `current_ratio` `CAGR` `ImpliedGrowth`

---

## 缓存策略

- 个股信息: 次日凌晨失效
- 历史数据: 1年
- 财务数据: 次年6月底

缓存支持范围复用: 缓存[2015-2024]可服务于[2020-2024]查询。
