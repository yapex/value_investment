# A股 vs 港股 财务指标差异对比

**更新**: 2026-03-11 | **对比股票**: A股(600519 贵州茅台) vs 港股(00700 腾讯控股)

---

## 一、数据规模对比

| 指标类型           | A股 (600519 茅台)       | 港股 (00700 腾讯) |
|-------------------|-------------------------|-------------------|
| 财务指标字段数     | 104 个                  | **21** 个             |
| 数据年份           | 55 个报告期             | 1 个报告期        |
| 共同标准字段       | -                       | 5 个              |

> **2026-03-11 实施更新**: 港股新增4个计算指标（毛利率、资产负债率、流动比率、速动比率），字段数从17增加到21

---

## 二、字段对比 (已标准化为统一格式)

| 指标               | A股字段                      | 港股字段                      | 状态 |
|-------------------|-----------------------------|------------------------------|------|
| 基础指标           | basic_eps                  | basic_eps                    | ✅ 共同 |
| 每股净资产         | book_value_per_share       | book_value_per_share         | ✅ |
| 每股经营现金流     | operating_cash_flow_per_share | operating_cash_flow_per_share | ✅ 共同 |
| ROE               | roe                        | roe                          | ✅ 共同 |
| ROA               | roa                        | roa                          | ✅ 共同 |
| 毛利率             | gross_profit_margin        | gross_profit_margin          | ✅ 新增 |
| 净利率             | net_profit_margin          | net_profit_margin            | ✅ 共同 |
| 流动比率           | current_ratio              | current_ratio                | ✅ 新增 |
| 速动比率           | quick_ratio                | quick_ratio                  | ✅ 新增 |
| 现金比率           | cash_ratio                 | cash_ratio                  | ✅ |
| 资产负债率         | debt_ratio                 | debt_ratio                   | ✅ 新增 |
| PE                | -                          | pe_ratio                     | 港股独有 |
| PB                | -                          | pb_ratio                     | 港股独有 |
| 股息率             | -                          | hk_dividend_yield_ttm      | 港股独有 |
| 派息比率           | -                          | hk_dividend_payout_ratio    | 港股独有 |
| 市值(港币)         | -                          | hk_market_cap               | 港股独有 |
| 营收增长(环比)     | -                          | hk_total_revenue_growth_qoq | 港股独有 |
| 净利润增长(环比)   | -                          | hk_net_profit_growth_qoq   | 港股独有 |

---

## 三、A股独有指标 (87个)

### 3.1 每股指标
- diluted_eps (稀释每股收益)
- total_revenue_per_share (每股总收入)
- capital_reserve_per_share (每股资本公积)
- surplus_reserve_per_share (每股盈余公积)
- undistributed_profit_per_share (每股未分配利润)

### 3.2 盈利能力
- extraordinary_item (营业外收支净额)
- deducted_net_profit (扣非净利润)
- gross_profit_margin (毛利率)

### 3.3 营运能力
- quick_ratio (速动比率)
- cash_ratio (现金比率)
- receivables_turnover (应收账款周转率)
- current_assets_turnover (流动资产周转率)
- fixed_assets_turnover (固定资产周转率)
- total_assets_turnover (总资产周转率)
- operating_cycle_days (营业周期)

### 3.4 估值/现金流
- ebit (息税前利润)
- ebitda (息税折旧摊销前利润)
- fcff (企业自由现金流)
- fcfe (股东自由现金流)
- interest_bearing_debt (带息负债)
- net_debt (净负债)

### 3.5 杜邦分析
- equity_multiplier (权益乘数)
- roic (投资资本回报率)
- roe_weighted_avg (加权平均ROE)
- roe_diluted (稀释ROE)

### 3.6 增长指标 (YoY)
- basic_eps_yoy (每股收益同比增长)
- net_profit_yoy (净利润同比增长)
- total_assets_yoy (总资产同比增长)
- ... 等

---

## 四、港股独有指标 (8个)

| 指标                       | 字段                          | 说明              | 状态 |
|---------------------------|------------------------------|------------------|------|
| 法定股本                   | hk_legal_shares             | 股份数量         | ✅ |
| 每股股息                   | hk_dividend_per_share       | 港元/股          | ✅ |
| 派息比率                   | hk_dividend_payout_ratio    | %                | ✅ |
| 股息率 TTM                 | hk_dividend_yield_ttm      | %                | ✅ |
| 港股市值                   | hk_market_cap               | 港元             | ✅ |
| 营收环比增长               | hk_total_revenue_growth_qoq | %                | ✅ |
| 净利润环比增长             | hk_net_profit_growth_qoq   | %                | ✅ |
| 总股本                     | total_shares                | 股               | ✅ |

