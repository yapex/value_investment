# IoC 字段映射重构实现计划 (第一阶段：字段映射)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将字段映射从 Provider 移至 Handler 层，Provider 只负责原始数据获取和映射声明。**本阶段不涉及缓存迁移。**

**Architecture:** 
- Provider: 获取原始数据 + 声明 FIELD_MAPPINGS + 保留现有缓存逻辑
- Handler: 执行字段映射（根据 Provider 声明的 FIELD_MAPPINGS）
- 缓存逻辑暂留在 Provider，第二阶段再迁移

**Tech Stack:** Python, pandas, pytest

---

## 当前架构问题

```
当前 (Provider 混杂职责):
┌─────────────────────────────────────────┐
│           HKProvider                     │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐  │
│  │获取原始数据│ │字段映射  │ │缓存逻辑   │  │
│  └─────────┘ └─────────┘ └──────────┘  │
└─────────────────────────────────────────┘
```

## 目标架构（第一阶段）

```
目标 (职责分离 - 第一阶段):
┌─────────────────┐     ┌─────────────────┐
│  BaseHandler    │────▶│   HKProvider    │
│  - 字段映射      │     │  - 获取原始数据  │
│                 │     │  - 数据清洗     │
│                 │     │  - 声明映射规则  │
│                 │     │  - 缓存逻辑(暂留)│
└─────────────────┘     └─────────────────┘
```

**第二阶段将把缓存逻辑从 Provider 移到 Handler。**

---

## Task 1: 重构 BaseHandler 添加字段映射能力

**Files:**
- Modify: `src/value_investment/handlers/base_handler.py`
- Test: `tests/pipeline/test_base_handler.py`

**Step 1: 编写测试 - Handler 字段映射功能**

```python
def test_handler_field_mapping():
    """Handler 应该能根据 Provider 声明的 FIELD_MAPPINGS 执行映射"""
    from value_investment.handlers.base_handler import BaseHandler
    
    # 创建 Mock Provider
    class MockProvider:
        FIELD_MAPPINGS = {
            "balance_sheet": {
                "原始资产": "total_assets",
                "原始负债": "total_liabilities",
            }
        }
        
        def fetch_raw_balance_sheet(self, stock_code, end_year, start_year):
            import pandas as pd
            return pd.DataFrame({
                "year": [2023, 2022],
                "原始资产": [1000, 900],
                "原始负债": [500, 450],
            })
        
        @property
        def supported_fields(self):
            return {"total_assets", "total_liabilities"}
    
    # 创建 Handler
    handler = BaseHandler(MockProvider(), "A股", {"total_assets", "total_liabilities"})
    
    # 获取数据并验证映射
    df = handler.get_balance_sheet("000001", 2023, 2022)
    
    assert "total_assets" in df.columns
    assert "total_liabilities" in df.columns
    assert "原始资产" not in df.columns  # 原始字段应被映射


def test_handler_standardize_with_missing_fields():
    """Handler 应该静默忽略映射中不存在的字段"""
    import pandas as pd
    from value_investment.handlers.base_handler import BaseHandler
    
    class MockProvider:
        FIELD_MAPPINGS = {
            "balance_sheet": {
                "存在字段": "total_assets",
                "不存在字段": "total_liabilities",  # 原始数据中没有
            }
        }
        
        def fetch_raw_balance_sheet(self, stock_code, end_year, start_year):
            return pd.DataFrame({
                "year": [2023],
                "存在字段": [1000],
                "其他字段": [500],  # 映射中没有，保持原样
            })
        
        @property
        def supported_fields(self):
            return {"total_assets"}
    
    handler = BaseHandler(MockProvider(), "A股", {"total_assets"})
    df = handler.get_balance_sheet("000001", 2023, 2022)
    
    assert "total_assets" in df.columns
    assert "存在字段" not in df.columns
    assert "其他字段" in df.columns  # 未映射的字段保留
```

**Step 2: 运行测试确认失败**

