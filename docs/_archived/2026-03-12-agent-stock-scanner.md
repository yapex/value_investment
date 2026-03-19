# Agent-based 股票 Scanner 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use @executing-plans to implement this plan task-by-task.

**Goal:** 构建基于 Agent 的股票筛选系统，提供 Python API 和 Agent 操作指南，支持连续 N 年财务指标过滤

**Architecture:** 
- 核心层：基于现有 TushareProvider + SmartCache，提供批量数据获取和速率限制
- API 层：`Scanner` 类提供 `get_stock_list()` 和 `get_financial_data()` 方法
- 过滤层：`filters` 模块提供 `consecutive_years` 过滤函数
- 指南层：Markdown 文档教 Agent 如何使用 API

**Tech Stack:** Python, pandas, tushare, existing SmartCache, RateLimiter

**Scope:** 
- ✅ First: A 股 only
- ✅ First: consecutive_years filter only (连续 N 年都满足)
- ⏭️ Later: majority_years filter (N 年中至少 M 年 + 平均值)
- ⏭️ Later: HK/US markets

---

## Task 1: 创建 RateLimiter 工具类

**Goal:** 实现速率限制器，控制 Tushare API 调用频率（200 次/分钟）

**Files:**
- Create: `src/value_investment/core/rate_limiter.py`
- Test: `tests/core/test_rate_limiter.py`

**Steps:**

1. **Write test** - 编写基本速率限制测试
   ```python
   # tests/core/test_rate_limiter.py
   import time
   from value_investment.core.rate_limiter import RateLimiter

   def test_rate_limiter_basic():
       limiter = RateLimiter(max_calls_per_minute=10)
       start = time.time()
       for _ in range(10):
           limiter.wait_if_needed()
       elapsed = time.time() - start
       assert elapsed < 1  # 应该很快完成

   def test_rate_limiter_status():
       limiter = RateLimiter(max_calls_per_minute=10)
       status = limiter.get_status()
       assert status['calls_in_last_minute'] == 0
       assert status['remaining'] == 10
   ```

2. **Red** - 运行测试确认失败
   ```bash
   uv run pytest tests/core/test_rate_limiter.py -v
   # Expected: Module not found
   ```

3. **Implement** - 实现 RateLimiter
   ```python
   # src/value_investment/core/rate_limiter.py
   import time
   from typing import Dict

   class RateLimiter:
       def __init__(self, max_calls_per_minute: int = 200):
           self.max_calls = max_calls_per_minute
           self._calls: list[float] = []

       def wait_if_needed(self) -> None:
           now = time.time()
           self._calls = [t for t in self._calls if now - t < 60]
           if len(self._calls) >= self.max_calls:
               oldest_call = min(self._calls)
               wait_time = 60 - (now - oldest_call) + 0.1
               if wait_time > 0:
                   time.sleep(wait_time)
               now = time.time()
               self._calls = [t for t in self._calls if now - t < 60]
           self._calls.append(time.time())

       def get_status(self) -> Dict[str, int]:
           now = time.time()
           self._calls = [t for t in self._calls if now - t < 60]
           return {
               'calls_in_last_minute': len(self._calls),
               'remaining': self.max_calls - len(self._calls)
           }
   ```

4. **Green** - 运行测试确认通过
   ```bash
   uv run pytest tests/core/test_rate_limiter.py -v
   # Expected: 2 tests PASS
   ```

5. **Commit**
   ```bash
   git add tests/core/test_rate_limiter.py src/value_investment/core/rate_limiter.py
   git commit -m "feat: add RateLimiter for API rate limiting"
   ```

---

## Task 2: 创建 Scanner 核心类

**Goal:** 实现 Scanner 类，提供获取股票列表和财务数据的 API

**Files:**
- Create: `src/value_investment/scanner/__init__.py`
- Create: `src/value_investment/scanner/scanner.py`
- Modify: `src/value_investment/__init__.py`
- Test: `tests/scanner/test_scanner.py`

**Steps:**

