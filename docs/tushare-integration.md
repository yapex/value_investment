# Tushare 集成指南

## 概述

Tushare 是一个免费、开源的财经数据接口包，提供 A 股、基金、期货、债券等金融数据。

**官网**: https://tushare.pro  
**文档**: https://tushare.pro/document/2

---

## 快速开始

### 1. 注册获取 Token

1. 访问 https://tushare.pro/register 注册账号
2. 登录后在个人中心获取 Token
3. 设置环境变量：

```bash
# .env 文件
TUSHARE_TOKEN=your_token_here
```

### 2. 安装依赖

```bash
uv add tushare
```

### 3. 基本使用

```python
import tushare as ts

# 设置 token
ts.set_token("your_token")

# 初始化 API
api = ts.pro_api()

# 获取股票基本信息
df = api.stock_basic(ts_code="000001.SZ")
print(df)

# 获取资产负债表
df = api.balancesheet(ts_code="000001.SZ", start_date="20230101", end_date="20231231")
print(df)
```

---

## 核心 API 接口

### 股票基本信息

```python
# 股票列表
df = api.stock_basic(
    exchange="",  # 交易所 (SSE/ SZSE/ BSE)
    list_status="L",  # L 上市/D 退市/P 暂停
    fields="ts_code,name,area,industry,market,list_date"
)

# 单个股票信息
df = api.stock_basic(ts_code="000001.SZ")
```

### 财务报表

#### 资产负债表

```python
df = api.balancesheet(
    ts_code="000001.SZ",
    start_date="20230101",
    end_date="20231231",
    fields="ts_code,end_date,total_assets,total_liab,total_hldr_eqy_inc_monetary_cap,acct_rcv,inventories,fixed_assets,acct_pay"
)
```

#### 利润表

```python
df = api.income(
    ts_code="000001.SZ",
    start_date="20230101",
    end_date="20231231",
    fields="ts_code,end_date,total_revenue,operating_revenue,net_profit,operating_profit,gross_profit,operating_cost"
)
```

#### 现金流量表

```python
df = api.cashflow(
    ts_code="000001.SZ",
    start_date="20230101",
    end_date="20231231",
    fields="ts_code,end_date,operating_cash_flow,investing_cash_flow,financing_cash_flow,capex"
)
```

### 行情数据

#### 日线行情

```python
df = api.daily(
    ts_code="000001.SZ",
    start_date="20230101",
    end_date="20231231",
    adj="qfq"  # 复权类型：""不复权/"qfq"前复权/"hfq"后复权
)
```

#### 复权因子

```python
df = api.adj_factor(ts_code="000001.SZ", trade_date="20231231")
```

---

## 字段映射说明

### Tushare 字段 → 标准字段

#### 资产负债表

| Tushare 字段 | 标准字段 | 说明 |
|------------|---------|------|
| `total_assets` | `total_assets` | 资产总计 |
| `total_liab` | `total_liabilities` | 负债合计 |
| `total_hldr_eqy_inc_monetary_cap` | `total_equity` | 股东权益合计 |
| `monetary_cap` | `cash_and_equivalents` | 货币资金 |
| `acct_rcv` | `accounts_receivable` | 应收账款 |
| `inventories` | `inventory` | 存货 |
| `fixed_assets` | `fixed_assets` | 固定资产 |
| `acct_pay` | `accounts_payable` | 应付账款 |

#### 利润表

| Tushare 字段 | 标准字段 | 说明 |
|------------|---------|------|
| `total_revenue` | `total_revenue` | 营业总收入 |
| `operating_revenue` | `total_revenue` | 营业收入 |
| `net_profit` | `net_profit` | 净利润 |
| `operating_profit` | `operating_profit` | 营业利润 |
| `gross_profit` | `gross_profit` | 毛利 |
| `operating_cost` | `operating_cost` | 营业成本 |

#### 现金流量表

