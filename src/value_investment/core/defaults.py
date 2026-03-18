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
        # Income statement mappings (tushare native → standard)
        "income": {
            "ts_code": "stock_code",
            "end_date": "report_date",
            "total_revenue": "total_revenue",
            "revenue": "operating_revenue",
            "n_income": "net_profit",
            "n_income_attr_p": "parent_net_profit",
            "operate_profit": "operating_profit",
            "oper_cost": "operating_cost",
            "total_cogs": "total_operating_cost",
            "sell_exp": "sales_expense",
            "admin_exp": "management_expense",
            "fin_exp": "financial_expense",
            "basic_eps": "basic_eps",
            "diluted_eps": "diluted_eps",
            "ebit": "ebit",
            "ebitda": "ebitda",
            "income_tax": "income_tax",
            "total_profit": "total_profit",
        },
        # Balance sheet mappings
        "balance": {
            "ts_code": "stock_code",
            "end_date": "report_date",
            "total_assets": "total_assets",
            "total_hldr_eqy_inc_min_int": "total_equity",
            "total_liab": "total_liabilities",
            "total_cur_assets": "current_assets",
            "total_cur_liab": "current_liabilities",
            "money_cap": "cash_and_equivalents",
            "inventories": "inventory",
            "accounts_receiv": "accounts_receivable",
            "acct_payable": "accounts_payable",
            "fix_assets": "fixed_assets",
            "total_nca": "non_current_assets",
            "total_ncl": "non_current_liabilities",
            "capital_rese": "capital_reserve",
            "surplus_rese": "surplus_reserve",
            "undistr_porfit": "retained_earnings",
            "intan_assets": "intangible_assets",
            "goodwill": "goodwill",
        },
        # Cash flow mappings
        "cashflow": {
            "ts_code": "stock_code",
            "end_date": "report_date",
            "n_cashflow_act": "operating_cash_flow",
            "n_cashflow_inv_act": "investing_cash_flow",
            "n_cash_flows_fnc_act": "financing_cash_flow",
            "c_pay_acq_const_fiolta": "capital_expenditure",
            "free_cashflow": "free_cash_flow",
            "c_fr_sale_sg": "cash_from_sales",
            "c_paid_goods_s": "cash_paid_for_goods",
            "c_paid_to_for_empl": "cash_paid_to_employees",
            "c_paid_for_taxes": "cash_paid_for_taxes",
        },
        # Market data mappings (pro_bar)
        "market": {
            "ts_code": "stock_code",
            "trade_date": "trade_date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "vol": "volume",
            "amount": "amount",
        },
        # Stock info mappings (stock_basic)
        "info": {
            "ts_code": "stock_code",
            "name": "name",
            "area": "area",
            "industry": "industry",
            "market": "market",
            "list_date": "list_date",
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
            "Date": "trade_date",
            "Close": "close",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Volume": "volume",
            "Adj Close": "adj_close",
        },
        "info": {
            "symbol": "symbol",
            "shortName": "name",
            "marketCap": "market_cap",
            "peRatio": "pe_ratio",
            "dividendYield": "dividend_yield",
        },
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