1. **Write test** - 编写 Scanner 初始化和 mock 测试
   ```python
   # tests/scanner/test_scanner.py
   import pandas as pd
   from unittest.mock import patch
   from value_investment.scanner import Scanner

   def test_scanner_initialization():
       scanner = Scanner(market="A")
       assert scanner.market == "A"

   def test_get_stock_list_mock():
       scanner = Scanner(market="A")
       mock_df = pd.DataFrame({
           'ts_code': ['600519.SH', '000001.SZ'],
           'symbol': ['600519', '000001'],
           'name': ['贵州茅台', '平安银行'],
       })
       with patch.object(scanner._provider, 'get_all_stocks', return_value=mock_df):
           result = scanner.get_stock_list()
       assert len(result) == 2
       assert '600519' in result['symbol'].values
   ```

2. **Red** - 运行测试确认失败
   ```bash
   uv run pytest tests/scanner/test_scanner.py -v
   # Expected: Module not found
   ```

3. **Implement** - 实现 Scanner 类
   ```python
   # src/value_investment/scanner/scanner.py
   import os
   from typing import List, Optional
   import pandas as pd
   import tushare as ts
   from value_investment.core.rate_limiter import RateLimiter
   from value_investment.data.cache import SmartCache

   class Scanner:
       def __init__(self, market: str = "A", cache_dir: Optional[str] = None):
           self.market = market
           self._cache = SmartCache(cache_dir=cache_dir)
           self._rate_limiter = RateLimiter(max_calls_per_minute=200)
           token = os.getenv("TUSHARE_TOKEN", "")
           if not token:
               raise ValueError("TUSHARE_TOKEN environment variable is required")
           ts.set_token(token)
           self._api = ts.pro_api()

       def get_stock_list(self) -> pd.DataFrame:
           cache_key = "scanner_all_stocks"
           cached = self._cache.get(cache_key)
           if cached is not None:
               return cached
           self._rate_limiter.wait_if_needed()
           df = self._api.stock_basic(
               exchange='',
               list_status='L',
               fields='ts_code,symbol,name,area,industry,list_date'
           )
           if df is not None and not df.empty:
               from value_investment.data.providers.base_provider import get_ttl_until_next_midnight
               self._cache.set(cache_key, df, ttl=get_ttl_until_next_midnight())
           return df

       def get_financial_data(
           self,
           stocks: List[str],
           fields: List[str],
           years: int = 5
       ) -> pd.DataFrame:
           ts_codes = [self._to_ts_code(s) for s in stocks]
           return self._get_financial_data_batch(ts_codes, fields, years)

       def _get_financial_data_batch(
           self,
           ts_codes: List[str],
           fields: List[str],
           years: int
       ) -> pd.DataFrame:
           from datetime import datetime
           end_year = datetime.now().year
           start_year = end_year - years + 1
           all_data = []
           for i, ts_code in enumerate(ts_codes):
               if i % 50 == 0 and i > 0:
                   status = self._rate_limiter.get_status()
                   print(f"  已处理 {i}/{len(ts_codes)} 只，剩余配额 {status['remaining']}")
               cache_key = f"scanner_finind_{ts_code}_{start_year}_{end_year}"
               cached = self._cache.get(cache_key)
               if cached is not None:
                   all_data.append(cached)
                   continue
               self._rate_limiter.wait_if_needed()
               try:
                   df = self._api.fina_indicator(
                       ts_code=ts_code,
                       start_date=f"{start_year}0101",
                       end_date=f"{end_year}1231"
                   )
                   if df is not None and not df.empty:
                       annual = df[df['end_date'].astype(str).str.endswith('1231')].copy()
                       if not annual.empty:
                           annual['stock_code'] = ts_code.replace('.SH', '').replace('.SZ', '')
                           keep_cols = ['stock_code', 'end_date'] + fields
                           available_cols = [c for c in keep_cols if c in annual.columns]
                           annual = annual[available_cols]
                           all_data.append(annual)
                           from value_investment.data.providers.base_provider import get_ttl_until_june_next_year
                           self._cache.set(cache_key, annual, ttl=get_ttl_until_june_next_year(end_year))
               except Exception as e:
                   print(f"  获取 {ts_code} 失败：{e}")
                   continue
           if all_data:
               return pd.concat(all_data, ignore_index=True)
           return pd.DataFrame()

       def _to_ts_code(self, stock_code: str) -> str:
           if "." in stock_code:
               return stock_code
           if len(stock_code) == 6 and stock_code.isdigit():
               if stock_code.startswith(("0", "3")):
                   return f"{stock_code}.SZ"
               elif stock_code.startswith("6"):
                   return f"{stock_code}.SH"
           return stock_code
   ```

