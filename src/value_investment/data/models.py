"""Standard financial data models"""
from dataclasses import dataclass, field


@dataclass
class BalanceSheet:
    """资产负债表标准模型"""
    # 基础标识
    year: int
    security_code: str

    # 资产类 (Assets)
    total_assets: float | None = None  # TOTAL_ASSETS
    current_assets: float | None = None  # TOTAL_CURRENT_ASSETS
    non_current_assets: float | None = None  # TOTAL_NONCURRENT_ASSETS
    cash_and_equivalents: float | None = None  # MONETARYFUNDS
    accounts_receivable: float | None = None  # ACCOUNTS_RECE
    inventory: float | None = None  # INVENTORY
    fixed_assets: float | None = None  # FIXED_ASSET
    intangible_assets: float | None = None  # INTANGIBLE_ASSET
    right_of_use_assets: float | None = None  # USERIGHT_ASSET
    long_term_equity_invest: float | None = None  # LONG_EQUITY_INVEST
    construction_in_progress: float | None = None  # CONSTRUCT_PROGRESS
    prepaid_expenses: float | None = None  # PREPAID_EXP
    deferred_tax_assets: float | None = None  # DEFERRED_TAX_ASSETS
    other_current_assets: float | None = None  # OTHER_CURRENT_ASSET
    other_non_current_assets: float | None = None  # OTHER_NONCURRENT_ASSET

    # 负债类 (Liabilities)
    total_liabilities: float | None = None  # TOTAL_LIABILITIES
    current_liabilities: float | None = None  # TOTAL_CURRENT_LIAB
    non_current_liabilities: float | None = None  # TOTAL_NONCURRENT_LIAB
    accounts_payable: float | None = None  # ACCOUNTS_PAYABLE
    short_term_debt: float | None = None  # SHORT_LOAN
    long_term_debt: float | None = None  # LONG_LOAN
    bonds_payable: float | None = None  # BOND_PAYABLE
    advance_receipts: float | None = None  # ADVANCE_RECEIPTS
    other_current_liabilities: float | None = None  # OTHER_CURRENT_LIAB
    deferred_tax_liabilities: float | None = None  # DEFERRED_TAX_LIAB

    # 运营资金相关字段（新增）
    contract_assets: float | None = None  # 合同资产
    contract_liab: float | None = None  # 合同负债
    prepayment: float | None = None  # 预付款项（流动资产）
    adv_receipts: float | None = None  # 预收款项

    # 权益类 (Equity)
    total_equity: float | None = None  # TOTAL_EQUITY


@dataclass
class IncomeStatement:
    """利润表标准模型"""
    # 基础标识
    year: int
    security_code: str

    # 收入类 (Revenue)
    total_revenue: float | None = None  # TOTAL_OPERATE_INCOME
    operating_income: float | None = None  # OPERATE_INCOME

    # 成本费用类 (Costs & Expenses)
    total_operating_cost: float | None = None  # TOTAL_OPERATE_COST
    operating_cost: float | None = None  # OPERATE_COST
    sales_expense: float | None = None  # SALE_EXPENSE
    management_expense: float | None = None  # MANAGE_EXPENSE
    financial_expense: float | None = None  # FINANCE_EXPENSE
    research_expense: float | None = None  # RESEARCH_EXPENSE

    # 利润类 (Profit)
    gross_profit: float | None = None  # 计算: operating_income - operating_cost
    operating_profit: float | None = None  # OPERATE_PROFIT
    total_profit: float | None = None  # TOTAL_PROFIT
    net_profit: float | None = None  # NETPROFIT
    parent_net_profit: float | None = None  # PARENT_NETPROFIT
    ebit: float | None = None  # 计算: net_profit + income_tax + financial_expense

    # 其他
    income_tax: float | None = None  # INCOME_TAX
    non_operating_income: float | None = None  # NON_OPERATE_INCOME
    non_operating_cost: float | None = None  # NON_OPERATE_COST
    investment_income: float | None = None  # INVEST_INCOME
    asset_disposal_gain: float | None = None  # ASSET_DISPOSAL_GAIN
    other_profit: float | None = None  # OTHER_PROFIT

    # 每股指标
    weighted_roe: float | None = None  # WEIGHTED_AVG_ROE
    basic_eps: float | None = None  # BASIC_EPS
    diluted_eps: float | None = None  # DILUTED_EPS


@dataclass
class CashFlowStatement:
    """现金流量表标准模型"""
    # 基础标识
    year: int
    security_code: str

    # 现金流量
    operating_cash_flow: float | None = None  # NETCASH_OPERATE
    investing_cash_flow: float | None = None  # NETCASH_INVEST
    financing_cash_flow: float | None = None  # NETCASH_FINANCE
    free_cash_flow: float | None = None  # 计算: operating_cash_flow - investing_cash_flow

    # 细分项目
    capital_expenditure: float | None = None  # CONSTRUCT_LONG_ASSET
    cash_and_equivalents_end: float | None = None  # END_CCE
    cash_and_equivalents_begin: float | None = None  # BEGIN_CCE
    cash_received_from_sales: float | None = None  # CASH_SALES
    cash_paid_for_goods: float | None = None  # CASH_PURCHASE
    cash_paid_to_employees: float | None = None  # CASH_TO_STAFF
    taxes_paid: float | None = None  # TAXES_PAYMENT
    dividend_received: float | None = None  # DIVIDEND_INCOME
    debt_acquisition: float | None = None  # BORROW_RECEIVE
    bond_issuance: float | None = None  # BOND_ISSUE
    debt_repayment: float | None = None  # DEBT_REPAYMENT
    dividend_paid: float | None = None  # DIVIDEND_PAYMENT


@dataclass
class StandardFinancialData:
    """合并后的标准财务数据"""
    year: int
    security_code: str

    # 资产负债表字段
    total_assets: float | None = None
    total_liabilities: float | None = None
    total_equity: float | None = None
    current_assets: float | None = None
    non_current_assets: float | None = None
    current_liabilities: float | None = None
    non_current_liabilities: float | None = None
    cash_and_equivalents: float | None = None
    accounts_receivable: float | None = None
    inventory: float | None = None
    fixed_assets: float | None = None
    intangible_assets: float | None = None
    accounts_payable: float | None = None
    short_term_debt: float | None = None
    long_term_debt: float | None = None

    # 利润表字段
    total_revenue: float | None = None
    operating_income: float | None = None
    operating_cost: float | None = None
    gross_profit: float | None = None
    operating_profit: float | None = None
    total_profit: float | None = None
    net_profit: float | None = None
    parent_net_profit: float | None = None
    ebit: float | None = None
    income_tax: float | None = None
    research_expense: float | None = None
    sales_expense: float | None = None
    management_expense: float | None = None
    financial_expense: float | None = None

    # 现金流量表字段
    operating_cash_flow: float | None = None
    investing_cash_flow: float | None = None
    financing_cash_flow: float | None = None
    free_cash_flow: float | None = None
    capital_expenditure: float | None = None
    cash_and_equivalents_end: float | None = None

    # 原始字段（用于追溯审计）
    _original_columns: dict = field(default_factory=dict)