```bash
uv run pytest tests/pipeline/test_base_handler.py::test_handler_field_mapping tests/pipeline/test_base_handler.py::test_handler_standardize_with_missing_fields -v
```

Expected: FAIL - BaseHandler 没有 get_balance_sheet 方法

**Step 3: 实现 BaseHandler 字段映射功能**

```python
"""BaseHandler with field mapping support"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from value_investment.core.types import Message


class BaseHandler(ABC):
    """Handler 基类 - 字段映射执行器
    
    职责：
    - 根据 Provider 声明的 FIELD_MAPPINGS 执行字段映射
    - 提供 get_* 方法返回标准字段的 DataFrame
    
    缓存逻辑在第二阶段迁移。
    """

    def __init__(
        self,
        provider,
        target_market: str,
        supported_fields: set[str],
    ):
        self._provider = provider
        self.target_market = target_market
        self._supported_fields = supported_fields

    @property
    def can_handle(self) -> set[str]:
        """该 Handler 能处理的字段集合"""
        return self._supported_fields & (
            self._provider.supported_fields if self._provider else set()
        )

    def _can_handle_market(self, message: "Message") -> bool:
        """快速判断：是否处理该市场"""
        return message.market == self.target_market

    def _can_handle_fields(self, message: "Message") -> bool:
        """快速判断：是否有可处理的字段"""
        return bool(message.require & self.can_handle)

    async def handle(self, message: "Message") -> None:
        """处理消息（模板方法）"""
        # 快速拒绝：市场不匹配
        if not self._can_handle_market(message):
            return
        # 快速拒绝：无支持的字段
        if not self._can_handle_fields(message):
            return

        # 交给子类处理具体逻辑
        await self._handle_impl(message)

    @abstractmethod
    async def _handle_impl(self, message: "Message") -> None:
        """子类实现具体处理逻辑"""
        pass

    # ========================================================================
    # 字段映射方法 (Handler 层统一执行)
    # ========================================================================

    def _standardize(
        self,
        df: pd.DataFrame | None,
        statement_type: str,
    ) -> pd.DataFrame:
        """将原始字段映射为标准字段
        
        从 Provider 的 FIELD_MAPPINGS 获取映射规则并执行。
        静默忽略映射中存在但原始数据中不存在的字段。
        """
        if df is None or df.empty:
            return pd.DataFrame()

        # 从 Provider 获取映射规则
        mappings = getattr(self._provider, 'FIELD_MAPPINGS', {})
        mapping = mappings.get(statement_type, {})

        if not mapping:
            return df

        # 只映射实际存在的列（静默忽略缺失字段）
        rename_map = {
            native: standard
            for native, standard in mapping.items()
            if native in df.columns
        }

        if rename_map:
            return df.rename(columns=rename_map)

        return df

    def get_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取资产负债表（执行字段映射）"""
        raw_df = self._provider.fetch_raw_balance_sheet(stock_code, end_year, start_year)
        return self._standardize(raw_df, "balance_sheet")

    def get_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取利润表（执行字段映射）"""
        raw_df = self._provider.fetch_raw_income_statement(stock_code, end_year, start_year)
        return self._standardize(raw_df, "income_statement")

    def get_cash_flow_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取现金流量表（执行字段映射）"""
        raw_df = self._provider.fetch_raw_cash_flow(stock_code, end_year, start_year)
        return self._standardize(raw_df, "cash_flow")
```

**Step 4: 运行测试确认通过**

```bash
uv run pytest tests/pipeline/test_base_handler.py::test_handler_field_mapping tests/pipeline/test_base_handler.py::test_handler_standardize_with_missing_fields -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add tests/pipeline/test_base_handler.py src/value_investment/handlers/base_handler.py
git commit -m "feat: add field mapping to BaseHandler"
```

---

## Task 2: 重构 HKProvider - 移除映射逻辑，声明 FIELD_MAPPINGS

**Files:**
- Modify: `src/value_investment/providers/hk_share.py`
- Test: `tests/providers/test_hk_provider.py` (创建)

