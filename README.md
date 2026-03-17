# value_investment

A股/港股/美股基本面分析工具，基于 **tushare** (A股) + akshare (港股美股) 数据源。

## 一分钟快速上手

### 第一步：配置 Tushare Token

A股数据需要配置 Tushare Token（环境变量）：

```bash
# 方式一：临时设置（当前终端有效）
export TUSHARE_TOKEN=你的token

# 方式二：写入 ~/.bashrc 或 ~/.zshrc（永久生效）
echo 'export TUSHARE_TOKEN=你的token' >> ~/.bashrc  # 或 ~/.zshrc
source ~/.bashrc
```

获取 Token: https://tushare.pro/user/token

### 第二步：安装工具

```bash
# 使用 uv 安装（推荐）
uv tool install -e .

# 或使用 pip
pip install -e .
```

### 第三步：开始分析

```bash
# 查看股票基本信息
v-invest info 600519

# 查看历史股价
v-invest hist 600519 --end 20241231

# 查看财务指标（当前值）
v-invest indicator roe -s 600519 -m A

# 查看财务指标（10年历史）
v-invest indicator roe -s 600519 -m A -y 10

# 查看利润表
v-invest income 600519
```

---

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/yapex/value_investment.git
cd value_investment
```

### 2. 配置 Tushare Token

**A股数据必须配置 Tushare Token（环境变量）**：

```bash
# 方式一：临时设置（当前终端有效）
export TUSHARE_TOKEN=你的token

# 方式二：写入 ~/.bashrc 或 ~/.zshrc（永久生效）
echo 'export TUSHARE_TOKEN=你的token' >> ~/.bashrc  # 或 ~/.zshrc
source ~/.bashrc
```

获取 Token: https://tushare.pro/user/token

> **说明**：
> - A股数据：需要 Tushare Token
> - 港股/美股数据：无需 Token（使用 akshare + yfinance）

### 3. 安装工具

```bash
# 使用 uv（推荐）
uv tool install -e .

# 或使用 pip
pip install -e .
```

安装后，`v-invest` 命令将全局可用。

---

## 快速命令

| 功能 | 命令 |
|------|------|
| 基本信息 | `v-invest info 600519` |
| 历史股价 | `v-invest hist 600519 --end 20241231` |
| 利润表 | `v-invest income 600519` |
| 资产负债表 | `v-invest balance 600519` |
| 现金流量表 | `v-invest cashflow 600519` |
| 财务指标 | `v-invest finind 600519` |
| 指标当前值 | `v-invest indicator roe -s 600519 -m A` |
| 指标10年历史 | `v-invest indicator roe -s 600519 -m A -y 10` |
| PE百分位 | `v-invest indicator PEPct -s 600519 -m A -y 10` |
| 股票筛选 | `v-invest scan --filter "roe 连续5年 ≥15%"` |
| 查看缓存 | `v-invest scan-list` |

### 市场代码格式

| 市场 | 代码格式 | 示例 | 参数 |
|-----|---------|------|------|
| A股 | 6位数字 | 600519 | `A` |
| 港股 | 5位数字 | 00700 | `HK` |
| 美股 | 字母 | AAPL | `US` |

---

## 常用选项

- `-m` / `--market`：指定市场（A/HK/US）
- `-y` / `--years`：指定年数（当 > 1 时返回多年历史数据）
- `-s` / `--stock`：指定股票代码
- `--refresh` / `-r`：强制刷新缓存

---

## 缓存策略

| 数据类型 | TTL |
|---------|-----|
| 个股信息 | 次日凌晨 (A股) / 次年6月底 (港美) |
| 历史价格 | 1年 |
| 财务报表 | 次年6月底 |

缓存支持范围复用：缓存[2015-2024]可服务于[2020-2024]查询。

---

## 开发

```bash
# 安装开发依赖
uv sync --group dev

# 运行测试
uv run python -m pytest tests/ -v

# 启动 Python 交互
uv run python -c "from value_investment import ValueInvestment; vi = ValueInvestment()"
```

> 注意：`uv run` 需要在项目根目录执行。
