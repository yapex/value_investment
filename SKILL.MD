---
name: v-invest
description: |
  A股/港股/美股基本面分析工具。触发场景：(1) 股票基本信息/市值/行业查询 (2) 历史股价 (3) 财务报表（资产负债表/利润表/现金流量表）(4) 财务指标计算（ROE/ROA/毛利率/DCF等）(5) 基本面/价值投资分析
---

# v-invest

## 场景化使用

根据用户需求选择**唯一**需要的命令：

| 需求 | 命令 | 说明 |
|------|------|------|
| 股票基本信息 | `v-invest info 600519` | 名称、市值、行业，A股/港股/美股 |
| 历史股价 | `v-invest hist 600519 --end 20241231` | 日线，A股/港股 |
| 资产负债表 | `v-invest balance 600519 --end 2024` | A股/港股/美股 |
| 利润表 | `v-invest profit 600519 --end 2024` | A股/港股/美股 |
| 现金流量表 | `v-invest cashflow 600519 --end 2024` | A股/港股/美股 |
| 单个指标 | `v-invest indicator ROE -s 600519` | **自包含**，自动获取数据 |
| 完整分析 | `v-invest analyze 600519` | 一次性所有指标 |

### 重要提示

- **`indicator` 命令自包含**：自动获取财务数据和市值，无需先调用 `info`/`balance`/`profit`
- **避免冗余**：查询单个指标时只执行 `indicator`，不要执行 `analyze`
- **`analyze` 适用场景**：用户明确要求"完整分析"、"全面分析"时使用

### 代码格式

- A股: 6位数字 (600519)
- 港股: 5位数字 (00700)
- 美股: 字母 (AAPL)

---

## 指标体系

| 指标 | 说明 | 公式 |
|------|------|------|
| `ROE` | 净资产收益率 | 净利润 / 股东权益 |
| `ROA` | 总资产收益率 | 净利润 / 总资产 |
| `gross_margin` | 毛利率 | (营收 - 成本) / 营收 |
| `net_profit_margin` | 净利率 | 净利润 / 营收 |
| `current_ratio` | 流动比率 | 流动资产 / 流动负债 |
| `quick_ratio` | 速动比率 | (流动资产 - 存货) / 流动负债 |
| `debt_ratio` | 资产负债率 | 总负债 / 总资产 |
| `asset_turnover` | 资产周转率 | 营业收入 / 总资产 |
| `inventory_turnover` | 存货周转率 | 营业成本 / 存货 |
| `receivable_turnover` | 应收周转率 | 营业收入 / 应收账款 |
| `payable_turnover` | 应付周转率 | 营业成本 / 应付账款 |
| `cfo_to_netprofit_sum` | 累计净现比 | 经营现金流累计 / 净利润累计 |
| `ROIC` | 投资资本回报率 | NOPAT / 投入资本 |
| `CAGR` | 复合增长率 | 支持 revenue/net_profit |
| `ImpliedGrowth` | 市场隐含增长率 | 基于DCF模型反推 |

---

## 参考文档（按需读取）

**市场字段**（需要了解具体返回字段时读取）：
- A股: [references/a-stock.md](references/a-stock.md)
- 港股: [references/hk-stock.md](references/hk-stock.md)
- 美股: [references/us-stock.md](references/us-stock.md)

**财务报表字段**（需要了解数据格式/列名时读取）：
- 资产负债表: [references/balance.md](references/balance.md)
- 利润表: [references/profit.md](references/profit.md)
- 现金流量表: [references/cashflow.md](references/cashflow.md)
