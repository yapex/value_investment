"""Field constants for pipeline

Structure:
1. IFRSFields - 国际标准字段 (硬编码，不依赖外部映射)
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
        # 收集所有大写常量对应的值
        return frozenset(
            v for k, v in vars(cls).items() 
            if k.isupper() and not k.startswith('_') and not callable(v)
        )


# 模块加载完成后冻结 IFRSFields
IFRSFields._frozen = True


# =============================================================================
# CustomFields - Agent 友好的字段定义
# =============================================================================


class CustomFields:
    """自定义字段 (Custom Calculated Fields)
    
    这些字段通过 Calculator 计算得出，不是直接从数据源获取。
    """
    
    # ========== 盈利能力类 ==========
    # 毛利率 = (营业收入 - 营业成本) / 营业收入 × 100%
    # 单位：百分比 (%)
    GROSS_MARGIN = "gross_margin"
    
    # 营业利润率 = 营业利润 / 营业收入 × 100%
    # 单位：百分比 (%)
    OPERATING_PROFIT_MARGIN = "operating_profit_margin"
    
    # 毛利润 = 营业收入 - 营业成本
    # 单位：元
    GROSS_PROFIT = "gross_profit"
    
    # ========== 营运能力类 ==========
    # 存货周转率 = 营业成本 / 平均存货
    # 单位：次/年
    INVENTORY_TURNOVER = "inventory_turnover"
    
    # ROIC = 税后净营业利润 / 投入资本 × 100%
    # 单位：百分比 (%)
    ROIC = "roic"
    
    # ========== 每股指标类 ==========
    # 流通市值 = 流通股本 × 股价
    # 单位：元
    CIRC_MARKET_CAP = "circ_market_cap"
    
    # 流通股本 = 总股本 - 限售股
    # 单位：股
    CIRC_SHARES = "circ_shares"
    
    # ========== 估值指标类 ==========
    # 隐含增长率 = 基于 DCF 模型反推的年增长率
    # 单位：百分比 (%)
    IMPLIED_GROWTH = "implied_growth"
    
    # ========== 资产负债表科目类 ==========
    # 商誉，企业合并时购买方支付的超过可辨认资产公允价值的溢价
    # 单位：元
    GOODWILL = "goodwill"
    
    # 无形资产，专利权、商标权、土地使用权等非实物资产
    # 单位：元
    INTANGIBLE_ASSETS = "intangible_assets"
    
    # 长期股权投资，对子公司、合营企业、联营企业的股权投资
    # 单位：元
    LONG_TERM_INVESTMENT = "long_term_investment"
    
    # 在建工程，正在建造尚未完工的固定资产
    # 单位：元
    CONSTRUCTION_IN_PROGRESS = "construction_in_progress"
    
    # 长期借款，一年以上到期的借款/债券
    # 单位：元
    LONG_TERM_DEBT = "long_term_debt"
    
    # 短期借款，一年内到期的借款/债券
    # 单位：元
    SHORT_TERM_DEBT = "short_term_debt"
    
    # 归属母公司净利润，合并报表中去除非控股子公司损益后的净利润
    # 单位：元
    PARENT_NET_PROFIT = "parent_net_profit"

    # ========== Phase 2 财务指标（来自 Tushare fina_indicator） ==========
    # 净债务 = 有息负债 - 货币资金
    # 单位：元
    NET_DEBT = "net_debt"

    # EBIT = 息税前利润
    # 单位：元
    EBIT = "ebit"

    # 企业自由现金流 = 息前税后利润 + 折旧摊销 - 资本开支 - 营运资本变动
    # 单位：元
    FREE_CASH_FLOW_TO_FIRM = "free_cash_flow_to_firm"

    # 股权自由现金流 = 企业自由现金流 - 利息费用 × (1 - 税率)
    # 单位：元
    FREE_CASH_FLOW_TO_EQUITY = "free_cash_flow_to_equity"

    # OCF/短期债务 = 经营活动现金流 / 短期借款
    # 单位：无（比例）
    OCF_TO_SHORT_DEBT = "ocf_to_short_debt"

    # 产权比率 = 负债合计 / 所有者权益合计
    # 单位：无（比例）
    DEBT_TO_EQUITY = "debt_to_equity"

    # 长期债务占比 = 长期借款 / 负债合计
    # 单位：百分比 (%)
    LONG_TERM_DEBT_RATIO = "long_term_debt_ratio"

    # 流动资产占比 = 流动资产 / 总资产
    # 单位：百分比 (%)
    CURRENT_ASSETS_RATIO = "current_assets_ratio"

    # 销售费用率 = 销售费用 / 营业收入
    # 单位：百分比 (%)
    SELLING_EXPENSE_RATIO = "selling_expense_ratio"

    # 管理费用率 = 管理费用 / 营业收入
    # 单位：百分比 (%)
    ADMIN_EXPENSE_RATIO = "admin_expense_ratio"

    # 财务费用率 = 财务费用 / 营业收入
    # 单位：百分比 (%)
    FINANCE_EXPENSE_RATIO = "finance_expense_ratio"

    # 总资产同比增长率
    # 单位：百分比 (%)
    TOTAL_ASSETS_YOY = "total_assets_yoy"

    # 净资产同比增长率
    # 单位：百分比 (%)
    EQUITY_YOY = "equity_yoy"

    # 经营活动现金流同比增长率
    # 单位：百分比 (%)
    OPERATING_CASH_FLOW_YOY = "operating_cash_flow_yoy"

    # ========== 财务指标类（来自 Tushare fina_indicator） ==========
    # 现金比率 = 货币资金 / 流动负债 × 100%
    # 单位：无（比例）
    CASH_RATIO = "cash_ratio"

    # 经营活动现金流/带息债务 = 经营活动现金流 / 带息债务
    # 单位：无（比例）
    OCF_TO_DEBT = "ocf_to_debt"

    # 带息债务 = 短期借款 + 长期借款 + 应付债券
    # 单位：元
    INTEREST_BEARING_DEBT = "interest_bearing_debt"

    # EBITDA = 息税折旧摊销前利润
    # 单位：元
    EBITDA = "ebitda"

    # 流动负债/总负债 = 流动负债 / 负债合计 × 100%
    # 单位：无（百分比）
    CURRENTDEBT_TO_DEBT = "currentdebt_to_debt"

    # 营业利润率 = 营业利润 / 营业收入 × 100%
    # 单位：百分比 (%)
    OPERATING_PROFIT_MARGIN_TS = "operating_profit_margin"

    # 营业收入同比增长率 = (本期营业收入 - 上期营业收入) / |上期营业收入| × 100%
    # 单位：百分比 (%)
    REVENUE_YOY = "revenue_yoy"

    # 净利润同比增长率 = (本期净利润 - 上期净利润) / |上期净利润| × 100%
    # 单位：百分比 (%)
    NET_PROFIT_YOY = "net_profit_yoy"

    # ========== Phase 3 财务指标（Calculator 计算） ==========
    # 净负债率 = 净债务 / 所有者权益
    # 单位：无（比例）
    # 净债务 = 有息负债 - 货币资金
    NET_DEBT_TO_EQUITY = "net_debt_to_equity"

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
