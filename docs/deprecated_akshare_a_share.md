# A股 AKShare 相关代码废弃说明

## 背景

项目已将 A 股数据源从 AKShare 迁移到 Tushare，港股历史交易数据建议使用 yfinance。以下代码已被标记为 **deprecated**，将在未来版本中移除。

## 已废弃的文件和类

### 1. HKShareProvider 历史数据 (`src/value_investment/data/providers/hk_share_provider.py`)

**部分功能废弃**

- `get_historical_data()` - 获取港股历史交易数据

**原因**: AKShare 的港股历史数据接口不够稳定

**替代方案**: 使用 `YFinanceProvider`

```python
# 旧代码 (已废弃)
from value_investment.data.providers.hk_share_provider import HKShareProvider
provider = HKShareProvider(cache=cache)
data = provider.get_historical_data("00700", end_date="20231231")

# 新代码
from value_investment.data.providers.yfinance_provider import YFinanceProvider
provider = YFinanceProvider(cache=cache)
data = provider.get_historical_data("0700.HK", start_date="2023-01-01", end_date="2023-12-31")
```

**注意**: 港股财务数据（`get_balance_sheet`, `get_income_statement`, `get_cash_flow_statement`）仍可使用 AKShare

### 2. AkshareProvider 港股历史数据 (`src/value_investment/data/providers/akshare_provider.py`)

**部分功能废弃**

- `_get_hk_historical_data()` - 获取港股历史数据
- `get_historical_data(market="HK")` - 当 market="HK" 时会触发警告

**替代方案**: 使用 `YFinanceProvider`

### 3. AShareProvider (`src/value_investment/data/providers/a_share_provider.py`)

**完整文件废弃**

- 类：`AShareProvider`
- 所有方法：
  - `get_stock_info()` - 获取 A 股股票信息
  - `get_historical_data()` - 获取 A 股历史数据
  - `get_balance_sheet()` - 获取资产负债表
  - `get_income_statement()` - 获取利润表
  - `get_cash_flow_statement()` - 获取现金流量表

**替代方案**: 使用 `TushareProvider`

### 4. AkshareProvider A股相关方法 (`src/value_investment/data/providers/akshare_provider.py`)

**部分方法废弃**（仅 A 股相关，港股和美股功能仍可用）

- `_get_a_stock_info()` - 获取 A 股股票信息
- `_get_a_historical_data()` - 获取 A 股历史数据
- `_get_a_financial_indicator()` - 获取 A 股财务指标
- `_get_a_quarterly_indicator()` - 获取 A 股季度指标
- `_convert_a_financial_strings()` - 转换 A 股财务数据格式
- `_calculate_pe_pb_for_a()` - 计算 A 股 PE/PB

**注意**：当 `market="A"` 初始化 `AkshareProvider` 时，会触发 `DeprecationWarning`

**替代方案**: 使用 `TushareProvider`

### 5. ProviderFactory (`src/value_investment/data/providers/factory.py`)

**部分功能废弃**

- `create_provider(market="A")` - 创建 A 股 provider
- `_PROVIDER_MAP["A"]` - 映射到已废弃的 `AShareProvider`

**替代方案**：直接使用 `TushareProvider`，或通过新的配置系统创建

## 迁移指南

### 从 HKShareProvider 历史数据迁移

```python
# 旧代码 (已废弃)
from value_investment.data.providers.hk_share_provider import HKShareProvider
provider = HKShareProvider(cache=cache)
data = provider.get_historical_data("00700", end_date="20231231")

# 新代码
from value_investment.data.providers.yfinance_provider import YFinanceProvider
provider = YFinanceProvider(cache=cache)
# 注意: yfinance 使用 "0700.HK" 格式
data = provider.get_historical_data("0700.HK", start_date="2023-01-01", end_date="2023-12-31")
```

### 从 AkshareProvider 港股历史数据迁移

```python
# 旧代码 (已废弃)
from value_investment.data.providers.akshare_provider import AkshareProvider
provider = AkshareProvider(cache=cache, market="HK")
data = provider.get_historical_data("00700", end_date="20231231")

# 新代码
from value_investment.data.providers.yfinance_provider import YFinanceProvider
provider = YFinanceProvider(cache=cache)
data = provider.get_historical_data("0700.HK", start_date="2023-01-01", end_date="2023-12-31")
```

### 从 AShareProvider 迁移

```python
# 旧代码 (已废弃)
from value_investment.data.providers.a_share_provider import AShareProvider
provider = AShareProvider(cache=cache, market="A")

# 新代码
from value_investment.data.providers.tushare_provider import TushareProvider
provider = TushareProvider(cache=cache, token="YOUR_TUSHARE_TOKEN")
```

### 从 AkshareProvider (market="A") 迁移

```python
# 旧代码 (已废弃)
from value_investment.data.providers.akshare_provider import AkshareProvider
provider = AkshareProvider(cache=cache, market="A")

# 新代码
from value_investment.data.providers.tushare_provider import TushareProvider
provider = TushareProvider(cache=cache, token="YOUR_TUSHARE_TOKEN")
```

### 使用默认配置

```python
# 推荐方式：使用配置系统
from value_investment.api import ValueInvestment

# 配置文件或环境变量会自动使用 Tushare 作为 A 股数据源
vi = ValueInvestment()
data = vi.get_financial_data("600519")
```

## 警告信息

使用已废弃的代码会触发以下警告：

```
DeprecationWarning: AShareProvider 基于 AKShare 实现，已被废弃。
请使用 TushareProvider 作为 A 股数据源。将在未来版本中移除。
```

## 时间线

- **当前版本**：代码已标记为 deprecated，仍可使用但会发出警告
- **下个主要版本**：计划移除所有 A 股 AKShare 相关代码

## 测试相关

相关测试文件：
- `tests/test_akshare_provider.py` - 包含 A 股测试用例
- `tests/test_provider.py` - 可能包含 AShareProvider 测试

建议：更新测试用例以使用 TushareProvider，或为废弃的功能添加 pytest.mark.skip

## 配置文件

检查并更新：
- `src/value_investment/core/defaults.py` - 确保默认配置使用 Tushare
- 环境变量配置 - 确保 TUSHARE_TOKEN 已设置

## 注意事项

1. **港股和美股功能不受影响**：`AkshareProvider` 的港股和美股功能仍然可用
2. **数据字段映射**：Tushare 和 AKShare 的字段名可能不同，参考 `CORE_FIELD_MAPPING`
3. **缓存兼容性**：切换数据源后可能需要清除缓存
4. **API 限流**：Tushare 有 API 调用限制，请合理使用缓存

