"""Default data source configurations

This module defines the default provider configurations for all markets.
Configurations can be overridden via environment variables or custom config files.

Current data source strategy:
- A 股 (A): tushare (financial + market)
- 港股 (HK): akshare (financial) + yfinance (market)
- 美股 (US): akshare (financial) + yfinance (market)
"""

from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource

# ============================================================================
# Provider Configurations
# ============================================================================

# Tushare Provider (A 股财务 + 交易数据)
TUSHARE_A_CONFIG = ProviderConfig(
    name="tushare_a",
    module="value_investment.data.providers.tushare_provider",
    class_name="TushareProvider",
    init_kwargs={"token": "${TUSHARE_TOKEN}"},
    field_mappings={
        # Income statement mappings (ts_code → standard)
        "income": {
            "ts_code": "stock_code",
            "end_date": "report_date",
            "total_revenue": "total_revenue",
            "operating_revenue": "total_revenue",
            "net_profit": "net_profit",
            "net_profit_attr_to_parent": "parent_net_profit",
            "operating_profit": "operating_profit",
            "gross_profit": "gross_profit",
            "operating_cost": "operating_cost",
        },
        # Balance sheet mappings
        "balance": {
            "ts_code": "stock_code",
            "end_date": "report_date",
            "total_assets": "total_assets",
            "total_equity": "total_equity",
            "total_liability": "total_liabilities",
            "current_assets": "current_assets",
            "current_liability": "current_liabilities",
            "monetary_cap": "cash_and_equivalents",
            "inventories": "inventory",
            "acct_rcv": "accounts_receivable",
            "acct_pay": "accounts_payable",
            "fixed_assets": "fixed_assets",
        },
        # Cash flow mappings
        "cashflow": {
            "ts_code": "stock_code",
            "end_date": "report_date",
            "operating_cash_flow": "operating_cash_flow",
            "investing_cash_flow": "investing_cash_flow",
            "financing_cash_flow": "financing_cash_flow",
            "capex": "capital_expenditure",
        },
    }
)

# Akshare Provider (港股/美股财务数据)
AKSHARE_HK_CONFIG = ProviderConfig(
    name="akshare_hk",
    module="value_investment.data.providers.akshare_provider",
    class_name="AkshareProvider",
    init_kwargs={"market": "HK"},
    field_mappings={
        "income": {
            "收益": "total_revenue",
            "期内溢利": "net_profit",
            "营业溢利": "operating_profit",
            "毛利": "gross_profit",
        },
        "balance": {
            "资产总值": "total_assets",
            "权益总额": "total_equity",
            "总负债": "total_liabilities",
            "流动资产合计": "current_assets",
            "流动负债合计": "current_liabilities",
            "现金及等价物": "cash_and_equivalents",
            "存货": "inventory",
            "应收帐款": "accounts_receivable",
            "应付帐款": "accounts_payable",
            "固定资产": "fixed_assets",
        },
        "cashflow": {
            "经营业务现金净额": "operating_cash_flow",
            "投资业务现金净额": "investing_cash_flow",
            "融资业务现金净额": "financing_cash_flow",
            "购建固定资产": "capital_expenditure",
        },
    }
)

AKSHARE_US_CONFIG = ProviderConfig(
    name="akshare_us",
    module="value_investment.data.providers.akshare_provider",
    class_name="AkshareProvider",
    init_kwargs={"market": "US"},
    field_mappings={
        "income": {
            "totalRevenue": "total_revenue",
            "netIncome": "net_profit",
            "operatingIncome": "operating_profit",
            "grossProfit": "gross_profit",
            "costOfRevenue": "operating_cost",
        },
        "balance": {
            "totalAssets": "total_assets",
            "totalStockholdersEquity": "total_equity",
            "totalLiabilities": "total_liabilities",
            "totalCurrentAssets": "current_assets",
            "totalCurrentLiabilities": "current_liabilities",
            "cashAndCashEquivalents": "cash_and_equivalents",
            "inventory": "inventory",
            "accountsReceivable": "accounts_receivable",
            "accountsPayable": "accounts_payable",
            "propertyPlantEquipment": "fixed_assets",
        },
        "cashflow": {
            "operatingCashFlow": "operating_cash_flow",
            "investingCashFlow": "investing_cash_flow",
            "financingCashFlow": "financing_cash_flow",
            "capitalExpenditure": "capital_expenditure",
        },
    }
)

# YFinance Provider (港股/美股交易数据)
YFINANCE_CONFIG = ProviderConfig(
    name="yfinance",
    module="value_investment.data.providers.yfinance_provider",
    class_name="YFinanceProvider",
    field_mappings={
        "market": {
            "Close": "close",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Volume": "volume",
            "Adj Close": "adj_close",
        }
    }
)

# ============================================================================
# Default Data Sources Configuration
# ============================================================================

DEFAULT_DATASOURCES = DataSourcesConfig(
    providers={
        # A 股使用 tushare
        "tushare_a": TUSHARE_A_CONFIG,
        # 港股/美股财务使用 akshare
        "akshare_hk": AKSHARE_HK_CONFIG,
        "akshare_us": AKSHARE_US_CONFIG,
        # 港股/美股交易使用 yfinance
        "yfinance": YFINANCE_CONFIG,
    },
    markets={
        # A 股：财务 + 交易都用 tushare
        "A": MarketDataSource(financial="tushare_a", market="tushare_a"),
        # 港股：财务用 akshare，交易用 yfinance
        "HK": MarketDataSource(financial="akshare_hk", market="yfinance"),
        # 美股：财务用 akshare，交易用 yfinance
        "US": MarketDataSource(financial="akshare_us", market="yfinance"),
    }
)
