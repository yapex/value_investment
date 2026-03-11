# 字段隔离实现计划 (TDD驱动)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 实现严格的字段隔离，内部只使用标准字段名，provider原始字段完全不可见。

**Architecture:** IFRS + Custom分层映射 - 依赖注入时自动映射

---

## Task 1: 添加 FINANCIAL_INDICATOR_MAPPING 字典

### Step 1: 写测试 (RED)

创建 `tests/test_mapper_financial_indicator.py`:

```python
import pytest
import pandas as pd
from value_investment.data.mapper import DataMapper

def test_financial_indicator_mapping_exists():
    """验证 FINANCIAL_INDICATOR_MAPPING 存在"""
    assert hasattr(DataMapper, 'FINANCIAL_INDICATOR_MAPPING')

def test_a_market_cap_mapped():
    """验证A股市值字段映射到 market_cap_cny"""
    df = pd.DataFrame({'总市值(元)': [1000000], '净利润': [100000]})
    result = DataMapper.map_financial_indicator(df, market='A')
    assert 'market_cap_cny' in result.columns

def test_hk_market_cap_mapped():
    """验证港股市值字段映射到 market_cap_hkd"""
    df = pd.DataFrame({'总市值(港元)': [1000000], '净利润': [100000]})
    result = DataMapper.map_financial_indicator(df, market='HK')
    assert 'market_cap_hkd' in result.columns
```

运行测试:
```bash
uv run pytest tests/test_mapper_financial_indicator.py -v
# 预期: FAIL - FINANCIAL_INDICATOR_MAPPING不存在
```

### Step 2: 写实现 (GREEN)

在 `src/value_investment/data/mapper.py` 末尾添加:

```python
# 财务指标映射 (IFRS标准 + 市场Custom)
FINANCIAL_INDICATOR_MAPPING = {
    # ===== IFRS 标准字段 (通用) =====
    '净利润': 'net_profit',
    '营业总收入': 'total_revenue',
    '基本每股收益': 'basic_eps',
    '每股净资产': 'bvps',
    '每股经营现金流': 'ocf_per_share',
    '销售净利率': 'net_profit_margin',
    '销售毛利率': 'gross_margin',
    '净资产收益率': 'roe',
    '总资产回报率': 'roa',

    # ===== A股 Custom 字段 =====
    'A': {
        '总市值(元)': 'market_cap_cny',
    },

    # ===== 港股 Custom 字段 =====
    'HK': {
        '总市值(港元)': 'market_cap_hkd',
        '港股市值(港元)': 'market_cap_hkd',
        '已发行股本(股)': 'total_shares',
        '每股股息TTM(港元)': 'dividend_per_share_hkd',
        '派息比率(%)': 'payout_ratio',
        '股息率TTM(%)': 'dividend_yield',
        '市盈率': 'pe_ratio',
        '市净率': 'pb_ratio',
    },
}
```

运行测试:
```bash
uv run pytest tests/test_mapper_financial_indicator.py::test_financial_indicator_mapping_exists -v
# 预期: PASS
```

---

## Task 2: 添加 map_financial_indicator 方法

### Step 1: 写测试 (RED)

在 `tests/test_mapper_financial_indicator.py` 添加:

```python
def test_map_financial_indicator_method_exists():
    """验证 map_financial_indicator 方法存在"""
    assert hasattr(DataMapper, 'map_financial_indicator')
    assert callable(DataMapper.map_financial_indicator)

def test_map_financial_indicator_rename_columns():
    """验证字段被正确重命名"""
    df = pd.DataFrame({
        '总市值(元)': [1000000],
        '净利润': [100000]
    })
    result = DataMapper.map_financial_indicator(df, market='A')

    # 原始字段应该被重命名
    assert 'market_cap_cny' in result.columns
    assert 'net_profit' in result.columns
    # 原始字段不应该存在（或在_original后缀中）
    assert '总市值(元)' not in result.columns or '总市值(元)_original' in result.columns

def test_map_financial_indicator_empty_df():
    """验证空DataFrame处理"""
    df = pd.DataFrame()
    result = DataMapper.map_financial_indicator(df, market='A')
    assert result.empty
```

