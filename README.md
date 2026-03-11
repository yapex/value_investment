# value_investment

A股/港股/美股基本面分析工具，基于akshare数据。

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/yapex/value_investment.git
cd value_investment
```

### 2. 安装工具

使用 uv tool install 直接安装为命令行工具：

```bash
uv tool install -e .
```

或使用 pip：

```bash
pip install -e .
```

安装后，`v-invest` 命令将全局可用。

## 使用

```bash
v-invest info 600519
v-invest hist 600519 --end 20241231
v-invest financial 600519 --end 2024
v-invest analyze 600519
v-invest indicator ImpliedGrowth -s 600519
v-invest list
```

### 市场代码格式

- A股: 6位数字 (600519)
- 港股: 5位数字 (00700)
- 美股: 字母 (AAPL)

## 缓存策略

- 个股信息: 次日凌晨失效
- 历史数据: 1年
- 财务数据: 次年6月底

缓存支持范围复用: 缓存[2015-2024]可服务于[2020-2024]查询。

## 开发

> 注意：`uv run` 需要在项目根目录执行，使用 `pwd` 获取当前路径后再执行命令。

```bash
# 安装开发依赖
uv sync --group dev

# 运行测试
uv run python -m pytest tests/ -v

# 启动Python交互
uv run python -c "from value_investment import ValueInvestment; vi = ValueInvestment()"
```
