# 字段映射控制反转 (IoC) 重构设计

> 日期: 2025-03-19
> 目标: 将字段映射从"中心向外"改为"Provider 声明 + 框架执行"的 IoC 模式

---

## 一、当前问题

### 1.1 架构缺陷

```
当前架构（控制流错误）：
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   DataMapper    │────▶│  HKProvider     │────▶│   AKShare API   │
│  (中心化映射)    │     │ (被动接受映射)   │     │  (原始数据)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  TushareMapper  │
│  (中心化映射)    │
└─────────────────┘
```

**问题**：
- Provider 依赖外部 Mapper，耦合度高
- 新增 Provider 需要修改中心化 Mapper
- 不符合开闭原则

### 1.2 目标架构（控制反转）

```
目标架构（IoC）：
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Framework      │────▶│  HKProvider     │────▶│   AKShare API   │
│ (执行映射规则)   │     │ (声明映射规则)   │     │  (原始数据)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │
        │                        ▼
        │               ┌─────────────────┐
        │               │  MAPPINGS = {   │
        │               │    "原始字段":   │
        │               │    "标准字段"    │
        │               │  }              │
        │               └─────────────────┘
        ▼
┌─────────────────┐
│  输出标准字段DF  │
└─────────────────┘
```

**优势**：
- Provider 只声明规则，不执行映射
- 新增 Provider 只需声明 MAPPINGS，零改动其他代码
- 框架统一处理，逻辑集中

---

## 二、核心设计

### 2.1 字段映射数据结构

```python
# Provider 内部声明，最简单形式
class HKProvider(BaseProvider):
    """港股数据 Provider
    
    开发者只需声明 FIELD_MAPPINGS，框架自动处理映射。
    可以只映射一个字段，也可以映射全部字段。
    """
    
    FIELD_MAPPINGS: dict[str, dict[str, str]] = {
        "balance_sheet": {
            # "原始字段名": "标准字段名"
            "流动资产合计": "current_assets",
            "资产总计": "total_assets",
            "负债合计": "total_liabilities",
            # ... 可以只声明部分字段
        },
        "income_statement": {
            "营业收入": "total_revenue",
            "净利润": "net_profit",
        },
        "cash_flow": {
            "经营活动产生的现金流量净额": "operating_cash_flow",
        },
        "indicators": {
            "净资产收益率": "roe",
        },
    }
```

### 2.2 BaseProvider 框架实现

```python
from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class BaseProvider(ABC):
    """数据 Provider 基类 - IoC 模式
    
    子类只需：
    1. 声明 FIELD_MAPPINGS
    2. 实现 _fetch_* 方法（返回原始数据）
    
    框架自动：
    1. 调用 _fetch_* 获取原始数据
    2. 根据 FIELD_MAPPINGS 执行字段映射
    3. 返回标准字段名的 DataFrame
    """
    
    # 子类必须覆盖：声明字段映射
    FIELD_MAPPINGS: dict[str, dict[str, str]] = {}
    
    # ========================================================================
    # 公共 API（Template Method，子类不覆盖）
    # ========================================================================
    
    def get_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取资产负债表（标准字段）
        
        流程：
        1. 调用 _fetch_balance_sheet 获取原始数据
        2. 自动应用 FIELD_MAPPINGS["balance_sheet"] 映射
        3. 返回标准字段名的 DataFrame
        """
        raw_df = self._fetch_balance_sheet(stock_code, end_year, start_year)
        return self._standardize(raw_df, "balance_sheet")
    
    def get_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取利润表（标准字段）"""
        raw_df = self._fetch_income_statement(stock_code, end_year, start_year)
        return self._standardize(raw_df, "income_statement")
    
    def get_cash_flow_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取现金流量表（标准字段）"""
        raw_df = self._fetch_cash_flow(stock_code, end_year, start_year)
        return self._standardize(raw_df, "cash_flow")
    
    def get_financial_indicators(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """获取财务指标（标准字段）"""
        raw_df = self._fetch_indicators(stock_code, end_year, start_year)
        return self._standardize(raw_df, "indicators")
    
    # ========================================================================
    # 子类必须实现的抽象方法（只返回原始数据）
    # ========================================================================
    
    @abstractmethod
    def _fetch_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None,
    ) -> pd.DataFrame:
        """获取原始资产负债表数据
        
        Returns:
            DataFrame with native field names (原始字段名)
        """
        pass
    
    @abstractmethod
    def _fetch_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None,
    ) -> pd.DataFrame:
        """获取原始利润表数据"""
        pass
    
    @abstractmethod
    def _fetch_cash_flow(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None,
    ) -> pd.DataFrame:
        """获取原始现金流量表数据"""
        pass
    
    @abstractmethod
    def _fetch_indicators(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None,
    ) -> pd.DataFrame:
        """获取原始财务指标数据"""
        pass
    
    # ========================================================================
    # 私有方法（框架层统一处理）
    # ========================================================================
    
    def _standardize(
        self,
        df: pd.DataFrame | None,
        statement_type: str,
    ) -> pd.DataFrame:
        """将原始字段名映射为标准字段名
        
        规则：
        1. 只映射 FIELD_MAPPINGS 中声明的字段
        2. 原始数据中不存在的字段，静默忽略
        3. 未映射的原始字段，保留在 DataFrame 中
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        mapping = self.FIELD_MAPPINGS.get(statement_type, {})
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
    
    def get_supported_fields(self, statement_type: str | None = None) -> set[str]:
        """获取支持的字段列表
        
        Args:
            statement_type: 报表类型，None 返回所有
        
        Returns:
            支持的标准字段名集合
        """
        if statement_type:
            return set(self.FIELD_MAPPINGS.get(statement_type, {}).values())
        
        fields = set()
        for mapping in self.FIELD_MAPPINGS.values():
            fields.update(mapping.values())
        return fields
```