运行测试:
```bash
uv run pytest tests/test_mapper_financial_indicator.py -v
# 预期: FAIL - map_financial_indicator方法不存在
```

### Step 2: 写实现 (GREEN)

在 `src/value_investment/data/mapper.py` 添加方法:

```python
@classmethod
def map_financial_indicator(cls, df: pd.DataFrame, market: str = 'A', keep_original: bool = True) -> pd.DataFrame:
    """映射财务指标字段

    Args:
        df: 原始财务指标 DataFrame
        market: 市场类型 ('A' 或 'HK')
        keep_original: 是否保留原始字段

    Returns:
        映射后的 DataFrame
    """
    if df is None or df.empty:
        return df

    result = df.copy()
    rename_map = {}

    # 1. 应用IFRS标准映射 (通用字段)
    for old_field, new_field in cls.FINANCIAL_INDICATOR_MAPPING.items():
        if isinstance(old_field, str) and old_field in result.columns:
            rename_map[old_field] = new_field

    # 2. 应用市场Custom映射
    market_mapping = cls.FINANCIAL_INDICATOR_MAPPING.get(market, {})
    for old_field, new_field in market_mapping.items():
        if old_field in result.columns:
            rename_map[old_field] = new_field

    # 重命名字段
    result = result.rename(columns=rename_map)

    # 保留原始字段
    if keep_original:
        result = cls._preserve_original_fields(df, result, rename_map)

    return result
```

运行测试:
```bash
uv run pytest tests/test_mapper_financial_indicator.py -v
# 预期: PASS
```

---

## Task 3: 添加 QUARTERLY_MAPPING 和 map_quarterly 方法

### Step 1: 写测试 (RED)

在 `tests/test_mapper_financial_indicator.py` 添加:

```python
def test_quarterly_mapping_exists():
    """验证 QUARTERLY_MAPPING 存在"""
    assert hasattr(DataMapper, 'QUARTERLY_MAPPING')

def test_map_quarterly_method_exists():
    """验证 map_quarterly 方法存在"""
    assert hasattr(DataMapper, 'map_quarterly')
    assert callable(DataMapper.map_quarterly)

def test_map_quarterly_renames_columns():
    """验证季度字段被正确重命名"""
    df = pd.DataFrame({
        '报告期': ['2024Q1'],
        '净利润': [100000],
        '营业总收入': [1000000]
    })
    result = DataMapper.map_quarterly(df)

    assert 'report_date' in result.columns or 'report_period' in result.columns
    assert 'net_profit' in result.columns
    assert 'total_revenue' in result.columns
```

运行测试:
```bash
uv run pytest tests/test_mapper_financial_indicator.py -v
# 预期: FAIL - QUARTERLY_MAPPING不存在
```

### Step 2: 写实现 (GREEN)

在 mapper.py 添加:

```python
# 季度指标映射
QUARTERLY_MAPPING = {
    # A股/港股通用
    '报告期': 'report_period',
    '净利润': 'net_profit',
    '营业总收入': 'total_revenue',
    '基本每股收益': 'basic_eps',
    '每股净资产': 'bvps',
}

@classmethod
def map_quarterly(cls, df: pd.DataFrame, keep_original: bool = True) -> pd.DataFrame:
    """映射季度指标字段"""
    if df is None or df.empty:
        return df

    result = df.copy()
    rename_map = {}

    for old_field, new_field in cls.QUARTERLY_MAPPING.items():
        if old_field in result.columns:
            rename_map[old_field] = new_field

    result = result.rename(columns=rename_map)

    if keep_original:
        result = cls._preserve_original_fields(df, result, rename_map)

    return result
```

运行测试:
```bash
uv run pytest tests/test_mapper_financial_indicator.py -v
# 预期: PASS
```