| Tushare 字段 | 标准字段 | 说明 |
|------------|---------|------|
| `operating_cash_flow` | `operating_cash_flow` | 经营活动现金流 |
| `investing_cash_flow` | `investing_cash_flow` | 投资活动现金流 |
| `financing_cash_flow` | `financing_cash_flow` | 筹资活动现金流 |
| `capex` | `capital_expenditure` | 资本支出 |

#### 行情数据

| Tushare 字段 | 标准字段 | 说明 |
|------------|---------|------|
| `trade_date` | `date` | 交易日期 |
| `open` | `open` | 开盘价 |
| `high` | `high` | 最高价 |
| `low` | `low` | 最低价 |
| `close` | `close` | 收盘价 |
| `vol` | `volume` | 成交量 |
| `amount` | `turnover` | 成交额 |

---

## 在项目中集成

### 配置文件 (core/defaults.py)

```python
from value_investment.core.config import ProviderConfig

TUSHARE_A_CONFIG = ProviderConfig(
    name="tushare_a",
    module="value_investment.data.providers.tushare_provider",
    class_name="TushareProvider",
    init_kwargs={"token": "${TUSHARE_TOKEN}"},
    field_mappings={
        "balance": {
            "ts_code": "stock_code",
            "end_date": "report_date",
            "total_assets": "total_assets",
            "total_liab": "total_liabilities",
            # ... 更多映射
        },
        "income": {...},
        "cashflow": {...},
        "market": {...},
    }
)
```

### Provider 实现 (data/providers/tushare_provider.py)

```python
from value_investment.data.providers.base_provider import BaseProvider
import tushare as ts

class TushareProvider(BaseProvider):
    def __init__(self, cache, field_mappings=None, token=""):
        super().__init__(cache, field_mappings, token=token)
        ts.set_token(token)
        self._api = ts.pro_api()
    
    def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
        df = self._api.balancesheet(
            ts_code=stock_code,
            start_date=f"{end_year - 5}0101",
            end_date=f"{end_year}1231",
        )
        return self._apply_mapping(df, "balance")
    
    # ... 其他方法
```

---

## 注意事项

### 1. Token 权限

Tushare 采用积分制，不同接口需要不同积分：

| 接口 | 所需积分 | 说明 |
|------|---------|------|
| 股票基本信息 | 120 积分 | 基础信息 |
| 财务报表 | 300 积分 | 资产负债表、利润表、现金流 |
| 日线行情 | 120 积分 | 日频行情 |
| 复权因子 | 300 积分 | 复权数据 |

**获取积分方式**:
- 注册送 100 积分
- 每日签到
- 充值（100 元=1000 积分）
- 贡献代码/文档

### 2. 调用限制

- 基础用户：500 次/分钟
- 积分用户：根据积分等级提升

### 3. 数据更新频率

- 股票基本信息：每日更新
- 财务报表：季报/年报发布后更新
- 行情数据：交易日 18:00 后更新

### 4. 错误处理

```python
try:
    df = api.balancesheet(ts_code="000001.SZ")
except Exception as e:
    if "权限不够" in str(e):
        # 处理积分不足
        pass
    elif "超过限制" in str(e):
        # 处理调用频率限制
        pass
    else:
        raise
```

---

## 测试

### 单元测试

```python
import pytest
import os
from value_investment.data.providers.tushare_provider import TushareProvider

@pytest.fixture
def provider():
    token = os.getenv("TUSHARE_TOKEN")
    return TushareProvider(cache=MockCache(), token=token)

def test_get_balance_sheet(provider):
    df = provider.get_balance_sheet("000001.SZ", 2023)
    assert not df.empty
    assert "total_assets" in df.columns
```

### 集成测试

```python
from value_investment.api import ValueInvestment

vi = ValueInvestment(market="A")

# 获取财务数据
balance = vi.get_balance_sheet("000001", end_year=2023)
print(balance)

# 获取历史行情
hist = vi.get_historical_data("000001", end_date="20231231")
print(hist)
```

---

## 参考资料

- [Tushare 官方文档](https://tushare.pro/document/2)
- [Tushare GitHub](https://github.com/waditu/tushare)
- [Tushare 社区](https://tushare.pro/user/index)
