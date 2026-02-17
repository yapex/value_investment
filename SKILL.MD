# v-invest

A股/港股/美股基本面分析工具，基于akshare数据。

---

## 安装

```bash
git clone https://github.com/yapex/value_investment.git
cd value_investment
uv tool install -e .
```

---

## 场景化使用

根据用户需求选择**唯一**需要的命令：

| 需求 | 命令 | 说明 |
|------|------|------|
| 股票基本信息 | `v-invest info 600519` | 名称、市值、行业 |
| 历史股价 | `v-invest hist 600519 --end 20241231` | 日线/周线/月线 |
| 财务报表 | `v-invest financial 600519 --end 2024` | 三表合并数据 |
| 单个指标 | `v-invest indicator ROE -s 600519` | **自包含**，自动获取数据 |
| 完整分析 | `v-invest analyze 600519` | 一次性所有指标 |

### 重要提示

- **`indicator` 命令自包含**：自动获取财务数据和市值，无需先调用 `info`/`financial`
- **避免冗余**：查询单个指标时只执行 `indicator`，不要执行 `analyze`
- **`analyze` 适用场景**：用户明确要求"完整分析"、"全面分析"时使用

---

## CLI 命令

| 命令 | 说明 |
|------|------|
| `info <code>` | 个股信息 |
| `hist <code> [--end YYYYMMDD]` | 历史行情 |
| `financial <code> [--end YYYY]` | 财务数据 |
| `indicator <name> -s <code>` | 计算指标 |
| `analyze <code>` | 完整分析 |
| `list` | 指标列表 |

### 市场代码格式

- A股: 6位数字 (600519)
- 港股: 5位数字 (00700)
- 美股: 字母 (AAPL)

---

## 指标体系

### 自研计算指标

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

## 市场参考文档

详细字段说明按市场分文档：

- **A股**: [references/a-stock.md](references/a-stock.md)
- **港股**: [references/hk-stock.md](references/hk-stock.md)
- **美股**: [references/us-stock.md](references/us-stock.md)

---

## 缓存策略

| 数据类型 | A股 | 港股/美股 |
|----------|-----|-----------|
| 个股信息 | 次日凌晨 | 次年6月底 |
| 历史数据 | 1年 | - |
| 财务数据 | 次年6月底 | - |

缓存支持范围复用: 缓存[2015-2024]可服务于[2020-2024]查询。