4. **Update exports** - 更新模块导出
   ```python
   # src/value_investment/scanner/__init__.py
   from value_investment.scanner.scanner import Scanner
   __all__ = ["Scanner"]

   # src/value_investment/__init__.py - 添加
   from value_investment.scanner import Scanner
   ```

5. **Green + Commit**
   ```bash
   uv run pytest tests/scanner/test_scanner.py -v
   # Expected: 2 tests PASS
   git add src/value_investment/scanner/ tests/scanner/ src/value_investment/__init__.py
   git commit -m "feat: add Scanner class for batch stock data retrieval"
   ```

---

## Task 3: 创建 consecutive_years 过滤器

**Goal:** 实现连续 N 年满足条件的过滤函数

**Files:**
- Create: `src/value_investment/scanner/filters.py`
- Test: `tests/scanner/test_filters.py`

**Steps:**

1. **Write test** - 编写连续年份过滤测试
   ```python
   # tests/scanner/test_filters.py
   import pandas as pd
   from value_investment.scanner import filters

   def test_consecutive_years_basic():
       df = pd.DataFrame({
           'stock_code': ['A', 'A', 'A', 'B', 'B', 'B'],
           'end_date': ['2022-12-31', '2023-12-31', '2024-12-31',
                       '2022-12-31', '2023-12-31', '2024-12-31'],
           'roe': [16.0, 17.0, 18.0, 10.0, 11.0, 12.0],
       })
       df['end_date'] = pd.to_datetime(df['end_date'])
       result = filters.consecutive_years(df, field='roe', min_value=15, years=3)
       assert len(result) == 1
       assert result.iloc[0]['stock_code'] == 'A'

   def test_consecutive_years_not_enough():
       df = pd.DataFrame({
           'stock_code': ['A', 'A'],
           'end_date': ['2023-12-31', '2024-12-31'],
           'roe': [16.0, 17.0],
       })
       df['end_date'] = pd.to_datetime(df['end_date'])
       result = filters.consecutive_years(df, field='roe', min_value=15, years=3)
       assert len(result) == 0
   ```

2. **Red** - 运行测试确认失败
   ```bash
   uv run pytest tests/scanner/test_filters.py -v
   # Expected: Module not found
   ```

3. **Implement** - 实现 filters 模块
   ```python
   # src/value_investment/scanner/filters.py
   import pandas as pd

   def consecutive_years(
       df: pd.DataFrame,
       field: str,
       min_value: float,
       years: int = 5
   ) -> pd.DataFrame:
       df = df.copy()
       df['end_date'] = pd.to_datetime(df['end_date'])
       results = []
       for code, group in df.groupby('stock_code'):
           recent = group.nlargest(years, 'end_date')
           if len(recent) < years:
               continue
           values = recent[field].astype(float)
           if (values >= min_value).all():
               results.append(code)
       return df[df['stock_code'].isin(results)].copy()
   ```

4. **Update exports** - 更新模块导出
   ```python
   # src/value_investment/scanner/__init__.py
   from value_investment.scanner.scanner import Scanner
   from value_investment.scanner import filters
   __all__ = ["Scanner", "filters"]
   ```

5. **Green + Commit**
   ```bash
   uv run pytest tests/scanner/test_filters.py -v
   # Expected: 2 tests PASS
   git add src/value_investment/scanner/filters.py tests/scanner/test_filters.py
   git commit -m "feat: add consecutive_years filter"
   ```

---

## Task 4: 创建 Agent 操作指南

**Goal:** 编写简洁的 Agent 使用文档，仅涵盖已实现功能

**Files:**
- Create: `docs/agent-guide-stock-scanner.md`

**Steps:**

