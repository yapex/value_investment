# 港股历史数据修复和 Deprecated 标记 - 2026-03-11

## 问题

1. 命令行查询港股历史数据失败（代码格式不兼容）
2. 港股历史交易数据应使用 yfinance 而非 AKShare
3. 缺少 deprecated 标记和迁移指引

## 解决方案

### 1. YFinanceProvider 代码转换

**文件**: `src/value_investment/data/providers/yfinance_provider.py`

**修改**:
- 添加 `_normalize_stock_code()` 方法，自动转换港股代码格式
- 支持多种输入格式:
  - `"00700"` → `"0700.HK"`
  - `"0700"` → `"0700.HK"`
  - `"0700.HK"` → `"0700.HK"` (不变)
  - `"AAPL"` → `"AAPL"` (不变)

**影响**:
- 用户可以直接使用5位港股代码，无需手动转换
- 向后兼容已有的 yfinance 格式代码

### 2. Deprecated 标记

**文件**:
- `src/value_investment/data/providers/hk_share_provider.py`
- `src/value_investment/data/providers/akshare_provider.py`

**修改**:
- `HKShareProvider.get_historical_data()` 标记为 deprecated
- `AkshareProvider._get_hk_historical_data()` 标记为 deprecated
- `AkshareProvider.get_historical_data(market="HK")` 触发运行时警告
- 更新文档说明，推荐使用 YFinanceProvider

**警告信息**:
```
DeprecationWarning: 港股历史交易数据建议使用 YFinanceProvider。
AKShare 的港股历史数据接口不够稳定。
建议迁移到 yfinance (例如: provider = YFinanceProvider(cache))
```

### 3. 文档更新

**文件**: `docs/deprecated_akshare_a_share.md`

**新增**:
- 港股历史数据废弃说明
- 迁移指南（从 HKShareProvider/AkshareProvider 到 YFinanceProvider）
- 代码格式说明

## 测试验证

### 功能测试

✅ 腾讯 (00700)
```bash
uv run python -m value_investment.cli hist 00700 --start 20210311 --end 20260311
# 数据行数: 1,227
# 日期范围: 2021-03-11 至 2026-03-10
# 最新收盘价: 553.50
```

✅ 汇丰银行 (00005)
```bash
uv run python -m value_investment.cli hist 00005 --start 20240101 --end 20260311
# 成功获取数据
```

✅ 阿里巴巴 (09988)
```bash
uv run python -m value_investment.cli hist 09988 --start 20240101 --end 20260311
# 成功获取数据
```

### Deprecated 警告测试

✅ HKShareProvider 触发警告
```python
from value_investment.data.providers.hk_share_provider import HKShareProvider
provider = HKShareProvider(cache=cache)
data = provider.get_historical_data("00700", end_date="20231231")
# DeprecationWarning: 港股历史交易数据建议使用 YFinanceProvider...
```

✅ AkshareProvider(market="HK") 触发警告
```python
from value_investment.data.providers.akshare_provider import AkshareProvider
provider = AkshareProvider(cache=cache, market="HK")
data = provider.get_historical_data("00700", end_date="20231231")
# DeprecationWarning: 港股历史交易数据建议使用 YFinanceProvider...
```

## 配置验证

✅ 数据源配置 (`src/value_investment/core/defaults.py`):
```python
markets={
    "HK": MarketDataSource(
        financial="akshare_hk",  # 财务数据: akshare
        market="yfinance"        # 市场数据: yfinance ✓
    ),
}
```

## 迁移指南

### 从 HKShareProvider 迁移

```python
# 旧代码 (已废弃)
from value_investment.data.providers.hk_share_provider import HKShareProvider
provider = HKShareProvider(cache=cache)
data = provider.get_historical_data("00700", end_date="20231231")

# 新代码
from value_investment.data.providers.yfinance_provider import YFinanceProvider
provider = YFinanceProvider(cache=cache)
# 支持多种代码格式: "00700", "0700", "0700.HK"
data = provider.get_historical_data("00700", start_date="2023-01-01", end_date="2023-12-31")
```

### 从 AkshareProvider(market="HK") 迁移

```python
# 旧代码 (已废弃)
from value_investment.data.providers.akshare_provider import AkshareProvider
provider = AkshareProvider(cache=cache, market="HK")
data = provider.get_historical_data("00700", end_date="20231231")

# 新代码
from value_investment.data.providers.yfinance_provider import YFinanceProvider
provider = YFinanceProvider(cache=cache)
data = provider.get_historical_data("00700", start_date="2023-01-01", end_date="2023-12-31")
```

### 使用 CLI（推荐）

```bash
# CLI 会自动使用正确的 provider (yfinance)
uv run python -m value_investment.cli hist 00700 --start 20210311 --end 20260311
```

## 注意事项

1. **港股财务数据仍使用 AKShare**: 资产负债表、利润表、现金流量表不受影响
2. **代码格式兼容**: YFinanceProvider 自动转换代码格式，用户无需关心
3. **缓存清除**: 建议在切换数据源后清除缓存: `uv run python -m value_investment.cli cache-clear`
4. **API 限制**: yfinance 是免费服务，可能有访问频率限制，请合理使用缓存

## 相关文件

### 修改的文件
- `src/value_investment/data/providers/yfinance_provider.py`
- `src/value_investment/data/providers/hk_share_provider.py`
- `src/value_investment/data/providers/akshare_provider.py`
- `docs/deprecated_akshare_a_share.md`

### 测试文件
- `/tmp/test_hk_historical_deprecated.py`
- `/tmp/test_hk_runtime_warning.py`
- `/tmp/test_yfinance_code.py`
- `/tmp/test_tencent_history.py`

## 下一步

1. ✅ 标记 deprecated 代码
2. ✅ 修复 yfinance 代码转换
3. ✅ 验证功能正常
4. 📝 更新用户文档
5. 📝 添加单元测试（可选）
6. 🗑️ 计划移除废弃代码（下个主要版本）

