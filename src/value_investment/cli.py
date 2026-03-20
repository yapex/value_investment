"""CLI for value investment analysis using PipelineAPI"""
import asyncio
import json
from typing import Any

import pandas as pd
import typer
from rich.console import Console

from value_investment.core.cache import SmartCache
from value_investment.pipeline.api import PipelineAPI
from value_investment.domain.fields import ALL_FIELDS
from value_investment.calculator_plugin import (
    registry,
    load_calculator,
    load_calculators_from_dir,
    CalculatorValidationError,
)

app = typer.Typer(name="v-invest", help="Value investment analysis tool")
console = Console()


def _get_market(market: str | None, symbol: str) -> str:
    """Get market, auto-detect from symbol if not specified"""
    if market:
        # Normalize market name to full form
        market_map = {
            "A": "A股",
            "HK": "港股",
            "US": "美股",
            "A股": "A股",
            "港股": "港股",
            "美股": "美股",
        }
        return market_map.get(market, market)
    # Auto-detect market
    if len(symbol) == 5 and symbol.isdigit():
        return "港股"
    elif len(symbol) == 6 and symbol.isdigit() and symbol.startswith(("0", "3", "6")):
        return "A股"
    else:
        return "美股"


def _format_output(
    data: dict[str, dict[int, Any]],
    fmt: str = "markdown",
) -> str:
    """Format pipeline data for display"""
    if fmt == "json":
        serializable = {k: {str(yr): v for yr, v in years.items()} for k, years in data.items()}
        return json.dumps(serializable, indent=2, ensure_ascii=False)

    if not data:
        return "No data"

    all_years = set()
    for years in data.values():
        all_years.update(years.keys())
    all_years = sorted(all_years, reverse=True)

    rows = []
    for field, years in sorted(data.items()):
        row = {"field": field}
        for year in all_years:
            row[str(year)] = years.get(year, "N/A")
        rows.append(row)

    df = pd.DataFrame(rows)

    if fmt == "plain":
        lines = []
        header = "field\t" + "\t".join(str(y) for y in all_years)
        lines.append(header)
        for _, row in df.iterrows():
            line = row["field"] + "\t" + "\t".join(str(row.get(str(y), "")) for y in all_years)
            lines.append(line)
        return "\n".join(lines)

    md_output = df.to_markdown(index=False)
    return md_output if md_output is not None else ""


@app.command()
def query(
    symbol: str = typer.Argument(..., help="Stock code (e.g., 600519, 00700, AAPL)"),
    requires: str = typer.Option(
        ...,
        "--requires",
        "-r",
        help="Comma-separated field names (e.g., roe,net_profit)",
    ),
    end: str = typer.Option("2024", "--end", "-e", help="End year"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown, json, plain"),
    calculator: list[str] = typer.Option(
        None,
        "--calculator",
        "-c",
        help="Dynamic calculator script path (can be repeated)",
    ),
    calculator_dir: list[str] = typer.Option(
        None,
        "--calculator-dir",
        "-d",
        help="Dynamic calculator directory path (can be repeated)",
    ),
):
    """Query financial data using PipelineAPI"""
    fields = [f.strip() for f in requires.split(",") if f.strip()]
    if not fields:
        typer.echo("Error: --requires/-r must specify at least one field", err=True)
        raise typer.Exit(code=1)

    # Load dynamic calculators
    if calculator:
        for path in calculator:
            try:
                calc_dict = load_calculator(path)
                registry.register_from_dict(calc_dict)
                console.print(f"[green]✓[/green] Loaded calculator: {calc_dict['name']}")
            except CalculatorValidationError as e:
                console.print(f"[red]✗[/red] Failed to load {path}: {e}")

    if calculator_dir:
        for dir_path in calculator_dir:
            try:
                calculators = load_calculators_from_dir(dir_path)
                for calc_dict in calculators:
                    registry.register_from_dict(calc_dict)
                    console.print(f"[green]✓[/green] Loaded calculator: {calc_dict['name']}")
            except Exception as e:
                console.print(f"[red]✗[/red] Failed to load directory {dir_path}: {e}")

    detected_market = _get_market(market, symbol)
    api = PipelineAPI()

    try:
        result = asyncio.run(api.get_data(
            symbol=symbol,
            fields=fields,
            end=end,
            years=years,
            market=detected_market,
        ))
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    output = _format_output(result, format)
    typer.echo(output)


@app.command()
def validate(
    symbol: str = typer.Argument(..., help="Stock code"),
    requires: str = typer.Option(
        ...,
        "--requires",
        "-r",
        help="Comma-separated field names",
    ),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US"),
    calculator: list[str] = typer.Option(
        None,
        "--calculator",
        "-c",
        help="Dynamic calculator script path (can be repeated)",
    ),
    calculator_dir: list[str] = typer.Option(
        None,
        "--calculator-dir",
        "-d",
        help="Dynamic calculator directory path (can be repeated)",
    ),
):
    """Validate pipeline configuration (dry run)"""
    fields = [f.strip() for f in requires.split(",") if f.strip()]
    if not fields:
        typer.echo("Error: --requires/-r must specify at least one field", err=True)
        raise typer.Exit(code=1)

    # Load dynamic calculators
    if calculator:
        for path in calculator:
            try:
                calc_dict = load_calculator(path)
                registry.register_from_dict(calc_dict)
                console.print(f"[green]✓[/green] Loaded calculator: {calc_dict['name']}")
            except CalculatorValidationError as e:
                console.print(f"[red]✗[/red] Failed to load {path}: {e}")

    if calculator_dir:
        for dir_path in calculator_dir:
            try:
                calculators = load_calculators_from_dir(dir_path)
                for calc_dict in calculators:
                    registry.register_from_dict(calc_dict)
                    console.print(f"[green]✓[/green] Loaded calculator: {calc_dict['name']}")
            except Exception as e:
                console.print(f"[red]✗[/red] Failed to load directory {dir_path}: {e}")

    detected_market = _get_market(market, symbol)
    api = PipelineAPI()
    report = api.validate(symbol, fields, detected_market)
    typer.echo(report.summary())

    if not report.is_valid:
        raise typer.Exit(code=1)


@app.command()
def fields(
    prefix: str | None = typer.Option(None, "--prefix", "-p", help="Filter by prefix"),
):
    """List all available standard fields"""
    all_fields = sorted(ALL_FIELDS)
    if prefix:
        all_fields = [f for f in all_fields if f.startswith(prefix)]
    for field in all_fields:
        print(field)


@app.command()
def cache_clear(
    symbol: str | None = typer.Argument(None, help="Specific stock code to clear"),
):
    """Clear cache"""
    cache = SmartCache()
    keys = cache.list_keys()

    if symbol:
        cleared = 0
        for key in keys:
            if symbol in key:
                cache.invalidate(key)
                cleared += 1
        print(f"Cleared {cleared} cache entries for {symbol}")
    else:
        for key in keys:
            cache.invalidate(key)
        print(f"Cleared {len(keys)} cache entries")


@app.command()
def version():
    """Show version"""
    print("v-investment 0.1.0")


if __name__ == "__main__":
    app()
