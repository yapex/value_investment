"""YFinance provider for港股/美股 market data

YFinance (Yahoo Finance) provides free market data for global stocks.

GitHub: https://github.com/ranaroussi/yfinance

Usage:
    from value_investment.data.providers.yfinance_provider import YFinanceProvider

    provider = YFinanceProvider(cache=cache)
    df = provider.get_historical_data("0005.HK", start_date="20230101", end_date="20231231")
    df = provider.get_historical_data("AAPL", start_date="20230101", end_date="20231231")
"""
import pandas as pd
import yfinance as yf  # type: ignore

from value_investment.core.constants import HISTORICAL_DATA_TTL
from value_investment.data.providers.base_provider import (
    BaseProvider,
    get_ttl_until_next_midnight,
)


class YFinanceProvider(BaseProvider):
    """YFinance provider for港股/美股 market data

    Implements:
    - get_historical_data() - 历史行情（日线）
    - get_stock_info() - 股票基本信息

    Note:
    - No API token required
    - Data quality may vary (free source)
    - Rate limits may apply
    """

    # 缓存 TTL 常量
    HISTORICAL_DATA_TTL = HISTORICAL_DATA_TTL

    def __init__(self, cache, field_mappings=None, **kwargs):
        """Initialize YFinance provider

        Args:
            cache: Cache instance
            field_mappings: Field name mappings (from config)
            **kwargs: Additional arguments (ignored, for compatibility)
        """
        super().__init__(cache, field_mappings, **kwargs)
    
    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "",
    ) -> pd.DataFrame:
        """Get historical market data (daily prices)

        Args:
            stock_code: Stock code
                - HK stocks: "0005.HK"
                - US stocks: "AAPL"
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adjust: Adjustment type ("", "qfq", "hfq")
                Note: yfinance handles adjustment internally

        Returns:
            DataFrame with historical data (open, high, low, close, volume)
            Standard field names if field_mappings provided
        """
        cache_key = self._get_cache_key(
            "market", stock_code,
            start_date or "all",
            end_date or "latest",
            adjust or "none"
        )
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # Create ticker
            ticker = yf.Ticker(stock_code)

            # Fetch history
            # yfinance expects YYYY-MM-DD format
            start = start_date
            end = end_date
            if start_date and len(start_date) == 8:
                start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            if end_date and len(end_date) == 8:
                end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"

            df = ticker.history(start=start, end=end)

            if df.empty:
                return pd.DataFrame()

            # Reset index to get date as column
            df = df.reset_index()

            # Rename 'Date' column to 'trade_date' for consistency
            if 'Date' in df.columns:
                df = df.rename(columns={'Date': 'trade_date'})

            # Apply field mapping
            result = self._apply_mapping(df, "market")

            if result is not None and not result.empty:
                self._set_to_cache(cache_key, result, ttl=self.HISTORICAL_DATA_TTL)
                return result

            return pd.DataFrame()

        except Exception as e:
            # Log error and return empty DataFrame
            print(f"YFinance error for {stock_code}: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """Get stock basic information

        Args:
            stock_code: Stock code

        Returns:
            DataFrame with stock info (symbol, name, market cap, etc.)
        """
        cache_key = self._get_cache_key("info", stock_code)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        try:
            ticker = yf.Ticker(stock_code)
            info = ticker.info

            if not info:
                return pd.DataFrame()

            # Convert dict to DataFrame
            df = pd.DataFrame([info])

            # Apply field mapping if available
            result = self._apply_mapping(df, "info")

            if result is not None and not result.empty:
                ttl = get_ttl_until_next_midnight()
                self._set_to_cache(cache_key, result, ttl=ttl)
                return result

            return pd.DataFrame()

        except Exception as e:
            print(f"YFinance info error for {stock_code}: {e}")
            return pd.DataFrame()

    # Override abstract method with not implemented
    def get_balance_sheet(self, stock_code: str, end_year: int, start_year: int | None = None) -> pd.DataFrame:
        """YFinance does not support reliable balance sheet data

        Use akshare for港股/美股 financial statements.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "YFinance provider does not support balance sheet data. "
            "Use akshare provider for financial statements."
        )

    def get_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """YFinance does not support reliable income statement data

        Use akshare for港股/美股 financial statements.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "YFinance provider does not support income statement data. "
            "Use akshare provider for financial statements."
        )

    def get_cash_flow_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """YFinance does not support reliable cash flow statement data

        Use akshare for港股/美股 financial statements.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "YFinance provider does not support cash flow statement data. "
            "Use akshare provider for financial statements."
        )
