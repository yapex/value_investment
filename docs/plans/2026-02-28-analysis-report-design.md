# 财报分析报告生成器设计文档

> **日期:** 2026-02-28
> **目标:** 扩展 analyze 方法，生成结构化 Markdown 分析报告

## 背景

当前 `analyze` 方法只输出指标表格，缺乏：
1. 异常信号检测
2. 结构化分析报告
3. LLM 参与的分析结论

## 目标

1. **新增 9 个指标** - 安全性、成长性、费用分析相关
2. **异常信号检测** - 根据《手把手教你读财报》框架检测危险/警惕信号
3. **Markdown 报告生成** - 通过 sessions_spawn 调用 LLM 生成分析报告

## 架构设计

```
value_investment/
├── src/value_investment/
│   ├── indicators/
│   │   ├── growth.py              # 新增：成长性指标
│   │   ├── safety.py              # 新增：安全性指标
│   │   └── efficiency.py          # 修改：补充固定资产周转率
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── detector.py            # 新增：异常信号检测
│   │   └── reporter.py            # 新增：报告生成器
│   └── api.py                     # 修改：扩展 analyze 方法
```

## 新增 Indicators

### 成长性指标 (growth.py)

| 指标 | 类名 | 计算方式 | 数据来源 |
|------|------|----------|----------|
| `revenue_growth` | RevenueGrowthIndicator | 营业收入同比增长率 | income.OPERATE_INCOME |
| `profit_growth` | ProfitGrowthIndicator | 净利润同比增长率 | income.NETPROFIT |
| `asset_growth` | AssetGrowthIndicator | 总资产同比增长率 | balance.TOTAL_ASSETS |
| `equity_growth` | EquityGrowthIndicator | 净资产同比增长率 | balance.TOTAL_EQUITY |

### 安全性指标 (safety.py)

| 指标 | 类名 | 计算方式 | 数据来源 |
|------|------|----------|----------|
| `cash_to_debt` | CashToDebtIndicator | 货币资金 / 有息负债 | balance.MONETARYFUNDS / (SHORT_LOAN + LONG_LOAN) |
| `debt_ratio_total` | DebtRatioTotalIndicator | 有息负债 / 总资产 | (SHORT_LOAN + LONG_LOAN) / TOTAL_ASSETS |

### 费用指标 (efficiency.py 补充)

| 指标 | 类名 | 计算方式 | 数据来源 |
|------|------|----------|----------|
| `expense_ratio` | ExpenseRatioIndicator | 三费 / 毛利润 | (SALE + MANAGE + FINANCE) / (OPERATE_INCOME - OPERATE_COST) |
| `fee_rate` | FeeRateIndicator | 三费 / 营业收入 | (SALE + MANAGE + FINANCE) / TOTAL_OPERATE_INCOME |
| `fixed_asset_turnover` | FixedAssetTurnoverIndicator | 营业收入 / 固定资产 | OPERATE_INCOME / FIXED_ASSET |

## 异常信号检测 (detector.py)

根据《手把手教你读财报》框架，检测以下信号：

### 危险信号（直接排除）

| 信号 | 检测条件 |
|------|----------|
| 盈利质量异常 | 经营现金流/净利润 连续多年 < 50% |

### 警惕信号

| 信号 | 检测条件 |
|------|----------|
| ROE 偏低 | ROE < 10% |
| 毛利率下降 | 毛利率连续下降 |
| 流动比率低 | 流动比率 < 1 |
| 负债率高 | 资产负债率 > 70% |
| 应收账款增长过快 | 应收增长率 > 收入增长率 * 1.5 |
| 存货增长过快 | 存货增长率 > 成本增长率 * 1.5 |
| 费用率过高 | 三费/毛利润 > 70% |
| 营收增长停滞 | 营收 CAGR < 5% |
| 利润增长停滞 | 净利润 CAGR < 5% |

### 积极信号

| 信号 | 检测条件 |
|------|----------|
| ROE 优秀 | ROE > 20% 且稳定 |
| 毛利率高 | 毛利率 > 40% |
| 盈利质量高 | 经营现金流/净利润 > 120% |
| 现金流健康 | 经营现金流持续为正，投资/筹资为负 |

## 报告生成 (reporter.py)

### 报告结构

```markdown
# {股票名称} 财务分析报告

**分析周期:** {year_range}

## 一、核心指标概览

| 指标 | 最新值 | 评价 |
|------|--------|------|

## 二、安全性分析

- 货币资金/有息负债
- 流动比率、速动比率
- 资产负债率

## 三、盈利能力分析

- ROE、ROA、ROIC
- 毛利率、净利率
- 费用率分析

## 四、成长性分析

- 营收增长率、CAGR
- 净利润增长率、CAGR
- 资产增长率

## 五、盈利质量分析

- 经营现金流/净利润
- 现金流类型

## 六、异常信号

⚠️ 警告列表
✅ 积极信号列表

## 七、综合结论

LLM 生成的分析结论

---
*报告由 AI 生成，仅供参考，不构成投资建议。*
```

### LLM 调用方式

使用 `sessions_spawn` 工具，在 analyze 方法外部调用。

由于 analyze 是同步方法，无法内部调用 sessions_spawn。

**解决方案：**
1. analyze() 返回结构化数据 + warnings + notes
2. 新增 generate_report(data) 方法，由外部调用
3. 或者：analyze(report=True) 时，返回包含 report 的完整结果

## API 变更

### analyze 方法扩展

```python
def analyze(
    self,
    stock_code: str,
    years: int = 10,
    report: bool = False,  # 新增：是否生成报告
    **kwargs,
) -> dict:
    """
    Returns:
        {
            "name": "股票名称",
            "year_range": "2014-2024",
            "table": DataFrame,
            "summary": [...],
            "warnings": [...],   # 新增
            "notes": [...],      # 新增
            "report": "..."      # 新增（report=True时）
        }
    """
```

## 实现计划

1. **Task 1:** 创建 growth.py - 成长性指标
2. **Task 2:** 创建 safety.py - 安全性指标
3. **Task 3:** 补充 efficiency.py - 费用指标
4. **Task 4:** 创建 detector.py - 异常信号检测
5. **Task 5:** 创建 reporter.py - 报告生成器
6. **Task 6:** 修改 api.py - 扩展 analyze 方法
7. **Task 7:** 集成测试 - 验证完整流程

## 验收标准

- [ ] 9 个新指标可独立调用
- [ ] 异常信号检测返回 warnings 和 notes
- [ ] analyze(report=True) 返回 Markdown 报告
- [ ] 报告包含所有章节
- [ ] 测试用例全部通过