1. **Create document** - 创建操作指南
   ```markdown
   # Agent 股票 Scanner 操作指南

   ## 快速开始

   ### 1. 初始化 Scanner
   ```python
   from value_investment import Scanner
   scanner = Scanner(market="A")
   ```

   ### 2. 获取股票列表
   ```python
   stocks = scanner.get_stock_list()
   print(f"共 {len(stocks)} 只股票")
   ```

   ### 3. 获取财务数据
   ```python
   financials = scanner.get_financial_data(
       stocks=['600519', '000001'],
       fields=['roe'],
       years=5
   )
   ```

   ## 过滤：连续 N 年满足条件

   **场景**: 连续 5 年 ROE >= 15%

   ```python
   from value_investment.scanner import filters

   result = filters.consecutive_years(
       financials,
       field='roe',
       min_value=15,
       years=5
   )
   ```

   ## 完整示例

   ```python
   from value_investment import Scanner, filters

   scanner = Scanner(market="A")
   stocks = scanner.get_stock_list()
   test_stocks = stocks['symbol'].head(100).tolist()

   financials = scanner.get_financial_data(
       stocks=test_stocks,
       fields=['roe'],
       years=5
   )

   result = filters.consecutive_years(
       financials, field='roe', min_value=15, years=5
   )

   print(f"符合条件：{result['stock_code'].nunique()} 只")
   ```

   ## 性能提示

   1. 首次扫描较慢（5000+ 股票约 25-30 分钟）
   2. 数据自动缓存，后续扫描极快
   3. 先用小批量（如前 100 只）测试逻辑
   ```

2. **Commit**
   ```bash
   git add docs/agent-guide-stock-scanner.md
   git commit -m "docs: add Agent stock scanner operation guide"
   ```

---

## Task 5: 创建示例脚本

**Goal:** 提供一个简单可运行的示例脚本

**Files:**
- Create: `examples/scanner_basic.py`
- Test: `tests/scanner/test_integration.py`

**Steps:**

1. **Create example** - 创建基础示例
   ```python
   # examples/scanner_basic.py
   from value_investment import Scanner, filters

   scanner = Scanner(market="A")
   stocks = scanner.get_stock_list()
   test_stocks = stocks['symbol'].head(20).tolist()

   print(f"测试股票：{len(test_stocks)} 只")

   financials = scanner.get_financial_data(
       stocks=test_stocks,
       fields=['roe'],
       years=5
   )

   result = filters.consecutive_years(
       financials, field='roe', min_value=15, years=5
   )

   print(f"符合条件：{result['stock_code'].nunique()} 只")
   ```

2. **Create integration test** - 创建集成测试
   ```python
   # tests/scanner/test_integration.py
   import pandas as pd
   from value_investment import filters

   def test_consecutive_years_integration():
       df = pd.DataFrame({
           'stock_code': ['600519', '600519', '600519'],
           'end_date': ['2022-12-31', '2023-12-31', '2024-12-31'],
           'roe': [30.0, 31.0, 32.0],
       })
       df['end_date'] = pd.to_datetime(df['end_date'])
       result = filters.consecutive_years(df, field='roe', min_value=15, years=3)
       assert len(result) == 1
   ```

3. **Red** - 运行测试
   ```bash
   uv run pytest tests/scanner/test_integration.py -v
   ```

4. **Green** - 确认通过
   ```bash
   # Expected: 1 test PASS
   ```

5. **Commit**
   ```bash
   git add examples/scanner_basic.py tests/scanner/test_integration.py
   git commit -m "feat: add basic example and integration test"
   ```

---

## Summary

完成后的功能：
- ✅ RateLimiter - 速率限制（200 次/分钟）
- ✅ Scanner - 获取股票列表和财务数据
- ✅ consecutive_years - 连续 N 年过滤
- ✅ Agent 指南 - 简洁使用文档
- ✅ 示例脚本 - 可直接运行

后续迭代（不在本次计划内）：
- ⏭️ majority_years 过滤器
- ⏭️ trend_up, stable 等其他过滤器
- ⏭️ HK/US 市场支持
- ⏭️ CLI 集成