---

## Task 4: 修改 DataProvider 自动映射

### Step 1: 写测试 (RED)

创建 `tests/test_dependencies_auto_mapping.py`:

```python
import pytest
import pandas as pd
from unittest.mock import MagicMock
from value_investment.core.dependencies import DataProvider, DependencyRegistry

def test_data_provider_maps_financial_indicator():
    """验证DataProvider获取financial_indicator后自动映射"""
    mock_provider = MagicMock()
    mock_provider.get_financial_indicator.return_value = pd.DataFrame({
        '总市值(元)': [1000000],
        '净利润': [100000]
    })

    dp = DataProvider(mock_provider, market='A')
    result = dp.get('financial_indicator', '600519')

    # 验证返回的是映射后的数据
    assert 'market_cap_cny' in result.columns
    assert 'net_profit' in result.columns

def test_data_provider_maps_quarterly():
    """验证DataProvider获取quarterly后自动映射"""
    mock_provider = MagicMock()
    mock_provider.get_quarterly_indicator.return_value = pd.DataFrame({
        '报告期': ['2024Q1'],
        '净利润': [100000]
    })

    dp = DataProvider(mock_provider, market='A')
    result = dp.get('quarterly', '600519')

    # 验证返回的是映射后的数据
    assert 'net_profit' in result.columns
```

运行测试:
```bash
uv run pytest tests/test_dependencies_auto_mapping.py -v
# 预期: FAIL - 没有自动映射
```

### Step 2: 写实现 (GREEN)

修改 `src/value_investment/core/dependencies.py`:

```python
from dataclasses import dataclass
from typing import Any
from datetime import datetime

# 导入DataMapper
from value_investment.data.mapper import DataMapper

class DataProvider:
    """Lightweight dependency provider - fetches data by stock_code"""

    def __init__(self, stock_provider, market: str = 'A'):
        self._provider = stock_provider
        self._market = market

    def get(self, data_type: str, stock_code: str, **kwargs) -> Any:
        # Set default end_date if not provided
        if data_type == 'prices' and 'end_date' not in kwargs:
            kwargs['end_date'] = datetime.now().strftime('%Y%m%d')

        # 获取市场参数（优先使用kwargs中的market）
        market = kwargs.pop('market', self._market)

        fetchers = {
            'quarterly': lambda: self._map_quarterly(
                self._provider.get_quarterly_indicator(stock_code)
            ),
            'prices': lambda: self._provider.get_historical_data(stock_code, **kwargs),
            'stock_info': lambda: self._provider.get_stock_info(stock_code),
            'financial_indicator': lambda: self._map_financial_indicator(
                self._provider.get_financial_indicator(stock_code), market
            ),
        }
        if data_type not in fetchers:
            raise ValueError(f"Unknown data type: {data_type}")
        return fetchers[data_type]()

    def _map_financial_indicator(self, df, market: str):
        """映射财务指标"""
        return DataMapper.map_financial_indicator(df, market=market)

    def _map_quarterly(self, df):
        """映射季度数据"""
        return DataMapper.map_quarterly(df)

class DependencyRegistry:
    """Dependency registry - maps declarations to fetchers"""

    def __init__(self, data_provider: DataProvider):
        self._provider = data_provider

    def resolve(self, needs: list[str], stock_code: str, **kwargs) -> dict:
        """Resolve dependencies based on declarations"""
        if not needs:
            return {}
        return {n: self._provider.get(n, stock_code, **kwargs) for n in needs}
```

运行测试:
```bash
uv run pytest tests/test_dependencies_auto_mapping.py -v
# 预期: PASS
```

---

## Task 5: 更新 api.py 传递 market

### Step 1: 写测试 (RED)

创建 `tests/test_api_market_pass.py`:

