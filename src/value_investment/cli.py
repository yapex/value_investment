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
    start: str = typer.Option("20200101", "--start", "-s", help="Start date (YYYYMMDD)"),
    end: str = typer.Option("20241231", "--end", "-e", help="End date (YYYYMMDD)"),
    adjust: str = typer.Option("hfq", "--adjust", "-a", help="Adjustment: '', 'qfq', 'hfq' (default: hfq for backtesting)"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK, US"),
):
    """Get historical price data"""
    vi = ValueInvestment(market=market)
    df = vi.get_historical_data(symbol, start, end, adjust)
    print(df.to_string())


@app.command()
def financial(
    symbol: str = typer.Argument(..., help="Stock code"),
    start_year: int = typer.Option(2015, "--start", "-s", help="Start year"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK, US"),
):
    """Get financial data (merged statements)"""
    vi = ValueInvestment(market=market)
    df = vi.get_financial_data(symbol, start_year, end_year)
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


@app.command()
def list():
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
def version():
    """Show version"""
    print("v-investment 0.1.0")


if __name__ == "__main__":
    app()