**Step 1: 编写测试 - HKProvider 返回原始字段**

```python
"""tests/providers/test_hk_provider.py"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


class TestHKProviderRawData:
    """HKProvider 应该返回原始字段名，不做映射"""
    
    @patch("value_investment.providers.hk_share.ak")
    def test_fetch_raw_returns_native_fields(self, mock_ak):
        """fetch_raw_* 方法应返回原始字段名"""
        from value_investment.providers.hk_share import HKProvider
        
        # 模拟 API 返回原始数据
        mock_ak.stock_financial_hk_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2023-12-31"],
            "STD_ITEM_NAME": ["资产总计"],
            "AMOUNT": [1000],
        })
        
        provider = HKProvider(MagicMock())
        df = provider.fetch_raw_balance_sheet("00700", 2024, 2020)
        
        # 原始数据应该是长表格式
        assert "STD_ITEM_NAME" in df.columns or "ITEM_NAME" in df.columns
        assert "AMOUNT" in df.columns
    
    @patch("value_investment.providers.hk_share.ak")
    def test_provider_declares_field_mappings(self, mock_ak):
        """HKProvider 应声明 FIELD_MAPPINGS"""
        from value_investment.providers.hk_share import HKProvider
        
        assert hasattr(HKProvider, "FIELD_MAPPINGS")
        assert "balance_sheet" in HKProvider.FIELD_MAPPINGS
        assert "income_statement" in HKProvider.FIELD_MAPPINGS
        assert "cash_flow" in HKProvider.FIELD_MAPPINGS
    
    def test_field_mappings_have_correct_structure(self):
        """FIELD_MAPPINGS 结构验证"""
        from value_investment.providers.hk_share import HKProvider
        
        for statement_type, mapping in HKProvider.FIELD_MAPPINGS.items():
            for native_field, standard_field in mapping.items():
                # 原始字段是中文，标准字段是英文
                assert isinstance(native_field, str)
                assert isinstance(standard_field, str)
```

**Step 2: 运行测试确认失败**

```bash
uv run pytest tests/providers/test_hk_provider.py -v
```

Expected: FAIL - HKProvider 没有 fetch_raw_* 方法

**Step 3: 重构 HKProvider**