### 2.3 Provider 实现示例

#### 最小 Provider（只映射一个字段）

```python
class MinimalProvider(BaseProvider):
    """最小示例 Provider - 只提供 revenue 字段
    
    开发者贡献新 Provider 的最小示例。
    """
    
    FIELD_MAPPINGS = {
        "income_statement": {
            "revenue_native": "total_revenue",
        },
    }
    
    def _fetch_income_statement(self, stock_code, end_year, start_year):
        # 调用外部 API 获取原始数据
        data = external_api.get_financials(stock_code)
        return pd.DataFrame(data)
    
    # 其他方法返回空 DataFrame（未实现）
    def _fetch_balance_sheet(self, *args, **kwargs):
        return pd.DataFrame()
    
    def _fetch_cash_flow(self, *args, **kwargs):
        return pd.DataFrame()
    
    def _fetch_indicators(self, *args, **kwargs):
        return pd.DataFrame()
```

#### 完整 Provider（HKProvider 重构后）

```python
class HKProvider(BaseProvider):
    """港股数据 Provider - IoC 模式重构版
    
    只需声明 FIELD_MAPPINGS，无需关心映射逻辑。
    """
    
    FIELD_MAPPINGS = {
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
    
    def _fetch_balance_sheet(self, stock_code, end_year, start_year):
        hk_code = self._normalize_code(stock_code)
        df = ak.stock_financial_hk_report_em(
            stock=hk_code, symbol="资产负债表", indicator="年度"
        )
        return self._transform_to_wide(df)  # 返回原始字段名
    
    def _fetch_income_statement(self, stock_code, end_year, start_year):
        hk_code = self._normalize_code(stock_code)
        df = ak.stock_financial_hk_report_em(
            stock=hk_code, symbol="利润表", indicator="年度"
        )
        return self._transform_to_wide(df)
    
    def _fetch_cash_flow(self, stock_code, end_year, start_year):
        hk_code = self._normalize_code(stock_code)
        df = ak.stock_financial_hk_report_em(
            stock=hk_code, symbol="现金流量表", indicator="年度"
        )
        return self._transform_to_wide(df)
    
    def _fetch_indicators(self, stock_code, end_year, start_year):
        # 港股指标 API 只返回最新数据
        hk_code = self._normalize_code(stock_code)
        return ak.stock_hk_financial_indicator_em(symbol=hk_code)
    
    def _normalize_code(self, symbol: str) -> str:
        """标准化港股代码"""
        digits = "".join(c for c in symbol if c.isdigit())
        return digits.zfill(5)
    
    def _transform_to_wide(self, df: pd.DataFrame) -> pd.DataFrame:
        """将长表转为宽表，保持原始字段名"""
        if df.empty:
            return df
        
        # 找到字段名列
        item_col = "STD_ITEM_NAME" if "STD_ITEM_NAME" in df.columns else "ITEM_NAME"
        
        if item_col not in df.columns or "AMOUNT" not in df.columns:
            return df
        
        # 提取年份
        df = df.copy()
        df["year"] = pd.to_datetime(df["REPORT_DATE"]).dt.year
        
        # 透视：保持原始字段名（item_col 的值）
        wide = df.pivot_table(
            index="year",
            columns=item_col,
            values="AMOUNT",
            aggfunc="first",
        )
        return wide.reset_index()
```

