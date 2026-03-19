"""Standard field constants for pipeline

Structure:
1. IFRSFields - 国际标准字段 (from CORE_FIELD_MAPPING)
2. CustomFields - 自定义字段 (system calculated fields)

Usage:
    from value_investment.domain.fields import IFRSFields, CustomFields

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

# TODO (Task 7): Update import to value_investment.mapper after restructuring
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


# =============================================================================
# CustomFields - Agent 友好的字段定义
# =============================================================================
# 
# 字段分类：
# 1. 盈利能力 (Profitability) - 评估公司赚钱能力
# 2. 估值指标 (Valuation) - 评估股价贵贱
# 3. 成长性 (Growth) - 评估业绩增长
# 4. 财务健康 (Financial Health) - 评估风险
# 5. 市场特有 (Market Specific) - 各市场特有指标
#
# Agent 使用指南：
# - 盈利能力分析：roe, roa, gross_margin, net_profit_margin, operating_profit_margin
# - 估值分析：pe_ratio, pb_ratio, market_cap
# - 成长性分析：implied_growth, revenue_growth
# - 财务健康：debt_ratio, current_ratio
#
# =============================================================================


class CustomFields:
    """自定义字段 (Custom Calculated Fields)
    
    这些字段通过 Calculator 计算得出，不是直接从数据源获取。
    Agent 使用这些字段进行财务分析时，应参考【使用场景】和【组合建议】。
    """
    
    # =========================================================================
    # 盈利能力指标 (Profitability)
    # 使用场景：筛选高盈利企业，对比同行业盈利能力
    # =========================================================================
    
    # 毛利率 = (营业收入 - 营业成本) / 营业收入 × 100%
    # 单位：百分比 (%)
    # 解读：茅台 90%+，制造业 20-40%，越高越强但需考虑行业差异
    GROSS_MARGIN = "gross_margin"
    
    # 营业利润率 = 营业利润 / 营业收入 × 100%
    # 单位：百分比 (%)
    # 解读：反映主营业务盈利能力，剔除非经常性损益
    OPERATING_PROFIT_MARGIN = "operating_profit_margin"
    
    # 毛利润 = 营业收入 - 营业成本
    # 单位：元
    # 解读：绝对值，适合比较同行业不同规模公司
    GROSS_PROFIT = "gross_profit"
    
    # 存货周转率 = 营业成本 / 平均存货
    # 单位：次/年
    # 解读：越高表示存货变现越快，消费行业重要指标
    INVENTORY_TURNOVER = "inventory_turnover"
    
    # =========================================================================
    # 投资回报指标 (Investment Returns)
    # 使用场景：评估资本配置效率，筛选高质量企业
    # =========================================================================
    
    # ROIC = 税后净营业利润 / 投资资本 × 100%
    # 单位：百分比 (%)
    # 解读：>WACC(通常10%) 为创造价值，>15% 为优秀，<8% 需谨慎
    # 组合：常与 roe、wacc 一起分析
    ROIC = "roic"
    
    # =========================================================================
    # 市场特有指标 (Market Specific)
    # 使用场景：A 股特有，限售股导致市值计算差异
    # =========================================================================
    
    # 流通市值 = 股价 × 流通股本
    # 单位：元
    # 解读：A 股部分股票有国家队/国有法人持股，流通市值更反映实际可交易价值
    CIRC_MARKET_CAP = "circ_market_cap"
    
    # 流通股本 = 总股本 - 限售股
    # 单位：股
    # 解读：衡量可在二级市场交易的股份数量
    CIRC_SHARES = "circ_shares"
    
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