```python
def test_api_passes_market_to_data_provider():
    """验证API将market传递给DataProvider"""
    from value_investment import ValueInvestment
    vi = ValueInvestment(market='HK')
    assert vi._data_provider._market == 'HK'

def test_api_passes_market_a():
    """验证A股市场传递"""
    from value_investment import ValueInvestment
    vi = ValueInvestment(market='A')
    assert vi._data_provider._market == 'A'
```

运行测试:
```bash
uv run pytest tests/test_api_market_pass.py -v
# 预期: FAIL - DataProvider没有market参数
```

### Step 2: 写实现 (GREEN)

修改 `src/value_investment/api.py`:

```python
# 在 __init__ 方法中修改:
self._data_provider = DataProvider(self._provider, market=market)
```

运行测试:
```bash
uv run pytest tests/test_api_market_pass.py -v
# 预期: PASS
```

---

## Task 6: 更新 LatestMarketCapIndicator 使用内部字段

### Step 1: 写测试 (RED)

创建 `tests/test_latest_market_cap_internal_fields.py`:

```python
import pytest
import pandas as pd
from value_investment.indicators.simple import LatestMarketCapIndicator

def test_latest_market_cap_uses_internal_fields_a():
    """验证LatestMarketCapIndicator使用A股内部字段"""
    indicator = LatestMarketCapIndicator()

    financial_indicator = pd.DataFrame({
        'market_cap_cny': [1000000000],
        'total_shares': [1000000000]
    })
    prices = pd.DataFrame({'收盘': [100]})

    result = indicator.calculate(pd.DataFrame(),
        financial_indicator=financial_indicator,
        prices=prices,
        stock_code='600519')

    assert result.value > 0
    assert 'A股' in result.description or '财务指标' in result.description

def test_latest_market_cap_uses_internal_fields_hk():
    """验证LatestMarketCapIndicator使用港股内部字段"""
    indicator = LatestMarketCapIndicator()

    financial_indicator = pd.DataFrame({
        'market_cap_hkd': [1000000000],
        'total_shares': [1000000000]
    })
    prices = pd.DataFrame({'收盘': [100]})

    result = indicator.calculate(pd.DataFrame(),
        financial_indicator=financial_indicator,
        prices=prices,
        stock_code='00700')

    assert result.value > 0
```

运行测试:
```bash
uv run pytest tests/test_latest_market_cap_internal_fields.py -v
# 预期: FAIL - 字段不存在
```

### Step 2: 写实现 (GREEN)

修改 `src/value_investment/indicators/simple.py` 中 LatestMarketCapIndicator:

```python
# 将:
if '总市值(元)' in finind.columns:
if '总市值(港元)' in finind.columns:

# 改为:
if 'market_cap_cny' in finind.columns:
    market_cap = float(finind['market_cap_cny'].iloc[0])
elif 'market_cap_hkd' in finind.columns:
    market_cap_hkd = float(finind['market_cap_hkd'].iloc[0])
    market_cap = market_cap_hkd * self.HKD_TO_CNY
```

运行测试:
```bash
uv run pytest tests/test_latest_market_cap_internal_fields.py -v
# 预期: PASS
```

---

## Task 7: 端到端验证

### Step 1: 验证A股

```bash
uv run python -m value_investment.cli indicator ImpliedGrowth -s 600519 -m A
# 预期: ImpliedGrowth: 10.0% (或非零值)
```

### Step 2: 验证港股

```bash
uv run python -m value_investment.cli indicator ImpliedGrowth -s 00700 -m HK
# 预期: ImpliedGrowth: 10.0% (或非零值)
```

### Step 3: 运行完整测试

```bash
uv run pytest tests/ -v --tb=short
# 预期: 全部通过
```

---

## 提交

```bash
git add -A
git commit -m "feat: 实现IFRS+Custom字段隔离

- 添加FINANCIAL_INDICATOR_MAPPING和QUARTERLY_MAPPING
- DataProvider自动映射依赖数据
- LatestMarketCapIndicator使用内部字段名
- 完整的TDD测试覆盖"
```
