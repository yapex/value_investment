"""CLI for value investment analysis

New design using PipelineAPI for unified data access.
"""
import asyncio
import json
from typing import Any

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from value_investment.api import ValueInvestment
from value_investment.data.cache import SmartCache
from value_investment.data.mapper import DataMapper
from value_investment.pipeline.api import PipelineAPI
from value_investment.pipeline.fields import ALL_FIELDS
from value_investment.scanner import Scanner, parse_filter

app = typer.Typer(name="v-invest", help="Value investment analysis tool")
console = Console()


def _get_market(market: str | None, symbol: str) -> str:
    """Get market, auto-detect from symbol if not specified"""
    if market:
        return market
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
    """Format pipeline data for display

    Args:
        data: {field: {year: value}} format from PipelineAPI
        fmt: Output format - markdown, json, plain

    Returns:
        Formatted string
    """
    if fmt == "json":
        # Convert year keys to strings for JSON serialization
        serializable = {k: {str(yr): v for yr, v in years.items()} for k, years in data.items()}
        return json.dumps(serializable, indent=2, ensure_ascii=False)

    # Convert to DataFrame for markdown/plain
    if not data:
        return "No data"

    # Find all years
    all_years = set()
    for years in data.values():
        all_years.update(years.keys())
    all_years = sorted(all_years, reverse=True)

    # Build rows
    rows = []
    for field, years in sorted(data.items()):
        row = {"field": field}
        for year in all_years:
            row[str(year)] = years.get(year, "N/A")
        rows.append(row)

    df = pd.DataFrame(rows)

    if fmt == "plain":
        # Simple text format
        lines = []
        header = "field\t" + "\t".join(str(y) for y in all_years)
        lines.append(header)
        for _, row in df.iterrows():
            line = row["field"] + "\t" + "\t".join(str(row.get(str(y), "")) for y in all_years)
            lines.append(line)
        return "\n".join(lines)

    # markdown (default)
    md_output = df.to_markdown(index=False)
    return md_output if md_output is not None else ""


@app.command()
def query(
    symbol: str = typer.Argument(..., help="Stock code (e.g., 600519, 00700, AAPL)"),
    requires: str = typer.Option(
        ...,
        "--requires",
        "-r",
        help="Comma-separated field names to fetch (e.g., roe,net_profit)",
    ),
    end: str = typer.Option("20241231", "--end", "-e", help="End date (YYYYMMDD)"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years to fetch"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown, json, plain"),
):
    """Query financial data using PipelineAPI

    Examples:
        v-invest query 600519 -r roe,net_profit
        v-invest query 00700 -r roe --years 5
        v-invest query AAPL -r roe,pe_ratio -f json
    """
    # Parse fields
    fields = [f.strip() for f in requires.split(",") if f.strip()]
    if not fields:
        typer.echo("Error: --requires/-r must specify at least one field", err=True)
        raise typer.Exit(code=1)

    # Detect market
    detected_market = _get_market(market, symbol)

    # Run async query
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

    # Format and output
    output = _format_output(result, format)
    typer.echo(output)


