"""Data mapper for converting A股 fields to IFRS standard fields"""
import pandas as pd
import numpy as np
from typing import Optional


class DataMapper:
    """A股字段 -> 国际标准字段映射器"""

    # 资产负债表映射 (A股字段 -> 标准字段, 港股字段 -> 标准字段)
    BALANCE_MAPPING = {
        # A股字段
        "TOTAL_ASSETS": "total_assets",
        "TOTAL_CURRENT_ASSETS": "current_assets",
        "TOTAL_NONCURRENT_ASSETS": "non_current_assets",
        "MONETARYFUNDS": "cash_and_equivalents",
        "ACCOUNTS_RECE": "accounts_receivable",
        "INVENTORY": "inventory",
        "FIXED_ASSET": "fixed_assets",
        "INTANGIBLE_ASSET": "intangible_assets",
        "USERIGHT_ASSET": "right_of_use_assets",
        "LONG_EQUITY_INVEST": "long_term_equity_invest",
        "CONSTRUCT_PROGRESS": "construction_in_progress",
        "PREPAID_EXP": "prepaid_expenses",
        "DEFERRED_TAX_ASSETS": "deferred_tax_assets",
        "OTHER_CURRENT_ASSET": "other_current_assets",
        "OTHER_NONCURRENT_ASSET": "other_non_current_assets",
        "TOTAL_LIABILITIES": "total_liabilities",
        "TOTAL_CURRENT_LIAB": "current_liabilities",
        "TOTAL_NONCURRENT_LIAB": "non_current_liabilities",
        "ACCOUNTS_PAYABLE": "accounts_payable",
        "SHORT_LOAN": "short_term_debt",
        "LONG_LOAN": "long_term_debt",
        "BOND_PAYABLE": "bonds_payable",
        "ADVANCE_RECEIPTS": "advance_receipts",
        "OTHER_CURRENT_LIAB": "other_current_liabilities",
        "DEFERRED_TAX_LIAB": "deferred_tax_liabilities",
        "TOTAL_EQUITY": "total_equity",
        # 港股字段
        "总资产": "total_assets",
        "总负债": "total_liabilities",
        "总权益": "total_equity",
        "流动资产合计": "current_assets",
        "非流动资产合计": "non_current_assets",
        "流动负债合计": "current_liabilities",
        "非流动负债合计": "non_current_liabilities",
        "现金及等价物": "cash_and_equivalents",
        "应收帐款": "accounts_receivable",
        "存货": "inventory",
        "固定资产": "fixed_assets",
        "无形资产": "intangible_assets",
        "短期贷款": "short_term_debt",
        "长期贷款": "long_term_debt",
        "应付帐款": "accounts_payable",
        "股东权益": "shareholders_equity",
        "股本": "share_capital",
        "股本溢价": "share_premium",
        "保留溢利(累计亏损)": "retained_earnings",
        "在建工程": "construction_in_progress",
        "联营公司权益": "investment_in_associates",
        "合营公司权益": "investment_in_joint_ventures",
    }

    # 利润表映射 (A股字段 -> 标准字段, 港股字段 -> 标准字段)
    INCOME_MAPPING = {
        # A股字段
        "TOTAL_OPERATE_INCOME": "total_revenue",
        "OPERATE_INCOME": "operating_income",
        "TOTAL_OPERATE_COST": "total_operating_cost",
        "OPERATE_COST": "operating_cost",
        "SALE_EXPENSE": "sales_expense",
        "MANAGE_EXPENSE": "management_expense",
        "FINANCE_EXPENSE": "financial_expense",
        "RESEARCH_EXPENSE": "research_expense",
        "OPERATE_PROFIT": "operating_profit",
        "TOTAL_PROFIT": "total_profit",
        "NETPROFIT": "net_profit",
        "PARENT_NETPROFIT": "parent_net_profit",
        "INCOME_TAX": "income_tax",
        "NON_OPERATE_INCOME": "non_operating_income",
        "NON_OPERATE_COST": "non_operating_cost",
        "INVEST_INCOME": "investment_income",
        "ASSET_DISPOSAL_GAIN": "asset_disposal_gain",
        "OTHER_PROFIT": "other_profit",
        "WEIGHTED_AVG_ROE": "weighted_roe",
        "BASIC_EPS": "basic_eps",
        "DILUTED_EPS": "diluted_eps",
        # 港股字段
        "营业额": "total_revenue",
        "经营溢利": "operating_profit",
        "毛利": "gross_profit",
        "除税前溢利": "profit_before_tax",
        "除税后溢利": "profit_after_tax",
        "股东应占溢利": "parent_net_profit",
        "持续经营业务税后利润": "net_profit_from_continuing_operations",
        "本公司拥有人应占全面收益总额": "total_comprehensive_income",
        "税项": "income_tax",
        "利息收入": "interest_income",
        "融资成本": "finance_cost",
        "行政开支": "administrative_expenses",
        "销售及分销费用": "selling_distribution_expenses",
        "折旧及摊销": "depreciation_amortization",
    }

    # 现金流量表映射 (A股字段 -> 标准字段, 港股字段 -> 标准字段)
    CASHFLOW_MAPPING = {
        # A股字段
        "NETCASH_OPERATE": "operating_cash_flow",
        "NETCASH_INVEST": "investing_cash_flow",
        "NETCASH_FINANCE": "financing_cash_flow",
        "CONSTRUCT_LONG_ASSET": "capital_expenditure",
        "END_CCE": "cash_and_equivalents_end",
        "BEGIN_CCE": "cash_and_equivalents_begin",
        "CASH_SALES": "cash_received_from_sales",
        "CASH_PURCHASE": "cash_paid_for_goods",
        "CASH_TO_STAFF": "cash_paid_to_employees",
        "TAXES_PAYMENT": "taxes_paid",
        "DIVIDEND_INCOME": "dividend_received",
        "BORROW_RECEIVE": "debt_acquisition",
        "BOND_ISSUE": "bond_issuance",
        "DEBT_REPAYMENT": "debt_repayment",
        "DIVIDEND_PAYMENT": "dividend_paid",
        # 港股字段
        "经营业务现金净额": "operating_cash_flow",
        "投资业务现金净额": "investing_cash_flow",
        "融资业务现金净额": "financing_cash_flow",
        "购建固定资产": "capital_expenditure",
        "购建无形资产及其他资产": "capital_expenditure_intangible",
        "已付利息(经营)": "interest_paid_operating",
        "已付利息(融资)": "interest_paid_financing",
        "已付税项": "taxes_paid",
        "已收利息(投资)": "interest_received",
        "已收股息(投资)": "dividend_received",
        "期初现金": "cash_begin",
        "期末现金": "cash_end",
        "现金净额": "net_cash_change",
        "经营产生现金": "cash_generated_from_operations",
        "营运资金变动前经营溢利": "operating_profit_before_working_capital",
    }

    # 基础字段（不映射）
    BASE_FIELDS = ["year", "SECURITY_CODE", "REPORT_DATE"]

    @classmethod
    def map_balance_sheet(cls, df: pd.DataFrame, keep_original: bool = True) -> pd.DataFrame:
        """
        映射资产负债表字段

        Args:
            df: 原始资产负债表 DataFrame
            keep_original: 是否保留原始字段（添加后缀 _original）

        Returns:
            映射后的 DataFrame
        """
        if df is None or df.empty:
            return df

        result = df.copy()
        rename_map = {}

        # 只映射存在的字段
        for old_field, new_field in cls.BALANCE_MAPPING.items():
            if old_field in result.columns:
                rename_map[old_field] = new_field

        # 重命名字段
        result = result.rename(columns=rename_map)

        # 计算衍生字段
        result = cls._calculate_balance_derived_fields(result)

        # 保留原始字段
        if keep_original:
            result = cls._preserve_original_fields(df, result, rename_map)

        return result

    @classmethod
    def map_income_statement(cls, df: pd.DataFrame, keep_original: bool = True) -> pd.DataFrame:
        """
        映射利润表字段

        Args:
            df: 原始利润表 DataFrame
            keep_original: 是否保留原始字段（添加后缀 _original）

        Returns:
            映射后的 DataFrame
        """
        if df is None or df.empty:
            return df

        result = df.copy()
        rename_map = {}

        # 只映射存在的字段
        for old_field, new_field in cls.INCOME_MAPPING.items():
            if old_field in result.columns:
                rename_map[old_field] = new_field

        # 重命名字段
        result = result.rename(columns=rename_map)

        # 计算衍生字段
        result = cls._calculate_income_derived_fields(result)

        # 保留原始字段
        if keep_original:
            result = cls._preserve_original_fields(df, result, rename_map)

        return result

    @classmethod
    def map_cash_flow(cls, df: pd.DataFrame, keep_original: bool = True) -> pd.DataFrame:
        """
        映射现金流量表字段

        Args:
            df: 原始现金流量表 DataFrame
            keep_original: 是否保留原始字段（添加后缀 _original）

        Returns:
            映射后的 DataFrame
        """
        if df is None or df.empty:
            return df

        result = df.copy()
        rename_map = {}

        # 只映射存在的字段
        for old_field, new_field in cls.CASHFLOW_MAPPING.items():
            if old_field in result.columns:
                rename_map[old_field] = new_field

        # 重命名字段
        result = result.rename(columns=rename_map)

        # 计算衍生字段
        result = cls._calculate_cashflow_derived_fields(result)

        # 保留原始字段
        if keep_original:
            result = cls._preserve_original_fields(df, result, rename_map)

        return result

    @classmethod
    def _calculate_balance_derived_fields(cls, df: pd.DataFrame) -> pd.DataFrame:
        """计算资产负债表衍生字段"""
        # 如果需要添加计算字段，在这里添加
        return df

    @classmethod
    def _calculate_income_derived_fields(cls, df: pd.DataFrame) -> pd.DataFrame:
        """计算利润表衍生字段"""
        # 毛利润 = 营业收入 - 营业成本
        if "operating_income" in df.columns and "operating_cost" in df.columns:
            df["gross_profit"] = df["operating_income"] - df["operating_cost"]

        # EBIT = 净利润 + 所得税 + 财务费用
        if "net_profit" in df.columns:
            net_profit = df["net_profit"].fillna(0)
            income_tax = df["income_tax"].fillna(0) if "income_tax" in df.columns else 0
            financial_expense = df["financial_expense"].fillna(0) if "financial_expense" in df.columns else 0
            df["ebit"] = net_profit + income_tax + financial_expense

        return df

    @classmethod
    def _calculate_cashflow_derived_fields(cls, df: pd.DataFrame) -> pd.DataFrame:
        """计算现金流量表衍生字段"""
        # 自由现金流 = 经营活动现金流 - 投资活动现金流
        if "operating_cash_flow" in df.columns and "investing_cash_flow" in df.columns:
            df["free_cash_flow"] = df["operating_cash_flow"] - df["investing_cash_flow"]

        return df

    @classmethod
    def _preserve_original_fields(
        cls,
        original_df: pd.DataFrame,
        mapped_df: pd.DataFrame,
        rename_map: dict
    ) -> pd.DataFrame:
        """保留原始字段，添加 _original 后缀"""
        for old_field in rename_map.keys():
            if old_field in original_df.columns:
                mapped_df[f"{rename_map[old_field]}_original"] = original_df[old_field]

        return mapped_df

    @classmethod
    def to_standard_format(cls, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        合并后的数据转换为标准格式

        对已合并的三张报表数据进行字段标准化处理

        Args:
            merged_df: 已合并的三张报表 DataFrame

        Returns:
            标准格式的 DataFrame
        """
        if merged_df is None or merged_df.empty:
            return merged_df

        result = merged_df.copy()

        # 确保有 year 字段
        if "year" not in result.columns and "REPORT_DATE" in result.columns:
            result["year"] = pd.to_datetime(result["REPORT_DATE"]).dt.year

        # 按年份排序
        if "year" in result.columns:
            result = result.sort_values("year")

        return result

    @classmethod
    def get_standard_columns(cls) -> list:
        """获取所有标准字段名列表"""
        balance_cols = list(cls.BALANCE_MAPPING.values())
        income_cols = list(cls.INCOME_MAPPING.values())
        cashflow_cols = list(cls.CASHFLOW_MAPPING.values())
        base_cols = cls.BASE_FIELDS.copy()

        # 添加计算字段
        calculated_cols = ["gross_profit", "ebit", "free_cash_flow"]

        return base_cols + balance_cols + income_cols + cashflow_cols + calculated_cols
