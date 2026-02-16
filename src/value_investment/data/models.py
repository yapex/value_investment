"""Standard financial data models"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BalanceSheet:
    """资产负债表标准模型"""
    # 基础标识
    year: int
    security_code: str

    # 资产类 (Assets)
    total_assets: Optional[float] = None  # TOTAL_ASSETS
    current_assets: Optional[float] = None  # TOTAL_CURRENT_ASSETS
    non_current_assets: Optional[float] = None  # TOTAL_NONCURRENT_ASSETS
    cash_and_equivalents: Optional[float] = None  # MONETARYFUNDS
    accounts_receivable: Optional[float] = None  # ACCOUNTS_RECE
    inventory: Optional[float] = None  # INVENTORY
    fixed_assets: Optional[float] = None  # FIXED_ASSET
    intangible_assets: Optional[float] = None  # INTANGIBLE_ASSET
    right_of_use_assets: Optional[float] = None  # USERIGHT_ASSET
    long_term_equity_invest: Optional[float] = None  # LONG_EQUITY_INVEST
    construction_in_progress: Optional[float] = None  # CONSTRUCT_PROGRESS
    prepaid_expenses: Optional[float] = None  # PREPAID_EXP
    deferred_tax_assets: Optional[float] = None  # DEFERRED_TAX_ASSETS
    other_current_assets: Optional[float] = None  # OTHER_CURRENT_ASSET
    other_non_current_assets: Optional[float] = None  # OTHER_NONCURRENT_ASSET

    # 负债类 (Liabilities)
    total_liabilities: Optional[float] = None  # TOTAL_LIABILITIES
    current_liabilities: Optional[float] = None  # TOTAL_CURRENT_LIAB
    non_current_liabilities: Optional[float] = None  # TOTAL_NONCURRENT_LIAB
    accounts_payable: Optional[float] = None  # ACCOUNTS_PAYABLE
    short_term_debt: Optional[float] = None  # SHORT_LOAN
    long_term_debt: Optional[float] = None  # LONG_LOAN
    bonds_payable: Optional[float] = None  # BOND_PAYABLE
    advance_receipts: Optional[float] = None  # ADVANCE_RECEIPTS
    other_current_liabilities: Optional[float] = None  # OTHER_CURRENT_LIAB
    deferred_tax_liabilities: Optional[float] = None  # DEFERRED_TAX_LIAB

    # 权益类 (Equity)
    total_equity: Optional[float] = None  # TOTAL_EQUITY


@dataclass
class IncomeStatement:
    """利润表标准模型"""
    # 基础标识
    year: int
    security_code: str

    # 收入类 (Revenue)
    total_revenue: Optional[float] = None  # TOTAL_OPERATE_INCOME
    operating_income: Optional[float] = None  # OPERATE_INCOME

    # 成本费用类 (Costs & Expenses)
    total_operating_cost: Optional[float] = None  # TOTAL_OPERATE_COST
    operating_cost: Optional[float] = None  # OPERATE_COST
    sales_expense: Optional[float] = None  # SALE_EXPENSE
    management_expense: Optional[float] = None  # MANAGE_EXPENSE
    financial_expense: Optional[float] = None  # FINANCE_EXPENSE
    research_expense: Optional[float] = None  # RESEARCH_EXPENSE

    # 利润类 (Profit)
    gross_profit: Optional[float] = None  # 计算: operating_income - operating_cost
    operating_profit: Optional[float] = None  # OPERATE_PROFIT
    total_profit: Optional[float] = None  # TOTAL_PROFIT
    net_profit: Optional[float] = None  # NETPROFIT
    parent_net_profit: Optional[float] = None  # PARENT_NETPROFIT
    ebit: Optional[float] = None  # 计算: net_profit + income_tax + financial_expense

    # 其他
    income_tax: Optional[float] = None  # INCOME_TAX
    non_operating_income: Optional[float] = None  # NON_OPERATE_INCOME
    non_operating_cost: Optional[float] = None  # NON_OPERATE_COST
    investment_income: Optional[float] = None  # INVEST_INCOME
    asset_disposal_gain: Optional[float] = None  # ASSET_DISPOSAL_GAIN
    other_profit: Optional[float] = None  # OTHER_PROFIT

    # 每股指标
    weighted_roe: Optional[float] = None  # WEIGHTED_AVG_ROE
    basic_eps: Optional[float] = None  # BASIC_EPS
    diluted_eps: Optional[float] = None  # DILUTED_EPS


@dataclass
class CashFlowStatement:
    """现金流量表标准模型"""
    # 基础标识
    year: int
    security_code: str

    # 现金流量
    operating_cash_flow: Optional[float] = None  # NETCASH_OPERATE
    investing_cash_flow: Optional[float] = None  # NETCASH_INVEST
    financing_cash_flow: Optional[float] = None  # NETCASH_FINANCE
    free_cash_flow: Optional[float] = None  # 计算: operating_cash_flow - investing_cash_flow

    # 细分项目
    capital_expenditure: Optional[float] = None  # CONSTRUCT_LONG_ASSET
    cash_and_equivalents_end: Optional[float] = None  # END_CCE
    cash_and_equivalents_begin: Optional[float] = None  # BEGIN_CCE
    cash_received_from_sales: Optional[float] = None  # CASH_SALES
    cash_paid_for_goods: Optional[float] = None  # CASH_PURCHASE
    cash_paid_to_employees: Optional[float] = None  # CASH_TO_STAFF
    taxes_paid: Optional[float] = None  # TAXES_PAYMENT
    dividend_received: Optional[float] = None  # DIVIDEND_INCOME
    debt_acquisition: Optional[float] = None  # BORROW_RECEIVE
    bond_issuance: Optional[float] = None  # BOND_ISSUE
    debt_repayment: Optional[float] = None  # DEBT_REPAYMENT
    dividend_paid: Optional[float] = None  # DIVIDEND_PAYMENT


@dataclass
class StandardFinancialData:
    """合并后的标准财务数据"""
    year: int
    security_code: str

    # 资产负债表字段
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    current_assets: Optional[float] = None
    non_current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    non_current_liabilities: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    accounts_receivable: Optional[float] = None
    inventory: Optional[float] = None
    fixed_assets: Optional[float] = None
    intangible_assets: Optional[float] = None
    accounts_payable: Optional[float] = None
    short_term_debt: Optional[float] = None
    long_term_debt: Optional[float] = None

    # 利润表字段
    total_revenue: Optional[float] = None
    operating_income: Optional[float] = None
    operating_cost: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_profit: Optional[float] = None
    total_profit: Optional[float] = None
    net_profit: Optional[float] = None
    parent_net_profit: Optional[float] = None
    ebit: Optional[float] = None
    income_tax: Optional[float] = None
    research_expense: Optional[float] = None
    sales_expense: Optional[float] = None
    management_expense: Optional[float] = None
    financial_expense: Optional[float] = None

    # 现金流量表字段
    operating_cash_flow: Optional[float] = None
    investing_cash_flow: Optional[float] = None
    financing_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    capital_expenditure: Optional[float] = None
    cash_and_equivalents_end: Optional[float] = None

    # 原始字段（用于追溯审计）
    _original_columns: dict = field(default_factory=dict)