@app.command()
def validate(
    symbol: str = typer.Argument(..., help="Stock code (e.g., 600519, 00700, AAPL)"),
    requires: str = typer.Option(
        ...,
        "--requires",
        "-r",
        help="Comma-separated field names to validate (e.g., roe,net_profit)",
    ),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Validate pipeline configuration without fetching actual data (dry run)

    This command checks:
    - All requested fields are registered
    - Calculator dependencies can be satisfied
    - Which Handlers will process the request

    Examples:
        v-invest validate 600519 -r roe,net_profit
        v-invest validate 00700 -r implied_growth
        v-invest validate AAPL -r roe,pe_ratio
    """
    # Parse fields
    fields = [f.strip() for f in requires.split(",") if f.strip()]
    if not fields:
        typer.echo("Error: --requires/-r must specify at least one field", err=True)
        raise typer.Exit(code=1)

    # Detect market
    detected_market = _get_market(market, symbol)

    # Validate
    api = PipelineAPI()
    report = api.validate(symbol, fields, detected_market)

    # Output report
    typer.echo(report.summary())

    # Exit with error code if issues found
    if not report.is_valid:
        raise typer.Exit(code=1)


@app.command()
def info(
    symbol: str = typer.Argument(..., help="Stock code (e.g., 600519)"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown, json, plain"),
):
    """Query stock basic information"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_stock_info(symbol, force_refresh=refresh)

    if format == "json":
        typer.echo(df.to_json(orient="records", indent=2, force_ascii=False))
    elif format == "plain":
        typer.echo(df.to_string(index=False))
    else:
        typer.echo(df.to_markdown(index=False))


@app.command()
def hist(
    symbol: str = typer.Argument(..., help="Stock code"),
    start: str = typer.Option("19700101", "--start", "-s", help="Start date (YYYYMMDD, optional, defaults to earliest)"),
    end: str = typer.Option("20241231", "--end", "-e", help="End date (YYYYMMDD)"),
    adjust: str = typer.Option("hfq", "--adjust", "-a", help="Adjustment: '', 'qfq', 'hfq' (default: hfq for backtesting)"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown, json, plain"),
):
    """Get historical price data"""
    vi = ValueInvestment(market=_get_market(market, symbol))
    df = vi.get_historical_data(symbol, end, start, adjust, force_refresh=refresh)

    if format == "json":
        typer.echo(df.to_json(orient="records", indent=2, force_ascii=False))
    elif format == "plain":
        typer.echo(df.to_string(index=False))
    else:
        typer.echo(df.to_markdown(index=False))


@app.command()
def balance(
    symbol: str = typer.Argument(..., help="Stock code"),
    end_year: int = typer.Option(2024, "--end", "-e", help="End year"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
    fields: str | None = typer.Option(None, "--fields", "-f", help="Comma-separated fields to return"),
    years: int = typer.Option(10, "--years", "-y", help="Number of years to fetch"),
):
    """Get balance sheet"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_balance_sheet(symbol, end_year, force_refresh=refresh, fields=field_list, years=years)
        typer.echo(df.to_markdown(index=False))
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
    years: int = typer.Option(10, "--years", "-y", help="Number of years to fetch"),
):
    """Get profit sheet (income statement)"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_profit_sheet(symbol, end_year, force_refresh=refresh, fields=field_list, years=years)
        typer.echo(df.to_markdown(index=False))
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
    years: int = typer.Option(10, "--years", "-y", help="Number of years to fetch"),
):
    """Get cash flow sheet"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_cashflow_sheet(symbol, end_year, force_refresh=refresh, fields=field_list, years=years)
        typer.echo(df.to_markdown(index=False))
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
    """Get indicator values (unified interface for RAW and CALCULATED)

    When years > 1, returns historical data as a DataFrame.
    """
    vi = ValueInvestment(market=_get_market(market, stock_code))

    # Parse indicator names
    if names:
        indicator_names = [n.strip() for n in names.split(",")]
    else:
        indicator_names = []

    # Handle multiple years: use calculate_indicator to get historical data
    if years > 1 and indicator_names:
        # Get historical data for each indicator
        dfs = []
        current_values = {}  # For indicators without historical data (e.g., ImpliedGrowth)

        for name in indicator_names:
            try:
                result = vi.calculate_indicator(name, stock_code, years)
                if result and result.years and result.values:
                    df = pd.DataFrame({
                        'year': result.years,
                        name: result.values
                    })
                    dfs.append(df)
                elif result and result.value is not None:
                    # Indicator has current value but no historical data
                    current_values[name] = result
            except Exception as e:
                print(f"Warning: Failed to get {name}: {e}")

        if dfs:
            # Merge all indicators into one DataFrame
            merged = dfs[0]
            for df in dfs[1:]:
                merged = merged.merge(df, on='year', how='outer')
            merged = merged.sort_values(by='year', ascending=False)

            print(f"### 指标历史数据 - {stock_code} (最近{years}年)\n")
            print(merged.to_markdown(index=False))

        # Output current-value-only indicators (like ImpliedGrowth)
        if current_values:
            print(f"\n### 当前值指标 - {stock_code}\n")
            items = []
            for name, result in current_values.items():
                items.append({"指标": name, "值": f"{result.value}{result.unit}", "说明": result.description})
            print(pd.DataFrame(items).to_markdown(index=False))

        if dfs or current_values:
            return

    # Original logic for single year or all indicators
    if len(indicator_names) == 1:
        indicator_names = indicator_names[0]
    else:
        indicator_names = None if not indicator_names else indicator_names

    # Get indicator values
    result = vi.indicator(indicator_names, stock_code, years)

    # Format output as Markdown
    if isinstance(result, pd.DataFrame):
        print(f"### 指标数据 - {stock_code}\n")
        print(result.T.to_markdown(headers="keys"))
    elif isinstance(result, dict):
        print(f"### 指标 - {stock_code}\n")
        items = [{"指标": k, "值": v if v is not None else "N/A"} for k, v in result.items()]
        print(pd.DataFrame(items).to_markdown(index=False))


@app.command()
def finind(
    stock_code: str = typer.Argument(..., help="Stock code"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh from data source"),
):
    """Get financial indicators directly from data source (no calculation needed)"""
    vi = ValueInvestment(market=_get_market(market, stock_code))

    df = vi.get_financial_indicator(stock_code, force_refresh=refresh)

    if df is None or df.empty:
        print(f"### 财务指标 - {stock_code}\n\n无数据")
        return

    # Take first row and convert to DataFrame for display
    row = df.iloc[0].dropna()
    items = [{"指标": idx, "值": val} for idx, val in row.items()]

    print(f"### 财务指标 - {stock_code}\n")
    print(pd.DataFrame(items).to_markdown(index=False))


@app.command("indicators")
def list_indicators(
    market: str = typer.Argument(..., help="Market: A, HK, US"),
):
    """List all available indicators for a specific market"""
    # 转换市场代码为中文名称（与项目统一格式）
    market_map = {"A": "A股", "HK": "港股", "US": "美股"}
    market_name = market_map.get(market.upper(), market)

    vi = ValueInvestment()
    indicators = vi.list_indicators(market=market_name)
    for name in indicators:
        print(name)


@app.command()
def fields(
    prefix: str | None = typer.Option(None, "--prefix", "-p", help="Filter fields by prefix (e.g., 'ro', 'total')"),
):
    """List all available standard fields

    Examples:
        v-invest fields
        v-invest fields --prefix ro
    """
    all_fields = sorted(ALL_FIELDS)

    if prefix:
        all_fields = [f for f in all_fields if f.startswith(prefix)]

    for field in all_fields:
        print(field)


# Agent 友好的字段信息字典
FIELD_INFO = {
    # === 盈利能力 ===
    "roe": {
        "name": "净资产收益率",
        "formula": "净利润 / 平均净资产 × 100%",
        "unit": "%",
        "usage": "评估股东权益回报，>15% 为优质，>20% 为优秀",
        "category": "盈利能力",
    },
    "roa": {
        "name": "资产回报率",
        "formula": "净利润 / 平均总资产 × 100%",
        "unit": "%",
        "usage": "评估资产赚钱效率，>5% 为良好",
        "category": "盈利能力",
    },
    "roic": {
        "name": "投资资本回报率",
        "formula": "税后净营业利润 / 投资资本 × 100%",
        "unit": "%",
        "usage": "评估资本配置效率，>WACC(通常10%) 为创造价值，>15% 为优秀",
        "category": "盈利能力",
    },
    "gross_margin": {
        "name": "毛利率",
        "formula": "(营业收入 - 营业成本) / 营业收入 × 100%",
        "unit": "%",
        "usage": "评估产品定价能力和成本控制，消费>50%、制造20-40%",
        "category": "盈利能力",
    },
    "net_profit_margin": {
        "name": "净利率",
        "formula": "净利润 / 营业收入 × 100%",
        "unit": "%",
        "usage": "评估最终盈利能力，>10% 为良好",
        "category": "盈利能力",
    },
    "operating_profit_margin": {
        "name": "营业利润率",
        "formula": "营业利润 / 营业收入 × 100%",
        "unit": "%",
        "usage": "评估主营业务盈利，剔除非经常性损益",
        "category": "盈利能力",
    },
    # === 估值指标 ===
    "pe_ratio": {
        "name": "市盈率",
        "formula": "股价 / 每股收益 (PE TTM)",
        "unit": "倍",
        "usage": "评估股价贵贱，<20 为合理，>30 偏高，需结合行业",
        "category": "估值指标",
    },
    "pb_ratio": {
        "name": "市净率",
        "formula": "股价 / 每股净资产",
        "unit": "倍",
        "usage": "评估股价与净资产关系，<3 为合理，银行/保险需特殊解读",
        "category": "估值指标",
    },
    "market_cap": {
        "name": "总市值",
        "formula": "股价 × 总股本",
        "unit": "元",
        "usage": "评估公司规模，用于市值分组对比",
        "category": "估值指标",
    },
    # === 财务健康 ===
    "debt_ratio": {
        "name": "资产负债率",
        "formula": "总负债 / 总资产 × 100%",
        "unit": "%",
        "usage": "评估财务杠杆，<50% 为稳健，>70% 风险较高",
        "category": "财务健康",
    },
    "current_ratio": {
        "name": "流动比率",
        "formula": "流动资产 / 流动负债",
        "unit": "倍",
        "usage": "评估短期偿债能力，>1.5 为良好",
        "category": "财务健康",
    },
    # === 成长性 ===
    "implied_growth": {
        "name": "隐含增长率",
        "formula": "基于DCF模型反推的市场预期增长率",
        "unit": "%",
        "usage": "评估市场对公司的成长预期，与历史增速对比判断高低估",
        "category": "成长性",
        "requires": ["operating_cash_flow", "market_cap"],
    },
    # === 市场特有 ===
    "circ_market_cap": {
        "name": "流通市值",
        "formula": "股价 × 流通股本",
        "unit": "元",
        "usage": "A 股特有，反映实际可交易股票价值",
        "category": "市场特有(A股)",
    },
}


@app.command()
def field_info(
    field: str = typer.Argument(..., help="Field name (e.g., roe, pe_ratio, roic)"),
):
    """Show detailed information about a field for Agent usage
    
    Examples:
        v-invest query roe
        v-invest query implied_growth
        v-invest query gross_margin
    """
    if field not in FIELD_INFO:
        typer.echo(f"Error: Unknown field '{field}'", err=True)
        typer.echo(f"Use 'v-investment fields' to see all available fields")
        raise typer.Exit(code=1)
    
    info = FIELD_INFO[field]
    
    typer.echo(f"""
╔══════════════════════════════════════════════════════════════════════╗
║ {info['name']:^62} ║
╠══════════════════════════════════════════════════════════════════════╣
║ 字段名: {field:<57} ║
║ 类别:   {info['category']:<57} ║
║ 公式:   {info['formula']:<57} ║
║ 单位:   {info['unit']:<57} ║
╠══════════════════════════════════════════════════════════════════════╣
║ 使用建议:                                                              ║
║ {info['usage']:<62} ║""")
    
    if "requires" in info:
        typer.echo(f"╠══════════════════════════════════════════════════════════════════════╣")
        typer.echo(f"║ 依赖字段: {', '.join(info['requires']):<51} ║")
    
    typer.echo(f"╚══════════════════════════════════════════════════════════════════════╝")
    
    # 推荐组合
    category_fields = {
        "盈利能力": ["roe", "roa", "roic", "gross_margin", "net_profit_margin"],
        "估值指标": ["pe_ratio", "pb_ratio", "market_cap"],
        "财务健康": ["debt_ratio", "current_ratio"],
        "成长性": ["implied_growth"],
    }
    
    if info["category"] in category_fields:
        related = [f for f in category_fields[info["category"]] if f != field]
        if related:
            typer.echo(f"""
推荐组合 (同一类别):
  v-invest query <symbol> -r {field},{related[0]}
  
其他可用字段:
  {' '.join(related)}""")


@app.command()
def cache_clear(
    symbol: str | None = typer.Argument(None, help="Specific stock code to clear"),
    market: str | None = typer.Option(None, "--market", "-m", help="Market: A, HK, US (auto-detect if omitted)"),
):
    """Clear cache"""
    cache = SmartCache()

    if symbol:
        # Clear specific stock cache - need to find all keys with this symbol
        keys = cache.list_keys()
        cleared = 0
        for key in keys:
            if symbol in key:
                cache.invalidate(key)
                cleared += 1
        print(f"Cleared {cleared} cache entries for {symbol}")
    else:
        # Clear all cache
        keys = cache.list_keys()
        for key in keys:
            cache.invalidate(key)
        print(f"Cleared {len(keys)} cache entries")


@app.command()
def cache_stats():
    """Show cache statistics."""
    cache = SmartCache()
    keys = cache.list_keys()

    # Categorize keys
    memory_keys = [k for k in keys if "memory" in k.lower() or "temp" in k.lower()]
    disk_keys = [k for k in keys if k not in memory_keys]

    print(f"Memory cache entries: {len(memory_keys)}")
    print(f"Disk cache entries: {len(disk_keys)}")
    print(f"Total cache entries: {len(keys)}")


@app.command()
def cache_list(
    symbol: str | None = typer.Argument(None, help="Filter by stock code"),
):
    """List cached items."""
    cache = SmartCache()
    keys = cache.list_keys()

    if symbol:
        keys = [k for k in keys if symbol in k]

    for key in keys:
        print(key)

    if not keys:
        print("(no cached items)")


@app.command()
def scan(
    filter_text: str = typer.Option(..., "--filter", "-f", help="Filter condition in text format, e.g., 'ROE 连续5年 ≥15%'"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK"),
    fields: str = typer.Option("roe", "--fields", help="Comma-separated fields to fetch (default: roe)"),
    years: int = typer.Option(5, "--years", "-y", help="Number of years to fetch (default: 5)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Limit number of stocks to scan (default: 100, 0 for all)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path (optional)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable cache, always re-scan"),
):
    """Scan stocks with filter conditions in text format

    Examples:
        v-investment scan --filter "ROE 连续5年 ≥15%"
        v-investment scan --filter "ROE 连续5年 ≥15% 且 毛利率 连续5年 ≥30%" -m A
        v-investment scan --filter "ROE 5年至少4年 ≥15%, 平均≥15%" --fields roe,gross_profit_margin
    """
    try:
        # 解析字段列表
        field_list = [f.strip() for f in fields.split(",")]

        # 初始化 Scanner
        scanner = Scanner(market=market)

        # 检查缓存
        if not no_cache:
            cached_result = scanner.get_cached_scan_result(filter_text, field_list, years)
            if cached_result is not None and not cached_result.empty:
                # 限制数量
                if limit > 0:
                    unique_stocks = list(cached_result['stock_code'].unique()[:limit])
                    result = cached_result[cached_result['stock_code'].isin(unique_stocks)]
                else:
                    result = cached_result

                qualified_stocks = list(result["stock_code"].unique())  # type: ignore[union-attr]
                print(f"✓ 从缓存读取，符合条件: {len(qualified_stocks)} 只股票")

                if output:
                    result.to_csv(output, index=False, encoding='utf-8-sig')
                    print(f"结果已保存到: {output}")
                else:
                    latest = result.sort_values(by='end_date', ascending=False)  # type: ignore[call-overload]
                    latest = latest.drop_duplicates('stock_code')
                    print(latest.to_markdown(index=False))
                return

        # 解析过滤条件
        fb = parse_filter(filter_text)

        # 获取股票列表
        print(f"正在获取 {market} 股市场股票列表...")
        stocks = scanner.get_stock_list()

        if stocks.empty:
            print("未获取到股票列表")
            return

        # 限制扫描数量
        if limit > 0:
            stocks = stocks.head(limit)
            print(f"限制扫描前 {limit} 只股票")

        # 获取财务数据
        print(f"正在获取财务数据: {field_list}...")
        stock_codes = stocks['symbol'].tolist()
        financial_data = scanner.get_financial_data(stock_codes, field_list, years=years)

        if financial_data.empty:
            print("未获取到财务数据")
            return

        print(f"获取到 {len(financial_data['stock_code'].unique())} 只股票的财务数据")

        # 应用过滤条件
        print(f"正在应用过滤条件: {filter_text}")
        result = fb.execute(financial_data)

        if result.empty:
            print("没有符合条件的股票")
            return

        # 缓存结果
        if not no_cache:
            scanner.cache_scan_result(filter_text, field_list, years, result)
            print("✓ 结果已缓存")

        # 获取符合条件的股票列表
        qualified_stocks = result['stock_code'].unique()
        print(f"符合条件: {len(qualified_stocks)} 只股票")

        # 输出结果
        if output:
            result.to_csv(output, index=False, encoding='utf-8-sig')
            print(f"结果已保存到: {output}")
        else:
            # 显示符合条件的股票（取最新的数据）
            latest = result.sort_values(by='end_date', ascending=False).drop_duplicates('stock_code')
            print(latest.to_markdown(index=False))

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def scan_list(
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK (default: A)"),
):
    """List cached scan results

    Examples:
        v-investment scan-list
        v-investment scan-list -m HK
    """
    scanner = Scanner(market=market)
    cached_keys = scanner.list_cached_scan_results()

    if not cached_keys:
        print(f"No cached scan results for {market} market")
        return

    print(f"Cached scan results for {market} market:")
    for key in cached_keys:
        # 解析缓存键以便阅读
        # 格式: scan_result_{filter_hash}_{fields_str}_{years}_{market}
        parts = key.split("_")
        if len(parts) >= 6:
            filter_hash = parts[2]
            fields_str = parts[3]
            years = parts[4]
            print(f"  - {filter_hash} | fields: {fields_str} | years: {years}")


@app.command()
def version():
    """Show version"""
    print("v-investment 0.1.0")


if __name__ == "__main__":
    app()