```python
"""港股 Pipeline Data Provider

只负责原始数据获取，字段映射由 Handler 执行。
缓存逻辑暂时保留在 Provider。
"""
from __future__ import annotations

import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

import akshare as ak
import pandas as pd

from value_investment.core.constants import HISTORICAL_DATA_TTL
from value_investment.providers.base import BaseProvider, get_ttl_until_june_next_year

if TYPE_CHECKING:
    from value_investment.core.cache import SmartCache


class HKProvider(BaseProvider):
    """港股数据 Provider - IoC 模式
    
    职责：
    - 从 AKShare API 获取原始数据
    - 声明 FIELD_MAPPINGS（由 Handler 执行映射）
    - 缓存逻辑暂时保留
    
    映射规则声明示例：
        FIELD_MAPPINGS = {
            "balance_sheet": {"流动资产合计": "current_assets"},
            "income_statement": {"净利润": "net_profit"},
        }
    """

    # 字段映射声明 (Handler 执行映射)
    FIELD_MAPPINGS: dict[str, dict[str, str]] = {
        "balance_sheet": {
            "流动资产合计": "current_assets",
            "资产总计": "total_assets",
            "负债合计": "total_liabilities",
            "股东权益合计": "total_equity",
            "流动负债合计": "current_liabilities",
            "货币资金": "cash_and_equivalents",
            "存货": "inventory",
            "应收账款": "accounts_receivable",
            "应付账款": "accounts_payable",
            "固定资产": "fixed_assets",
            "预付款项": "prepayment",
        },
        "income_statement": {
            "营业总收入": "total_revenue",
            "净利润": "net_profit",
            "营业利润": "operating_profit",
            "营业成本": "operating_cost",
        },
        "cash_flow": {
            "经营活动产生的现金流量净额": "operating_cash_flow",
            "投资活动产生的现金流量净额": "investing_cash_flow",
            "筹资活动产生的现金流量净额": "financing_cash_flow",
            "购建固定资产、无形资产支付的现金": "capital_expenditure",
        },
    }

    # Provider 支持的字段集合
    SUPPORTED_FIELDS: set[str] = {
        # 利润表
        "total_revenue", "net_profit", "operating_profit", "operating_cost",
        # 资产负债表
        "total_assets", "total_liabilities", "total_equity",
        "current_assets", "current_liabilities",
        "cash_and_equivalents", "inventory",
        "accounts_receivable", "accounts_payable", "fixed_assets",
        # 现金流量表
        "operating_cash_flow", "investing_cash_flow", "financing_cash_flow",
        "capital_expenditure",
    }

    def __init__(self, cache: "SmartCache") -> None:
        """初始化 HK Provider"""
        super().__init__(cache)
        self._ak = ak

    @property
    def supported_fields(self) -> set[str]:
        """该 Provider 支持的字段集合"""
        return self.SUPPORTED_FIELDS

    # ========================================================================
    # 原始数据获取方法 (供 Handler 调用)
    # ========================================================================

    def fetch_raw_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取原始资产负债表数据（不做映射）"""
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="资产负债表", indicator="年度"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            return self._transform_to_wide(df)
        except Exception:
            return pd.DataFrame()

    def fetch_raw_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取原始利润表数据（不做映射）"""
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="利润表", indicator="年度"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            return self._transform_to_wide(df)
        except Exception:
            return pd.DataFrame()

    def fetch_raw_cash_flow(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取原始现金流量表数据（不做映射）"""
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="现金流量表", indicator="年度"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            return self._transform_to_wide(df)
        except Exception:
            return pd.DataFrame()

    # ========================================================================
    # 私有辅助方法
    # ========================================================================

    def _normalize_hk_code(self, symbol: str) -> str:
        """标准化港股代码为 5 位数字格式"""
        if not symbol:
            return symbol
        digits = "".join(c for c in symbol if c.isdigit())
        if len(digits) < 5:
            digits = digits.zfill(5)
        return digits

    def _transform_to_wide(self, df: pd.DataFrame) -> pd.DataFrame:
        """将长表转为宽表，保持原始字段名"""
        if df.empty:
            return df

        item_col = "STD_ITEM_NAME" if "STD_ITEM_NAME" in df.columns else "ITEM_NAME"

        if item_col not in df.columns or "AMOUNT" not in df.columns:
            return df

        df = df.copy()
        df["year"] = pd.to_datetime(df["REPORT_DATE"]).dt.year

        try:
            wide_df = df.pivot_table(
                index="year",
                columns=item_col,
                values="AMOUNT",
                aggfunc="first",
            )
            return wide_df.reset_index()
        except Exception:
            return df
```

**Step 4: 运行测试确认通过**

```bash
uv run pytest tests/providers/test_hk_provider.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/providers/hk_share.py tests/providers/test_hk_provider.py
git commit -m "refactor: HKProvider declares FIELD_MAPPINGS, removes mapping logic"
```

---

## Task 3: 重构 HKShareStatementHandler 使用新的 Provider 接口

**Files:**
- Modify: `src/value_investment/handlers/hk_share.py`
- Test: `tests/pipeline/test_hk_handlers.py`

**Step 1: 编写测试 - Handler 使用 BaseHandler 映射方法**

