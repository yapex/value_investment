# Pipeline 架构重构实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将项目重构为扁平化架构，减少层级，统一命名，提高可维护性

**Architecture:** 采用扁平化 + 领域驱动设计。按功能/市场组织文件，而非按技术分层。Handler 按市场合并到一个文件（类仍独立）。删除重复的 `data/` 和 `pipeline/data/` 目录。

**Tech Stack:** Python, dependency-injector, asyncio, pytest

---

## 目录结构变更

### 变更前 (当前)
```
src/value_investment/
├── __init__.py
├── __main__.py
├── cli.py
├── core/
│   └── constants.py
├── data/
│   ├── __init__.py
│   ├── cache.py
│   ├── mapper.py
│   └── providers/           # 空目录
└── pipeline/
    ├── api.py, container.py, fields.py, validator.py
    ├── bus/
    │   ├── message_bus.py
    │   └── message.py
    ├── calculators/
    │   └── 5个文件
    ├── data/
    │   ├── base_provider.py
    │   ├── provider.py
    │   ├── hk_provider.py, tushare_provider.py, us_provider.py
    │   └── tushare_mapper.py
    └── handlers/
        └── 11个文件 (base_handler.py, base.py + 9个市场Handler)
```

### 变更后 (目标)
```
src/value_investment/
├── __init__.py              # 导出 PipelineAPI
├── __main__.py
├── cli.py                   # CLI
├── core/
│   ├── __init__.py
│   ├── cache.py             # 从 data/ 移入
│   ├── constants.py
│   └── types.py             # Message 类
├── domain/
│   ├── __init__.py
│   ├── fields.py            # 字段定义 (IFRSFields, CustomFields, ALL_FIELDS)
│   └── calculators/         # 计算器
│       ├── __init__.py      # 导出 CALCULATOR_MAP, @calculator
│       ├── base.py          # Calculator 基类
│       ├── gross_profit.py
│       ├── implied_growth.py
│       ├── inventory_turnover.py
│       └── operating_profit_margin.py
├── providers/
│   ├── __init__.py         # 导出所有 Provider
│   ├── base.py              # BaseProvider (Template Method)
│   ├── a_share.py           # TushareProvider + TushareFieldMapper
│   ├── hk_share.py          # HKProvider
│   └── us_share.py          # USProvider
├── handlers/
│   ├── __init__.py         # 导出所有 Handler
│   ├── base.py              # Handler Protocol + BaseHandler
│   ├── a_share.py           # A股: AShareStatementHandler + AShareIndicatorHandler + AShareMarketHandler
│   ├── hk_share.py          # 港股: HKShareStatementHandler + HKShareIndicatorHandler + HKShareMarketHandler
│   └── us_share.py          # 美股: USShareStatementHandler + USShareIndicatorHandler + USShareMarketHandler
├── pipeline/
│   ├── __init__.py
│   ├── api.py               # PipelineAPI
│   ├── bus.py               # MessageBus + Message
│   ├── container.py         # Container (DI)
│   └── validator.py          # validate_pipeline()
└── mapper.py                # CORE_FIELD_MAPPING (从 data/mapper.py 移入)
```

---

## 任务清单

### Phase 1: 基础设施重构

#### Task 1: 创建 core/types.py (Message 类)

**Files:**
- Create: `src/value_investment/core/types.py`

**Step 1: 创建文件**

```python
"""Core types for pipeline"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    """Message class for pipeline"""
    symbol: str
    market: str
    end: str
    years: int
    require: set[str] = field(default_factory=set)
    results: dict[str, dict[int, Any]] = field(default_factory=dict)
    force_refresh: bool = False

    def add_result(self, field_name: str, data: dict[int, Any]) -> None:
        """Add result to results basket"""
        self.results[field_name] = data
        self.require.discard(field_name)
```

**Step 2: 验证导入**

Run: `python -c "from value_investment.core.types import Message; m = Message(symbol='600519', market='A股', end='2024', years=10); print('OK')"`
Expected: OK

**Step 3: 提交**

```bash
git add src/value_investment/core/types.py
git commit -m "feat(core): add Message type"
```

---

#### Task 2: 创建 domain/fields.py

**Files:**
- Create: `src/value_investment/domain/__init__.py`
- Create: `src/value_investment/domain/fields.py`

**Step 1: 创建 domain/__init__.py**

```python
"""Domain layer - core business logic"""
from value_investment.domain.fields import (
    IFRSFields,
    CustomFields,
    ALL_FIELDS,
    validate_fields,
)

__all__ = ["IFRSFields", "CustomFields", "ALL_FIELDS", "validate_fields"]
```

