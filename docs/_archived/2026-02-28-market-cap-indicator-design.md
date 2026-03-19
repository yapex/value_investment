# MarketCap Indicator 设计文档

> **日期:** 2026-02-28
> **目标:** 让 `market_cap` 指标可用，自动检测市场返回对应市值

## 问题

当前状态：
- `list-indicators` 显示 `market_cap`
- 但查询时报 `Unknown indicator: market_cap`
- 根因：`market_cap` 只在 registry.py 定义，factory.py 没有注册

## 解决方案

新增 `MarketCapIndicator` 类，从财务指标直接获取市值。

### 行为

| 市场 | 数据源字段 | 返回单位 |
|------|-----------|---------|
| 港股 | `hk_market_cap` 或 `港股市值(港元)` | 港元 |
| A股 | `a_market_cap` 或 `总市值(元)` | 人民币 |
| 美股 | `us_market_cap` 或 `总市值(美元)` | 美元 |

### 与 `latest_market_cap` 的区别

| 指标 | 数据来源 | 特点 |
|------|---------|------|
| `market_cap` | 财务指标 | 财报时的市值 |
| `latest_market_cap` | 股价 × 股本 | 实时计算，可能做汇率转换 |

## 实现位置

- 新文件：`src/value_investment/indicators/market_cap.py`
- 修改：`src/value_investment/indicators/factory.py`（注册新指标）

## 依赖

- `financial_indicator` - 从财务指标获取市值字段
- 无需价格数据

## 测试计划

1. 港股测试：`00700` (腾讯)
2. A股测试：`600519` (茅台)
3. 美股测试：`AAPL`

## 验收标准

- [ ] `cli indicator market_cap -s 00700 -m HK` 返回腾讯市值
- [ ] `cli indicator market_cap -s 600519 -m A` 返回茅台市值
- [ ] `cli indicator market_cap -s AAPL -m US` 返回苹果市值
- [ ] 单元测试通过
