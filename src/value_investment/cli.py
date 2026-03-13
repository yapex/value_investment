"""CLI for value investment analysis"""

import pandas as pd
import typer

from value_investment.api import ValueInvestment
from value_investment.data.mapper import DataMapper
from value_investment.scanner import Scanner, parse_filter

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
    years: int = typer.Option(10, "--years", "-y", help="Number of years to fetch"),
):
    """Get balance sheet"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_balance_sheet(symbol, end_year, force_refresh=refresh, fields=field_list, years=years)
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
    years: int = typer.Option(10, "--years", "-y", help="Number of years to fetch"),
):
    """Get profit sheet (income statement)"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_profit_sheet(symbol, end_year, force_refresh=refresh, fields=field_list, years=years)
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
    years: int = typer.Option(10, "--years", "-y", help="Number of years to fetch"),
):
    """Get cash flow sheet"""
    try:
        vi = ValueInvestment(market=_get_market(market, symbol))
        field_list = [f.strip() for f in fields.split(",")] if fields else None
        df = vi.get_cashflow_sheet(symbol, end_year, force_refresh=refresh, fields=field_list, years=years)
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
        for name in indicator_names:
            try:
                result = vi.calculate_indicator(name, stock_code, years)
                if result and result.years and result.values:
                    df = pd.DataFrame({
                        'year': result.years,
                        name: result.values
                    })
                    dfs.append(df)
            except Exception as e:
                print(f"Warning: Failed to get {name}: {e}")
        
        if dfs:
            # Merge all indicators into one DataFrame
            merged = dfs[0]
            for df in dfs[1:]:
                merged = merged.merge(df, on='year', how='outer')
            merged = merged.sort_values('year', ascending=False)
            
            print(f"### 指标历史数据 - {stock_code} (最近{years}年)\n")
            print(merged.to_markdown(index=False))
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
def scan(
    filter_text: str = typer.Option(..., "--filter", "-f", help="Filter condition in text format, e.g., 'ROE 连续5年 ≥15%'"),
    market: str = typer.Option("A", "--market", "-m", help="Market: A, HK"),
    fields: str = typer.Option("roe", "--fields", help="Comma-separated fields to fetch (default: roe)"),
    years: int = typer.Option(5, "--years", "-y", help="Number of years to fetch (default: 5)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Limit number of stocks to scan (default: 100, 0 for all)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path (optional)"),
):
    """Scan stocks with filter conditions in text format
    
    Examples:
        v-investment scan --filter "ROE 连续5年 ≥15%"
        v-investment scan --filter "ROE 连续5年 ≥15% 且 毛利率 连续5年 ≥30%" -m A
        v-investment scan --filter "ROE 5年至少4年 ≥15%, 平均≥15%" --fields roe,gross_profit_margin
    """
    try:
        # 解析过滤条件
        fb = parse_filter(filter_text)
        
        # 初始化 Scanner
        scanner = Scanner(market=market)
        
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
        
        # 解析字段列表
        field_list = [f.strip() for f in fields.split(",")]
        
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
        
        # 获取符合条件的股票列表
        qualified_stocks = result['stock_code'].unique()
        print(f"符合条件: {len(qualified_stocks)} 只股票")
        
        # 输出结果
        if output:
            result.to_csv(output, index=False, encoding='utf-8-sig')
            print(f"结果已保存到: {output}")
        else:
            # 显示符合条件的股票（取最新的数据）
            latest = result.sort_values('end_date', ascending=False).drop_duplicates('stock_code')
            print(latest.to_markdown(index=False))
            
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show version"""
    print("v-investment 0.1.0")


if __name__ == "__main__":
    app()
