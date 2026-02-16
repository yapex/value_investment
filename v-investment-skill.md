# Value Investment Skill

## Overview

This skill provides stock fundamental analysis capabilities for A股/港股/美股 markets using akshare data.

## Capabilities

- **Stock Info**: Query basic information for A股/港股/美股 stocks
- **Historical Data**: Get historical price data with forward/backward adjustment
- **Financial Data**: Retrieve merged balance sheet, income statement, cash flow
- **Indicators**: Calculate ROE, ROA, ROIC, Gross Margin, Net Profit Margin, Current Ratio, CAGR, DCF
- **Indicator Registry**: Unified metadata management for RAW/SIMPLE/COMPLEX indicators across markets
- **Analysis**: Complete fundamental analysis with recommendations

## Usage

### CLI

```bash
# Stock info
python -m value_investment info 600519

# Historical data
python -m value_investment hist 600519 --start 20200101 --end 20241231

# Financial data
python -m value_investment financial 600519 --start 2015 --end 2024

# Indicators
python -m value_investment indicator 600519 ROE

# Complete analysis
python -m value_investment analyze 600519

# List indicators
python -m value_investment list

# Cache management
python -m value_investment cache-clear 600519
python -m value_investment cache-stats
```

### Python API

```python
from value_investment import ValueInvestment

vi = ValueInvestment(market="A")

# Get stock info
info = vi.get_stock_info("600519")

# Historical data (default: hfq - backward adjusted)
hist = vi.get_historical_data("600519", "20200101", "20241231")

# Financial data (merged three statements)
financial = vi.get_financial_data("600519", 2015, 2024)

# Calculate indicator
result = vi.calculate_indicator("ROE", "600519", [2020, 2021, 2022, 2023, 2024])

# Get indicator metadata
indicator = vi.get_indicator("revenue")
print(indicator.display_name)  # 营业收入

# List indicators (supports market/type filtering)
all_indics = vi.list_indicators()
abc_indics = vi.list_indicators(market="A股")
raw_indics = vi.list_indicators(indicator_type="RAW")

# Complete analysis
analysis = vi.analyze("600519", years=5)

# Clear cache
vi.clear_cache("600519")
```

## Indicator Registry

The project uses an Indicator Registry to manage financial indicator metadata:

- **RAW**: Raw financial data from API (revenue, net_profit, etc.)
- **SIMPLE**: Simple calculated indicators (ROE, ROA, gross_margin, etc.)
- **COMPLEX**: Complex calculated indicators (DCF, CAGR, etc.)

### Market Support

| Market | Code Format | Example |
|--------|-------------|---------|
| A股 | 6-digit | 600519 |
| 港股 | 5-digit | 00700 |
| 美股 | Letter | AAPL |

## Indicators

| Indicator | Description | Type |
|-----------|-------------|------|
| ROE | Return on Equity | SIMPLE |
| ROA | Return on Assets | SIMPLE |
| ROIC | Return on Invested Capital | SIMPLE |
| gross_margin | Gross Margin | SIMPLE |
| net_profit_margin | Net Profit Margin | SIMPLE |
| current_ratio | Current Ratio | SIMPLE |
| CAGR | Compound Annual Growth Rate | COMPLEX |
| DCF | Discounted Cash Flow Valuation | COMPLEX |
| revenue | 营业收入 | RAW |
| net_profit | 净利润 | RAW |
| total_assets | 总资产 | RAW |

## Cache

- Stock info: expires at next midnight (1 day TTL)
- Historical data: 1 year TTL (default hfq)
- Financial data: expires June 30 next year

Cache supports range reuse: cached [2015-2024] can serve queries for [2020-2024].
