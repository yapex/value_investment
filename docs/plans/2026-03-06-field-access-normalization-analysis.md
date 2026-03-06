# 字段访问规范化改造识别报告

**日期**: 2026-03-06  
**目标**: 实现"数据源 → 映射层 (严格过滤) → 计算层 (零防御)"架构

---

## 一、改造范围总览

| 类别 | 数量 | 说明 |
|-----|------|------|
| **Indicator 类** | 37 个 | 继承 BaseIndicator 的所有指标 |
| **calculate() 方法** | 37 个 | 需要添加字段验证 |
| **_find_column 调用** | 117 处 | 需要移除或替换 |
| **data[...] 直接访问** | 126 处 | 需要保留（验证后直接使用） |
| **get_required_fields()** | 37 个 | 需要统一实现 |

---

## 二、按文件分类的改造清单

### 2.1 profitability.py (5 个指标)

| 指标类 | 当前状态 | 改造点 |
|-------|---------|-------|
| ROEIndicator | ✓ 有 get_required_fields | 移除 _find_column，添加 _required_fields 声明 |
| ROAIndicator | ✓ 有 get_required_fields | 移除 _find_column，添加 _required_fields 声明 |
| GrossMarginIndicator | ✓ 有 get_required_fields | 移除 _find_column，添加 _required_fields 声明 |
| NetProfitMarginIndicator | ✓ 有 get_required_fields | 移除 _find_column，添加 _required_fields 声明 |
| OperatingProfitMarginIndicator | ✓ 有 get_required_fields | 移除 _find_column，添加 _required_fields 声明 |

**字段需求**:
- ROE: `['net_profit', 'total_equity']`
- ROA: `['net_profit', 'total_assets']`
- GrossMargin: `['operating_income', 'total_revenue', 'operating_cost']`
- NetProfitMargin: `['net_profit', 'operating_income', 'total_revenue']`
- OperatingProfitMargin: `['operating_profit', 'operating_income', 'total_revenue']`

---

### 2.2 efficiency.py (12 个指标)

| 指标类 | 当前状态 | 改造点 |
|-------|---------|-------|
| AssetTurnoverIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| InventoryTurnoverIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| ReceivableTurnoverIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| PayableTurnoverIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| ExpenseRatioIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| FeeRateIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| FixedAssetTurnoverIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| FeeToGrossProfitRatioIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| AccountsReceivableRatioIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| ProductionAssetRatioIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| ReturnOnProductionAssetsIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| ReceivablesToAssetsRatioIndicator | ✓ 有 get_required_fields | 移除 _find_column |

**字段需求** (部分示例):
- AssetTurnover: `['operating_income', 'total_assets']`
- InventoryTurnover: `['operating_cost', 'inventory']`
- FeeToGrossProfitRatio: `['operating_income', 'operating_cost', 'sales_expense', 'management_expense', 'financial_expense']`

---

### 2.3 growth.py (6 个指标)

| 指标类 | 当前状态 | 改造点 |
|-------|---------|-------|
| ROICIndicator | ? 待检查 | 检查 get_required_fields |
| CAGRIndicator | ? 待检查 | 检查 get_required_fields |
| RevenueGrowthIndicator | ? 待检查 | 检查 get_required_fields |
| OperatingProfitGrowthIndicator | ? 待检查 | 检查 get_required_fields |
| TotalAssetGrowthIndicator | ? 待检查 | 检查 get_required_fields |
| NetAssetGrowthIndicator | ? 待检查 | 检查 get_required_fields |

---

### 2.4 solvency.py (3 个指标)

| 指标类 | 当前状态 | 改造点 |
|-------|---------|-------|
| CurrentRatioIndicator | ? 待检查 | 检查 get_required_fields |
| QuickRatioIndicator | ? 待检查 | 检查 get_required_fields |
| DebtRatioIndicator | ? 待检查 | 检查 get_required_fields |

**字段需求**:
- CurrentRatio: `['current_assets', 'current_liabilities']`
- QuickRatio: `['current_assets', 'inventory', 'current_liabilities']`
- DebtRatio: `['total_liabilities', 'total_assets']`

---

### 2.5 safety.py (2 个指标)

| 指标类 | 当前状态 | 改造点 |
|-------|---------|-------|
| CashToDebtIndicator | ✓ 有 get_required_fields | 移除 _find_column |
| DebtRatioTotalIndicator | ✓ 有 get_required_fields | 移除 _find_column |

**字段需求**:
- CashToDebt: `['cash_and_equivalents', 'short_term_debt', 'long_term_debt', 'bonds_payable']`
- DebtRatioTotal: `['total_assets', 'short_term_debt', 'long_term_debt', 'bonds_payable']`

---

### 2.6 cashflow.py (3 个指标)

| 指标类 | 当前状态 | 改造点 |
|-------|---------|-------|
| CfoToNetprofitIndicator | ? 待检查 | 检查 get_required_fields |
| FcfToRevenueIndicator | ? 待检查 | 检查 get_required_fields |
| CfoToNetprofitSumIndicator | ? 待检查 | 检查 get_required_fields |

**字段需求**:
- CfoToNetprofit: `['operating_cash_flow', 'net_profit']`
- FcfToRevenue: `['operating_cash_flow', 'investing_cash_flow', 'total_revenue']`

---

### 2.7 valuation.py (4 个指标)

| 指标类 | 当前状态 | 改造点 |
|-------|---------|-------|
| LatestMarketCapIndicator | ? 复杂，有外部依赖 | 特殊处理 |
| ImpliedGrowthIndicator | ? 复杂，有外部依赖 | 特殊处理 |
| PEPercentileIndicator | ? 复杂，有外部依赖 | 特殊处理 |
| MarketCapIndicator | ? 待检查 | 检查 get_required_fields |

