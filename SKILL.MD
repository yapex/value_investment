---
name: v-invest
description: |
  A股/港股/美股基本面分析工具。触发场景：(1) 股票基本信息/市值/行业查询 (2) 历史股价 (3) 财务报表（资产负债表/利润表/现金流量表）(4) 财务指标计算（ROE/ROA/ROIC/毛利率/CAGR/PE百分位等）(5) 基本面/价值投资分析
---

# v-invest

## 快速命令

| 需求 | 命令 |
|------|------|
| 股票基本信息 | `uv run python -m value_investment.cli info 600519` |
| 历史股价 | `uv run python -m value_investment.cli hist 600519 --end 20241231` |
| 资产负债表 | `uv run python -m value_investment.cli balance 600519 --end 2024` |
| 利润表 | `uv run python -m value_investment.cli profit 600519 --end 2024` |
| 现金流量表 | `uv run python -m value_investment.cli cashflow 600519 --end 2024` |
| 财务指标 | `uv run python -m value_investment.cli finind 600519 -m A` |
| 单个指标 | `uv run python -m value_investment.cli indicator ROIC -s 00700 -m HK` |
| 完整分析 | `uv run python -m value_investment.cli analyze 600519` |

### 股票代码

- A股: `600519`
- 港股: `00700`
- 美股: `AAPL`

### 常用指标

```bash
# 港股示例
uv run python -m value_investment.cli indicator ROIC -s 00700 -m HK           # 投资资本回报率
uv run python -m value_investment.cli indicator CAGR -s 00700 -m HK            # 营收复合增长率
uv run python -m value_investment.cli indicator ImpliedGrowth -s 00700 -m HK  # 市场隐含增长率
uv run python -m value_investment.cli indicator PEPct -s 00700 -m HK -y 10   # PE历史百分位
uv run python -m value_investment.cli indicator latest_market_cap -s 00700 -m HK  # 最新市值

# A股示例
uv run python -m value_investment.cli indicator ROIC -s 600519 -m A
uv run python -m value_investment.cli indicator PEPct -s 600519 -m A -y 10
```

---

### 数据格式说明

- **CLI输出格式**: 使用Markdown表格格式（易于解析和阅读）
- **查看格式**: 使用 `head -n 5` 先查看数据格式
- **解析提示**: Agent可使用正则或简单字符串解析Markdown表格

---

## 参考文档

- **指标体系**: [references/indicators.md](references/indicators.md)
- **ROIC计算**: [references/roic.md](references/roic.md)
- **市场字段**: [references/a-stock.md](references/a-stock.md) / [references/hk-stock.md](references/hk-stock.md)
- **财务报表**: [references/balance.md](references/balance.md) / [references/profit.md](references/profit.md)