---

## 三、迁移计划

### 3.1 文件变更清单

| 文件 | 操作 | 说明 |
|-----|------|------|
| `src/value_investment/providers/base.py` | 修改 | 重构 BaseProvider，添加 IoC 逻辑 |
| `src/value_investment/providers/hk_share.py` | 修改 | 重构为声明式映射 |
| `src/value_investment/providers/us_share.py` | 修改 | 重构为声明式映射 |
| `src/value_investment/providers/tushare_mapper.py` | 删除 | 不再需要中心化 mapper |
| `src/value_investment/providers/a_share.py` | 修改 | 重构为声明式映射 |
| `src/value_investment/mapper.py` | 删除 | 删除旧版中心化 mapper |

### 3.2 迁移步骤

```
Step 1: 重构 BaseProvider
    - 添加 FIELD_MAPPINGS 类属性
    - 添加 _standardize() 方法
    - 修改 get_balance_sheet 等公共方法
    - 修改抽象方法 _fetch_balance_sheet 等

Step 2: 重构 HKProvider
    - 删除 DataMapper 导入
    - 声明 FIELD_MAPPINGS
    - 简化 _fetch_* 方法（只做数据获取和转换）
    - 删除主动映射调用

Step 3: 重构 USProvider
    - 同上

Step 4: 重构 TushareProvider
    - 删除 TushareFieldMapper
    - 声明 FIELD_MAPPINGS
    - 简化代码

Step 5: 清理
    - 删除 mapper.py
    - 删除 tushare_mapper.py
    - 更新所有导入

Step 6: 测试
    - 验证所有 provider 正常工作
    - 验证字段映射正确
```

---

## 四、接口对比

### 4.1 旧接口（Provider 主动映射）

```python
class HKProvider(BaseProvider):
    def _fetch_balance_sheet(self, ...):
        raw = ak.get_data(...)
        wide = self._transform(raw)
        # Provider 必须知道如何映射
        return DataMapper.map_balance_sheet(wide)  # 主动调用
```

### 4.2 新接口（框架自动映射）

```python
class HKProvider(BaseProvider):
    FIELD_MAPPINGS = {
        "balance_sheet": {
            "流动资产合计": "current_assets",
            ...
        }
    }
    
    def _fetch_balance_sheet(self, ...):
        raw = ak.get_data(...)
        return self._transform(raw)  # 只返回原始字段，不映射
        # 框架自动调用 _standardize()
```

---

## 五、贡献者指南

### 5.1 添加新 Provider 的步骤

```python
# Step 1: 创建文件 src/value_investment/providers/my_provider.py

from value_investment.providers.base import BaseProvider
import pandas as pd


class MyProvider(BaseProvider):
    """我的数据源 Provider
    
    只需声明 FIELD_MAPPINGS，框架自动处理映射。
    """
    
    # Step 2: 声明字段映射（可以只声明部分字段）
    FIELD_MAPPINGS = {
        "balance_sheet": {
            "原始字段1": "total_assets",
            "原始字段2": "total_liabilities",
        },
        "income_statement": {
            "原始收入字段": "total_revenue",
        },
    }
    
    # Step 3: 实现 _fetch_* 方法（返回原始字段数据）
    def _fetch_balance_sheet(self, stock_code, end_year, start_year):
        data = my_api.get_balance_sheet(stock_code)
        return pd.DataFrame(data)
    
    def _fetch_income_statement(self, stock_code, end_year, start_year):
        data = my_api.get_income_statement(stock_code)
        return pd.DataFrame(data)
    
    def _fetch_cash_flow(self, stock_code, end_year, start_year):
        # 如果不支持，返回空 DataFrame
        return pd.DataFrame()
    
    def _fetch_indicators(self, stock_code, end_year, start_year):
        return pd.DataFrame()
```

