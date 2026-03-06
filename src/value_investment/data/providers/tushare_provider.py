"""Tushare data provider for A 股 market

Tushare API documentation: https://tushare.pro/document/2

Required environment variable:
    TUSHARE_TOKEN: Your tushare API token

Usage:
    from value_investment.data.providers.tushare_provider import TushareProvider
    
    provider = TushareProvider(cache=cache, token="your_token")
    df = provider.get_balance_sheet("000001.SZ", 2023)
"""
import pandas as pd
import tushare as ts  # type: ignore

from value_investment.data.providers.base_provider import BaseProvider


class TushareProvider(BaseProvider):
    """Tushare provider for A 股 financial and market data
    
    Implements:
    - get_balance_sheet() - 资产负债表
    - get_income_statement() - 利润表
    - get_cash_flow_statement() - 现金流量表
    - get_historical_data() - 历史行情
    - get_stock_info() - 股票基本信息
    """
    
    def __init__(self, cache, field_mappings=None, token=""):
        """Initialize Tushare provider
        
        Args:
            cache: Cache instance
            field_mappings: Field name mappings (from config)
            token: Tushare API token (required)
        """
        super().__init__(cache, field_mappings, token=token)
        
        if not token:
            raise ValueError("Tushare token is required. Set TUSHARE_TOKEN environment variable.")
        
        # Initialize tushare
        ts.set_token(token)
        self._api = ts.pro_api()
    
    def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get balance sheet data
        
        Args:
            stock_code: Stock code (e.g., "000001.SZ")
            end_year: End year (e.g., 2023)
            
        Returns:
            DataFrame with balance sheet data (standard field names)
        """
        cache_key = self._get_cache_key("balance", stock_code, str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Fetch from tushare
        df = self._api.balancesheet(
            ts_code=stock_code,
            start_date=f"{end_year - 5}0101",  # Get last 5 years
            end_date=f"{end_year}1231",
            fields="ts_code,end_date,total_assets,total_liab,total_hldr_eqy_inc_monetary_cap,acct_rcv,inventories,fixed_assets,acct_pay"
        )
        
        # Apply field mapping
        result = self._apply_mapping(df, "balance")
        
        if result is not None:
            self._set_to_cache(cache_key, result)
            return result
        
        return pd.DataFrame()
    
    def get_income_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get income statement data
        
        Args:
            stock_code: Stock code
            end_year: End year
            
        Returns:
            DataFrame with income statement data
        """
        cache_key = self._get_cache_key("income", stock_code, str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Fetch from tushare
        df = self._api.income(
            ts_code=stock_code,
            start_date=f"{end_year - 5}0101",
            end_date=f"{end_year}1231",
            fields="ts_code,end_date,total_revenue,operating_revenue,net_profit,operating_profit,gross_profit,operating_cost"
        )
        
        # Apply field mapping
        result = self._apply_mapping(df, "income")
        
        if result is not None:
            self._set_to_cache(cache_key, result)
            return result
        
        return pd.DataFrame()
    
    def get_cash_flow_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get cash flow statement data
        
        Args:
            stock_code: Stock code
            end_year: End year
            
        Returns:
            DataFrame with cash flow statement data
        """
        cache_key = self._get_cache_key("cashflow", stock_code, str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Fetch from tushare
        df = self._api.cashflow(
            ts_code=stock_code,
            start_date=f"{end_year - 5}0101",
            end_date=f"{end_year}1231",
            fields="ts_code,end_date,operating_cash_flow,investing_cash_flow,financing_cash_flow,capex"
        )
        
        # Apply field mapping
        result = self._apply_mapping(df, "cashflow")
        
        if result is not None:
            self._set_to_cache(cache_key, result)
            return result
        
        return pd.DataFrame()
    
    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "",
    ) -> pd.DataFrame:
        """Get historical market data (daily prices)
        
        Args:
            stock_code: Stock code (e.g., "000001.SZ")
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adjust: Adjustment type ("", "qfq", "hfq")
            
        Returns:
            DataFrame with historical data (open, high, low, close, volume)
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
        
        # Map adjust parameter
        adj_map = {"": "", "qfq": "qfq", "hfq": "hfq"}
        adj = adj_map.get(adjust, "")
        
        # Fetch from tushare
        df = self._api.daily(
            ts_code=stock_code,
            start_date=start_date or "20100101",
            end_date=end_date or "20991231",
            adj=adj
        )
        
        # Apply field mapping
        result = self._apply_mapping(df, "market")
        
        if result is not None:
            self._set_to_cache(cache_key, result)
            return result
        
        return pd.DataFrame()
    
    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """Get stock basic information
        
        Args:
            stock_code: Stock code
            
        Returns:
            DataFrame with stock info
        """
        cache_key = self._get_cache_key("info", stock_code)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Fetch from tushare
        df = self._api.stock_basic(
            ts_code=stock_code,
            fields="ts_code,name,area,industry,market,list_date"
        )
        
        if not df.empty:
            self._set_to_cache(cache_key, df)
            return df
        
        return pd.DataFrame()
