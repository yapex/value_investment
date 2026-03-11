# 项目架构审计与重构计划 (Architecture Audit & Refactoring Plan)

> **参考标准**: [IFRS 标准财务字段参考](ifrs_standard_fields.md)

## 1. 现状审计 (Current State Audit)

### 1.1 SOLID 违规项分析

| 违规项 | 证据 | 影响 |
|--------|------|------|
| **SRP**: `AkshareProvider` 承担抓取、缓存、转换、**业务计算** (`_calculate_pe_pb_for_a`) | 955 行代码 | 难以测试和维护 |
| **SRP**: 每个 `Indicator` 重复 `_find_column` + 候选字段列表 | `simple.py` 12 个指标，每个 30+ 行重复代码 | DRY 违规 |
| **OCP**: if-else 分发市场 | 每个方法 `if market=="A" elif "HK" elif "US"` | 新市场需改核心方法 |
| **LSP**: `kwargs` 反向调用 Provider | `PEPercentileIndicator`, `ImpliedGrowthIndicator`, `LatestMarketCapIndicator` 通过 `kwargs.get('provider')` 破坏 data-passing | 违反架构模式 |
| **DIP**: 缺乏抽象接口 | 无 `IStockProvider`，直接依赖 `AkshareProvider` | 无法替换数据源 |

### 1.2 工程健壮性与稳定性问题

| 问题 | 当前表现 | 风险等级 |
|------|----------|----------|
| **DataFrame 弱契约** | `_find_column` 运行时动态查找，字段不存在时静默返回 0 | 🔴 严重 - 静默错误 |
| **缓存逻辑污染** | TTL 硬编码 (`ttl=86400*365`)，散落各处 | 🟡 中等 |
| **可观测性缺失** | 无结构化日志，计算链路黑盒化 | 🟡 中等 |
| **多币种风险** | 缺乏汇率换算与单位强制标识 | 🟢 低 - 待支持新市场 |

### 1.3 现有资产（未被充分利用）

| 组件 | 状态 | 说明 |
|------|------|------|
| `DataMapper` | **未启用** | 定义了完整 A股→IFRS 映射 (277行)，但 Provider 从未调用 |
| `ifrs_standard_fields.md` | **文档** | 定义了标准字段规范，需作为 Schema 定义依据 |

---

## 2. 目标架构：分层校验管道 (Layered Pipeline)

### 2.1 核心原则：分层校验

