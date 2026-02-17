"""CLI for value investment analysis"""
import typer
from typing import Optional
import pandas as pd

from value_investment.api import ValueInvestment

app = typer.Typer(name="v-investment", help="Value investment analysis tool")


def _detect_market_from_code(code: str) -> str:
    """Detect market from stock code

    Args:
        code: Stock code

    Returns:
        Market code: "A", "HK", or "US"
    """
    if not code:
        return "A"

    code = code.strip()

    # A股: 6-digit codes starting with 0, 3, 6
    if code.isdigit() and len(code) == 6:
        if code[0] in ("0", "3", "6"):
            return "A"

    # 港股: 5-digit codes
    if code.isdigit() and len(code) == 5:
        return "HK"

    # 美股: alphabetic ticker symbols
    if code.isalpha():
        return "US"

    # Default to A股
    return "A"


def _get_market(market: Optional[str], symbol: str) -> str:
    """Get market, auto-detect from symbol if not specified"""
    if market:
        return market
    return _detect_market_from_code(symbol)


@app.command()
def info(
    symbol: str = typer.Argument(..., help="Stock code (e.g., 600519)"),
    market: Optional[str] = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Query stock basic information"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_stock_info(symbol)
    print(df.to_string())


@app.command()
def hist(
    symbol: str = typer.Argument(..., help="Stock code"),
    start: str = typer.Option("19700101", "--start", "-s", help="Start date (YYYYMMDD, optional, defaults to earliest)"),
    end: str = typer.Option("20241231", "--end", "-e", help="End date (YYYYMMDD)"),
    adjust: str = typer.Option("hfq", "--adjust", "-a", help="Adjustment: '', 'qfq', 'hfq' (default: hfq for backtesting)"),
    market: Optional[str] = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Get historical price data"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_historical_data(symbol, end, start, adjust)
    print(df.to_string())


@app.command()
def balance(
    symbol: str = typer.Argument(..., help="Stock code"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year"),
    market: Optional[str] = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Get balance sheet"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_balance_sheet(symbol, end_year)
    print(df.to_string())


@app.command()
def profit(
    symbol: str = typer.Argument(..., help="Stock code"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year"),
    market: Optional[str] = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Get profit sheet (income statement)"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_profit_sheet(symbol, end_year)
    print(df.to_string())


@app.command()
def cashflow(
    symbol: str = typer.Argument(..., help="Stock code"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year"),
    market: Optional[str] = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Get cash flow sheet"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_cashflow_sheet(symbol, end_year)
    print(df.to_string())


@app.command()
def indicator(
    name: str = typer.Argument(..., help="Indicator name"),
    stock_code: str = typer.Option(..., "--stock", "-s", help="Stock code"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years"),
    market: Optional[str] = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Calculate a specific indicator"""
    vi = ValueInvestment(market=_get_market(market, stock_code))
    try:
        result = vi.calculate_indicator(name, stock_code, years)
        print(f"{name}: {result.value} {result.unit}")
        print(f"Description: {result.description}")
        if result.values and len(result.values) > 0:
            # Show per-year values
            print("\nYear-by-Year:")
            for year, val in zip(result.years, result.values):
                print(f"  {year}: {val:.2f}{result.unit}")
        else:
            print(f"Years: {result.years}")
    except Exception as e:
        print(f"Error: {e}")


@app.command()
def analyze(
    stock_code: str = typer.Argument(..., help="Stock code"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years"),
    market: Optional[str] = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Perform complete analysis"""
    import pandas as pd

    vi = ValueInvestment(market=_get_market(market, stock_code))

    # Get stock info first
    try:
        info = vi.get_stock_info(stock_code)
        # Try to find stock name from info - prioritize 简称/名称 over 股票代码
        name = stock_code
        if 'item' in info.columns:
            # First try to find 股票简称 or 名称
            for _, row in info.iterrows():
                item = str(row['item'])
                if '简称' in item or '名称' in item:
                    name = f"{row['value']} ({stock_code})"
                    break
    except Exception as e:
        name = stock_code

    # Call analyze with additional CAGR metrics
    results = vi.analyze(stock_code, years, cagr_metrics=["revenue", "net_profit"])

    # Collect all years from results (filter out invalid years like 0, 1, 2)
    all_years = set()
    for name_result in results.values():
        if hasattr(name_result, 'years') and name_result.years:
            for y in name_result.years:
                if y > 100:  # Filter out invalid year numbers
                    all_years.add(y)

    if not all_years:
        print(f"=== {stock_code} 财务分析 ===")
        print("无财务数据")
        return

    sorted_years = sorted(all_years, reverse=True)
    year_range = f"{min(sorted_years)}-{max(sorted_years)}"

    # Chinese labels for indicators
    label_map = {
        "ROE": "ROE",
        "ROA": "ROA",
        "gross_margin": "毛利率",
        "net_profit_margin": "净利率",
        "current_ratio": "流动比率",
        "ROIC": "ROIC",
        "CAGR": "营收CAGR",
        "CAGR_revenue": "营收CAGR",
        "CAGR_net_profit": "净利润CAGR",
        "ImpliedGrowth": "市场隐含增长率",
        "asset_turnover": "资产周转率",
        "inventory_turnover": "存货周转率",
        "quick_ratio": "速动比率",
        "debt_ratio": "资产负债率",
        "receivable_turnover": "应收账款周转率",
        "payable_turnover": "应付账款周转率",
        "cfo_to_netprofit_sum": "盈利质量(CFO/净利)",
    }

    # Build DataFrame: rows = years, columns = indicators
    data = []
    for year in sorted_years:
        row = {"年份": year}
        for ind_name, result in results.items():
            label = label_map.get(ind_name, ind_name)
            if hasattr(result, 'values') and result.values and hasattr(result, 'years') and result.years:
                if year in result.years:
                    idx = result.years.index(year)
                    if idx < len(result.values):
                        value = result.values[idx]
                        import math
                        if math.isnan(value):
                            value = 0
                        if result.unit == "%":
                            row[label] = f"{value:.1f}%"
                        elif result.unit == "ratio":
                            row[label] = f"{value:.2f}"
                        elif result.unit == "CNY":
                            if abs(value) > 1e9:
                                row[label] = f"{value/1e9:.2f}十亿"
                            else:
                                row[label] = f"{value:.2f}"
                            continue
                        else:
                            row[label] = value
        data.append(row)

    df = pd.DataFrame(data)

    # Reorder columns: ROIC first, then by category
    column_order = [
        "年份",
        "ROIC", "ROE", "ROA", "毛利率", "净利率",
        "流动比率", "速动比率", "资产负债率",
        "资产周转率", "存货周转率", "应收账款周转率", "应付账款周转率",
    ]
    # Only include columns that exist
    existing_cols = [c for c in column_order if c in df.columns]
    df = df[existing_cols]

    # Output
    print(f"\n### {name} 财务分析 ({year_range})")
    print()
    if not df.empty:
        print(df.to_markdown(index=False))

    # Show summary metrics (CAGR, DCF) that don't have per-year values
    summary_metrics = []
    for ind_name, result in results.items():
        if hasattr(result, 'values') and not result.values and hasattr(result, 'value') and result.value:
            # Skip default CAGR (no suffix), only show specific ones like CAGR_revenue, CAGR_net_profit
            if ind_name == "CAGR":
                continue
            label = label_map.get(ind_name, ind_name)
            if result.unit == "%":
                summary_metrics.append((label, f"{result.value:.1f}%"))
            elif result.unit == "CNY":
                if abs(result.value) > 1e9:
                    summary_metrics.append((label, f"{result.value/1e9:.2f}十亿"))
                else:
                    summary_metrics.append((label, f"{result.value:.2f}"))
            else:
                summary_metrics.append((label, f"{result.value}"))

    if summary_metrics:
        print()
        for label, value in summary_metrics:
            print(f"- {label}: {value}")


@app.command("list")
@app.command("list-indicators")
def list_indicators():
    """List all available indicators"""
    vi = ValueInvestment()
    indicators = vi.list_indicators()
    for name in indicators:
        print(name)


@app.command()
def cache_clear(
    symbol: Optional[str] = typer.Argument(None, help="Specific stock code to clear"),
    market: Optional[str] = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Clear cache"""
    # Use symbol to detect market if not specified, default to A if no symbol
    detected_market = _get_market(market, symbol) if symbol else (market or "A")
    vi = ValueInvestment(market=detected_market)
    vi.clear_cache(symbol)
    if symbol:
        print(f"Cleared cache for {symbol}")
    else:
        print("Cleared all cache")


@app.command()
def cache_stats():
    """Show cache statistics."""
    vi = ValueInvestment()
    cache = vi._cache

    stats = {
        "memory_size": len(cache._memory_cache) if hasattr(cache, '_memory_cache') else 0,
    }

    # Check disk cache
    if hasattr(cache, '_disk_cache'):
        stats["disk_cache_size"] = len(cache._disk_cache)
    else:
        stats["disk_cache_size"] = 0

    print(f"Memory cache entries: {stats['memory_size']}")
    print(f"Disk cache entries: {stats['disk_cache_size']}")


@app.command()
def cache_list(symbol: Optional[str] = typer.Argument(None, help="Filter by stock code")):
    """List cached items."""
    vi = ValueInvestment()
    cache = vi._cache

    keys = []
    if hasattr(cache, '_disk_cache'):
        keys = list(cache._disk_cache.keys())
    elif hasattr(cache, '_memory_cache'):
        keys = list(cache._memory_cache.keys())

    if symbol:
        keys = [k for k in keys if symbol in k]

    for key in keys[:20]:
        print(key)


@app.command()
def version():
    """Show version"""
    print("v-investment 0.1.0")


if __name__ == "__main__":
    app()
