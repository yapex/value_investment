# Pydantic + Container 数据源配置化改造计划

**日期**: 2026-03-06  
**分支**: `feature/pydantic-datasource-config`  
**目标**: 使用 Pydantic + DI Container 实现可配置的数据源架构，支持多数据源组合（tushare/yfinance/akshare）

---

## 一、背景与动机

### 1.1 当前问题

| 问题 | 影响 |
|------|------|
| 映射关系硬编码在 `mapper.py` | 换数据源需要改代码 |
| Provider 与映射分离 | 职责不清，维护成本高 |
| 不支持多数据源组合 | 港股/美股需要交易数据 + 财务数据 |
| 配置不灵活 | 新增基金类数据困难 |

### 1.2 新需求

- **A 股数据迁移**: akshare → tushare
- **交易数据**: yfinance（港股/美股）
- **财务数据**: akshare 维持（港股/美股）
- **未来扩展**: 基金类数据

### 1.3 设计原则

1. **配置即代码** - Python + Pydantic，享受类型检查和 IDE 支持
2. **Provider 拥有映射** - 每个 Provider 自带字段映射配置
3. **Container 统一管理** - DI Container 负责组装
4. **TDD 驱动** - 先写测试，再实现功能

---

## 二、架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    ValueInvestment API                   │
│                     (上层应用无感知)                       │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      Container                           │
│  • 加载 Pydantic 配置                                     │
│  • 注册 Provider                                         │
│  • 应用字段映射                                          │
│  • 构建依赖图                                            │
└─────────────────────────────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Tushare   │  │  Akshare   │  │  YFinance  │
    │  Provider  │  │  Provider  │  │  Provider  │
    │  (A 股)     │  │  (港股/美股) │  │  (交易数据)  │
    └────────────┘  └────────────┘  └────────────┘