```
┌─────────────────────────────────────────────────────────────┐
│  Adapter Layer (宽松)                                        │
│  akshare API → 原始 DataFrame (字段可能缺失/类型错误)        │
│  职责: 数据获取 + 原始字段映射                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Validation Layer (严格)  ← 引入 Pandera                     │
│  Schema 校验: 必要字段存在 + 类型正确 + 业务规则              │
│  失败 → 明确报错 (哪些字段缺失/值异常)                       │
│  职责: 把关契约，过滤脏数据                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Domain Layer (纯净)                                         │
│  Indicator.calculate(data) → 确信数据格式正确                │
│  职责: 纯金融计算，不感知数据源                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 标准财务模型 (SFM)

> **字段标准**: 参见 [IFRS 标准财务字段参考](ifrs_standard_fields.md)

*   **标准化 (Canonical Model)**: 内部统一使用 IFRS 字段 (`net_profit`, `revenue`, `total_equity`)
*   **隔离差异**: Adapter 层处理市场差异，Domain 层只认识 SFM
*   **层级 Schema**:
    *   `CoreFinancialSchema`: 核心字段 (ROE/ROA/毛利率等)
    *   `ExtendedFinancialSchema`: 扩展字段 (ROIC 等复杂指标)

### 2.3 差异化处理

*   **字段回退 (Fallback)**: 在 Adapter 层实现，不在 Indicator 层
*   **策略分发**: 复杂指标 (如 ROIC) 根据市场类型选择计算策略
*   **混合验证**:
    *   **Pandera**: DataFrame 格式校验（必填字段、类型、会计准则）
    *   **Pydantic**: 元数据与配置（`IndicatorMeta`, 市场配置）

### 2.4 Token 效率与 Agent 友好

*   **输出投影**: 支持按需返回字段 (Field Selection)
*   **精简序列化**: 数值精度截断 (2 位小数)，移除冗余元数据
*   **多维模式**: `SUMMARY` (核心指标) / `FULL` (全量历史)

### 2.5 开发规范

*   **TDD 驱动**: Red-Green-Refactor
*   **分支管理**: `feature/refactor-engine`
*   **无副作用**: `Indicator.calculate` 必须是纯函数

---

## 3. 重构战略与层级设计

### 3.1 现有代码复用

*   **激活 `DataMapper`**: 已有完整映射逻辑，需在 Adapter 层调用
*   **复用 `ifrs_standard_fields.md`**: 作为 Pandera Schema 定义依据

### 3.2 接口设计规范

> **原则**: 使用 `Protocol` 而非 `ABC`

| 当前 (违规) | 重构后 |
|------------|--------|
| `class BaseIndicator(ABC)` | `class IIndicator(Protocol)` |
| `class AkshareProvider` | `class IStockProvider(Protocol)` |

**理由**:
- `Protocol` 是静态类型检查工具，不强制继承
- `ABC` 适合需要强制实现的场景，但增加了耦合
- 使用 `Protocol` 可以让类自由选择是否实现接口

### 3.3 新增组件

| 组件 | 职责 |
|------|------|
| `DependencyRegistry` | 声明式依赖注册与自动解析 |
| `FinancialDataSchema` (Pandera) | 校验核心字段存在 + 类型 + 业务规则 |
| `IStockProvider` (Protocol) | 抽象数据源接口，支持多实现 |
| `IIndicator` (Protocol) | 指标接口，使用 Protocol 而非 ABC |
| `CacheConfig` | 缓存策略配置化 |

### 3.3 指标数据依赖分析

#### 指标分类

| 类别 | 指标 | 数据依赖 |
|------|------|----------|
| **纯计算** | ROE, ROA, GrossMargin, NetProfitMargin, CurrentRatio, QuickRatio, DebtRatio, AssetTurnover, InventoryTurnover, ReceivableTurnover, PayableTurnover, CfoToNetprofit, FcfToRevenue, CAGR, ROIC | 只用合并后的财务报表 |
| **需要额外数据** | LatestMarketCap, ImpliedGrowth, PEPct | 需要 Provider 逆向调用（违规） |

#### Provider 逆向调用的指标（需重构）

| 指标 | 当前需要的 Provider 方法 | 重构后 |
|------|------------------------|--------|
| `LatestMarketCapIndicator` | `get_financial_indicator()`, `get_historical_data()` | 声明 `needs = ['stock_info', 'prices']` |
| `ImpliedGrowthIndicator` | 市值（间接调用） | 声明 `needs = ['stock_info']` |
| `PEPercentileIndicator` | `get_quarterly_indicator()`, `get_historical_data()` | 声明 `needs = ['quarterly', 'prices']` |

#### A股 vs 港股字段差异（当前散落各处）

| 财务项 | A股字段 | 港股字段 |
|--------|---------|----------|
| 净利润 | `净利润`, `NET_PROFIT` | `股东应占溢利`, `除税后溢利` |
| 营业收入 | `营业收入`, `OPERATE_INCOME` | `营业额`, `营运收入` |
| 经营现金流 | `经营活动产生的现金流量净额` | `经营业务现金净额` |
| 营业利润 | `营业利润` | `经营溢利` |

**问题**: 这些字段映射逻辑散落在 18 个 Indicator 的 `_find_column` 方法中，DRY 违规。

---

## 4. 落地路线图 (Roadmap)

### 阶段 0: 止血优先 (Quick Wins)

> **原则**: 先修复最痛的问题，再追求架构升级

| 步骤 | 任务 | 工作量 | 优先级 |
|------|------|--------|--------|
| **0.1** | 实现声明式依赖 + 自动注入框架 (`DependencyRegistry`) | 2h | 🔴 P0 |
| **0.2** | 为 3 个违规 Indicator 添加 `needs` 声明 | 1h | 🔴 P0 |
| **0.3** | 激活 `DataMapper`，统一字段映射逻辑（消除 `_find_column` 重复） | 2h | 🔴 P0 |
| **0.4** | 缓存策略配置化 (`CacheConfig`) | 1h | 🟡 P1 |

### 阶段 1: 强契约建立 (Schema & Validation)

| 步骤 | 任务 | 工作量 | 优先级 |
|------|------|--------|--------|
| **1.1** | 定义 `CoreFinancialSchema` (Pandera): 核心必填字段 | 2h | 🔴 P0 |
| **1.2** | 定义 `ExtendedFinancialSchema`: ROIC 等扩展字段 | 1h | 🟡 P1 |
| **1.3** | 实现 Validation Pipeline: Adapter 输出 → Schema 校验 | 2h | 🔴 P0 |
| **1.4** | 移除 Indicator 中的防御性检查 (`_find_column` 替换为直接访问) | 3h | 🟡 P1 |

### 阶段 2: 架构分离 (Adapter & Interface)

| 步骤 | 任务 | 工作量 | 优先级 |
|------|------|--------|--------|
| **2.1** | 提取 `IStockProvider` Protocol 接口 | 1h | 🟡 P1 |
| **2.2** | 拆分 Adapter: `AShareAdapter`, `HKShareAdapter`, `USShareAdapter` | 4-6h | 🟢 P2 |
| **2.3** | 配置化字段映射 (`mapping.yaml`) | 2h | 🟢 P2 |

### 阶段 3: 可观测性与扩展 (Observability)

| 步骤 | 任务 | 工作量 | 优先级 |
|------|------|--------|--------|
| **3.1** | 接入 `structlog` 结构化日志 | 1h | 🟢 P2 |
| **3.2** | 实现指标插件动态加载 | 2h | 🟢 P3 |
| **3.3** | 实现 `CurrencyConverter` (多币种支持) | 2h | 🟢 P3 |

---

## 5. 技术细节

### 5.1 声明式依赖 + 自动注入

#### Indicator 声明

```python
class ROEIndicator(BaseIndicator):
    name = "ROE"
    needs: list[str] = []  # 只需要基础财务数据，已在上下文中

