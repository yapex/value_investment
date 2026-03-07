"""CLI for value investment analysis"""

import pandas as pd
import typer

from value_investment.api import ValueInvestment
from value_investment.data.mapper import DataMapper

app = typer.Typer(name="v-investment", help="Value investment analysis tool")


def _get_market(market: str | None, symbol: str) -> str:
    """Get market, auto-detect from symbol if not specified"""
    if market:
        return market
    return ValueInvestment.detect_market(symbol)


@app.command()
def info(
    symbol: str = typer.Argument(..., help="Stock code (e.g., 600519)"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
):
    """Query stock basic information"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_stock_info(symbol, force_refresh=refresh)
    print(df.to_markdown(index=False))


@app.command()
def hist(
    symbol: str = typer.Argument(..., help="Stock code"),
    start: str = typer.Option("19700101", "--start", "-s", help="Start date (YYYYMMDD, optional, defaults to earliest)"),
    end: str = typer.Option("20241231", "--end", "-e", help="End date (YYYYMMDD)"),
    adjust: str = typer.Option("hfq", "--adjust", "-a", help="Adjustment: '', 'qfq', 'hfq' (default: hfq for backtesting)"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
):
    """Get historical price data"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_historical_data(symbol, end, start, adjust, force_refresh=refresh)
    print(df.to_markdown(index=False))


@app.command()
def balance(
    symbol: str = typer.Argument(..., help="Stock code"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
    fields: str | None = typer.Option(None, "--fields", "-f", help="Comma-separated fields to return"),
):
    """Get balance sheet"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_balance_sheet(symbol, end_year, force_refresh=refresh, fields=field_list)
        print(df.to_markdown(index=False))
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def income(
    symbol: str = typer.Argument(..., help="Stock code"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
    fields: str | None = typer.Option(None, "--fields", "-f", help="Comma-separated fields to return"),
):
    """Get profit sheet (income statement)"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_profit_sheet(symbol, end_year, force_refresh=refresh, fields=field_list)
        print(df.to_markdown(index=False))
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def cashflow(
    symbol: str = typer.Argument(..., help="Stock code"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
    fields: str | None = typer.Option(None, "--fields", "-f", help="Comma-separated fields to return"),
):
    """Get cash flow sheet"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_cashflow_sheet(symbol, end_year, force_refresh=refresh, fields=field_list)
        print(df.to_markdown(index=False))
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def indicator(
    names: str = typer.Argument(None, help="Indicator name(s), comma-separated (e.g., 'roe,roa'). Leave empty for all."),
    stock_code: str = typer.Option(..., "--stock", "-s", help="Stock code"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Get indicator values (unified interface for RAW and CALCULATED)"""
    vi = ValueInvestment(market=_get_market(market, stock_code))
    try:
        import warnings
        import pandas as pd
        
        # Parse indicator names
        if names:
            indicator_names = [n.strip() for n in names.split(",")]
            if len(indicator_names) == 1:
                indicator_names = indicator_names[0]
        else:
            indicator_names = None
        
        # Get indicator values using unified interface
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = vi.indicator(indicator_names, stock_code, years)
            
            # Show warning if getting all indicators
            if w:
                for warning in w:
                    print(f"⚠️  Warning: {warning.message}")
        
        # Handle different result types
        if isinstance(result, pd.DataFrame):
            # All indicators - show as table
            print(f"=== All Indicators for {stock_code} ===")
            print(result.T.to_markdown(headers="keys"))
        elif isinstance(result, dict):
            # Single or multiple indicators
            print(f"=== Indicators for {stock_code} ===")
            for name, value in result.items():
                if value is not None:
                    # Try to get unit from metadata
                    try:
                        from value_investment.indicators.registry import IndicatorRegistry
                        registry = IndicatorRegistry.get_instance()
                        meta = registry.get(name)
                        unit = getattr(meta, 'unit', '') if meta else ''
                        print(f"{name}: {value} {unit}".strip())
                    except:
                        print(f"{name}: {value}")
                else:
                    print(f"{name}: N/A")
        else:
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


@app.command()
def finind(
    stock_code: str = typer.Argument(..., help="Stock code"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
):
    """Get financial indicators directly from data source (no calculation needed)"""
    vi = ValueInvestment(market=_get_market(market, stock_code))

    try:
        df = vi.get_financial_indicator(stock_code, force_refresh=refresh)
        if df is None or df.empty:
            print(f"No financial indicators found for {stock_code}")
            return

        # Print each indicator
        print(f"=== Financial Indicators for {stock_code} ===")
        for col in df.columns:
            val = df[col].iloc[0]
            if pd.notna(val):
                print(f"{col}: {val}")
    except Exception as e:
        print(f"Error: {e}")


@app.command()
def analyze(
    stock_code: str = typer.Argument(..., help="Stock code"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Perform complete analysis"""
    vi = ValueInvestment(market=_get_market(market, stock_code))
    result = vi.analyze(stock_code, years, cagr_metrics=["revenue", "net_profit"])

    # Handle empty results
    if result["table"].empty and not result["summary"]:
        print(f"=== {stock_code} 财务分析 ===")
        print("无财务数据")
        return

    # Output
    print(f"\n### {result['name']} 财务分析 ({result['year_range']})")
    print()
    if not result["table"].empty:
        print(result["table"].to_markdown(index=False))

    if result["summary"]:
        print()
        for item in result["summary"]:
            print(f"- {item['label']}: {item['value']}")


@app.command("indicators")
def list_indicators():
    """List all available indicators"""
    vi = ValueInvestment()
    indicators = vi.list_indicators()
    for name in indicators:
        print(name)


@app.command()
def fields(
    market: str = typer.Argument(..., help="Market: A, HK, US"),
    report: str = typer.Argument(..., help="Report type: balance, income, cashflow, finind, quarterly"),
):
    """List available standard fields for a market and report type"""
    try:
        fields_list = DataMapper.get_standard_fields(report, market)
        for field in fields_list:
            print(field)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def cache_clear(
    symbol: str | None = typer.Argument(None, help="Specific stock code to clear"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
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
    stats = vi.get_cache_stats()
    print(f"Memory cache entries: {stats['memory_size']}")
    print(f"Disk cache entries: {stats['disk_cache_size']}")


@app.command()
def cache_list(symbol: str | None = typer.Argument(None, help="Filter by stock code")):
    """List cached items."""
    vi = ValueInvestment()
    keys = vi.list_cache_keys(symbol=symbol)
    for key in keys:
        print(key)


@app.command()
def version():
    """Show version"""
    print("v-investment 0.1.0")


if __name__ == "__main__":
    app()
