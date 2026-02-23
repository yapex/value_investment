# 财务三表字段筛选功能设计

## 背景

当前 `balance`, `income`, `cashflow` 三个命令返回完整数据，对 Agent token 不友好。用户希望只返回指定字段。

## 需求

- 支持指定只返回特定字段
- 默认包含 year 字段
- 支持 IFRS 标准字段 + 自定义字段
- 字段不存在时报错

## 设计

### CLI 参数

在 `balance`, `income`, `cashflow` 三个命令添加：

```python
fields: Optional[str] = typer.Option(None, "--fields", "-f", help="Comma-separated fields to return")
```

### 数据流

```
CLI --fields → 解析字段列表 → 验证字段存在 → DataFrame列筛选 → 返回结果
```

### 字段验证

- 始终添加 "year" 到字段列表
- 检查字段是否存在于 DataFrame 列中
- 不存在则报错并提示可用字段

## 验证

```bash
# 测试1: 查询净利润
uv run --directory . python -m value_investment.cli income 600519 --fields "net_profit"

# 测试2: 查询多个字段
uv run --directory . python -m value_investment.cli balance 00700 --fields "year,total_assets"

# 测试3: 不存在的字段
uv run --directory . python -m value_investment.cli income 600519 --fields "not_exist_field"
```