### 5.2 字段映射查找技巧

```python
# 1. 先打印原始数据的列名
raw_df = my_api.get_data()
print(raw_df.columns.tolist())

# 2. 对照标准字段名，创建映射
# 标准字段名参见：src/value_investment/domain/fields.py

# 3. 声明映射
FIELD_MAPPINGS = {
    "balance_sheet": {
        "原始看到的字段名": "total_assets",  # 标准字段名
    }
}
```

---

## 六、测试策略

### 6.1 单元测试

```python
def test_provider_field_mappings():
    """测试 Provider 字段映射正确"""
    provider = HKProvider(cache)
    
    # 获取标准字段数据
    df = provider.get_balance_sheet("00700", 2024, 2020)
    
    # 验证列名是标准字段
    assert "total_assets" in df.columns
    assert "current_assets" in df.columns
    
    # 验证原始字段已被映射
    assert "资产总计" not in df.columns  # 原始字段名不应存在


def test_partial_mappings():
    """测试部分字段映射"""
    provider = MinimalProvider(cache)
    
    df = provider.get_income_statement("00001", 2024, 2020)
    
    # 只映射了 total_revenue
    assert "total_revenue" in df.columns
```

### 6.2 集成测试

```python
def test_end_to_end():
    """端到端测试：从 API 到标准字段"""
    provider = HKProvider(cache)
    
    # 完整流程
    df = provider.get_balance_sheet("00700", 2024, 2020)
    
    # 验证数据正确性
    assert not df.empty
    assert "year" in df.columns
    assert "total_assets" in df.columns
    assert df["total_assets"].dtype == float
```

---

## 七、风险评估

| 风险 | 可能性 | 影响 | 缓解措施 |
|-----|--------|------|---------|
| 字段映射错误 | 中 | 高 | 增加单元测试，验证映射正确性 |
| 原始字段名变化 | 低 | 中 | 监控 API 变化，版本锁定 |
| 性能下降 | 低 | 低 | 映射是简单的 rename，开销极小 |
| 向后不兼容 | 高 | 中 | 这是预期内的破坏性变更 |

---

## 八、总结

### 8.1 设计原则

1. **控制反转 (IoC)**：Provider 声明规则，框架执行规则
2. **最小知识原则**：Provider 不需要知道如何映射，只需要声明映射
3. **开闭原则**：新增 Provider 无需修改框架代码
4. **渐进式**：可以只映射一个字段，逐步完善

### 8.2 关键变更

| 项目 | 旧架构 | 新架构 |
|-----|--------|--------|
| 映射方向 | 中心 → Provider | Provider → 框架 |
| Provider 职责 | 获取数据 + 执行映射 | 只获取数据 |
| 新增 Provider | 修改中心化 Mapper | 声明 FIELD_MAPPINGS |
| 代码量 | Provider 需要调用 Mapper | Provider 只声明 dict |

### 8.3 预期收益

- **开发者体验**：贡献 Provider 只需 10 行代码声明映射
- **可维护性**：映射逻辑集中在框架，易于统一修改
- **可测试性**：映射逻辑独立，易于单元测试
- **扩展性**：支持任意数量的 Provider，零冲突

---

## 附录：标准字段参考

参见 `src/value_investment/domain/fields.py` 中的 `IFRSFields` 类。

常用标准字段：

```python
# 资产负债表
total_assets, total_liabilities, total_equity
current_assets, current_liabilities
cash_and_equivalents, inventory
accounts_receivable, accounts_payable

# 利润表
total_revenue, net_profit, operating_profit, operating_cost

# 现金流量表
operating_cash_flow, investing_cash_flow, financing_cash_flow

# 财务指标
roe, roa, gross_margin, net_profit_margin
```
