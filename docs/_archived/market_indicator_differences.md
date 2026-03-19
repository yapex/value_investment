# A 股、港股、美股指标差异对齐

**更新**: 2026-03-06 | **项目**: 价值投资分析工具

---

## 一、快速参考

### 1.1 市场识别

| 市场 | 代码格式 | 示例 |
|-----|---------|------|
| A 股 | 6 位数字 (0/3/6 开头) | 600519, 000001 |
| 港股 | 5 位数字 | 00700, 09988 |
| 美股 | 字母代码 | AAPL, TSLA |

### 1.2 核心差异速览

| 维度 | A 股 | 港股 | 美股 |
|-----|-----|------|------|
| **财务指标** | 140+ 字段 | 21 字段 | 47 字段 |
| **报表格式** | 宽表 | 长表→宽表 | 长表→宽表 |
| **PE/PB** | 手动计算 | API 返回 | API 返回 |
| **货币** | 人民币 | 港元 (×0.88 转 CNY) | 美元 |
| **特有指标** | 银行/保险专用 | 股息/派息率 | 英文字段 |

---

## 二、核心字段映射 (IFRS 标准)

### 2.1 利润表

| 标准字段 | A 股 | 港股 | 美股 |
|---------|-----|------|------|
| total_revenue | 营业总收入 | 收益 | totalRevenue |
| net_profit | 净利润 | 期内溢利 | netIncome |
| operating_profit | 营业利润 | 营业溢利 | operatingIncome |
| gross_profit | 毛利 | 毛利 | grossProfit |
| operating_cost | 营业成本 | 已售存货成本 | costOfRevenue |

### 2.2 资产负债表

| 标准字段 | A 股 | 港股 | 美股 |
|---------|-----|------|------|
| total_assets | 资产总计 | 资产总值 | totalAssets |
| total_equity | 股东权益合计 | 权益总额 | totalStockholdersEquity |
| total_liabilities | 负债合计 | 总负债 | totalLiabilities |
| cash_and_equivalents | 货币资金 | 现金及等价物 | cashAndCashEquivalents |
| inventory | 存货 | 存货 | inventory |

### 2.3 现金流量表

| 标准字段 | A 股 | 港股 | 美股 |
|---------|-----|------|------|
| operating_cash_flow | 经营活动现金流量净额 | 经营业务现金净额 | operatingCashFlow |
| investing_cash_flow | 投资活动现金流量净额 | 投资业务现金净额 | investingCashFlow |
| financing_cash_flow | 筹资活动现金流量净额 | 融资业务现金净额 | financingCashFlow |

### 2.4 关键比率

| 标准字段 | A 股 | 港股 | 美股 |
|---------|-----|------|------|
| roe | 净资产收益率 (%) | 股东权益回报率 (%) | returnOnEquity |
| roa | 总资产收益率 (%) | 总资产回报率 (%) | returnOnAssets |
| gross_margin | 销售毛利率 (%) | 毛利率 | grossMargin |
| net_profit_margin | 销售净利率 (%) | 销售净利率 (%) | netProfitMargin |
| current_ratio | 流动比率 | 流动比率 | currentRatio |
| quick_ratio | 速动比率 | 速动比率 | quickRatio |
| debt_ratio | 资产负债率 (%) | 资产负债率 | debtToAssetsRatio |

### 2.5 估值与每股指标

| 标准字段 | A 股 | 港股 | 美股 |
|---------|-----|------|------|
| pe_ratio | 市盈率 | 市盈率 | peRatio |
| pb_ratio | 市净率 | 市净率 | pbRatio |
| basic_eps | 基本每股收益 | 基本每股收益 (元) | basicEps |
| book_value_per_share | 每股净资产 | 每股净资产 (元) | bookValuePerShare |

---

## 三、市场特有指标

### 3.1 港股特有 (13 个)

| 指标 | 字段 | 说明 |
|-----|------|------|
| hk_dividend_yield | 股息率 TTM(%) | 股息率 |
| hk_payout_ratio | 派息比率 (%) | 派息比例 |
| hk_dividend_per_share | 每股股息 TTM(港元) | 每股股息 |
| hk_legal_capital | 法定股本 (股) | 法定股本 |
| hk_issued_shares | 已发行股本 (股) | 总股本 |
| hk_h_shares | 已发行股本-H 股 (股) | H 股部分 |
| hk_market_cap | 港股市值 (港元) | 港元市值 |
| hk_revenue_growth | 营业总收入滚动环比增长 (%) | 营收环比 |
| hk_net_profit_growth | 净利润滚动环比增长 (%) | 净利环比 |

### 3.2 A 股特有

- **银行指标** (28 个): 不良贷款率、拨备覆盖率、资本充足率等
- **保险指标** (7 个): 保费收入、偿付能力充足率等
- **增长指标**: 基本每股收益同比增长、扣非净利润同比增长等
- **运营指标**: 人均营收、预付账款占比等

