---
name: value-forge
description: 财务分析技能生成器 - 读取分析师文档，自动创建可用于任意股票的分析技能。Use when 用户提供分析文档，需要生成可复用的分析技能。
---

# value-forge

> Meta Skill: 技能生成器，用于将分析师文档转化为可执行的分析技能。

## 快速开始

```
用户: "帮我把 docs/企业财务排雷手册.md 创建为 skill"
```

## 工作流程

### Step 1: 阅读分析师文档
读取用户提供的分析文档，理解其结构和需要的字段。

**重要**：不要用脚本解析字段，直接阅读文档，由agent提取需要的字段。

### Step 2: 提取字段
阅读文档后，手动识别每个分析段需要的字段，整理成字段清单。

### Step 3: 创建新 Skill 目录
默认在 `.pi/skills/` 下创建新 skill，也可以指定位置

```bash
mkdir -p .pi/skills/{skill-name}
```

### Step 4: 生成 SKILL.md
```markdown
---
name: {skill-name}
description: {从文档中提取的描述}
---

# {文档标题}

## 使用方式
```bash
# 数据获取 - 默认10年
v-invest query {股票} -r "{字段}" -e {年份} -y 10
```

## 执行
读取 REFERENCE.md，按文档格式输出分析报告。
```

### Step 5: 生成 REFERENCE.md
将原始分析师文档内容拷贝进去，直接拷贝，不做任何修改。

---

## 字段提取指南

### 人工提取原则

1. **直接阅读文档**：不要用脚本，每个文档格式不同
2. **关注表格列**：查找"使用字段"、"需要字段"等列
3. **整理字段清单**：按数据类型分组（利润表、资产负债表、现金流量表、财务指标）

### 字段分组示例

```markdown
### 利润表字段
- total_revenue, operating_cost, operating_profit, net_profit
- interest_expense, non_operating_income, investment_income

### 资产负债表字段
- total_assets, total_liabilities, total_equity
- cash_and_equivalents, inventory, accounts_receivable

### 现金流量表字段
- operating_cash_flow, investing_cash_flow, financing_cash_flow

### 财务指标
- roe, gross_margin, debt_ratio, current_ratio
```

---

## 输出

创建完成后，输出：
```
✅ Skill 已创建: .pi/skills/{skill-name}/

包含：
- SKILL.md      # 数据获取指令（默认10年）
- REFERENCE.md  # 分析师文档

使用方式：
"""
用户: "对贵州茅台进行风险扫描"
Skill: 执行 SKILL.md 中的指令（默认10年数据），然后阅读 REFERENCE.md 输出报告
"""
```