```

### 2.2 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| `Settings` | `core/settings.py` | 应用级配置（缓存、默认市场、API token） |
| `ProviderConfig` | `core/config.py` | Provider 配置（模块、类、映射） |
| `DataSourcesConfig` | `core/config.py` | 数据源总配置 |
| `Container` | `core/container.py` | DI Container，组装所有组件 |
| `BaseProvider` | `data/providers/base.py` | Provider 基类，支持字段映射 |
| 具体 Provider | `data/providers/*.py` | 实现具体数据源 |

### 2.3 字段映射流程

```
Provider 获取数据 → 应用 field_mappings → 返回标准字段 → Indicator 直接使用
```

**示例**:
```python
# Provider 配置
TUSHARE_CONFIG = ProviderConfig(
    field_mappings={
        "income": {
            "ts_code": "stock_code",
            "end_date": "report_date",
            "total_revenue": "total_revenue",  # tushare 字段名 = 标准字段名
        }
    }
)

# Provider 内部
def get_income_statement(self, stock_code, end_year):
    df = self._api.query('income', ...)  # 返回原生字段
    return self._apply_mapping(df, "income")  # 应用映射
```

---

## 三、实施计划（TDD）

### Phase 1: 基础设施（1-2 天）✅ COMPLETED

#### 1.1 安装依赖 ✅
- [x] `pydantic`
- [x] `pydantic-settings`

#### 1.2 创建配置模型 ✅
- [x] `core/settings.py` - 应用设置
- [x] `core/config.py` - 数据源配置模型
- [x] `core/defaults.py` - 默认配置

**测试** ✅:
- [x] `test_settings.py` - 6 passed
- [x] `test_config.py` - 15 passed
- [x] `test_defaults.py` - 7 passed

#### 1.3 Provider 基类支持映射 ✅
- [x] `data/providers/base_provider.py` - 添加 `_apply_mapping()`

**测试** ✅:
- [x] `test_base_provider.py` - 16 passed

#### 1.4 Container 简化 ⚠️
- [ ] `core/container.py` - 简化实现（当前有 dependency-injector 兼容性问题）

**测试**:
- [ ] `test_container.py` - 待适配

---

### Phase 1 总结

**测试覆盖**: 83 个测试通过 ✅
- Settings: 6 passed
- Config: 15 passed
- Defaults: 7 passed
- BaseProvider: 16 passed
- TushareProvider: 14 passed
- Container: 20 passed
- Cache: 25 passed

**核心成果**:
1. ✅ Pydantic 配置系统（类型安全、环境变量支持）
2. ✅ 默认数据源配置（A 股 tushare、港股/美股 akshare+yfinance）
3. ✅ BaseProvider 抽象类（字段映射、缓存支持、TTL 辅助函数）
4. ✅ TushareProvider 修复（字段对齐、API 修复、TTL 设置）
5. ✅ YFinanceProvider 修复（TTL 设置）
6. ✅ DI Container（dependency-injector）

**待完成**:
- AkshareProvider 改造（继承 BaseProvider，使用配置驱动）

---

### Phase 2: Provider 实现（2-3 天）

#### 2.1 TushareProvider（A 股）✅
- [x] `data/providers/tushare_provider.py`
- [x] 配置字段映射（income/balance/cashflow/market/info）
- [x] 实现核心方法
- [x] 添加 TTL 设置

**测试** ✅:
- [x] `test_tushare_provider_unit.py` - 14 passed

#### 2.2 YFinanceProvider（交易数据）✅
- [x] `data/providers/yfinance_provider.py`
- [x] 配置字段映射（market）
- [x] 添加 TTL 设置

**测试** ✅:
- [x] 集成测试通过（港股/美股历史数据）

#### 2.3 AkshareProvider 改造 ⚠️ 待定
- [ ] 移除硬编码映射
- [ ] 使用配置驱动
- [ ] 继承 BaseProvider

**测试**:
- [ ] `test_akshare_provider.py` - 回归测试

---

### Phase 3: 集成与迁移（2-3 天）

#### 3.1 API 层适配 ✅
- [x] `api.py` - 使用 Container 获取 Provider
- [x] 支持市场路由（A/HK/US）
- [x] 修复 `get_market()` 方法逻辑（symbol 参数应覆盖默认市场）
- [x] 修复 `get_stock_info()` 参数不匹配问题（force_refresh 在 API 层处理）
- [x] 修复 `_get_financial_data()` 年度报告去重问题（filter_annual 函数）
- [x] 修复股票名称获取逻辑（支持 Tushare 和 Akshare 两种格式）

**测试**:
- [x] `test_api_market_routing.py` - 验证市场路由（8 个测试全部通过）
  - A 股初始化验证（使用 tushare）
  - 港股初始化验证（使用 akshare + yfinance）
  - 美股初始化验证（使用 akshare + yfinance）
  - 市场自动检测（从股票代码）
  - 跨市场实例独立性
- [x] 修复 `test_api_indicator.py` 中 `test_get_indicator_unknown` 测试（行为变更：抛出异常而非返回 None）
- [x] 修复 analyze 命令（CLI 可正常输出多年财务分析数据）

#### 3.2 数据迁移验证
- [ ] A 股数据对比（akshare vs tushare）
- [ ] 港股数据验证（akshare + yfinance）
- [ ] 美股数据验证（akshare + yfinance）

**测试**:
- [ ] `test_data_consistency.py` - 验证数据一致性

#### 3.3 现有 Indicator 回归
- [ ] 运行所有 Indicator 测试
- [ ] 修复字段名问题

**测试**:
- [ ] `test_indicators_regression.py` - 全量回归

---

### Phase 4: 文档与优化（1 天）

#### 4.1 文档
- [ ] `docs/datasource-config.md` - 配置指南
- [ ] `docs/providers.md` - Provider 开发指南
- [ ] `.env.example` - 环境变量示例

#### 4.2 优化
- [ ] 性能基准测试
- [ ] 缓存策略优化
- [ ] 错误处理增强

---

## 四、配置模型设计

### 4.1 Settings（应用设置）

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    # Cache
    cache_dir: str = Field(default="./.cache")
    cache_ttl: int = Field(default=86400)
    
    # Default market
    default_market: str = Field(default="A")
    
    # API tokens
    tushare_token: str = Field(default="")
```

### 4.2 ProviderConfig（Provider 配置）

```python
class ProviderConfig(BaseModel):
    name: str
    module: str
    class_name: str
    init_kwargs: dict[str, str] = Field(default_factory=dict)
    field_mappings: dict[str, dict[str, str]] = Field(default_factory=dict)
    
    @field_validator('init_kwargs')
    @classmethod
    def expand_env_vars(cls, v: dict) -> dict:
        """支持环境变量：${TOKEN} → 实际值"""
        result = {}
        for k, val in v.items():
            if isinstance(val, str) and val.startswith('${') and val.endswith('}'):
                env_var = val[2:-1]
                result[k] = os.getenv(env_var, '')
            else:
                result[k] = val
        return result
```

### 4.3 DataSourcesConfig（总配置）

```python
class DataSourcesConfig(BaseModel):
    providers: dict[str, ProviderConfig]
    markets: dict[str, MarketDataSource]
    
    @field_validator('markets')
    @classmethod
    def validate_providers_exist(cls, v: dict, info) -> dict:
        """验证所有引用的 Provider 都已定义"""
        providers = set(info.data.get('providers', {}).keys())
        for market, ds in v.items():
            if ds.financial not in providers:
                raise ValueError(f"Market '{market}' references unknown provider: {ds.financial}")
        return v
```

### 4.4 默认配置示例

```python
# core/defaults.py
DEFAULT_DATASOURCES = DataSourcesConfig(
    providers={
        "tushare_a": ProviderConfig(
            name="tushare_a",
            module="value_investment.data.providers.tushare_provider",
            class_name="TushareProvider",
            init_kwargs={"token": "${TUSHARE_TOKEN}"},
            field_mappings={
                "income": {
                    "total_revenue": "total_revenue",
                    "net_profit": "net_profit",
                },
                "balance": {...},
                "cashflow": {...},
            }
        ),
        "yfinance": ProviderConfig(
            name="yfinance",
            module="value_investment.data.providers.yfinance_provider",
            class_name="YFinanceProvider",
            field_mappings={
                "market": {
                    "Close": "close",
                    "Open": "open",
                    "Volume": "volume",
                }
            }
        ),
    },
    markets={
        "A": MarketDataSource(financial="tushare_a", market="tushare_a"),
        "HK": MarketDataSource(financial="akshare_hk", market="yfinance"),
        "US": MarketDataSource(financial="akshare_us", market="yfinance"),
    }
)
```

---

## 五、测试策略

### 5.1 单元测试

| 测试文件 | 覆盖内容 |
|---------|---------|
| `test_settings.py` | Settings 加载、环境变量 |
| `test_config.py` | ProviderConfig 验证 |
| `test_defaults.py` | 默认配置完整性 |
| `test_container.py` | DI Container 组装 |
| `test_base_provider.py` | 字段映射逻辑 |

### 5.2 集成测试

| 测试文件 | 覆盖内容 |
|---------|---------|
| `test_tushare_provider.py` | Tushare 数据获取 |
| `test_yfinance_provider.py` | YFinance 数据获取 |
| `test_api_datasource.py` | API 层数据源切换 |

### 5.3 回归测试

| 测试文件 | 覆盖内容 |
|---------|---------|
| `test_indicators_regression.py` | 所有 Indicator 计算 |
| `test_data_consistency.py` | 数据一致性验证 |

---

## 六、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Tushare API 限制 | 数据获取失败 | 缓存策略、限流处理 |
| 字段映射不完整 | Indicator 计算失败 | 日志记录、逐步完善 |
| 现有代码不兼容 | 回归测试失败 | 分支开发、充分测试 |
| 性能下降 | 映射增加开销 | 基准测试、优化热点 |

---

## 七、完成标准

- [ ] 所有 Phase 任务完成
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 回归测试通过
- [ ] 文档完善
- [ ] Code Review 通过

---

## 八、参考文档

- [Pydantic 文档](https://docs.pydantic.dev/)
- [Dependency Injector 文档](https://python-dependency-injector.ets-labs.org/)
- [现有分析](docs/plans/2026-03-06-field-access-normalization-analysis.md)
