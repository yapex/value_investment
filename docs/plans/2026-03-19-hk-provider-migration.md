# 港股 Pipeline Provider 迁移计划

**目标**: 完成港股 Pipeline Provider 重构，支持 38 个 IFRS 字段 + 3 个 CustomFields

**时间**: 第一阶段

---

## 现状分析

### 老代码港股 Provider (`hk_share_provider.py`)

| 方法 | 数据源 API | 说明 |
|-----|-----------|------|
| `get_balance_sheet()` | `ak.stock_financial_hk_report_em(symbol="资产负债表")` | 资产负债表 |
| `get_income_statement()` | `ak.stock_financial_hk_report_em(symbol="利润表")` | 利润表 |
| `get_cash_flow_statement()` | `ak.stock_financial_hk_report_em(symbol="现金流量表")` | 现金流量表 |
| `get_stock_info()` | `ak.stock_hk_company_profile_em()` | 股票基本信息 |
| `get_financial_indicator()` | `ak.stock_hk_financial_indicator_em()` + 三表补充 | 财务指标 |

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

### 字段映射

复用 `CORE_FIELD_MAPPING` 中的港股映射，无需新增。

---

## 任务拆分

### Task 1: 创建 `HKDataProvider` 基础结构

**文件**: `src/value_investment/pipeline/data/hk_provider.py`

**内容**:
- 类 `HKDataProvider` 实现 `DataProvider` Protocol
- 属性 `supported_fields` 返回该 Provider 支持的字段集合
- 方法 `fetch_financial_data()` - 封装财务报表获取
- 方法 `fetch_indicators()` - 封装财务指标获取
- 方法 `fetch_market_data()` - 封装市值数据获取

**验收标准**:
- [ ] 类实现 `DataProvider` Protocol
- [ ] `supported_fields` 返回正确的字段集合

---

### Task 2: 实现财务报表获取 (`fetch_financial_data`)

**数据源**: AkShare `stock_financial_hk_report_em()`

**实现逻辑**:
1. 接收字段集合 `fields`
2. 遍历需要的报表类型（资产负债表/利润表/现金流量表）
3. 调用 AkShare API 获取数据
4. 使用 `DataMapper.map_xxx()` 映射字段名
5. 转换为 `{field: {year: value}}` 格式返回

**返回值格式**:
```python
{
    "total_assets": {2024: 1000, 2023: 900},
    "total_revenue": {2024: 100, 2023: 90},
    ...
}
```

**验收标准**:
- [ ] 能获取资产负债表字段
- [ ] 能获取利润表字段
- [ ] 能获取现金流量表字段
- [ ] 字段映射正确

---

### Task 3: 实现财务指标获取 (`fetch_indicators`)

**数据源**: AkShare `stock_hk_financial_indicator_em()` + 三表补充

**实现逻辑**:
1. 接收字段集合 `fields`
2. 调用 AkShare API 获取基础指标
3. 从三表补充更多指标（参考老代码 `_enrich_hk_indicators_from_statements`）
4. 映射字段名
5. 转换为 `{field: {year: value}}` 格式返回

**验收标准**:
- [ ] 能获取 ROE、ROA 等基础指标
- [ ] 能补充计算毛利率、净利率等

---

### Task 4: 实现市值数据获取 (`fetch_market_data`)

**数据源**: 待确认（参考老代码 `get_stock_info`）

**需要获取的字段**:
- `market_cap` - 总市值
- `pe_ratio` - 市盈率
- `pb_ratio` - 市净率
- `total_shares` - 总股本
- `basic_eps` - 基本每股收益
- `diluted_eps` - 稀释每股收益
- `book_value_per_share` - 每股净资产

**验收标准**:
- [ ] 能获取市值相关字段

---

### Task 5: 集成测试

**测试文件**: `tests/pipeline/test_hk_provider.py`

**测试内容**:
- 单元测试：各方法返回值格式正确
- 端到端测试：通过 Pipeline 获取港股数据

**验收标准**:
- [ ] 所有测试通过
- [ ] 能通过 `PipelineAPI` 获取港股数据

---

### Task 6: 注册到 Container

**文件**: `src/value_investment/pipeline/container.py`

**修改**:
- 添加 `HKDataProvider` 实例创建方法
- 在 `create()` 中注册到 Handler

**验收标准**:
- [ ] `Container` 能提供 `HKDataProvider`
- [ ] Handler 能正确注入 Provider

---

### Task 7: 端到端验证

**验证场景**:
1. 获取港股 `00700`（腾讯）的 ROE、ROA、毛利率等
2. 获取港股 `09988`（阿里巴巴）的市值、PE、PB 等
3. 验证 Calculator（gross_profit, inventory_turnover 等）正常工作

**验收标准**:
- [ ] 能成功获取真实数据
- [ ] 字段数量和格式正确

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
| 港股字段映射缺失 | 某些字段无法获取 | 先实现能获取的字段，缺失部分记录 |
| 数据年份不完整 | 返回数据少于预期 | 警告：有多少返回多少 |

---

## 完成后

- 删除老代码 `src/value_investment/data/providers/hk_share_provider.py`（待第二阶段）
- 运行 `test_validator.py` 验证 Calculator 依赖链
- 运行 `test_ifrs_fields_lock.py` 验证字段锁定
