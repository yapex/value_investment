# 数据 Schema 规范 (Data Schema Specification)

## 1. 核心理念：标准财务模型 (SFM)

为了消除 A 股、港股、美股之间原始字段名的差异，系统引入 **BaseFinancialSchema** 作为全市场的“协议中心”。所有计算指标仅面向此 Schema 编写，不直接感知底层数据源。

### 1.1 定义位置
*   **代码位置**: `src/value_investment/data/schemas.py`
*   **技术选型**: `Pandera (SchemaModel)`

---

## 2. 设计与推导逻辑 (Derivation Logic)

`BaseFinancialSchema` 并非凭空想象，而是通过 **“双向对标”** 推导得出的：

### 2.1 自顶向下 (Top-Down): 指标需求驱动
分析核心指标（ROE, ROIC, CAGR, DCF）所需的计算因子：
*   **盈利分析**: 需要 `net_profit`, `revenue`, `operating_profit`。
*   **资本效率**: 需要 `total_equity`, `invested_capital` (涉及有息负债与现金)。
*   **现金流质量**: 需要 `operating_cash_flow`, `capital_expenditure` (CAPEX)。

### 2.2 自底向上 (Bottom-Up): 市场交集驱动
对标 A 股 (CAS)、港股 (IFRS)、美股 (US GAAP) 的 API 返回值，提取语义交集：
*   **CAS `净利润`** ↔ **IFRS `期内溢利`** ↔ **GAAP `Net Income`** ➔ 映射为标准字段 `net_profit`。

---

## 3. 分层设计 (Layering)

### 3.1 基础层: BaseFinancialSchema (Canonical)
包含 80% 跨市场通用的核心会计科目。
*   **校验规则**: 强制执行会计恒等式（如 `资产 = 负债 + 权益`）。
*   **Token 优化**: 设置 `strict="filter"`，自动剔除未定义的冗余原始列。

### 3.2 扩展层: MarketSpecificSchema
针对特定市场的会计准则差异进行扩展：
*   **AShareSchema**: 增加 `deducted_net_profit` (扣非净利润)。
*   **HKShareSchema**: 增加 `profit_attributable_to_owners` (股东应占溢利)。

---

## 4. 工作原理 (Working Principle)

1.  **拦截与验证**: Adapter 获取原始数据并经 DataMapper 映射后，立即调用 `Schema.validate(df)`。
2.  **强制转换 (Coercion)**: 自动将字符串、缺失值等“脏数据”转换为标准浮点数或日期。
3.  **零防御计算**: 经过校验的 DataFrame 进入指标层。指标函数不再需要处理 `KeyError` 或空值判断，代码实现回归数学本质。

---

## 5. Token 效率保障 (Agent-Friendly)

通过 Pandera 的 **Strict Filtering** 机制：
*   原始 API 可能返回 100+ 列数据。
*   Schema 仅定义计算所需的 15-20 个核心字段。
*   校验后，冗余的 80+ 列将被自动丢弃，大幅降低传给 Agent 的上下文 Token 消耗。
