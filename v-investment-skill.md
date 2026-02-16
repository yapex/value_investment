# v-invest

A股/港股/美股基本面分析工具，基于akshare数据。

## 安装

首次使用请先安装工具，详见 [README.md](https://github.com/yapex/value_investment#安装)。

```bash
git clone https://github.com/yapex/value_investment.git
cd value_investment
uv tool install -e .
```

## 场景化使用指南

根据用户需求选择**唯一**需要的命令：

| 用户需求 | 执行命令 | 说明 |
|----------|----------|------|
| 查询股票基本信息 | `v-invest info 600519` | 股票名称、市值、行业等 |
| 查询历史股价 | `v-invest hist 600519 --end 20241231` | 历史行情数据 |
| 查询财务报表 | `v-invest financial 600519 --end 2024` | 资产负债、利润、现金流 |
| 查询单个指标 | `v-invest indicator ROE -s 600519` | **自包含**，无需其他命令 |
| 完整财务分析 | `v-invest analyze 600519` | 一次性计算所有指标 |

### 重要提示

- **`indicator` 命令是自包含的**：会自动获取财务数据和市值，无需先调用 `info`/`financial`
- **避免冗余调用**：用户只需查询单个指标时，只执行 `indicator` 即可，不要执行 `analyze`
- **`analyze` 适用场景**：用户明确要求"完整分析"、"全面分析"时才使用

### 示例

```bash
# 用户问"贵州茅台的ROE是多少" → 只需一个命令
v-invest indicator ROE -s 600519

# 用户问"贵州茅台的隐含增长率" → 只需一个命令
v-invest indicator ImpliedGrowth -s 600519

# 用户问"分析贵州茅台的财务状况" → 使用 analyze
v-invest analyze 600519
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