---

## 五、关键差异总结

| 差异维度         | A股                                    | 港股              |
|----------------|----------------------------------------|-------------------|
| 指标数量        | 101 个字段                             | 17 个字段         |
| 共同字段        | 5 个 (basic_eps, roe, roa, net_profit_margin, operating_cash_flow_per_share) |
| 数据深度        | 55 个报告期 (多年历史)                | 1 个报告期        |
| 货币单位        | 人民币                                | 港元              |
| PE/PB 计算     | 需手动计算                            | API 返回          |
| 估值指标        | 需从市值计算                          | 直接提供          |
| 特有指标        | 银行/保险专用、增长类                 | 股息类            |
| 增长率          | YOY (同比增长)                        | QoQ (环比)        |

---

## 六、实施成果 (2026-03-11)

### 6.1 完成的字段对齐

| 阶段 | 任务 | 字段数 | 状态 |
|------|------|--------|------|
| 第一阶段 | 核心指标对齐 | 8 | ✅ |
| 第二阶段 | 扩展指标对齐 | 10 | ✅ |
| 第三阶段 | 特色指标对齐 | 8 | ✅ |
| 集成测试 | 端到端验证 | - | ✅ |

### 6.2 测试验证结果

```
测试通过: 44 个测试用例全部通过

A股字段数: 101
港股字段数: 17
共同字段数: 5 (basic_eps, roe, roa, net_profit_margin, operating_cash_flow_per_share)
```

### 6.3 核心修改

1. **data/mapper.py**: 修改 `get_standard_field()` 方法，支持标准字段名透传
   - 港股 API 返回英文标准字段名时自动透传
   - 找不到映射时返回原字段名

2. **tests/test_field_mapping.py**: 新增 38 个测试用例
   - 覆盖利润表、资产负债表、现金流量表
   - 覆盖关键比率、每股指标、营运能力
   - 覆盖港股特有指标
   - 跨市场集成测试

---

## 七、核心结论

### 1. A股财务指标更丰富
- 101个字段 vs 港股17个字段
- 包含银行/保险专用指标
- 多年历史数据可追溯

### 2. 港股特色指标
- **股息相关**: hk_dividend_yield_ttm, hk_dividend_payout_ratio
- **估值指标**: pe_ratio, pb_ratio (A股需计算)
- **市值**: hk_market_cap (直接获取港币市值)

### 3. 数据频率差异
- A股: 支持 YoY (同比增长) 分析
- 港股: 仅支持 QoQ (环比增长) 分析

### 4. 计算需求
- A股计算 PE/PB: 需要手动用市值/净利润
- 港股计算: API 直接返回 pe_ratio, pb_ratio

---

## 八、使用建议

### 8.1 A股分析优势
```python
# 使用A股丰富的指标
vi = ValueInvestment(market="A")
data = vi.get_financial_indicator("600519")

# 计算ROE趋势
data['roe_yoy']  # 同比增长
data['roe']       # 本期值
```

### 8.2 港股分析优势
```python
# 使用港股特有的股息指标
vi = ValueInvestment(market="HK")
data = vi.get_financial_indicator("00700")

# 直接获取PE/PB
pe = data['pe_ratio']  # 市盈率
pb = data['pb_ratio']  # 市净率

# 获取股息信息
dividend_yield = data['hk_dividend_yield_ttm']  # 股息率
payout_ratio = data['hk_dividend_payout_ratio']  # 派息比率
```

### 8.3 跨市场对比注意事项

1. **货币转换**: 港股市值需 ×0.88 转换为人民币
2. **字段映射**: 使用 `DataMapper.get_standard_field()` 标准化字段名
3. **时间对齐**: A股用 YoY，港股用 QoQ
4. **共同字段**: 使用 5 个共同字段进行跨市场对比

---

## 九、相关文档

- [market_indicator_differences.md](./market_indicator_differences.md) - 三市场指标差异对齐
- [ifrs_standard_fields.md](./ifrs_standard_fields.md) - IFRS 标准字段映射
- [deprecated_akshare_a_share.md](./deprecated_akshare_a_share.md) - AKShare 废弃说明
- [plans/2026-03-11-a-hk-indicator-alignment.md](./plans/2026-03-11-a-hk-indicator-alignment.md) - 字段对齐实施计划
