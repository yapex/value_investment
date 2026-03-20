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

    # 短期借款（资产负债表科目），企业从银行或其他金融机构的短期借款
    # 单位：元
    # 注：Tushare st_borrow 字段映射到本字段
    SHORT_TERM_BORROWINGS = "short_term_borrowings"

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

    # 利息保障倍数 = 营业利润 / 利息支出
    # 单位：无（倍数）
    INTEREST_COVERAGE_RATIO = "interest_coverage_ratio"

    # ========== 利润表补充字段 ==========
    # 利息支出 = 借款利息、债券利息等财务费用
    # 单位：元
    INTEREST_EXPENSE = "interest_expense"

    # ========== Phase 3 偿债能力补充字段 ==========
    # 总债务 = 有息负债（短期借款 + 长期借款 + 应付债券）
    # 注意：在价值投资项目中，总债务 = interest_bearing_debt
    # 单位：元
    TOTAL_DEBT = "total_debt"

    # 自由现金流/债务 = 企业自由现金流 / 总债务
    # 单位：无（比例）
    FREE_CASH_FLOW_TO_DEBT = "free_cash_flow_to_debt"

    # ========== Phase 3.2 偿债能力补充指标（Calculator 计算） ==========
    # 债务/EBITDA = 总债务 / EBITDA
    # 单位：无（倍数）
    # 行业标准: < 3x 可接受, > 4x 需警惕
    DEBT_TO_EBITDA = "debt_to_ebitda"

    # 融资成本 = 财务费用率 / 有息负债
    # 单位：元（反映每元债务对应的财务费用）
    FINANCING_COST_RATE = "financing_cost_rate"

    # ========== Phase 3.4 组合信号指标（Calculator 计算） ==========
    # 现金流/净利润比 = 经营活动现金流 / 净利润
    # 单位：无（比例）
    # 健康公司通常 > 1（现金流利润 > 会计利润）
    # 排雷标准：应 > 0.8
    CASH_TO_NET_PROFIT_RATIO = "cash_to_net_profit_ratio"

    # ========== Phase 3.5 增长类指标（Calculator 计算） ==========
    # 存货同比增长率 = (本期存货 - 上期存货) / 上期存货
    # 单位：百分比（小数形式，如 0.2 表示 20%）
    INVENTORY_GROWTH_RATE = "inventory_growth_rate"

    # 应收账款同比增长率 = (本期应收 - 上期应收) / 上期应收
    # 单位：百分比（小数形式）
    ACCOUNTS_RECEIVABLE_GROWTH_RATE = "accounts_receivable_growth_rate"

    # 存货营收增速差 = 存货增长率 - 营收同比增长率
    # 单位：百分比（小数形式）
    # 正值：存货增速 > 营收增速 -> 积压风险
    # 负值：存货增速 < 营收增速 -> 健康信号
    INVENTORY_REVENUE_GROWTH_GAP = "inventory_revenue_growth_gap"

    # 应收营收增速差 = 应收增长率 - 营收同比增长率
    # 单位：百分比（小数形式）
    # 正值：应收增速 > 营收增速 -> 回款风险
    # 负值：应收增速 < 营收增速 -> 健康信号
    RECEIVABLE_REVENUE_GROWTH_GAP = "receivable_revenue_growth_gap"

    # ========== 利润表补充字段（来自 Provider） ==========
    # 主营业务收入 = 营业收入（区别于营业总收入）
    # 单位：元
    # 注：主营业务收入 + 其他业务收入 = 营业总收入
    MAIN_BUSINESS_INCOME = "main_business_income"

    # ========== Phase 3.6 业务结构类指标（Calculator 计算） ==========
    # 主营业务占比 = 主营业务收入 / 营业总收入
    # 单位：无（比例，0~1）
    # 接近 1 表示公司业务高度聚焦
    # 明显 < 1 表示存在较多非主营业务收入
    CORE_BUSINESS_RATIO = "core_business_ratio"

    # ========== Phase 4 盈利能力类指标（Calculator 计算） ==========
    # 净利率 = 净利润 / 营业收入
    # 单位：无（比例）
    # P1优先级，优秀公司通常 > 15%
    NET_MARGIN = "net_margin"

    # ========== Phase 4 偿债能力类指标（Calculator 计算） ==========
    # 现金短债比 = (货币资金) / 短期有息负债
    # 单位：无（比例）
    # P1优先级，>1 为安全
    CASH_SHORT_DEBT_RATIO = "cash_short_debt_ratio"

    # ========== Phase 4 营运能力类指标（Calculator 计算） ==========
    # 应收账款周转率 = 营业收入 / 平均应收账款
    # 单位：次/年
    # P2优先级，反映收账速度
    RECEIVABLES_TURNOVER = "receivables_turnover"

    # 总资产周转率 = 营业收入 / 平均总资产
    # 单位：次/年
    # P2优先级，反映资产利用效率
    TOTAL_ASSET_TURNOVER = "total_asset_turnover"

    # ========== Phase 3.4 组合信号指标补充字段 ==========
    # 利息收入 = 银行存款利息、债券利息等金融活动产生的收入
    # 单位：元
    # 注：来自 Tushare income 表的 int_income 字段
    INTEREST_INCOME = "interest_income"

    # ========== Phase 3.5 增长类补充指标（Calculator 计算） ==========
    # 利息收入率 = 利息收入 / 货币资金
    # 单位：无（比例）
    # 反映货币资金的利息回报率
    INTEREST_INCOME_RATE = "interest_income_rate"

    # ========== Phase 3.5 结构占比类指标（Calculator 计算） ==========
    # 预付款占比 = 预付款 / 总资产
    # 单位：无（比例）
    # 高预付款可能表示供应商议价能力强或存在资金占用
    PREPAYMENT_RATIO = "prepayment_ratio"

    # 资本开支营收比 = 资本开支 / 营业收入
    # 单位：无（比例）
    # 反映公司扩张程度，资本密集型公司通常 > 0.3
    CAPEX_TO_REVENUE_RATIO = "capex_to_revenue_ratio"

    # ========== Phase 3.7 偿债能力指标（Calculator 计算） ==========
    # 一年内到期债务占比 = (短期借款 + 一年内到期的非流动负债 + 应付债券) / 总负债
    # 单位：无（比例）
    # 反映短期债务压力，高占比可能存在再融资风险
    DEBT_DUE_WITHIN_1Y_RATIO = "debt_due_within_1y_ratio"

    # ========== Phase 3.8 增长指标（Calculator 计算） ==========
    # 营收复合增长率(5年) = (终值/初值)^(1/5) - 1
    # 单位：无（比例）
    # 衡量营业收入在5年期间的平均年增长率
    REVENUE_CAGR_5Y = "revenue_cagr_5y"

    # 净利润复合增长率(5年) = (终值/初值)^(1/5) - 1
    # 单位：无（比例）
    # 衡量净利润在5年期间的平均年增长率
    NET_PROFIT_CAGR_5Y = "net_profit_cagr_5y"

    # ========== Phase 3.9 稳定性/波动率指标（Calculator 计算） ==========
    # ROE波动率 = 标准差 / 均值
    # 单位：无（比例）
    # 衡量ROE的稳定性，低波动率表示盈利稳定
    ROE_VOLATILITY = "roe_volatility"

    # ========== 资产负债表补充字段 ==========
    # 一年内到期的非流动负债 = 长期负债中将在1年内到期部分
    # 单位：元
    # 注：来自 Tushare balance_sheet 表的 non_cur_liab_due_1y 字段
    NON_CURRENT_LIABILITIES_DUE_1Y = "non_current_liabilities_due_1y"

    # 应付债券 = 企业发行的债券
    # 单位：元
    BOND_PAYABLE = "bond_payable"

    # ========== Phase 3.8 增长指标（10年 CAGR） ==========
    # 营收复合增长率(10年) = (终值/初值)^(1/10) - 1
    # 单位：无（比例）
    # 衡量营业收入在10年期间的平均年增长率
    REVENUE_CAGR_10Y = "revenue_cagr_10y"

    # 净利润复合增长率(10年) = (终值/初值)^(1/10) - 1
    # 单位：无（比例）
    # 衡量净利润在10年期间的平均年增长率
    NET_PROFIT_CAGR_10Y = "net_profit_cagr_10y"

    # ========== Phase 3.4 组合信号指标（Calculator 计算） ==========
    # 其他应收款占比 = 其他应收款 / 总资产
    # 单位：无（比例）
    # 高占比可能表示资金被关联方占用（排雷指标）
    OTHER_RECEIVABLES_RATIO = "other_receivables_ratio"

    # 商誉净资产比 = 商誉 / 净资产
    # 单位：无（比例）
    # 高商誉可能存在减值风险（排雷指标）
    GOODWILL_TO_NET_ASSETS_RATIO = "goodwill_to_net_assets_ratio"

    # ========== Phase 3.5 结构占比指标（Calculator 计算） ==========
    # 长期投资占比 = 长期股权投资 / 总资产
    # 单位：无（比例）
    # 反映公司多元化程度和对外投资规模
    LONG_TERM_INVESTMENT_RATIO = "long_term_investment_ratio"

    # 营业外收入占比 = 营业外收入 / 利润总额
    # 单位：无（比例）
    # 高占比表示公司盈利质量不佳（排雷指标）
    NON_OPERATING_INCOME_RATIO = "non_operating_income_ratio"

    # ========== 资产负债表补充字段（来自 Provider） ==========
    # 其他应收款 = 暂付、押金、备用金等
    # 单位：元
    # 注：来自 Tushare balance_sheet 表的 other_recv 字段
    OTHER_RECEIVABLES = "other_receivables"

    # ========== 利润表补充字段（来自 Provider） ==========
    # 营业外收入 = 罚款收入、捐赠收入、无法支付的应付款等非主营业务收入
    # 单位：元
    # 注：来自 Tushare income 表的 non_op_income 字段
    NON_OPERATING_INCOME = "non_operating_income"

    # ========== 利润表补充字段（Phase 3 待确认） ==========
    # 公允价值变动损益 = 以公允价值计量且其变动计入当期损益的金融资产/负债的公允价值变动
    # 单位：元
    # 注：Tushare 字段名待确认
    FAIR_VALUE_CHANGE = "fair_value_change"

    # 投资收益 = 股权投资、债权投资等投资收益
    # 单位：元
    # 注：Tushare 字段名待确认
    INVESTMENT_INCOME = "investment_income"

    # ========== Phase 3.4 组合信号指标补充（Calculator 计算） ==========
    # 公允价值变动占比 = 公允价值变动损益 / 利润总额
    # 单位：无（比例）
    # 高占比可能表示非经常性损益较大
    FAIR_VALUE_CHANGE_RATIO = "fair_value_change_ratio"

    # 投资收益占比 = 投资收益 / 利润总额
    # 单位：无（比例）
    # 高占比表示公司盈利依赖投资活动
    INVESTMENT_INCOME_RATIO = "investment_income_ratio"

    # ========== Phase 3.5 结构占比指标（Calculator 计算） ==========
    # 主营业务占比 = 主营业务收入 / 营业总收入
    # 单位：无（比例）
    # 接近 1 表示公司业务高度聚焦
    # 明显 < 1 表示存在较多非主营业务收入
    CORE_BUSINESS_RATIO = "core_business_ratio"

    # ========== Phase 3.6 稳定性/波动率指标（Calculator 计算） ==========
    # 增长一致性 = 正增长年数 / 总年数
    # 单位：无（比例，0~1）
    # 衡量营收/利润增长稳定性
    GROWTH_CONSISTENCY = "growth_consistency"

    # 毛利率波动率 = 毛利率的标准差 / 均值
    # 单位：无（比例）
    # 衡量毛利率的稳定性
    GROSS_MARGIN_VOLATILITY = "gross_margin_volatility"

    # 现金流净利润波动率 = 现金流净利润比的标准差 / 均值
    # 单位：无（比例）
    # 衡量现金流与利润匹配度的稳定性
    CASH_TO_PROFIT_VOLATILITY = "cash_to_profit_volatility"

    # 资本开支稳定性 = 资本开支营收比的变异系数
    # 单位：无（比例）
    # 衡量资本开支的稳定性
    CAPEX_STABILITY = "capex_stability"

    # ========== Phase 3.7 危机期指标（Calculator 计算） ==========
    # 危机期CAGR = 危机期间的复合增长率
    # 单位：无（比例）
    # 衡量公司在危机期间的增长/衰退速度
    CRISIS_PERIOD_CAGR = "crisis_period_cagr"

    # 危机后恢复速度 = 危机后恢复到危机前水平所需的年数
    # 单位：年
    # 衡量公司从危机中恢复的能力
    POST_CRISIS_RECOVERY = "post_crisis_recovery"

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