**Step 2: 创建 domain/fields.py (从 pipeline/fields.py 复制)**

从 `src/value_investment/pipeline/fields.py` 复制内容到新文件。

**Step 3: 验证导入**

Run: `python -c "from value_investment.domain.fields import ALL_FIELDS; print(f'Fields count: {len(ALL_FIELDS)}')"`
Expected: Fields count: XX

**Step 4: 提交**

```bash
git add src/value_investment/domain/
git commit -m "feat(domain): add fields module"
```

---

#### Task 3: 创建 domain/calculators/

**Files:**
- Create: `src/value_investment/domain/calculators/__init__.py`
- Create: `src/value_investment/domain/calculators/base.py`
- Create: `src/value_investment/domain/calculators/gross_profit.py`
- Create: `src/value_investment/domain/calculators/implied_growth.py`
- Create: `src/value_investment/domain/calculators/inventory_turnover.py`
- Create: `src/value_investment/domain/calculators/operating_profit_margin.py`

**Step 1: 创建 domain/calculators/__init__.py**

```python
"""Calculators for derived fields"""
from value_investment.domain.calculators.registry import (
    calculator,
    get_registered_calculators,
    instantiate_calculators,
    CALCULATOR_MAP,
)

from value_investment.domain.calculators.gross_profit import GrossProfit
from value_investment.domain.calculators.implied_growth import ImpliedGrowth
from value_investment.domain.calculators.inventory_turnover import InventoryTurnover
from value_investment.domain.calculators.operating_profit_margin import OperatingProfitMargin

ALL_CALCULATORS = instantiate_calculators()
CALCULATOR_MAP = {calc.name: calc for calc in ALL_CALCULATORS}

__all__ = [
    "calculator",
    "GrossProfit",
    "ImpliedGrowth",
    "InventoryTurnover",
    "OperatingProfitMargin",
    "ALL_CALCULATORS",
    "CALCULATOR_MAP",
]
```

**Step 2: 创建 base.py 和其他计算器文件**

从 `src/value_investment/pipeline/calculators/` 复制各文件内容到新位置。

**Step 3: 验证**

Run: `python -c "from value_investment.domain.calculators import CALCULATOR_MAP; print(f'Calculators: {list(CALCULATOR_MAP.keys())}')"`

**Step 4: 提交**

```bash
git add src/value_investment/domain/calculators/
git commit -m "feat(domain): move calculators to domain layer"
```

---

### Phase 2: Providers 重构

#### Task 4: 创建 providers/ 目录

**Files:**
- Create: `src/value_investment/providers/__init__.py`
- Create: `src/value_investment/providers/base.py` (从 pipeline/data/base_provider.py 复制)
- Create: `src/value_investment/providers/a_share.py` (TushareProvider + TushareFieldMapper)
- Create: `src/value_investment/providers/hk_share.py` (HKProvider)
- Create: `src/value_investment/providers/us_share.py` (USProvider)

**Step 1: 创建 providers/__init__.py**

```python
"""Data providers for different markets"""
from value_investment.providers.base import BaseProvider, get_ttl_until_june_next_year
from value_investment.providers.a_share import TushareProvider
from value_investment.providers.hk_share import HKProvider
from value_investment.providers.us_share import USProvider

__all__ = [
    "BaseProvider",
    "get_ttl_until_june_next_year",
    "TushareProvider",
    "HKProvider",
    "USProvider",
]
```

**Step 2: 复制并修改各 Provider 文件**

从 `src/value_investment/pipeline/data/` 复制到 `src/value_investment/providers/`，更新 import 路径。

**Step 3: 验证**

Run: `python -c "from value_investment.providers import TushareProvider, HKProvider, USProvider; print('All providers OK')"`

**Step 4: 提交**

```bash
git add src/value_investment/providers/
git commit -m "feat(providers): restructure providers directory"
```

---

### Phase 3: Handlers 重构 (按市场合并)

#### Task 5: 创建 handlers/ 目录

**Files:**
- Create: `src/value_investment/handlers/__init__.py`
- Create: `src/value_investment/handlers/base.py` (Handler Protocol + BaseHandler)
- Create: `src/value_investment/handlers/a_share.py` (合并 A股 3个 Handler)
- Create: `src/value_investment/handlers/hk_share.py` (合并 港股 3个 Handler)
- Create: `src/value_investment/handlers/us_share.py` (合并 美股 3个 Handler)

**Step 1: 创建 handlers/base.py**