```python
"""tests/pipeline/test_hk_handlers.py"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, AsyncMock


class TestHKShareStatementHandler:
    """HKShareStatementHandler 集成测试"""
    
    @pytest.mark.asyncio
    async def test_handler_returns_mapped_fields(self):
        """Handler 应返回标准字段名"""
        from value_investment.handlers.hk_share import HKShareStatementHandler
        from value_investment.core.types import Message
        
        # Mock Provider 返回原始字段
        class MockProvider:
            FIELD_MAPPINGS = {
                "balance_sheet": {"资产总计": "total_assets"},
                "income_statement": {"净利润": "net_profit"},
            }
            
            SUPPORTED_FIELDS = {"total_assets", "net_profit"}
            
            @property
            def supported_fields(self):
                return self.SUPPORTED_FIELDS
            
            def fetch_raw_balance_sheet(self, stock_code, end_year, start_year):
                return pd.DataFrame({
                    "year": [2023, 2022],
                    "资产总计": [1000, 900],
                })
            
            def fetch_raw_income_statement(self, stock_code, end_year, start_year):
                return pd.DataFrame({
                    "year": [2023, 2022],
                    "净利润": [100, 90],
                })
        
        handler = HKShareStatementHandler(MockProvider())
        
        message = Message(
            symbol="00700",
            market="港股",
            require={"total_assets", "net_profit"},
            end="2023-12-31",
            years=2,
        )
        
        await handler.handle(message)
        
        # 验证返回的是标准字段
        assert "total_assets" in message.results
        assert "net_profit" in message.results
        # 验证年份数据正确
        assert 2023 in message.results["total_assets"]
        assert 2023 in message.results["net_profit"]
```

**Step 2: 运行测试确认失败**

```bash
uv run pytest tests/pipeline/test_hk_handlers.py -v
```

Expected: FAIL

**Step 3: 重构 HKShareStatementHandler**

```python
"""港股 (HK-Share) Handlers

使用 BaseHandler 的字段映射功能。
"""
from typing import TYPE_CHECKING

from value_investment.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.core.types import Message


HK_SHARE_STATEMENT_FIELDS: set[str] = {
    # 利润表
    "total_revenue", "net_profit", "operating_profit", "gross_profit", "operating_cost",
    # 资产负债表
    "total_assets", "total_liabilities", "total_equity",
    "current_assets", "current_liabilities",
    "cash_and_equivalents", "inventory",
    "accounts_receivable", "accounts_payable", "fixed_assets",
    # 现金流量表
    "operating_cash_flow", "investing_cash_flow", "financing_cash_flow",
    "capital_expenditure",
}


class HKShareStatementHandler(BaseHandler):
    """港股财务报表 Handler
    
    使用 BaseHandler 的 _standardize() 执行字段映射。
    """

    def __init__(self, provider=None):
        super().__init__(provider, "港股", HK_SHARE_STATEMENT_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理港股财务报表请求"""
        if not self._provider:
            return

        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        end_year = int(message.end[:4])
        start_year = end_year - message.years + 1

        # 使用 BaseHandler 的方法获取映射后的数据
        balance_fields = to_handle & self._get_balance_fields()
        if balance_fields:
            df = self.get_balance_sheet(message.symbol, end_year, start_year)
            self._add_results_from_df(df, message, balance_fields)

        income_fields = to_handle & self._get_income_fields()
        if income_fields:
            df = self.get_income_statement(message.symbol, end_year, start_year)
            self._add_results_from_df(df, message, income_fields)

        cashflow_fields = to_handle & self._get_cashflow_fields()
        if cashflow_fields:
            df = self.get_cash_flow_statement(message.symbol, end_year, start_year)
            self._add_results_from_df(df, message, cashflow_fields)

    def _add_results_from_df(
        self,
        df: pd.DataFrame,
        message: "Message",
        fields: set[str],
    ) -> None:
        """从 DataFrame 提取结果到 Message"""
        if df.empty or "year" not in df.columns:
            return

        for _, row in df.iterrows():
            year = int(row["year"])
            for field in fields:
                if field in df.columns:
                    value = row.get(field)
                    if pd.notna(value):
                        try:
                            message.add_result(field, {year: float(value)})
                        except (ValueError, TypeError):
                            pass

    def _get_balance_fields(self) -> set[str]:
        return {
            "total_assets", "total_liabilities", "total_equity",
            "current_assets", "current_liabilities",
            "cash_and_equivalents", "inventory",
            "accounts_receivable", "accounts_payable", "fixed_assets",
        }

    def _get_income_fields(self) -> set[str]:
        return {"total_revenue", "net_profit", "operating_profit", "gross_profit", "operating_cost"}

    def _get_cashflow_fields(self) -> set[str]:
        return {
            "operating_cash_flow", "investing_cash_flow", 
            "financing_cash_flow", "capital_expenditure",
        }
```

