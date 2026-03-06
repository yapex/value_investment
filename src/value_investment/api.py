"""Python API for value investment analysis

Refactored to use SimpleContainer for dependency injection.
"""

from datetime import datetime

import pandas as pd

from value_investment.core.container_simple import SimpleContainer
from value_investment.core.dependencies import DataProvider, DependencyRegistry
from value_investment.data.mapper import DataMapper
from value_investment.indicators.base import IndicatorMeta, IndicatorResult
from value_investment.indicators.factory import IndicatorFactory
from value_investment.indicators.registry import IndicatorRegistry, register_defaults


class ValueInvestment:
    """
    Python API for value investment analysis

    Example:
        >>> vi = ValueInvestment()
        >>> info = vi.get_stock_info("600519")
        >>> print(info)
    """

    def __init__(self, cache_dir: str | None = None, market: str = "A"):
        """
        Initialize ValueInvestment API

        Args:
            cache_dir: Cache directory path
            market: Market type - "A" (A 股), "HK" (港股), "US" (美股). Can be auto-detected from symbol.
        """
        # Use SimpleContainer for dependency injection
        self._container = SimpleContainer(cache_dir=cache_dir)
        self._market = market
        
        # Get market-specific providers
        self._financial_provider = self._container.get_financial_provider(market)
        self._market_provider = self._container.get_market_provider(market)
        
        # Use financial provider as default provider
        self._provider = self._financial_provider
        
        # Initialize indicator factory with provider
        self._factory = IndicatorFactory(provider=self._provider)
        
        # Add dependency injection
        self._data_provider = DataProvider(self._provider, market=market)
        self._registry = DependencyRegistry(self._data_provider)
        
        # Initialize indicator registry with defaults
        register_defaults()

    @staticmethod
    def detect_market(code: str) -> str:
        """Detect market from stock code

        Args:
            code: Stock code

        Returns:
            Market code: "A", "HK", or "US"
        """
        if not code:
            return "A"

        code = code.strip()

        # A 股：6-digit codes starting with 0, 3, 6
        if code.isdigit() and len(code) == 6:
            if code[0] in ("0", "3", "6"):
                return "A"

        # 港股：5-digit codes
        if code.isdigit() and len(code) == 5:
            return "HK"

        # 美股：alphabetic ticker symbols
        if code.isalpha():
            return "US"

        # Default to A 股
        return "A"

    def get_market(self, symbol: str | None = None) -> str:
        """Get market, auto-detect from symbol if not specified

        Args:
            symbol: Stock code (optional)

        Returns:
            Market code
        """
        if self._market:
            return self._market
        if symbol:
            return self.detect_market(symbol)
        return "A"

    def get_stock_info(self, symbol: str, force_refresh: bool = False):
        """
        Get stock basic information

        Args:
            symbol: Stock code (e.g., "600519")
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with stock info
        """
        return self._provider.get_stock_info(symbol, force_refresh=force_refresh)

    def get_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ):
        """
        Get historical price data

        Args:
            symbol: Stock code
            end_date: End date (YYYYMMDD, required)
            start_date: Start date (YYYYMMDD, optional, defaults to earliest available)
            adjust: Adjustment type - "" (none), "qfq" (forward), "hfq" (backward, default for backtesting)
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with historical prices
        """
        # Use market provider for historical data
        return self._market_provider.get_historical_data(
            symbol, start_date, end_date, adjust
        )

    def get_balance_sheet(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
        fields: list[str] | None = None,
    ):
        """
        Get balance sheet

        Args:
            symbol: Stock code
            end_year: End year (optional, defaults to current year)
            force_refresh: If True, force refresh from data source
            fields: List of fields to return (optional). If not provided, returns all fields.
                   REPORT_DATE is always included if fields is provided.

        Returns:
            DataFrame with balance sheet data
        """
        df = self._provider.get_balance_sheet(symbol, end_year)
        return self._filter_fields(df, fields)

    def get_profit_sheet(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
        fields: list[str] | None = None,
    ):
        """
        Get profit sheet (income statement)

        Args:
            symbol: Stock code
            end_year: End year (optional, defaults to current year)
            force_refresh: If True, force refresh from data source
            fields: List of fields to return (optional). If not provided, returns all fields.
                   REPORT_DATE is always included if fields is provided.

        Returns:
            DataFrame with profit sheet data
        """
        df = self._provider.get_income_statement(symbol, end_year)
        return self._filter_fields(df, fields)

    def get_cashflow_sheet(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
        fields: list[str] | None = None,
    ):
        """
        Get cash flow sheet

        Args:
            symbol: Stock code
            end_year: End year (optional, defaults to current year)
            force_refresh: If True, force refresh from data source
            fields: List of fields to return (optional). If not provided, returns all fields.
                   REPORT_DATE is always included if fields is provided.

        Returns:
            DataFrame with cash flow sheet data
        """
        df = self._provider.get_cash_flow_statement(symbol, end_year)
        return self._filter_fields(df, fields)

    def get_financial_indicator(self, symbol: str, force_refresh: bool = False):
        """
        Get financial analysis indicators

        Args:
            symbol: Stock code
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with financial indicators
        """
        return self._provider.get_financial_indicator(symbol, force_refresh=force_refresh)

    def calculate_indicator(
        self,
        indicator_name: str,
        stock_code: str,
        years: int = 10,
        **kwargs,
    ) -> IndicatorResult:
        """
        Calculate a specific indicator

        Args:
            indicator_name: Name of the indicator (e.g., "roe", "roa")
            stock_code: Stock code
            years: Number of years for calculation
            **kwargs: Additional parameters for the indicator

        Returns:
            IndicatorResult with calculated value
        """
        # 计算日期范围，用于获取多年历史数据（如 prices 依赖）
        end_date = datetime.now().strftime('%Y%m%d')
        start_year = datetime.now().year - years
        start_date = f'{start_year}0101'

        # 将日期范围传入 kwargs，这样 prices 依赖会获取多年数据
        # 注意：使用不复权价格 (adjust="") 来计算历史 PE，因为复权价格会扭曲历史 PE
        kwargs['start_date'] = start_date
        kwargs['end_date'] = end_date
        kwargs['adjust'] = ""

        indicator = self._factory.get(indicator_name)

        # Resolve dependencies if indicator has 'needs'
        needs = getattr(indicator, 'needs', [])
        injected = self._registry.resolve(needs, stock_code, **kwargs)

        # Use shared method to prepare data
        years = kwargs.pop('years', 10)
        market_cap = kwargs.get('market_cap')
        financial_data, market_cap = self._prepare_data(stock_code, years, market_cap)

        if market_cap:
            kwargs['market_cap'] = market_cap

        # Pass stock_code for indicators that need it
        kwargs['stock_code'] = stock_code

        # Merge injected data into kwargs for indicators that need it
        full_kwargs = {**kwargs, **injected}

        # Pass data to indicator (data-passing pattern)
        return indicator.calculate(financial_data, **full_kwargs)

    def _prepare_data(
        self,
        stock_code: str,
        years: int = 10,
        market_cap: float = None,
    ) -> tuple:
        """
        Prepare financial data and market cap for indicators.
        """
        current_year = datetime.now().year

        # Get merged financial data (fetches cached sheets, merges in memory)
        all_data = self._get_financial_data(stock_code, current_year)

        # Take latest years
        if 'year' in all_data.columns:
            all_data = all_data.sort_values('year', ascending=False)
            financial_data = all_data.head(years)
        else:
            financial_data = all_data

        # Auto-fetch market_cap if not provided
        if market_cap is None:
            try:
                info = self._provider.get_stock_info(stock_code)
                if 'item' in info.columns:
                    for _, row in info.iterrows():
                        if '市值' in str(row['item']):
                            market_cap = float(row['value'])
                            break
            except Exception:
                pass

        return financial_data, market_cap

    def _filter_fields(self, df: pd.DataFrame, fields: list[str] | None = None) -> pd.DataFrame:
        """
        Filter DataFrame columns and format dates.

        Args:
            df: Input DataFrame
            fields: List of fields to return. If None, returns all columns.
                   REPORT_DATE is always included if fields is provided.

        Returns:
            DataFrame with filtered columns and formatted dates
        """
        if not fields:
            return df

        field_list = list(fields)
        # 强制包含 REPORT_DATE
        if "REPORT_DATE" not in field_list:
            field_list.insert(0, "REPORT_DATE")

        # 验证字段存在
        available_cols = set(df.columns)
        invalid_fields = [f for f in field_list if f not in available_cols]
        if invalid_fields:
            raise ValueError(f"Invalid fields: {invalid_fields}. Available fields: {sorted(available_cols)}")

        # 筛选列
        result = df[field_list].copy()

        # 格式化日期为 YYYY-MM-DD
        if "REPORT_DATE" in result.columns:
            result["REPORT_DATE"] = pd.to_datetime(result["REPORT_DATE"]).dt.strftime("%Y-%m-%d")

        return result

    def _get_financial_data(
        self,
        symbol: str,
        end_year: int,
    ) -> pd.DataFrame:
        """
        Get merged financial data for indicator calculation.
        Fetches cached sheets and merges in memory (no merged cache).

        Args:
            symbol: Stock code
            end_year: End year

        Returns:
            Merged DataFrame with all financial data
        """
        # Fetch individual sheets (each is cached separately)
        balance = self._provider.get_balance_sheet(symbol, end_year)
        profit = self._provider.get_income_statement(symbol, end_year)
        cashflow = self._provider.get_cash_flow_statement(symbol, end_year)

        # Apply field mapping to standardize column names to IFRS standard
        balance = DataMapper.map_balance_sheet(balance)
        profit = DataMapper.map_income_statement(profit)
        cashflow = DataMapper.map_cash_flow(cashflow)

        if balance.empty:
            return profit if not profit.empty else cashflow

        # Ensure year column exists
        for df in [balance, profit, cashflow]:
            if 'year' not in df.columns and 'REPORT_DATE' in df.columns:
                df['year'] = pd.to_datetime(df['REPORT_DATE']).dt.year

        # Merge on year
        merged = balance.copy()
        if not profit.empty and 'year' in profit.columns:
            profit_cols = [c for c in profit.columns if c not in merged.columns or c == 'year']
            merged = merged.merge(profit[profit_cols], on='year', how='outer', suffixes=('', '_profit'))

        if not cashflow.empty and 'year' in cashflow.columns:
            cashflow_cols = [c for c in cashflow.columns if c not in merged.columns or c == 'year']
            merged = merged.merge(cashflow[cashflow_cols], on='year', how='outer', suffixes=('', '_cashflow'))

        return merged

    def analyze(
        self,
        stock_code: str,
        years: int = 10,
        cagr_metrics: list = None,
        market_cap: float = None,
        report: bool = False,
        **kwargs,
    ) -> dict:
        """
        Perform complete analysis

        Args:
            stock_code: Stock code
            years: Number of years for analysis
            cagr_metrics: List of metrics for CAGR calculation, e.g. ["revenue", "net_profit"]
            market_cap: Market capitalization (if not provided, will try to fetch from stock info)
            report: If True, generate analysis report with warnings and notes
            **kwargs: Additional parameters for indicators

        Returns:
            Dictionary with:
                - name: Stock name with code
                - year_range: Year range string
                - table: DataFrame with yearly indicators
                - summary: List of summary metrics with labels
                - warnings: List of warning messages (if report=True)
                - notes: List of note messages (if report=True)
                - report: Markdown formatted report (if report=True)
        """
        # Get stock name
        name = stock_code
        try:
            info = self._provider.get_stock_info(stock_code)
            if 'item' in info.columns:
                for _, row in info.iterrows():
                    item = str(row['item'])
                    if '简称' in item or '名称' in item:
                        name = f"{row['value']} ({stock_code})"
                        break
        except Exception:
            pass

        # Use shared method to prepare data
        financial_data, market_cap = self._prepare_data(stock_code, years, market_cap)

        # Pass market_cap to indicators
        if market_cap:
            kwargs['market_cap'] = market_cap

        # Calculate all indicators
        results = {}
        for ind_name in self._factory.list_indicators():
            try:
                indicator = self._factory.get(ind_name)
                result = indicator.calculate(financial_data, **kwargs)
                results[ind_name] = result
            except Exception as e:
                results[ind_name] = {"error": str(e)}

        # Calculate additional CAGR metrics if specified
        if cagr_metrics:
            for metric in cagr_metrics:
                cagr_name = f"CAGR_{metric}"
                if cagr_name not in results:
                    try:
                        cagr_indicator = self._factory.get("CAGR")
                        result = cagr_indicator.calculate(financial_data, metric=metric, **kwargs)
                        results[cagr_name] = result
                    except Exception as e:
                        results[cagr_name] = {"error": str(e)}

        # Format results
        result_dict = self._format_analyze_results(name, results, years)

        # If report=True, add warnings, notes, and generate Markdown report
        if report:
            # Import detector and generate warnings
            from value_investment.analysis.detector import detect_warnings
            from value_investment.indicators.base import IndicatorResult

            # Extract indicator values for detector
            indicator_values = {}
            for ind_name, ind_result in results.items():
                # Skip error results
                if isinstance(ind_result, dict) and "error" in ind_result:
                    continue
                # Handle IndicatorResult objects
                if isinstance(ind_result, IndicatorResult):
                    if ind_result.value is not None:
                        indicator_values[ind_name] = ind_result.value
                    elif ind_result.values:
                        # Use latest value
                        indicator_values[ind_name] = ind_result.values[0]

            warnings, notes = detect_warnings(indicator_values)

            # Add warnings and notes to result
            result_dict["warnings"] = warnings
            result_dict["notes"] = notes

            # Generate Markdown report
            from value_investment.analysis.reporter import generate_report
            result_dict["report"] = generate_report(result_dict, stock_code)

        return result_dict

    def _format_analyze_results(self, name: str, results: dict, years: int) -> dict:
        """Format analyze results for display."""
        import math

        # Chinese labels for indicators
        label_map = {
            "ROE": "ROE",
            "ROA": "ROA",
            "gross_margin": "毛利率",
            "net_profit_margin": "净利率",
            "current_ratio": "流动比率",
            "ROIC": "ROIC",
            "CAGR": "营收 CAGR",
            "CAGR_revenue": "营收 CAGR",
            "CAGR_net_profit": "净利润 CAGR",
            "ImpliedGrowth": "市场隐含增长率",
            "asset_turnover": "资产周转率",
            "inventory_turnover": "存货周转率",
            "quick_ratio": "速动比率",
            "debt_ratio": "资产负债率",
            "receivable_turnover": "应收账款周转率",
            "payable_turnover": "应付账款周转率",
            "cfo_to_netprofit_sum": "盈利质量 (CFO/净利)",
        }

        # Collect all years from results
        all_years = set()
        for name_result in results.values():
            if hasattr(name_result, 'years') and name_result.years:
                for y in name_result.years:
                    if y > 100:
                        all_years.add(y)

        if not all_years:
            return {
                "name": name,
                "year_range": "",
                "table": pd.DataFrame(),
                "summary": []
            }

        sorted_years = sorted(all_years, reverse=True)
        year_range = f"{min(sorted_years)}-{max(sorted_years)}"

        # Build DataFrame
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

        # Reorder columns
        column_order = [
            "年份",
            "ROIC", "ROE", "ROA", "毛利率", "净利率",
            "流动比率", "速动比率", "资产负债率",
            "资产周转率", "存货周转率", "应收账款周转率", "应付账款周转率",
        ]
        existing_cols = [c for c in column_order if c in df.columns]
        df = df[existing_cols]

        # Summary metrics
        summary = []
        for ind_name, result in results.items():
            if hasattr(result, 'values') and not result.values and hasattr(result, 'value') and result.value:
                if ind_name == "CAGR":
                    continue
                label = label_map.get(ind_name, ind_name)
                if result.unit == "%":
                    summary.append({"label": label, "value": f"{result.value:.1f}%"})
                elif result.unit == "CNY":
                    if abs(result.value) > 1e9:
                        summary.append({"label": label, "value": f"{result.value/1e9:.2f}十亿"})
                    else:
                        summary.append({"label": label, "value": f"{result.value:.2f}"})
                else:
                    summary.append({"label": label, "value": str(result.value)})

        return {
            "name": name,
            "year_range": year_range,
            "table": df,
            "summary": summary
        }

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        cache = self._container.cache
        stats = {
            "memory_size": len(cache._memory_cache) if hasattr(cache, '_memory_cache') else 0,
        }
        if hasattr(cache, '_disk_cache'):
            stats["disk_cache_size"] = len(cache._disk_cache)
        else:
            stats["disk_cache_size"] = 0
        return stats

    def list_cache_keys(self, symbol: str | None = None, limit: int = 20) -> list[str]:
        """List cache keys."""
        cache = self._container.cache
        keys = []
        if hasattr(cache, '_disk_cache'):
            keys = list(cache._disk_cache.keys())
        elif hasattr(cache, '_memory_cache'):
            keys = list(cache._memory_cache.keys())

        if symbol:
            keys = [k for k in keys if symbol in k]

        return keys[:limit]

    def get_indicator(self, name: str) -> IndicatorMeta | None:
        """
        Get indicator metadata by name

        Args:
            name: Indicator name

        Returns:
            Indicator metadata or None if not found
        """
        registry = IndicatorRegistry.get_instance()
        return registry.get(name)

    def list_indicators(
        self,
        market: str | None = None,
        indicator_type: str | None = None,
    ) -> list:
        """
        List available indicators with optional filters

        Args:
            market: Filter by market ("A 股", "港股", "美股")
            indicator_type: Filter by type ("RAW", "SIMPLE", "COMPLEX")

        Returns:
            List of indicator names
        """
        registry = IndicatorRegistry.get_instance()

        results = registry.list_all()

        # Also get indicators from factory (for backward compatibility)
        factory_indicators = self._factory.list_indicators()

        # Combine both sources - get names from registry
        registry_names = {ind.name for ind in results}

        # Add factory indicators that are not in registry
        for name in factory_indicators:
            if name not in registry_names:
                # Create a minimal meta for factory indicators
                from value_investment.indicators.base import IndicatorMeta, IndicatorType
                meta = IndicatorMeta(
                    name=name,
                    display_name=name,
                    type=IndicatorType.CALCULATED,
                    description="",
                )
                results.append(meta)

        # Filter by market
        if market:
            results = [ind for ind in results if market in ind.market_fields or not ind.market_fields]

        # Filter by type
        if indicator_type:
            results = [ind for ind in results if ind.type.value == indicator_type]

        # Return indicator names (backward compatible)
        return [ind.name for ind in results]

    def clear_cache(self, symbol: str | None = None):
        """
        Clear cache

        Args:
            symbol: Optional specific symbol to clear cache for
        """
        if symbol:
            self._container.cache.invalidate(f"info_{symbol}")
            # Clear financial data cache (all end_years)
            for key in self._container.cache.list_keys():
                if key.startswith(f"financial_{symbol}_"):
                    self._container.cache.invalidate(key)
            # Clear historical data cache (all end_dates)
            for key in self._container.cache.list_keys():
                if key.startswith(f"hist_{symbol}_"):
                    self._container.cache.invalidate(key)
            self._container.cache.invalidate(f"indicator_{symbol}")
        else:
            # Clear all cache
            self._container.clear_cache()
