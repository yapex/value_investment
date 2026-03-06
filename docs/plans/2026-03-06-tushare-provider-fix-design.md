# TushareProvider 修复设计

## 背景

Phase 1（基础设施）已完成：Pydantic settings、config models、BaseProvider with field mapping、DI container。

当前 TushareProvider 实现存在问题，需要修复以完成 Phase 2。

## 当前状态

### 已完成
- ✅ Pydantic settings 和 config models
- ✅ BaseProvider with field mapping support
- ✅ DI Container (dependency-injector)
- ✅ TTL 辅助函数：`get_ttl_until_next_midnight()`, `get_ttl_until_june_next_year()`
- ✅ 14 个单元测试通过
- ✅ 20 个 container 测试通过

### 待修复问题

| 功能 | 方法 | 问题 |
|------|------|------|
| 资产负债表 | `get_balance_sheet()` | 请求的字段与映射配置不匹配 |
| 利润表 | `get_income_statement()` | 请求的字段与映射配置不匹配 |
| 现金流量表 | `get_cash_flow_statement()` | 请求的字段与映射配置不匹配 |
| 历史行情 | `get_historical_data()` | 使用了错误的 API（daily 不支持 adj，应使用 pro_bar） |
| 股票信息 | `get_stock_info()` | 缺少缓存 TTL |
| 所有方法 | - | 缺少按数据类型的缓存 TTL 设置 |

## 设计决策

### 1. 字段对齐方案 ✅ 已确认

**选择：方案1 - 修复字段对齐**

更新 tushare API 调用，请求与 `defaults.py` 映射匹配的字段。

标准字段名定义在 `defaults.py` 中，各 provider 应请求对应这些标准字段的原生字段。

### 2. 实现范围 ✅ 已确认

**选择：方案2 - 修复全部功能**

修复所有 5 个方法：
- `get_balance_sheet()` - 资产负债表
- `get_income_statement()` - 利润表
- `get_cash_flow_statement()` - 现金流量表
- `get_historical_data()` - 历史行情
- `get_stock_info()` - 股票信息

### 3. 缓存 TTL 策略 ✅ 已确认

| 数据类型 | TTL 策略 |
|---------|---------|
| 财务三表 (balance/income/cashflow) | `get_ttl_until_june_next_year(end_year)` |
| 股票信息 (stock_info) | `get_ttl_until_next_midnight()` |
| 历史行情 (historical_data) | 1 天（86400 秒） |

### 4. 历史行情 API 修正 ✅ 已确认

**问题**：当前使用 `pro.daily()` + `adj` 参数，但 `daily()` 不支持复权

**修正**：改用 `ts.pro_bar()` 接口，该接口支持 `adj` 参数（qfq/hfq）

```python
# 错误 ❌
df = self._api.daily(ts_code=..., adj=adj)

# 正确 ✅
df = ts.pro_bar(ts_code=..., adj=adj)
```

## 待办事项

### 下一步
1. 查阅 tushare pro 文档确认各接口返回的字段名
2. 更新 `defaults.py` 中的 TUSHARE_A_CONFIG 字段映射
3. 更新 `TushareProvider` 各方法的 API 调用：
   - 请求正确的字段集
   - 设置正确的缓存 TTL
   - 历史行情改用 `pro_bar()` 接口
4. 更新单元测试以匹配新的字段名

## 相关文件

- `src/value_investment/data/providers/tushare_provider.py` - 待修复
- `src/value_investment/data/providers/base_provider.py` - 基类，TTL 辅助函数
- `src/value_investment/core/defaults.py` - 字段映射配置
- `src/value_investment/core/config.py` - Pydantic 配置模型
- `src/value_investment/core/container.py` - DI Container
- `tests/test_tushare_provider.py` - 集成测试
- `tests/test_tushare_provider_unit.py` - 单元测试

## 环境信息

- Tushare Token: 已配置在 `.env` 中
- Git 分支: `feature/pydantic-datasource-config`
- 测试命令: `uv run python -m pytest tests/test_tushare_provider_unit.py -v`