**Step 4: 运行测试确认通过**

```bash
uv run pytest tests/pipeline/test_hk_handlers.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/handlers/hk_share.py tests/pipeline/test_hk_handlers.py
git commit -m "refactor: HKShareStatementHandler uses BaseHandler mapping"
```

---

## Task 4: 重构 USProvider 和 US Handler

**Files:**
- Modify: `src/value_investment/providers/us_share.py`
- Modify: `src/value_investment/handlers/us_share.py`
- Test: `tests/providers/test_us_provider.py` (创建)
- Test: `tests/pipeline/test_us_handlers.py`

**Step 1: 编写测试**

```python
"""tests/providers/test_us_provider.py"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


class TestUSProviderRawData:
    """USProvider 应该返回原始字段名"""
    
    @patch("value_investment.providers.us_share.ak")
    def test_provider_declares_field_mappings(self, mock_ak):
        """USProvider 应声明 FIELD_MAPPINGS"""
        from value_investment.providers.us_share import USProvider
        
        assert hasattr(USProvider, "FIELD_MAPPINGS")
        assert "balance_sheet" in USProvider.FIELD_MAPPINGS
```

**Step 2: 重构 USProvider**

```python
"""美股 Pipeline Data Provider

只负责原始数据获取，字段映射由 Handler 执行。
"""
class USProvider(BaseProvider):
    """美股数据 Provider - IoC 模式"""
    
    FIELD_MAPPINGS: dict[str, dict[str, str]] = {
        "balance_sheet": {
            "资产总计": "total_assets",
            "负债合计": "total_liabilities",
            "股东权益合计": "total_equity",
        },
        "income_statement": {
            "营业总收入": "total_revenue",
            "净利润": "net_profit",
        },
        "cash_flow": {
            "经营活动产生的现金流量净额": "operating_cash_flow",
        },
    }
    
    # ... 类似的 fetch_raw_* 方法
```

**Step 3: 重构 US Handler (使用 BaseHandler 映射)**

```python
class USShareStatementHandler(BaseHandler):
    """美股财务报表 Handler"""
    
    def __init__(self, provider=None):
        super().__init__(provider, "美股", US_SHARE_STATEMENT_FIELDS)
    
    async def _handle_impl(self, message: "Message") -> None:
        # 使用 self.get_balance_sheet() 等方法，自动执行映射
```

**Step 4: 运行测试**

```bash
uv run pytest tests/providers/test_us_provider.py tests/pipeline/test_us_handlers.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/providers/us_share.py src/value_investment/handlers/us_share.py
git add tests/providers/test_us_provider.py tests/pipeline/test_us_handlers.py
git commit -m "refactor: USProvider and USShareStatementHandler use IoC mapping"
```

---

## Task 5: 重构 AShareProvider 和 AShare Handler

**Files:**
- Modify: `src/value_investment/providers/a_share.py`
- Modify: `src/value_investment/handlers/a_share.py`
- Delete: `src/value_investment/providers/tushare_mapper.py` (迁移映射后删除)
- Test: `tests/providers/test_a_provider.py` (创建)
- Test: `tests/pipeline/test_a_handlers.py`

**Step 1: 提取 TushareFieldMapper 的映射到 FIELD_MAPPINGS**

从 `tushare_mapper.py` 中提取所有映射声明：

```python
# AShareProvider.FIELD_MAPPINGS
FIELD_MAPPINGS: dict[str, dict[str, str]] = {
    "balance_sheet": {
        # 从 TushareFieldMapper.balance_sheet 提取
        "total_assets": "total_assets",  # Tushare 同名
        "total_liab": "total_liabilities",
        # ...
    },
    "income_statement": {
        "total_operate_income": "total_revenue",
        "netprofit": "net_profit",
        # ...
    },
    "cash_flow": {
        "n_cashflow_act": "operating_cash_flow",
        # ...
    },
}
```