**特殊说明**: 这些指标有 `needs` 依赖（prices, financial_indicator 等），需要特殊处理。

---

### 2.8 market_cap.py (1 个指标)

| 指标类 | 当前状态 | 改造点 |
|-------|---------|-------|
| MarketCapIndicator | ? 待检查 | 检查 get_required_fields |

---

## 三、DataMapper 改造点

### 3.1 当前状态

```python
# 当前 map_balance_sheet 等方法没有严格过滤
def map_balance_sheet(cls, df: pd.DataFrame, keep_original: bool = True) -> pd.DataFrame:
    # 只重命名，不过滤
    result = df.rename(columns=rename_map)
    return result
```

### 3.2 需要改造

```python
# 改造后：严格过滤
def map_balance_sheet(cls, df: pd.DataFrame, strict: bool = True) -> pd.DataFrame:
    # 1. 重命名
    result = df.rename(columns=rename_map)
    
    # 2. 严格过滤：只保留 CORE_FIELD_MAPPING 中定义的字段
    if strict:
        allowed_fields = set(CORE_FIELD_MAPPING.keys())
        allowed_fields.add('year')  # 保留 year 字段
        allowed_fields.add('REPORT_DATE')  # 保留日期字段
        result = result[[c for c in result.columns if c in allowed_fields]]
    
    return result
```

---

## 四、API 层改造点

### 4.1 _get_financial_data 方法

**当前**:
```python
def _get_financial_data(self, symbol, end_year):
    balance = self._provider.get_balance_sheet(symbol, end_year)
    balance = DataMapper.map_balance_sheet(balance)
    # ... 合并逻辑
    return merged
```

**改造后**:
```python
def _get_financial_data(self, symbol, end_year):
    balance = self._provider.get_balance_sheet(symbol, end_year)
    balance = DataMapper.map_balance_sheet(balance, strict=True)  # 严格过滤
    
    # 验证：检查是否有未映射的重要字段被丢弃
    unmapped = self._log_unmapped_fields(balance, original_df)
    
    return merged
```

---

## 五、BaseIndicator 改造点

### 5.1 添加字段验证装饰器/方法

```python
class BaseIndicator(ABC):
    _required_fields: list[str] = []  # 类属性声明
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        pass
    
    def get_required_fields(self) -> list:
        """自动返回 _required_fields，避免手动维护"""
        return self._required_fields
    
    def _validate_fields(self, data: pd.DataFrame) -> None:
        """验证 DataFrame 包含所有 required_fields"""
        required = self.get_required_fields()
        missing = [f for f in required if f not in data.columns]
        if missing:
            raise FieldAccessError(
                f"Indicator '{self.name}' missing required fields: {missing}. "
                f"Available fields: {list(data.columns)}"
            )
```

---

## 六、CORE_FIELD_MAPPING 扩展需求

### 6.1 需要添加的市场特有字段

**港股特有**:
```python
"hk_dividend_yield": {"A 股": None, "港股": "股息率 TTM(%)", "美股": None},
"hk_payout_ratio": {"A 股": None, "港股": "派息比率 (%)", "美股": None},
"hk_dividend_per_share": {"A 股": None, "港股": "每股股息 TTM(港元)", "美股": None},
```

**A 股特有**:
```python
"deducted_net_profit": {"A 股": "扣非净利润", "港股": None, "美股": None},
```

---

## 七、TDD 改造顺序建议

### Phase 1: 基础设施 (1-2 天)
1. [ ] 扩展 `CORE_FIELD_MAPPING` 支持市场特有字段
2. [ ] 改造 `DataMapper` 添加严格过滤
3. [ ] 改造 `BaseIndicator` 添加 `_validate_fields()`
4. [ ] 编写基础设施测试

### Phase 2: 简单指标 (3-5 天)
**优先级：高（使用频率高）**
1. [ ] profitability.py (5 个) - ROE, ROA, 毛利率，净利率
2. [ ] solvency.py (3 个) - 流动比率，速动比率，资产负债率
3. [ ] safety.py (2 个) - CashToDebt, DebtRatioTotal

### Phase 3: 效率指标 (2-3 天)
1. [ ] efficiency.py (12 个) - 周转率类指标

### Phase 4: 增长与现金流 (2-3 天)
1. [ ] growth.py (6 个)
2. [ ] cashflow.py (3 个)

### Phase 5: 复杂指标 (3-5 天)
1. [ ] valuation.py (4 个) - 需要特殊处理外部依赖

---

## 八、测试覆盖要求

每个指标改造后需要：
1. [ ] 单元测试：验证字段访问正确
2. [ ] 集成测试：验证三市场数据都能计算
3. [ ] 边界测试：验证缺失字段时的错误处理

---

## 九、风险与缓解

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 映射表不完整 | 某些市场字段丢失 | 添加 unmapped fields 日志，逐步补充 |
| 现有测试失败 | 阻塞 CI/CD | 分批次提交，每批确保测试通过 |
| 性能下降 | 过滤增加开销 | 基准测试，优化过滤逻辑 |

---

## 十、完成标准

- [ ] 所有 37 个指标都有 `_required_fields` 声明
- [ ] 所有指标都不再使用 `_find_column()`
- [ ] DataMapper 默认启用严格过滤
- [ ] 所有单元测试通过
- [ ] 三市场数据都能正常计算
- [ ] 新增指标必须遵循新规范（CI 检查）
