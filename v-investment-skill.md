# v-invest

A股/港股/美股基本面分析工具，基于akshare数据。

## 快速使用

```bash
v-invest info 600519
v-invest hist 600519 --end 20241231
v-invest financial 600519 --end 2024
v-invest analyze 600519
v-invest indicator ImpliedGrowth -s 600519
```

---

## CLI 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `info <code>` | 个股信息 | `v-invest info 600519` |
| `hist <code>` | 历史行情 | `v-invest hist 600519 --end 20241231` |
| `financial <code>` | 财务数据 | `v-invest financial 600519 --end 2024` |
| `indicator <name> -s <code>` | 计算指标 | `v-invest indicator ImpliedGrowth -s 600519` |
| `analyze <code>` | 完整分析 | `v-invest analyze 600519` |
| `list` | 指标列表 | `v-invest list` |

### 市场代码格式

- A股: 6位数字 (600519)
- 港股: 5位数字 (00700)
- 美股: 字母 (AAPL)

---

## 指标类型

- **RAW**: 原始财务数据 (revenue, net_profit, total_assets)
- **SIMPLE**: 简单计算 (ROE, ROA, gross_margin, net_profit_margin, current_ratio, etc.)
- **COMPLEX**: 复杂计算 (ROIC, CAGR, ImpliedGrowth)

### 常用指标

| 指标 | 说明 |
|------|------|
| `ROE` | 净资产收益率 |
| `ROA` | 总资产收益率 |
| `ROIC` | 投资资本回报率 |
| `gross_margin` | 毛利率 |
| `net_profit_margin` | 净利率 |
| `current_ratio` | 流动比率 |
| `CAGR` | 复合增长率 (支持revenue/net_profit) |
| `cfo_to_netprofit_sum` | 累计净现比 (盈利质量) |
| `ImpliedGrowth` | 市场隐含增长率 |

---

## 缓存策略

- 个股信息: 次日凌晨失效
- 历史数据: 1年
- 财务数据: 次年6月底

缓存支持范围复用: 缓存[2015-2024]可服务于[2020-2024]查询。