```python
"""Base handler for pipeline"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, set

if TYPE_CHECKING:
    from value_investment.core.types import Message


class Handler(Protocol):
    """Protocol for message handlers"""
    @property
    def can_handle(self) -> set[str]: ...
    async def handle(self, message: "Message") -> None: ...


class BaseHandler(ABC):
    """Base handler with fast-reject pattern"""
    def __init__(self, provider, target_market: str, supported_fields: set[str]):
        self._provider = provider
        self.target_market = target_market
        self._supported_fields = supported_fields

    @property
    def can_handle(self) -> set[str]:
        return self._supported_fields & (
            self._provider.supported_fields if self._provider else set()
        )

    async def handle(self, message: "Message") -> None:
        if message.market != self.target_market:
            return
        if not (message.require & self.can_handle):
            return
        await self._handle_impl(message)

    @abstractmethod
    async def _handle_impl(self, message: "Message") -> None:
        pass
```

**Step 2: 创建 handlers/a_share.py (合并 A股 Handler)**

```python
"""A share (A股) handlers"""
from typing import TYPE_CHECKING

from value_investment.handlers.base import BaseHandler

if TYPE_CHECKING:
    from value_investment.core.types import Message


# A股字段常量
A_SHARE_STATEMENT_FIELDS: set[str] = {
    "total_assets", "total_liabilities", "total_equity",
    "current_assets", "current_liabilities", "cash_and_equivalents",
    "inventory", "accounts_receivable", "accounts_payable",
    "fixed_assets", "prepayment", "contract_assets",
    "contract_liab", "adv_receipts", "total_shares",
    "total_revenue", "net_profit", "operating_profit", "operating_cost",
    "operating_cash_flow", "investing_cash_flow", "financing_cash_flow",
    "capital_expenditure",
}

A_SHARE_INDICATOR_FIELDS: set[str] = {
    "roe", "roa", "gross_margin", "net_profit_margin",
    "current_ratio", "quick_ratio", "debt_ratio",
    "asset_turnover", "receivable_turnover",
}

A_SHARE_MARKET_FIELDS: set[str] = {
    "market_cap", "circ_market_cap", "pe_ratio", "pb_ratio",
    "basic_eps", "diluted_eps", "book_value_per_share",
}


class AShareStatementHandler(BaseHandler):
    """A share statement handler"""
    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_SHARE_STATEMENT_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        if not self._provider:
            return
        to_handle = message.require & self.can_handle
        if not to_handle:
            return
        data = self._provider.fetch_financial_data(
            stock_code=message.symbol,
            fields=to_handle,
            end_year=int(message.end[:4]),
            years=message.years,
        )
        for field, values in data.items():
            if values:
                message.add_result(field, values)


class AShareIndicatorHandler(BaseHandler):
    """A share indicator handler"""
    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_SHARE_INDICATOR_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        # ... 类似实现


class AShareMarketHandler(BaseHandler):
    """A share market handler"""
    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_SHARE_MARKET_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        # ... 类似实现
```

**Step 3: 同样创建 hk_share.py 和 us_share.py**

**Step 4: 创建 handlers/__init__.py**

```python
"""Handlers for different markets"""
from value_investment.handlers.base import Handler, BaseHandler
from value_investment.handlers.a_share import (
    AShareStatementHandler,
    AShareIndicatorHandler,
    AShareMarketHandler,
)
from value_investment.handlers.hk_share import (
    HKShareStatementHandler,
    HKShareIndicatorHandler,
    HKShareMarketHandler,
)
from value_investment.handlers.us_share import (
    USShareStatementHandler,
    USShareIndicatorHandler,
    USShareMarketHandler,
)

__all__ = [
    "Handler",
    "BaseHandler",
    "AShareStatementHandler",
    "AShareIndicatorHandler",
    "AShareMarketHandler",
    "HKShareStatementHandler",
    "HKShareIndicatorHandler",
    "HKShareMarketHandler",
    "USShareStatementHandler",
    "USShareIndicatorHandler",
    "USShareMarketHandler",
]
```

**Step 5: 验证**

Run: `python -c "from value_investment.handlers import AShareStatementHandler; print('Handlers OK')"`

**Step 6: 提交**

```bash
git add src/value_investment/handlers/
git commit -m "feat(handlers): restructure handlers by market"
```

---

### Phase 4: Pipeline 层重构

#### Task 6: 创建 pipeline/ 目录

**Files:**
- Create: `src/value_investment/pipeline/__init__.py`
- Create: `src/value_investment/pipeline/bus.py` (MessageBus + Message)
- Create: `src/value_investment/pipeline/api.py` (更新导入)
- Create: `src/value_investment/pipeline/container.py` (更新导入)
- Create: `src/value_investment/pipeline/validator.py` (更新导入)

**Step 1: 创建 pipeline/bus.py**

