# 港股 Pipeline Provider 迁移计划

**目标**: 完成港股 Pipeline Provider 重构，支持 38 个 IFRS 字段 + 3 个 CustomFields

**时间**: 第一阶段

---

## 核心原则

1. **Provider 只提供数据，不做计算**
2. **数据源有什么就返回什么，缺失数据发出警告**
3. **需要计算的历史指标由 Calculator 处理**

---

## 已知限制

**AkShare `stock_hk_financial_indicator_em` API 问题**：
- 只返回最新一年的数据（不是多年历史）
- 多年历史指标需要通过 Calculator 从财务报表计算

---

## 现状分析

### 老代码港股 Provider (`hk_share_provider.py`)

| 方法 | 数据源 API | 说明 |
|-----|-----------|------|
| `get_balance_sheet()` | `ak.stock_financial_hk_report_em(symbol="资产负债表")` | 资产负债表（多年） |
| `get_income_statement()` | `ak.stock_financial_hk_report_em(symbol="利润表")` | 利润表（多年） |
| `get_cash_flow_statement()` | `ak.stock_financial_hk_report_em(symbol="现金流量表")` | 现金流量表（多年） |
| `get_stock_info()` | `ak.stock_hk_company_profile_em()` | 股票基本信息 |
| `get_financial_indicator()` | `ak.stock_hk_financial_indicator_em()` | 财务指标（**仅一年**） |

### 新架构目标接口 (`DataProvider` Protocol)

```python
class DataProvider(Protocol):
    def fetch_financial_data(
        self, stock_code: str, fields: set[str], end_year: int, years: int = 10
    ) -> dict[str, dict[int, Any]]: ...

    def fetch_indicators(
        self, stock_code: str, fields: set[str], end_year: int, years: int = 10
    ) -> dict[str, dict[int, Any]]: ...

    def fetch_market_data(
        self, stock_code: str, fields: set[str]
    ) -> dict[str, Any]: ...

    @property
    def supported_fields(self) -> set[str]: ...
```

---

## 任务拆分

### Task 1: 创建 `HKProvider` 基础结构 ✅ DONE

**文件**: `src/value_investment/pipeline/data/hk_provider.py`

**内容**:
- 类 `HKProvider` 实现 `DataProvider` Protocol
- 属性 `supported_fields` 返回该 Provider 支持的字段集合
- 初始化 AkShare 客户端
- 缓存配置

**验收标准**:
- [x] 类实现 `DataProvider` Protocol
- [x] `supported_fields` 返回正确的字段集合

---

### Task 2: 实现 `fetch_financial_data` - 财务报表 ✅ DONE

**数据源**: AkShare `stock_financial_hk_report_em()`

**实现逻辑**:
1. 根据字段判断需要调用哪些报表（资产负债表/利润表/现金流量表）
2. 调用 AkShare API 获取多年数据
3. 使用 `DataMapper` 映射字段名
4. 转换为 `{field: {year: value}}` 格式
5. 返回结果

**返回值格式**:
```python
{
    "total_assets": {2024: 1000, 2023: 900, 2022: 800},
    "total_revenue": {2024: 100, 2023: 90, 2022: 80},
    ...
}
```

**验收标准**:
- [x] 能获取多年（~10年）财务报表数据
- [x] 字段映射正确
- [x] 无数据时发出警告

---

### Task 3: 实现 `fetch_indicators` - 财务指标 ✅ DONE

**数据源**: AkShare `stock_hk_financial_indicator_em()`

**已知限制**: 只返回最新一年数据

**实现逻辑**:
1. 调用 AkShare API 获取财务指标
2. 映射字段名
3. 转换为 `{field: {year: value}}` 格式
4. **发出警告**：告知用户只有一年数据

**返回值格式**:
```python
{
    "roe": {2026: 21.13},  # 只有一年
    "roa": {2026: 11.77},
    "basic_eps": {2026: 24.75},
    ...
}
```

