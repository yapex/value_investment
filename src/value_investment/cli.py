"""CLI for value investment analysis"""
import typer
from typing import Optional
import pandas as pd

from value_investment.api import ValueInvestment

app = typer.Typer(name="v-investment", help="Value investment analysis tool")


@app.command()
def info(
    symbol: str = typer.Argument(..., help="Stock code (e.g., 600519)"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK, US"),
):
    """Query stock basic information"""
    vi = ValueInvestment(market=market)
    df = vi.get_stock_info(symbol)
    print(df.to_string())


@app.command()
def hist(
    symbol: str = typer.Argument(..., help="Stock code"),
    start: str = typer.Option("19700101", "--start", "-s", help="Start date (YYYYMMDD, optional, defaults to earliest)"),
    end: str = typer.Option("20241231", "--end", "-e", help="End date (YYYYMMDD)"),
    adjust: str = typer.Option("hfq", "--adjust", "-a", help="Adjustment: '', 'qfq', 'hfq' (default: hfq for backtesting)"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK, US"),
):
    """Get historical price data"""
    vi = ValueInvestment(market=market)
    df = vi.get_historical_data(symbol, end, start, adjust)
    print(df.to_string())


@app.command()
def financial(
    symbol: str = typer.Argument(..., help="Stock code"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year (required)"),
    start_year: int = typer.Option(None, "--start", "-s", help="Start year (optional, defaults to earliest)"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK, US"),
):
    """Get financial data (merged statements)"""
    vi = ValueInvestment(market=market)
    df = vi.get_financial_data(symbol, end_year, start_year)
    print(df.to_string())


@app.command()
def indicator(
    name: str = typer.Argument(..., help="Indicator name"),
    stock_code: str = typer.Option(..., "--stock", "-s", help="Stock code"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK, US"),
):
    """Calculate a specific indicator"""
    vi = ValueInvestment(market=market)
    try:
        result = vi.calculate_indicator(name, stock_code, years)
        print(f"{name}: {result.value} {result.unit}")
        print(f"Description: {result.description}")
        print(f"Years: {result.years}")
    except Exception as e:
        print(f"Error: {e}")


@app.command()
def analyze(
    stock_code: str = typer.Argument(..., help="Stock code"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK, US"),
):
    """Perform complete analysis"""
    vi = ValueInvestment(market=market)
    results = vi.analyze(stock_code, years)
    for name, result in results.items():
        if hasattr(result, "value"):
            print(f"{name}: {result.value}")
        else:
            print(f"{name}: {result}")


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
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK, US"),
):
    """Clear cache"""
    vi = ValueInvestment(market=market)
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