```python
"""Message bus for pipeline"""
from typing import Any
from value_investment.core.types import Message


class MessageBus:
    """Message bus for processing messages through handlers"""
    def __init__(self):
        self.handlers: list = []

    def register(self, handler) -> None:
        self.handlers.append(handler)

    async def process(self, message: Message) -> Any:
        while message.require:
            before = len(message.require)
            for handler in self.handlers:
                await handler.handle(message)
            after = len(message.require)
            if before == after:
                break
        return message
```

**Step 2: 更新 api.py, container.py, validator.py**

更新所有 import 路径，从旧位置指向新位置。

**Step 3: 验证**

Run: `python -c "from value_investment import PipelineAPI; print('Pipeline API OK')"`

**Step 4: 提交**

```bash
git add src/value_investment/pipeline/
git commit -m "refactor(pipeline): restructure pipeline layer"
```

---

### Phase 5: 清理与整合

#### Task 7: 更新顶层模块

**Files:**
- Modify: `src/value_investment/__init__.py`
- Create: `src/value_investment/mapper.py` (从 data/mapper.py 复制 CORE_FIELD_MAPPING)
- Modify: `src/value_investment/core/cache.py` (从 data/cache.py 移动)
- Delete: `src/value_investment/data/` 目录
- Delete: `src/value_investment/pipeline/data/` 目录
- Delete: `src/value_investment/pipeline/handlers/` 目录
- Delete: `src/value_investment/pipeline/calculators/` 目录
- Delete: `src/value_investment/pipeline/bus/` 目录
- Delete: `src/value_investment/pipeline/fields.py`

**Step 1: 更新 __init__.py**

```python
"""Value investment analysis tool"""
from value_investment.pipeline.api import PipelineAPI

__all__ = ["PipelineAPI"]
```

**Step 2: 移动 mapper.py 和 cache.py**

```bash
mv src/value_investment/data/mapper.py src/value_investment/mapper.py
mv src/value_investment/data/cache.py src/value_investment/core/cache.py
```

**Step 3: 删除旧目录**

```bash
rm -rf src/value_investment/data/
rm -rf src/value_investment/pipeline/data/
rm -rf src/value_investment/pipeline/handlers/
rm -rf src/value_investment/pipeline/calculators/
rm -rf src/value_investment/pipeline/bus/
rm src/value_investment/pipeline/fields.py
```

**Step 4: 验证**

Run: `python -c "from value_investment import PipelineAPI; api = PipelineAPI(); print('OK')"`

**Step 5: 提交**

```bash
git add -A && git commit -m "refactor: complete architecture restructure"
```

---

### Phase 6: 测试更新

#### Task 8: 更新测试文件

**Files:**
- Modify: `tests/` 目录下所有 import 路径
- Delete: `tests/pipeline/handlers/` (对应已删除的 handlers)
- Delete: `tests/pipeline/calculators/` (对应已删除的 calculators)

**Step 1: 更新 import 路径**

```bash
# 更新测试文件中的 import
sed -i '' 's/from value_investment.pipeline.handlers/from value_investment.handlers/g' tests/**/*.py
sed -i '' 's/from value_investment.pipeline.calculators/from value_investment.domain.calculators/g' tests/**/*.py
sed -i '' 's/from value_investment.pipeline.bus/from value_investment.pipeline.bus/g' tests/**/*.py
```

**Step 2: 运行测试**

Run: `uv run python -m pytest tests/ -v --tb=short`

**Step 3: 提交**

```bash
git add -A && git commit -m "test: update imports after restructure"
```

---

## 最终验证

### Task 9: 完整验证

**Step 1: 验证导入**

```bash
python -c "
from value_investment import PipelineAPI
from value_investment.handlers import AShareStatementHandler, HKShareStatementHandler, USShareStatementHandler
from value_investment.providers import TushareProvider, HKProvider, USProvider
from value_investment.domain.calculators import CALCULATOR_MAP
from value_investment.core.types import Message
print('All imports OK')
"
```

**Step 2: 验证 dry run**

```bash
uv run python -m value_investment.cli validate 600519 -r roe,net_profit
uv run python -m value_investment.cli validate 00700 -r roe,net_profit
uv run python -m value_investment.cli validate AAPL -r roe,net_profit
```

**Step 3: 运行测试**

```bash
uv run python -m pytest tests/ -v
```

---

## 计划完成

**预计任务数:** 9 个主要任务
**预计时间:** 约 2-3 小时

**执行方式选择:**
1. **Subagent-Driven (本会话)** - 每个任务派发新的 subagent，任务间审查，快速迭代
2. **Parallel Session (单独会话)** - 在新会话中使用 executing-plans，批量执行带检查点

你想选择哪种方式？
