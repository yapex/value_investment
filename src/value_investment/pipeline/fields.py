"""Standard field constants for pipeline

Structure:
1. IFRSFields - 国际标准字段 (from CORE_FIELD_MAPPING)
2. CustomFields - 自定义字段 (system calculated fields)

Usage:
    from value_investment.pipeline.fields import IFRSFields, CustomFields

    class ROICCalculator:
        required_fields = {
            IFRSFields.NET_PROFIT,
            IFRSFields.TOTAL_EQUITY,
        }

Constraints:
    - IFRSFields 是冻结的，不允许添加新字段
    - 新字段必须添加到 CustomFields
    - 通过 test_ifrs_fields_lock.py 测试锁定
"""

from value_investment.data.mapper import CORE_FIELD_MAPPING


class IFRSFieldsMeta(type):
    """IFRSFields 元类，用于阻止动态添加新字段"""
    
    def __setattr__(cls, name, value):
        # 检查是否是尝试添加新的字段常量
        if (name.startswith('_') or name in ('all',)) and name != '_frozen':
            # 允许内部属性和方法
            super().__setattr__(name, value)
        elif name.isupper():
            # 大写名称是常量，冻结后不允许添加
            if getattr(cls, '_frozen', False):
                raise AttributeError(
                    f"IFRSFields 已冻结，禁止添加新字段 '{name}'。"
                    f"新字段必须添加到 CustomFields。"
                )
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)


class IFRSFields(metaclass=IFRSFieldsMeta):
    """国际标准字段 (IFRS Standard Fields)
    
    注意：此类在模块加载完成后会自动冻结，任何尝试添加新字段的操作都会失败。
    """
    
    # 冻结标记，模块加载完成后设为 True
    _frozen: bool = False
    
    # --- 资产负债表 (Balance Sheet) ---
    TOTAL_ASSETS = "total_assets"
    TOTAL_LIABILITIES = "total_liabilities"
    TOTAL_EQUITY = "total_equity"
    CURRENT_ASSETS = "current_assets"
    CURRENT_LIABILITIES = "current_liabilities"
    CASH_AND_EQUIVALENTS = "cash_and_equivalents"
    INVENTORY = "inventory"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    ACCOUNTS_PAYABLE = "accounts_payable"
    FIXED_ASSETS = "fixed_assets"
    PREPAYMENT = "prepayment"
    ADV_RECEIPTS = "adv_receipts"
    CONTRACT_ASSETS = "contract_assets"
    CONTRACT_LIAB = "contract_liab"

    # --- 利润表 (Income Statement) ---
    TOTAL_REVENUE = "total_revenue"
    NET_PROFIT = "net_profit"
    OPERATING_PROFIT = "operating_profit"
    OPERATING_COST = "operating_cost"

    # --- 现金流量表 (Cash Flow Statement) ---
    OPERATING_CASH_FLOW = "operating_cash_flow"
    INVESTING_CASH_FLOW = "investing_cash_flow"
    FINANCING_CASH_FLOW = "financing_cash_flow"
    CAPITAL_EXPENDITURE = "capital_expenditure"

    # --- 关键比率 (Key Ratios) ---
    ROE = "roe"
    ROA = "roa"
    GROSS_MARGIN = "gross_margin"
    NET_PROFIT_MARGIN = "net_profit_margin"
    CURRENT_RATIO = "current_ratio"
    QUICK_RATIO = "quick_ratio"
    DEBT_RATIO = "debt_ratio"
    ASSET_TURNOVER = "asset_turnover"
    RECEIVABLE_TURNOVER = "receivable_turnover"

    # --- 市场数据 (Market Data) ---
    MARKET_CAP = "market_cap"
    TOTAL_SHARES = "total_shares"
    PE_RATIO = "pe_ratio"
    PB_RATIO = "pb_ratio"
    BASIC_EPS = "basic_eps"
    DILUTED_EPS = "diluted_eps"
    BOOK_VALUE_PER_SHARE = "book_value_per_share"

    @classmethod
    def all(cls) -> frozenset:
        """Get all IFRS fields as a set"""
        return frozenset(CORE_FIELD_MAPPING.keys())


# 模块加载完成后冻结 IFRSFields
IFRSFields._frozen = True


class CustomFields:
    """自定义字段 (Custom Calculated Fields)
    
    这些字段通过 Calculator 计算得出，不是直接从数据源获取。
    命名规范：使用 snake_case，清晰描述计算逻辑。
    """
    
    # === 利润率指标 (Profit Margins) ===
    OPERATING_PROFIT_MARGIN = "operating_profit_margin"  # 营业利润率 = 营业利润 / 营业收入
    GROSS_PROFIT = "gross_profit"  # 毛利润 = 营业收入 - 营业成本
    INVENTORY_TURNOVER = "inventory_turnover"  # 存货周转率 = 营业成本 / 平均存货
    
    @classmethod
    def all(cls) -> frozenset:
        """Get all custom fields as a set"""
        return frozenset(
            v for k, v in vars(cls).items() if k.isupper() and not callable(v)
        )


# All valid fields for calculators
ALL_FIELDS = IFRSFields.all() | CustomFields.all()


def validate_fields(calculator_cls) -> None:
    """Validate calculator's required_fields are all valid fields

    Raises:
        ValueError: If any field is not in ALL_FIELDS
    """
    for field in calculator_cls.required_fields:
        if field not in ALL_FIELDS:
            raise ValueError(
                f"Calculator {calculator_cls.__name__} uses invalid field: {field}. "
                f"Valid fields: {sorted(ALL_FIELDS)}"
            )
