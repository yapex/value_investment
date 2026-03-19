"""Tushare field mapper (Tushare 原始字段 -> 标准字段)

Single source of truth for Tushare API field mappings.
Auto-generates reverse index, no manual maintenance needed.
"""
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from value_investment.data.mapper import CUSTOM_FIELD_MAPPING
from value_investment.pipeline.fields import IFRSFields


@dataclass
class ReverseIndex:
    """Reverse index: 标准字段 -> Tushare 字段 (自动生成)"""
    balance_sheet: dict[str, str] = field(default_factory=dict)
    income_statement: dict[str, str] = field(default_factory=dict)
    cash_flow: dict[str, str] = field(default_factory=dict)
    indicators: dict[str, str] = field(default_factory=dict)
    market: dict[str, str] = field(default_factory=dict)  # daily_basic API


class TushareFieldMapper:
    """Tushare-specific field mapper (Tushare 原始字段 -> 标准字段)
    
    Single source of truth for Tushare API field mappings.
    Organized by statement type: balance_sheet, income_statement, cash_flow.
    
    Usage:
        mapper = TushareFieldMapper()
        
        # Map DataFrame columns to standard field names
        df = mapper.map_dataframe(raw_df, "balance_sheet")
        
        # Convert between Tushare and standard field names
        std_field = mapper.tushare_to_standard("total_assets", "balance_sheet")
        ts_field = mapper.standard_to_tushare(IFRSFields.TOTAL_ASSETS, "balance_sheet")
    """

    _instance: "TushareFieldMapper | None" = None

    def __new__(cls) -> "TushareFieldMapper":
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        # Initialize mappings from CUSTOM_FIELD_MAPPING
        self._init_mappings()

        # Auto-generate reverse index
        self._build_reverse_index()

    def _init_mappings(self) -> None:
        """Initialize field mappings from CUSTOM_FIELD_MAPPING"""
        # Filter only A股 (Tushare) mappings
        self.balance_sheet: dict[str, str] = {}
        self.income_statement: dict[str, str] = {}
        self.cash_flow: dict[str, str] = {}
        self.indicators: dict[str, str] = {}
        self.market: dict[str, str] = {}  # daily_basic API 字段映射

        # Define which standard fields belong to which statement type
        balance_fields = {
            IFRSFields.TOTAL_ASSETS,
            IFRSFields.TOTAL_LIABILITIES,
            IFRSFields.TOTAL_EQUITY,
            IFRSFields.CURRENT_ASSETS,
            IFRSFields.CURRENT_LIABILITIES,
            IFRSFields.CASH_AND_EQUIVALENTS,
            IFRSFields.INVENTORY,
            IFRSFields.ACCOUNTS_RECEIVABLE,
            IFRSFields.ACCOUNTS_PAYABLE,
            IFRSFields.FIXED_ASSETS,
            IFRSFields.PREPAYMENT,
            IFRSFields.CONTRACT_ASSETS,
            IFRSFields.CONTRACT_LIAB,
            IFRSFields.ADV_RECEIPTS,
        }

        income_fields = {
            IFRSFields.TOTAL_REVENUE,
            IFRSFields.NET_PROFIT,
            IFRSFields.OPERATING_PROFIT,
            IFRSFields.OPERATING_COST,
        }

        cash_flow_fields = {
            IFRSFields.OPERATING_CASH_FLOW,
            IFRSFields.INVESTING_CASH_FLOW,
            IFRSFields.FINANCING_CASH_FLOW,
            IFRSFields.CAPITAL_EXPENDITURE,
        }

        # Build mappings from CUSTOM_FIELD_MAPPING
        for standard_field, market_map in CUSTOM_FIELD_MAPPING.items():
            if "A股" in market_map:
                ts_field = market_map["A股"]
                
                # Skip metadata fields (not actual financial data)
                if standard_field in ("stock_code", "report_date", "announce_date", "update_flag"):
                    continue
                
                if standard_field in balance_fields:
                    self.balance_sheet[ts_field] = standard_field
                elif standard_field in income_fields:
                    self.income_statement[ts_field] = standard_field
                elif standard_field in cash_flow_fields:
                    self.cash_flow[ts_field] = standard_field

        # Add additional mappings based on actual Tushare API behavior
        # These are Tushare column names that match standard field names
        # or need special handling
        
        # Balance sheet: Tushare uses same name as standard
        direct_balance_fields = {
            IFRSFields.TOTAL_ASSETS: "total_assets",
            IFRSFields.TOTAL_LIABILITIES: "total_liab",
            IFRSFields.TOTAL_EQUITY: "total_hldr_eqy_exc_min_int",
            IFRSFields.CURRENT_LIABILITIES: "total_cur_liab",
            IFRSFields.CASH_AND_EQUIVALENTS: "money_cap",
            IFRSFields.INVENTORY: "inventories",
            IFRSFields.ACCOUNTS_RECEIVABLE: "accounts_receiv",
            IFRSFields.FIXED_ASSETS: "fix_assets",
            # 补充缺失的资产负债表字段
            IFRSFields.CURRENT_ASSETS: "total_cur_assets",
            IFRSFields.ACCOUNTS_PAYABLE: "accounts_pay",
            IFRSFields.PREPAYMENT: "prepayment",
            IFRSFields.CONTRACT_ASSETS: "contract_assets",
            IFRSFields.CONTRACT_LIAB: "contract_liab",
            IFRSFields.ADV_RECEIPTS: "adv_receipts",
            # 总股本
            "total_shares": "total_share",
        }
        
        for std_field, ts_field in direct_balance_fields.items():
            if ts_field not in self.balance_sheet:
                self.balance_sheet[ts_field] = std_field

        # Income statement: Tushare uses same name as standard
        direct_income_fields = {
            IFRSFields.TOTAL_REVENUE: "total_operate_income",
            IFRSFields.NET_PROFIT: "netprofit",
            IFRSFields.OPERATING_PROFIT: "operate_profit",
            # gross_profit 从 fina_indicator 获取
        }
        
        for std_field, ts_field in direct_income_fields.items():
            if ts_field not in self.income_statement:
                self.income_statement[ts_field] = std_field

        # Cash flow: Tushare uses different names
        direct_cash_flow_fields = {
            IFRSFields.OPERATING_CASH_FLOW: "n_cashflow_act",
            IFRSFields.INVESTING_CASH_FLOW: "n_cashflow_inv_act",
            IFRSFields.FINANCING_CASH_FLOW: "n_cash_flows_fnc_act",
            IFRSFields.CAPITAL_EXPENDITURE: "construct_long_asset",
        }
        
        for std_field, ts_field in direct_cash_flow_fields.items():
            if ts_field not in self.cash_flow:
                self.cash_flow[ts_field] = std_field

        # Financial indicators from fina_indicator API
        # Tushare fina_indicator returns pre-calculated ratios
        indicator_fields = {
            IFRSFields.ROE: "roe",
            IFRSFields.ROA: "roa",
            # 注意: gross_margin 是毛利率百分比，不是毛利润金额
            IFRSFields.GROSS_MARGIN: "gross_margin",
            IFRSFields.NET_PROFIT_MARGIN: "netprofit_margin",
            IFRSFields.CURRENT_RATIO: "current_ratio",
            IFRSFields.QUICK_RATIO: "quick_ratio",
            IFRSFields.DEBT_RATIO: "debt_to_assets",
            IFRSFields.ASSET_TURNOVER: "assets_turn",
            # ar_turn 是应收账款周转率
            IFRSFields.RECEIVABLE_TURNOVER: "ar_turn",
            "roic": "roic",
            # 每股指标
            IFRSFields.BASIC_EPS: "eps",
            IFRSFields.DILUTED_EPS: "dt_eps",
            IFRSFields.BOOK_VALUE_PER_SHARE: "bps",
        }

        # Market data from daily_basic API
        # Tushare daily_basic returns: total_mv, circ_mv, total_share, circ_share, pe, pe_ttm, pb
        market_fields = {
            IFRSFields.MARKET_CAP: "total_mv",  # 总市值 (万元)
            IFRSFields.PE_RATIO: "pe_ttm",     # 市盈率 TTM
            IFRSFields.PB_RATIO: "pb",          # 市净率
            "total_shares": "total_share",      # 总股本 (万股)
            "circ_market_cap": "circ_mv",       # 流通市值 (万元)
            "circ_shares": "circ_share",        # 流通股本 (万股)
        }

        # 注意: 以下字段需要特殊处理，不直接从 fina_indicator 获取
        # - gross_profit: 从 income statement 计算 (total_revenue - operating_cost)
        # - inventory_turnover: 需要从 balancesheet/income 计算
        # - accounts_payable, current_assets: 从 balancesheet 获取

        for std_field, ts_field in indicator_fields.items():
            self.indicators[ts_field] = std_field

        for std_field, ts_field in market_fields.items():
            self.market[ts_field] = std_field

    def _build_reverse_index(self) -> None:
        """Auto-generate reverse index: 标准字段 -> Tushare 字段"""
        self.reverse = ReverseIndex()

        for ts_field, std_field in self.balance_sheet.items():
            self.reverse.balance_sheet[std_field] = ts_field

        for ts_field, std_field in self.income_statement.items():
            self.reverse.income_statement[std_field] = ts_field

        for ts_field, std_field in self.cash_flow.items():
            self.reverse.cash_flow[std_field] = ts_field

        for ts_field, std_field in self.indicators.items():
            self.reverse.indicators[std_field] = ts_field

        for ts_field, std_field in self.market.items():
            self.reverse.market[std_field] = ts_field

    @property
    def supported_fields(self) -> set[str]:
        """Get all supported standard fields"""
        fields = set()
        fields.update(self.reverse.balance_sheet.keys())
        fields.update(self.reverse.income_statement.keys())
        fields.update(self.reverse.cash_flow.keys())
        fields.update(self.reverse.indicators.keys())
        fields.update(self.reverse.market.keys())  # market_cap, pe_ratio, pb_ratio
        return fields

    def _get_market_fields(self) -> set[str]:
        """Get standard fields from market data (daily_basic)"""
        return set(self.reverse.market.keys())

    def get_mapping(self, statement_type: str) -> dict[str, str]:
        """Get field mapping for statement type
        
        Args:
            statement_type: "balance_sheet" | "income_statement" | "cash_flow" | "indicators"
            
        Returns:
            {Tushare 字段名: 标准字段名}
        """
        mapping_map = {
            "balance_sheet": self.balance_sheet,
            "income_statement": self.income_statement,
            "cash_flow": self.cash_flow,
            "indicators": self.indicators,
            "market": self.market,
        }
        return mapping_map.get(statement_type, {})

    def map_dataframe(self, df: pd.DataFrame, statement_type: str) -> pd.DataFrame:
        """Map DataFrame columns from Tushare names to standard field names
        
        Args:
            df: Raw DataFrame with Tushare column names
            statement_type: "balance_sheet" | "income_statement" | "cash_flow" | "indicators"
            
        Returns:
            DataFrame with standard field names as columns
        """
        if df is None or df.empty:
            return df

        mapping = self.get_mapping(statement_type)
        if not mapping:
            return df

        result = df.copy()
        rename_map = {}

        # Only rename columns that exist in both DataFrame and mapping
        for ts_field, std_field in mapping.items():
            if ts_field in result.columns:
                rename_map[ts_field] = std_field

        # Apply renaming
        if rename_map:
            result = result.rename(columns=rename_map)

        return result

    def tushare_to_standard(self, ts_field: str, statement_type: str) -> str | None:
        """Convert Tushare field name to standard field name
        
        Args:
            ts_field: Tushare field name
            statement_type: "balance_sheet" | "income_statement" | "cash_flow"
            
        Returns:
            Standard field name, or None if not mapped
        """
        mapping = self.get_mapping(statement_type)
        return mapping.get(ts_field)

    def standard_to_tushare(self, std_field: str, statement_type: str) -> str | None:
        """Convert standard field name to Tushare field name
        
        Args:
            std_field: Standard field name
            statement_type: "balance_sheet" | "income_statement" | "cash_flow"
            
        Returns:
            Tushare field name, or None if not mapped
        """
        reverse_map = {
            "balance_sheet": self.reverse.balance_sheet,
            "income_statement": self.reverse.income_statement,
            "cash_flow": self.reverse.cash_flow,
        }
        return reverse_map.get(statement_type, {}).get(std_field)

    def get_tushare_fields(self, std_fields: set[str], statement_type: str) -> set[str]:
        """Get Tushare field names for a set of standard fields
        
        Args:
            std_fields: Set of standard field names
            statement_type: "balance_sheet" | "income_statement" | "cash_flow"
            
        Returns:
            Set of Tushare field names
        """
        reverse_map = {
            "balance_sheet": self.reverse.balance_sheet,
            "income_statement": self.reverse.income_statement,
            "cash_flow": self.reverse.cash_flow,
        }
        
        mapping = reverse_map.get(statement_type, {})
        return {mapping[f] for f in std_fields if f in mapping}