**Step 2-5:** 同前，测试并重构

```bash
uv run pytest tests/providers/test_a_provider.py tests/pipeline/test_a_handlers.py -v
```

---

## Task 6: 集成测试

**Files:**
- Test: `tests/pipeline/test_e2e_handler_split.py` (创建)

**Step 1: 端到端测试**

```python
"""tests/pipeline/test_e2e_handler_split.py"""
import pytest
from unittest.mock import MagicMock, patch


class TestEndToEndIoCMapping:
    """端到端测试：Provider -> Handler -> 标准字段"""
    
    @pytest.mark.asyncio
    async def test_hk_provider_to_handler_mapping(self):
        """验证 HK 数据流：原始字段 -> 映射 -> 标准字段"""
        from value_investment.handlers.hk_share import HKShareStatementHandler
        from value_investment.core.types import Message
        
        class MockProvider:
            FIELD_MAPPINGS = {
                "balance_sheet": {"资产总计": "total_assets"},
            }
            SUPPORTED_FIELDS = {"total_assets"}
            
            @property
            def supported_fields(self):
                return self.SUPPORTED_FIELDS
            
            def fetch_raw_balance_sheet(self, *args, **kwargs):
                import pandas as pd
                return pd.DataFrame({
                    "year": [2023],
                    "资产总计": [1000],
                })
        
        handler = HKShareStatementHandler(MockProvider())
        message = Message(
            symbol="00700", market="港股",
            require={"total_assets"}, end="2023-12-31", years=1,
        )
        
        await handler.handle(message)
        
        assert "total_assets" in message.results
        assert message.results["total_assets"][2023] == 1000.0
```

**Step 2: 运行所有测试**

```bash
uv run pytest tests/providers/test_hk_provider.py tests/providers/test_us_provider.py tests/providers/test_a_provider.py -v
uv run pytest tests/pipeline/test_base_handler.py tests/pipeline/test_hk_handlers.py tests/pipeline/test_us_handlers.py tests/pipeline/test_a_handlers.py -v
```

**Step 3: Commit**

```bash
git add tests/pipeline/test_e2e_handler_split.py
git commit -m "test: add end-to-end IoC mapping tests"
```

---

## Task 7: 验证现有功能未被破坏

**Step 1: 运行完整测试套件**

```bash
uv run pytest tests/ -v --tb=short 2>&1 | head -100
```

**Step 2: 检查关键功能**

```bash
# 测试 Provider 原始数据获取
uv run python -c "
from value_investment.providers.hk_share import HKProvider
from value_investment.providers.us_share import USProvider

# 验证 FIELD_MAPPINGS 存在
print('HK FIELD_MAPPINGS:', bool(HKProvider.FIELD_MAPPINGS))
print('US FIELD_MAPPINGS:', bool(USProvider.FIELD_MAPPINGS))
"
```

---

## 变更清单

| 文件 | 操作 | 说明 |
|-----|------|------|
| `handlers/base_handler.py` | 修改 | 添加 `_standardize()` 和 `get_*` 方法 |
| `providers/hk_share.py` | 修改 | 声明 FIELD_MAPPINGS，添加 fetch_raw_* |
| `providers/us_share.py` | 修改 | 同上 |
| `providers/a_share.py` | 修改 | 同上，内联 tushare_mapper 映射 |
| `providers/tushare_mapper.py` | 删除 | 映射迁移后删除 |
| `handlers/hk_share.py` | 修改 | 使用 BaseHandler 映射方法 |
| `handlers/us_share.py` | 修改 | 同上 |
| `handlers/a_share.py` | 修改 | 同上 |

---

## 第二阶段预告

**缓存迁移**（后续任务）:
- 将 Provider 中的缓存逻辑移到 Handler
- Handler 添加 `@cache` 或类似装饰器
- Provider 纯化为无状态数据获取器