### 3.3 美股特有

| 原始字段 | 标准字段 | 说明 |
|---------|---------|------|
| ROE_AVG | roe | 平均 ROE |
| PARENT_HOLDER_NETPROFIT | net_profit | 归属净利润 |
| DEBT_ASSET_RATIO | debt_ratio | 资产负债率 |
| CURRENT_RATIO | current_ratio | 流动比率 |

---

## 四、指标计算层

### 4.1 设计原则

**所有指标使用 IFRS 标准字段计算，市场差异在 DataMapper 层处理**

```python
# ROE 示例 - 三市场通用
class ROEIndicator(BaseIndicator):
    def calculate(self, data: pd.DataFrame) -> IndicatorResult:
        net_profit = data['net_profit']      # 标准字段
        equity = data['total_equity']        # 标准字段
        roe = (net_profit / equity) * 100
```

### 4.2 市场特有处理

```python
# 市值计算 - 需要货币转换
if market == "HK":
    market_cap = hk_market_cap * 0.88  # 港元→人民币
elif market == "US":
    market_cap = us_market_cap         # 美元
else:
    market_cap = a_market_cap          # 人民币
```

---

## 五、数据获取

### 5.1 Provider 接口

| 数据类型 | A 股 | 港股 | 美股 |
|---------|-----|------|------|
| **股票信息** | stock_individual_info_em | stock_hk_company_profile_em | stock_individual_basic_info_us_xq |
| **历史价格** | stock_zh_a_hist_tx | stock_hk_daily | stock_us_daily |
| **资产负债表** | stock_balance_sheet_by_yearly_em | stock_financial_hk_report_em | stock_financial_us_report_em |
| **利润表** | stock_profit_sheet_by_yearly_em | stock_financial_hk_report_em | stock_financial_us_report_em |
| **财务指标** | stock_financial_analysis_indicator_em | stock_hk_financial_indicator_em | stock_financial_us_analysis_indicator_em |

### 5.2 缓存策略

| 数据类型 | TTL |
|---------|-----|
| 股票信息 | 次日凌晨 (A 股) / 次年 6 月底 (港/美) |
| 历史价格 | 1 年 |
| 财务报表 | 次年 6 月底 |
| 财务指标 | 1 年 (A 股) / 次年 6 月底 (港/美) |

---

## 六、使用示例

```python
from value_investment import ValueInvestment

# 自动识别市场
vi = ValueInvestment()

# 获取标准化数据 (字段已映射为 IFRS)
balance = vi.get_balance_sheet("600519")  # A 股
balance_hk = vi.get_balance_sheet("00700", market="HK")
balance_us = vi.get_balance_sheet("AAPL", market="US")

# 计算指标 (三市场通用)
roe = vi.calculate_indicator("ROE", "600519")
roe_hk = vi.calculate_indicator("ROE", "00700")
roe_us = vi.calculate_indicator("ROE", "AAPL")

# 市场特有指标
dividend_hk = vi.calculate_indicator("hk_dividend_yield", "00700")
```

---

## 七、开发参考

### 7.1 添加新指标

1. 优先使用 `CORE_FIELD_MAPPING` 中的标准字段
2. 市场特有字段添加到 `HK_SPECIFIC_INDICATORS` 或对应映射
3. 计算指标使用 `BaseIndicator._find_column()` 自动匹配

### 7.2 扩展字段映射

```python
# src/value_investment/data/mapper.py
CORE_FIELD_MAPPING["new_field"] = {
    "A 股": "A 股字段名",
    "港股": "港股字段名",
    "美股": "美股字段名",
}
```

### 7.3 关键文件

| 文件 | 说明 |
|-----|------|
| `data/mapper.py` | CORE_FIELD_MAPPING, DataMapper |
| `indicators/registry.py` | 指标注册，HK_SPECIFIC_INDICATORS |
| `data/providers/*_provider.py` | 三市场 Provider 实现 |
| `api.py` | ValueInvestment API 入口 |

---

## 附录：指标覆盖对比

| 类别 | A 股 | 港股 | 美股 |
|-----|:---:|:---:|:---:|
| 每股收益 | ✓ | ✓ | ✓ |
| 每股净资产 | ✓ | ✓ | - |
| 每股经营现金流 | ✓ | ✓ | - |
| 营收/净利润 | ✓ | ✓ | ✓ |
| ROE/ROA | ✓ | ✓ | ✓ |
| 毛利率/净利率 | ✓ | ✓ | ✓ |
| 流动/速动比率 | ✓ | ✓ | ✓ |
| 资产负债率 | ✓ | ✓ | ✓ |
| 周转率指标 | ✓ | ✓ | ✓ |
| 市盈率/市净率 | 计算 | ✓ | - |
| 股息率 | - | ✓ | - |
| 银行/保险专用 | ✓ | - | - |