class PEPercentileIndicator(BaseIndicator):
    name = "PEPct"
    needs: list[str] = ['quarterly', 'prices']  # 声明需要季度数据和价格

class LatestMarketCapIndicator(BaseIndicator):
    name = "latest_market_cap"
    needs: list[str] = ['stock_info', 'prices']
```

#### DependencyRegistry 实现

```python
from dataclasses import dataclass
from typing import Callable, Any

class DataProvider:
    """轻量级依赖提供者 - 按 stock_code 获取"""

    def __init__(self, stock_provider):
        self._provider = stock_provider

    def get(self, data_type: str, stock_code: str, **kwargs) -> Any:
        fetchers = {
            'quarterly': lambda: self._provider.get_quarterly_indicator(stock_code),
            'prices': lambda: self._provider.get_historical_data(stock_code, **kwargs),
            'stock_info': lambda: self._provider.get_stock_info(stock_code),
        }
        return fetchers[data_type]()

class DependencyRegistry:
    """依赖注册表 - 映射声明到获取器"""

    def __init__(self, data_provider: DataProvider):
        self._provider = data_provider

    def resolve(self, needs: list[str], stock_code: str, **kwargs) -> dict:
        """根据声明解析依赖"""
        if not needs:
            return {}
        return {n: self._provider.get(n, stock_code, **kwargs) for n in needs}
```

#### API 层使用

```python
class ValueInvestment:
    def __init__(self, ...):
        self._registry = DependencyRegistry(DataProvider(self._provider))

    def calculate_indicator(self, name: str, stock_code: str, **kwargs):
        indicator = self._factory.get(name)

        # 自动注入依赖
        injected = self._registry.resolve(
            getattr(indicator, 'needs', []),
            stock_code,
            **kwargs
        )

        return indicator.calculate(**injected)
```

### 5.2 字段映射：Adapter 层统一处理

```python
class AShareAdapter:
    """A股适配器"""

    def __init__(self, provider: IStockProvider):
        self._provider = provider

    def fetch_and_map(self, stock_code: str, end_year: int) -> pd.DataFrame:
        # 获取原始数据
        balance = self._provider.get_balance_sheet(stock_code, end_year)
        profit = self._provider.get_profit_sheet(stock_code, end_year)
        cashflow = self._provider.get_cashflow_sheet(stock_code, end_year)

        # 统一映射为 IFRS 标准字段
        balance_mapped = DataMapper.map_balance_sheet(balance)
        profit_mapped = DataMapper.map_income_statement(profit)
        cashflow_mapped = DataMapper.map_cash_flow(cashflow)

        # 合并
        return self._merge_and_validate(balance_mapped, profit_mapped, cashflow_mapped)

class HKShareAdapter:
    """港股适配器 - 同样的接口，不同的实现"""

    def fetch_and_map(self, stock_code: str, end_year: int) -> pd.DataFrame:
        # 获取港股原始数据
        balance = self._provider.get_balance_sheet(stock_code, end_year)
        # ... 港股特定处理

        # 映射为 IFRS 标准字段
        balance_mapped = DataMapper.map_balance_sheet(balance)
        # ...
```

### 5.3 Pandera Schema 示例

```python
import pandera as pa
from pandera import Column, Check, DataFrameModel

class CoreFinancialSchema(DataFrameModel):
    """核心财务字段 - 计算 90% 指标所需"""
    year: int = Column(int, Check.greater_than(1990))

    # 必填字段
    net_profit: float = Column(float, nullable=False)
    total_equity: float = Column(float, nullable=False)
    total_assets: float = Column(float, nullable=False)
    revenue: float = Column(float, nullable=False)
    operating_cash_flow: float = Column(float, nullable=True)

    # 业务规则校验
    @pa.check("total_assets")
    def assets_positive(cls, v):
        return (v > 0).all()

    class Config:
        strict = False  # 非必填字段缺失不报错
```

### 5.4 数据流变更

```
旧流程:
Provider → DataFrame → Indicator.calculate(df, provider=xxx)  ❌ 违规

新流程:
Adapter → 原始 DF → DataMapper → SFM DF → Validation (Pandera) → 依赖注入 → Indicator.calculate(**deps)  ✅

Indicator 声明 needs=['quarterly'] → API 层解析 → 自动获取 → 注入
```

---

## 6. 验收标准

*   [ ] 3 个违规 Indicator (`PEPct`, `ImpliedGrowth`, `LatestMarketCap`) 声明 `needs` 依赖
*   [ ] Indicator 不再直接访问 Provider 或 kwargs.get('provider')
*   [ ] 所有 Indicator 使用统一的 Schema 校验
*   [ ] `_find_column` 方法从所有 Indicator 中移除
*   [ ] 字段映射统一在 Adapter 层处理
*   [ ] 新增市场只需配置 `mapping.yaml` + 实现 Adapter
*   [ ] 字段缺失时抛出明确错误，而非静默返回 0
*   [ ] 所有接口使用 `Protocol` 而非 `ABC` (`IIndicator`, `IStockProvider`)
