# Pipeline 架构详解

> 本文档是 [开发者指南](./developer-guide.md) 的详细参考，涵盖架构细节、设计决策和实现细节。

---

## 目录

1. [核心组件](#1-核心组件)
2. [数据流](#2-数据流)
3. [9 Handler 矩阵](#3-9-handler-矩阵)
4. [字段体系](#4-字段体系)
5. [Calculator 机制](#5-calculator-机制)
6. [依赖注入](#6-依赖注入)
7. [验证机制](#7-验证机制)

---

## 1. 核心组件

### 1.1 PipelineAPI

高层入口，负责：
- 接收用户请求
- 扩展字段依赖
- 调用 MessageBus
- 应用 Calculator

```python
from value_investment.pipeline.api import PipelineAPI

api = PipelineAPI()
result = await api.get_data(
    symbol="600519",
    fields=["roe", "roic"],
    end="2024",
    years=10,
    market="A股",
)
```

### 1.2 MessageBus

消息总线，负责 Handler 的调度：

```python
class MessageBus:
    def process(self, message: Message) -> Any:
        while message.require:
            for handler in self.handlers:
                await handler.handle(message)
```

特点：
- **多轮执行**：直到 `message.require` 为空或无进展
- **并行处理**：所有 Handler 都有机会处理消息

### 1.3 Message

消息对象，携带请求上下文：

```python
@dataclass
class Message:
    symbol: str           # 股票代码
    market: str           # 市场 (A股/港股/美股)
    end: str             # 结束日期
    years: int           # 年数
    require: set[str]    # 需要的字段
    results: dict         # 结果 {field: {year: value}}
```

### 1.4 Container

依赖注入容器，使用 `dependency-injector`：

```python
class Container(containers.DeclarativeContainer):
    bus = providers.Singleton(MessageBus)
    tushare_provider = providers.Singleton(TushareProvider, ...)
    # ... 9 个 Handler
```

---

## 2. 数据流

```
用户请求
    ↓
PipelineAPI.get_data()
    ↓
┌─────────────────────────────────────────┐
│  Step 1: 扩展字段依赖                    │
│  Calculator.required_fields → require   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Step 2: MessageBus.process()           │
│  多轮执行，每个 Handler 尝试处理消息    │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Step 3: 应用 Calculator                │
│  根据 results 计算派生字段              │
└─────────────────────────────────────────┘
    ↓
返回 {field: {year: value}}
```

---

## 3. 9 Handler 矩阵

| 市场 | 财务报表 | 财务指标 | 市值数据 |
|-----|---------|---------|---------|
| A股 | AStatement | AIndicator | AMarket |
| 港股 | HKStatement | HKIndicator | HKMarket |
| 美股 | USStatement | USIndicator | USMarket |

### 3.1 Handler 结构

```python
class BaseHandler:
    target_market: str        # 目标市场
    data_type: str            # 数据类型
    can_handle: set[str]      # 能处理的字段
    provider: DataProvider    # 数据源
    
    async def handle(self, message: Message) -> None:
        # 检查是否目标市场
        # 检查是否有需要的字段
        # 调用 provider 获取数据
        # 填充 message.results
```

### 3.2 Handler 文件位置

```
src/value_investment/
├── handlers/
│   ├── a_share.py       # A股 3 Handler
│   ├── hk_share.py       # 港股 3 Handler
│   └── us_share.py       # 美股 3 Handler
```

### 3.3 数据类型对应

| Handler | 数据来源 | 说明 |
|---------|---------|------|
| StatementHandler | `fetch_financial_statement()` | 资产负债表、利润表、现金流量表 |
| IndicatorHandler | `fetch_financial_indicator()` | ROE、ROA、毛利率等指标 |
| MarketHandler | `fetch_market_data()` | 市值、PE、PB |

---

## 4. 字段体系

### 4.1 IFRSFields

国际标准字段，定义在 `domain/fields.py`：

```python
class IFRSFields(metaclass=IFRSFieldsMeta):
    """已冻结，禁止添加新字段"""
    TOTAL_ASSETS = "total_assets"
    TOTAL_EQUITY = "total_equity"
    NET_PROFIT = "net_profit"
    # ...
```

**规则**：
- 冻结后禁止添加新字段
- 新字段必须添加到 `CustomFields`

### 4.2 CustomFields

自定义字段，通过 Calculator 计算：

```python
class CustomFields:
    ROIC = "roic"
    GROSS_MARGIN = "gross_margin"
    # ...
```

### 4.3 字段分类

| 类型 | 来源 | 示例 |
|-----|------|------|
| 原始字段 | Provider 直接获取 | `total_assets`, `net_profit` |
| 指标字段 | Provider 计算返回 | `roe`, `pe_ratio` |
| 派生字段 | Calculator 计算 | `roic`, `gross_margin` |

---

## 5. Calculator 机制

### 5.1 Calculator 文件

```python
# calculators/calc_xxx.py

name = "my_metric"
required_fields = ["field_a", "field_b"]

def calculate(results):
    # results: {field: {year: value}}
    a = results.get("field_a", {})
    b = results.get("field_b", {})
    return {
        year: a.get(year, 0) / b.get(year, 1)
        for year in a
    }
```

### 5.2 加载机制

```
load_builtin_calculators()
    ↓
1. 包内 calculators/ (package://)
2. 项目 calculators/ (项目根目录)
3. 用户 calculators/ ({cwd}/calculators)
```

优先级：3 > 2 > 1（后者覆盖前者）

### 5.3 依赖扩展

```python
# PipelineAPI._expand_required_fields()
for field in message.require:
    if field in CALCULATOR_MAP:
        message.require.update(
            CALCULATOR_MAP[field].required_fields
        )
```

---

## 6. 依赖注入

### 6.1 Provider 注入

```
Container
    ├── tushare_provider → TushareProvider (A股)
    ├── hk_provider → HKProvider (港股)
    └── us_provider → USProvider (美股)
```

### 6.2 Handler 注入

```
Container
    ├── a_share_statement_handler → AShareStatementHandler(tushare_provider)
    ├── a_share_indicator_handler → AShareIndicatorHandler(tushare_provider)
    └── ...
```

### 6.3 Container 单例

```python
Container._instance = None  # 类变量
container = Container.create()  # 创建或返回单例
```

---

## 7. 验证机制

### 7.1 Validator

```python
from value_investment.pipeline.validator import validate_pipeline

report = validate_pipeline(
    fields=["roic", "roe"],
    symbol="600519",
    market="A股",
)
print(report.summary())
```

### 7.2 验证内容

| 检查项 | 说明 |
|-------|------|
| 字段注册 | 字段是否在 `ALL_FIELDS` 中 |
| Handler 支持 | 是否有 Handler 能提供字段 |
| Calculator 依赖 | Calculator 的 `required_fields` 是否满足 |
| 市场覆盖 | 该市场的 Handler 是否完整 |

### 7.3 CLI 验证

```bash
# Dry run，不获取数据
v-invest validate 600519 --requires implied_growth
```

---

## 相关文档

- [开发者指南](./developer-guide.md) - 快速上手
- [IFRS 标准字段](./ifrs_standard_fields.md) - 字段定义