**警告信息**:
```python
warnings.warn(
    f"AkShare 港股财务指标 API 只返回最新一年数据，"
    f"多年历史指标请使用 Calculator 计算",
    UserWarning,
)
```

**验收标准**:
- [x] 能获取当前年度财务指标
- [x] 字段映射正确
- [x] 发出数据限制警告

---

### Task 4: 实现 `fetch_market_data` - 市值数据 ✅ DONE

**数据源**: AkShare `stock_hk_financial_indicator_em()` (与 Task 3 同一 API)

**需要获取的字段**:
- `market_cap` - 总市值
- `pe_ratio` - 市盈率
- `pb_ratio` - 市净率
- `total_shares` - 总股本
- `basic_eps` - 基本每股收益（已在 indicators 中）
- `diluted_eps` - 稀释每股收益
- `book_value_per_share` - 每股净资产

**实现逻辑**:
1. 调用 AkShare API 获取市值数据（复用 Task 3 的 API）
2. 映射字段名
3. 返回单时间点数据

**返回值格式**:
```python
{
    "market_cap": 3500000000000,
    "pe_ratio": 20.14,
    "pb_ratio": 3.92,
    ...
}
```

**验收标准**:
- [x] 能获取市值相关字段
- [x] 发出数据限制警告（如适用）

---

### Task 5: 集成测试 ✅ DONE

**测试文件**: `tests/pipeline/test_hk_provider.py`

**测试内容**:
- 单元测试：各方法返回值格式正确
- Mock 测试：不依赖真实 API
- 警告测试：验证警告信息正确发出

**验收标准**:
- [x] 所有测试通过 (13/13)
- [x] 警告测试验证 `warnings.warn` 被正确调用

---

### Task 6: 注册到 Container ✅ DONE

**文件**: `src/value_investment/pipeline/container.py`

**修改**:
- 添加 `hk_provider()` 方法
- 更新 Handler 注入

**验收标准**:
- [x] `Container` 能提供 `HKProvider`
- [x] Handler 能正确注入 Provider

---

### Task 7: 端到端验证 ⏳ 待验证

**验证场景**:
1. 通过 `PipelineAPI` 获取港股 `00700`（腾讯）的 ROE、ROA 等
2. 验证 Calculator 正常工作
3. 检查警告信息

**验收标准**:
- [ ] 能成功获取数据
- [ ] 警告信息正确
- [ ] Calculator 依赖链完整

**手动验证命令**:
```bash
uv run python -c "
from value_investment.pipeline.container import Container
container = Container.create()
provider = container.hk_provider()
result = provider.fetch_indicators('00700', {'roe', 'roa'}, 2024)
print(result)
"
```

---

## 依赖关系

```
Task 1 (基础结构)
    ↓
Task 2 (财务报表) ──┐
Task 3 (财务指标) ──┼── Task 6 (Container 注册)
Task 4 (市值数据) ──┘
    ↓
Task 5 (集成测试)
    ↓
Task 7 (端到端验证)
```

---

## 风险点

| 风险 | 影响 | 应对 |
|-----|------|------|
| AkShare API 不稳定 | 数据获取失败 | 添加异常处理，返回空数据 |
| 财务指标 API 只返回一年 | 历史指标缺失 | 警告 + Calculator 补充 |
| 字段映射缺失 | 某些字段无法获取 | 先实现能获取的字段 |

---

## 完成后

1. 运行 `test_validator.py` 验证 Calculator 依赖链
2. 运行 `test_ifrs_fields_lock.py` 验证字段锁定
3. 删除老代码（待第二阶段）

---

## 参考文档

- Pipeline 架构: `docs/pipeline-architecture.md`
- IFRS 标准字段: `docs/ifrs_standard_fields.md`
- A 股 Provider 实现: `src/value_investment/pipeline/data/tushare_provider.py`
