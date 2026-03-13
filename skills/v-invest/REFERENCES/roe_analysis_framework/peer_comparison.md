# 同业对比分析

将目标公司与同业公司进行对比，识别竞争优势和差距。

## 工作流程

### Step 1: 获取目标公司数据

```bash
v-invest indicator "roe,roa,net_profit_margin,total_assets_turnover,equity_multiplier" -s {目标代码} -m {市场} -y 5
```

### Step 2: 获取同业公司数据

```bash
v-invest indicator "roe,roa,net_profit_margin,total_assets_turnover,equity_multiplier" -s {同业A代码} -m {市场} -y 5
v-invest indicator "roe,roa,net_profit_margin,total_assets_turnover,equity_multiplier" -s {同业B代码} -m {市场} -y 5
```

### Step 3: 对比分析

### Step 4: 输出结论

---

## 数据获取命令

```bash
# 目标公司
v-invest indicator "roe,roa,net_profit_margin,total_assets_turnover,equity_multiplier" -s 00700 -m HK -y 5

# 同业公司（港股示例）
v-invest indicator "roe,roa,net_profit_margin,total_assets_turnover,equity_multiplier" -s 09988 -m HK -y 5
```

---

## 同业选择原则

1. **主营业务相似**: 产品/服务相近
2. **规模相当**: 市值在同一数量级
3. **可比的商业模式**: 毛利率、周转率特征相似

---

## 分析框架

### 1. 核心指标对比

| 公司 | ROE | 净利润率 | 周转率 | 权益乘数 | 负债率 |
|------|-----|---------|--------|---------|--------|
| 目标公司 | {x}% | {x}% | {x} | {x} | {x}% |
| 同业A | {x}% | {x}% | {x} | {x} | {x}% |
| 同业B | {x}% | {x}% | {x} | {x} | {x}% |

### 2. 驱动因素拆解

- **净利润率驱动**: 高毛利、高费用效率
- **周转率驱动**: 运营效率高
- **杠杆驱动**: 适度负债

### 3. 竞争优势识别

| 优势类型 | 表现 | 验证 |
|----------|------|------|
| 成本优势 | 毛利率高于同业 | 供应链分析 |
| 品牌溢价 | 定价高于同业 | 市场定位 |
| 运营效率 | 周转快于同业 | 资产利用率 |
| 财务稳健 | 负债率低于同业 | 偿债能力 |

---

## 输出模板

按以下结构整理：

### 同业对比

- 目标公司 vs 同业A vs 同业B
- 核心指标对比表
- 竞争优势/差距分析
