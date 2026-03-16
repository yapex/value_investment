# 七看八问财报分析框架

系统化的企业分析框架：七看财务 + 八问非财务 + 偏见校验 + 标准报告。

## 快速入口

| 模块 | 适用场景 | 文件 |
|------|---------|------|
| **七看财务** | 财务基本面深度分析 | [7_looks_financial.md](./7_looks_financial.md) |
| **八问非财务** | 生意模式/行业/竞争/护城河 | [8_questions_nonfinancial.md](./8_questions_nonfinancial.md) |
| **偏见校验** | 认知偏差自查 | [bias_check.md](./bias_check.md) |
| **报告模板** | 标准化输出格式 | [report_template.md](./report_template.md) |

## 执行流程

```
准备数据 → 七看财务 → 八问非财务 → 偏见校验 → 输出报告
    ↓           ↓           ↓           ↓          ↓
  数据清洗    财务指标     定性分析    自查清单    Markdown
```

## 选择指南

```
分析目标是什么？
    ├─ 仅财务分析 → 7_looks_financial.md
    ├─ 仅定性分析 → 8_questions_nonfinancial.md
    └─ 完整分析 → 按顺序执行全部模块
```

## 核心命令速查

```bash
# 准备阶段：获取基本信息
v-invest info {股票代码}

# 七看：获取多年财务指标
v-invest indicator "roe,roa,gross_margin,net_profit_margin,debt_ratio" -s {股票代码} -m {市场} -y 5

# 七看：获取财务报表
v-invest income {股票代码} -m {市场}
v-invest balance {股票代码} -m {市场}
v-invest cashflow {股票代码} -m {市场}
```

## 常用市场代码

| 市场 | 代码示例 | 参数 |
|:-----|:---------|:-----|
| A股 | 600519 | `-m A` |
| 港股 | 00700 | `-m HK` |
| 美股 | AAPL | `-m US` |

## 数据优先级

```
公司公告 > 金融终端 > 券商研报
```
