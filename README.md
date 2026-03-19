# value_investment

A 股/港股/美股基本面分析工具，支持动态计算器扩展。

## 核心特性

- **三市场支持**：A 股、港股、美股统一接口
- **Pipeline 架构**：基于 MessageBus 的数据处理流水线
- **Calculator 插件**：动态加载自定义财务指标计算器
- **IFRS 标准字段**：统一的字段命名规范
- **智能缓存**：多级 TTL 缓存策略

---

## 快速开始

### 安装

```bash
# 使用 uv（推荐）
uv tool install -e .

# 或使用 pip
pip install -e .
```

### 查询数据

```bash
# 查询单个字段（支持 10 年历史）
v-invest query 600519 --requires roe --years 10

# 查询多个字段
v-invest query 600519 --requires roe,roic,gross_margin --years 5

# 指定市场
v-invest query 00700 --requires roe --market HK --years 10
v-invest query AAPL --requires net_profit_margin --market US --years 10

# 输出格式（支持 markdown/json/plain）
v-invest query 600519 --requires roe --format json
```

### 验证配置

```bash
# 验证字段配置是否正确（dry run，不获取数据）
v-invest validate 600519 --requires implied_growth --market A
```

### 其他命令

```bash
# 列出所有可用字段
v-invest fields

# 按前缀筛选
v-invest fields --prefix ro

# 清除缓存
v-invest cache-clear          # 清除所有缓存
v-invest cache-clear 600519   # 清除指定股票缓存

# 查看版本
v-invest version
```

---

## 可用字段

| 类别 | 字段 |
|------|------|
| 盈利能力 | `roe`, `roa`, `roic`, `gross_margin`, `net_profit_margin`, `operating_profit_margin` |
| 财务数据 | `total_revenue`, `net_profit`, `gross_profit`, `operating_profit`, `parent_net_profit` |
| 资产负债表 | `total_assets`, `total_liabilities`, `total_equity`, `current_assets`, `current_liabilities` |
| 现金流量 | `operating_cash_flow`, `investing_cash_flow`, `financing_cash_flow` |
| 估值指标 | `pe_ratio`, `pb_ratio`, `market_cap`, `circ_market_cap` |
| 周转率 | `inventory_turnover`, `asset_turnover`, `receivable_turnover` |
| 增长指标 | `implied_growth` |

### 市场代码格式

| 市场 | 代码格式 | 示例 | 参数 |
|-----|---------|------|------|
| A 股 | 6 位数字 | 600519 | `A` |
| 港股 | 5 位数字 | 00700 | `HK` |
| 美股 | 字母 | AAPL | `US` |

---

## 自定义计算器

在 `calculators/` 目录下创建 `calc_xxx.py` 文件即可扩展指标：

```python
# calculators/calc_my_metric.py

name = "my_metric"

required_fields = [
    "total_revenue",
    "net_profit",
]

def calculate(results):
    if "total_revenue" not in results or "net_profit" not in results:
        return None
    return results["net_profit"] / results["total_revenue"] * 100
```

加载外部计算器：

```bash
v-invest query 600519 --requires my_metric --calculator ./my_calc.py
```

---

## 架构

```
value_investment/
├── pipeline/          # Pipeline 架构
│   ├── api.py        # PipelineAPI（高层接口）
│   ├── bus.py        # MessageBus（消息总线）
│   ├── container.py  # Container（依赖注入）
│   └── validator.py  # 验证器
├── handlers/         # 市场处理器
│   ├── a_share.py    # A 股
│   ├── hk_share.py   # 港股
│   └── us_share.py   # 美股
├── domain/
│   └── fields.py     # IFRS 标准字段定义
├── core/
│   ├── cache.py      # 智能缓存
│   └── types.py     # 类型定义
└── calculators/      # 内置计算器
    ├── calc_gross_profit.py
    ├── calc_roic.py
    └── ...
```

### 数据流

```
用户请求 → PipelineAPI → MessageBus → Handler（自动路由）→ Calculator → 结果
```

---

## 缓存策略

| 数据类型 | TTL |
|---------|-----|
| 个股信息 | 次日凌晨 (A 股) / 次年 6 月底 (港/美) |
| 历史价格 | 1 年 |
| 财务报表 | 次年 6 月底 |

缓存支持范围复用：缓存 [2015-2024] 可服务于 [2020-2024] 查询。

---

## 开发

```bash
# 安装开发依赖
uv sync --group dev

# 运行测试
uv run python -m pytest tests/ -v

# 启动 Python 交互
uv run python -c "from value_investment.pipeline.api import PipelineAPI; api = PipelineAPI()"
```

---

## 版本

当前版本：**0.3.0**
