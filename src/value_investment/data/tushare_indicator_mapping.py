# Tushare fina_indicator 字段映射
# 来源: https://tushare.pro/document/2?doc_id=79
# 格式: Tushare字段 -> 标准字段名

# ============================================================================
# Tushare A 股财务指标映射 (137 个字段)
# ============================================================================
# 设计原则:
# - 优先使用 Tushare 字段名作为标准 (因为数据来自 Tushare)
# - 与现有 IFRS 标准一致的字段保持不变
# - 我们特有的字段 (带 hk_/us_ 前缀) 保留
# ============================================================================

TUSHARE_FINANCIAL_INDICATOR_MAPPING = {
    # ----- 每股指标 (Per Share) -----
    'eps': 'basic_eps',                    # 基本每股收益
    'dt_eps': 'diluted_eps',               # 稀释每股收益
    'total_revenue_ps': 'total_revenue_per_share',    # 每股营业总收入
    'revenue_ps': 'revenue_per_share',     # 每股营业收入
    'capital_rese_ps': 'capital_reserve_per_share',   # 每股资本公积
    'surplus_rese_ps': 'surplus_reserve_per_share',   # 每股盈余公积
    'undist_profit_ps': 'undistributed_profit_per_share',  # 每股未分配利润
    'extra_item': 'extraordinary_item',    # 非经常性损益
    'profit_dedt': 'deducted_net_profit',  # 扣非净利润
    'bps': 'book_value_per_share',         # 每股净资产
    'ocfps': 'operating_cash_flow_per_share',  # 每股经营活动现金流
    'cfps': 'cash_flow_per_share',         # 每股现金流量净额
    'retainedps': 'retained_earnings_per_share',  # 每股留存收益
    'ebit_ps': 'ebit_per_share',           # 每股息税前利润
    'fcff_ps': 'fcff_per_share',           # 每股企业自由现金流
    'fcfe_ps': 'fcfe_per_share',           # 每股股东自由现金流
    'diluted2_eps': 'diluted_eps_2',      # 期末摊薄每股收益

    # ----- 盈利能力 (Profitability) -----
    'gross_margin': 'gross_profit_margin', # 销售毛利率
    'netprofit_margin': 'net_profit_margin',  # 销售净利率
    'cogs_of_sales': 'cost_of_sales_ratio',  # 销售成本率
    'expense_of_sales': 'sales_expense_ratio',  # 销售期间费用率
    'profit_to_gr': 'profit_to_gross_revenue',  # 净利润/营业总收入
    'saleexp_to_gr': 'sales_expense_to_gr',  # 销售费用/营业总收入
    'adminexp_of_gr': 'admin_expense_to_gr',  # 管理费用/营业总收入
    'finaexp_of_gr': 'financial_expense_to_gr',  # 财务费用/营业总收入
    'impai_ttm': 'impairment_to_gr',       # 资产减值损失/营业总收入
    'gc_of_gr': 'total_cost_to_gr',        # 营业总成本/营业总收入
    'op_of_gr': 'operating_profit_to_gr',  # 营业利润/营业总收入
    'ebit_of_gr': 'ebit_to_gr',            # 息税前利润/营业总收入
    'roe': 'roe',                          # 净资产收益率
    'roe_waa': 'roe_weighted_avg',        # 加权平均净资产收益率
    'roe_dt': 'roe_diluted',               # 净资产收益率(扣除非经常损益)
    'roa': 'roa',                          # 总资产报酬率
    'npta': 'net_profit_to_assets',        # 总资产净利润
    'roic': 'roic',                        # 投入资本回报率
    'roe_yearly': 'roe_yearly',            # 年化净资产收益率
    'roa2_yearly': 'roa_yearly_2',        # 年化总资产报酬率
    'roe_avg': 'roe_avg',                  # 平均净资产收益率

    # ----- 偿债能力 (Solvency) -----
    'current_ratio': 'current_ratio',      # 流动比率
    'quick_ratio': 'quick_ratio',          # 速动比率
    'cash_ratio': 'cash_ratio',            # 保守速动比率
    'debt_to_assets': 'debt_ratio',        # 资产负债率
    'assets_to_eqt': 'equity_multiplier',  # 权益乘数
    'dp_assets_to_eqt': 'equity_multiplier_dupont',  # 权益乘数(杜邦)
    'ca_to_assets': 'current_assets_ratio',  # 流动资产/总资产
    'nca_to_assets': 'non_current_assets_ratio',  # 非流动资产/总资产
    'tbassets_to_totalassets': 'tangible_assets_ratio',  # 有形资产/总资产
    'int_to_talcap': 'interest_debt_to_capital',  # 带息债务/全部投入资本
    'eqt_to_talcapital': 'equity_to_capital',  # 归属于母公司的股东权益/全部投入资本
    'currentdebt_to_debt': 'current_debt_ratio',  # 流动负债/负债合计
    'longdeb_to_debt': 'long_term_debt_ratio',  # 非流动负债/负债合计
    'ocf_to_shortdebt': 'ocf_to_current_debt',  # 经营现金流/流动负债
    'debt_to_eqt': 'debt_to_equity',       # 产权比率
    'eqt_to_debt': 'equity_to_debt',       # 归属于母公司的股东权益/负债合计
    'eqt_to_interestdebt': 'equity_to_interest_debt',  # 归属于母公司的股东权益/带息债务
    'tangibleasset_to_debt': 'tangible_asset_to_debt',  # 有形资产/负债合计
    'tangasset_to_intdebt': 'tangible_asset_to_interest_debt',  # 有形资产/带息债务
    'tangibleasset_to_netdebt': 'tangible_asset_to_net_debt',  # 有形资产/净债务
    'ocf_to_debt': 'ocf_to_debt',          # 经营现金流/负债合计
    'ocf_to_interestdebt': 'ocf_to_interest_debt',  # 经营现金流/带息债务
    'ocf_to_netdebt': 'ocf_to_net_debt',   # 经营现金流/净债务
    'ebit_to_interest': 'ebit_to_interest',  # 已获利息倍数
    'longdebt_to_workingcapital': 'long_debt_to_working_capital',  # 长期债务与营运资金比率
    'ebitda_to_debt': 'ebitda_to_debt',    # 息税折旧摊销前利润/负债合计

    # ----- 营运效率 (Efficiency) -----
    'invturn_days': 'inventory_turnover_days',  # 存货周转天数
    'arturn_days': 'receivables_turnover_days',  # 应收账款周转天数
    'inv_turn': 'inventory_turnover',       # 存货周转率
    'ar_turn': 'receivables_turnover',      # 应收账款周转率
    'ca_turn': 'current_assets_turnover',   # 流动资产周转率
    'fa_turn': 'fixed_assets_turnover',     # 固定资产周转率
    'assets_turn': 'total_assets_turnover', # 总资产周转率
    'turn_days': 'operating_cycle_days',     # 营业周期
    'total_fa_trun': 'fixed_assets_total_turnover',  # 固定资产合计周转率

    # ----- 现金流 (Cash Flow) -----
    'op_income': 'operating_income',        # 经营活动净收益
    'valuechange_income': 'value_change_income',  # 价值变动净收益
    'interst_income': 'interest_expense',   # 利息费用
    'daa': 'depreciation_amortization',     # 折旧与摊销
    'ebit': 'ebit',                         # 息税前利润
    'ebitda': 'ebitda',                     # 息税折旧摊销前利润
    'fcff': 'fcff',                         # 企业自由现金流
    'fcfe': 'fcfe',                         # 股权自由现金流
    'current_exint': 'interest_free_current_liabilities',  # 无息流动负债
    'noncurrent_exint': 'interest_free_non_current_liabilities',  # 无息非流动负债
    'interestdebt': 'interest_bearing_debt',  # 带息债务
    'netdebt': 'net_debt',                  # 净债务
    'tangible_asset': 'tangible_assets',     # 有形资产
    'working_capital': 'working_capital',   # 营运资金
    'networking_capital': 'net_working_capital',  # 营运流动资本
    'invest_capital': 'invested_capital',   # 全部投入资本
    'retained_earnings': 'retained_earnings',  # 留存收益
    'fixed_assets': 'fixed_assets',         # 固定资产合计

    # ----- 现金流比率 (Cash Flow Ratios) -----
    'opincome_of_ebt': 'operating_income_to_ebt',  # 经营活动净收益/利润总额
    'investincome_of_ebt': 'investment_income_to_ebt',  # 价值变动净收益/利润总额
    'n_op_profit_of_ebt': 'non_operating_profit_to_ebt',  # 营业外收支净额/利润总额
    'tax_to_ebt': 'tax_to_ebt',             # 所得税/利润总额
    'dtprofit_to_profit': 'deducted_profit_to_profit',  # 扣除非经常损益后的净利润/净利润
    'salescash_to_or': 'sales_cash_to_operating_revenue',  # 销售商品提供劳务收到的现金/营业收入
    'ocf_to_or': 'ocf_to_operating_revenue',  # 经营现金流/营业收入
    'ocf_to_opincome': 'ocf_to_operating_income',  # 经营现金流/经营活动净收益
    'capitalized_to_da': 'capitalized_to_da',  # 资本支出/折旧和摊销

    # ----- 利润分析 (Profit Analysis) -----
    'profit_prefin_exp': 'profit_before_financial_expense',  # 扣除财务费用前营业利润
    'non_op_profit': 'non_operating_profit',  # 非营业利润
    'op_to_ebt': 'operating_profit_to_ebt',  # 营业利润／利润总额
    'nop_to_ebt': 'non_operating_profit_to_ebt',  # 非营业利润／利润总额
    'ocf_to_profit': 'ocf_to_profit',        # 经营现金流／营业利润
    'cash_to_liqdebt': 'cash_to_current_liabilities',  # 货币资金／流动负债
    'cash_to_liqdebt_withinterest': 'cash_to_interest_bearing_liabilities',  # 货币资金／带息流动负债
    'op_to_liqdebt': 'operating_profit_to_current_liabilities',  # 营业利润／流动负债
    'op_to_debt': 'operating_profit_to_debt',  # 营业利润／负债合计
    'roic_yearly': 'roic_yearly',            # 年化投入资本回报率
    'profit_to_op': 'profit_to_operating_revenue',  # 利润总额／营业收入

    # ----- 单季度指标 (Quarterly) -----
    'q_opincome': 'q_operating_income',      # 经营活动单季度净收益
    'q_investincome': 'q_investment_income',  # 价值变动单季度净收益
    'q_dtprofit': 'q_deducted_net_profit',   # 扣除非经常损益后的单季度净利润
    'q_eps': 'q_basic_eps',                  # 每股收益(单季度)
    'q_netprofit_margin': 'q_net_profit_margin',  # 销售净利率(单季度)
    'q_gsprofit_margin': 'q_gross_profit_margin',  # 销售毛利率(单季度)
    'q_exp_to_sales': 'q_expense_to_sales',  # 销售期间费用率(单季度)
    'q_profit_to_gr': 'q_profit_to_gross_revenue',  # 净利润／营业总收入(单季度)
    'q_saleexp_to_gr': 'q_sales_expense_to_gr',  # 销售费用／营业总收入 (单季度)
    'q_adminexp_to_gr': 'q_admin_expense_to_gr',  # 管理费用／营业总收入 (单季度)
    'q_finaexp_to_gr': 'q_financial_expense_to_gr',  # 财务费用／营业总收入 (单季度)
    'q_impair_to_gr_ttm': 'q_impairment_to_gr',  # 资产减值损失／营业总收入(单季度)
    'q_gc_to_gr': 'q_total_cost_to_gr',     # 营业总成本／营业总收入 (单季度)
    'q_op_to_gr': 'q_operating_profit_to_gr',  # 营业利润／营业总收入(单季度)
    'q_roe': 'q_roe',                        # 净资产收益率(单季度)
    'q_dt_roe': 'q_roe_diluted',             # 净资产单季度收益率(扣除非经常损益)
    'q_npta': 'q_net_profit_to_assets',      # 总资产净利润(单季度)
    'q_opincome_to_ebt': 'q_operating_income_to_ebt',  # 经营活动净收益／利润总额(单季度)
    'q_investincome_to_ebt': 'q_investment_income_to_ebt',  # 价值变动净收益／利润总额(单季度)
    'q_dtprofit_to_profit': 'q_deducted_profit_to_profit',  # 扣除非经常损益后的净利润／净利润(单季度)
    'q_salescash_to_or': 'q_sales_cash_to_revenue',  # 销售商品提供劳务收到的现金／营业收入(单季度)
    'q_ocf_to_sales': 'q_ocf_to_sales',      # 经营现金流／营业收入(单季度)
    'q_ocf_to_or': 'q_ocf_to_revenue',       # 经营现金流／营业收入(单季度)

    # ----- 增长指标 (Growth) -----
    'basic_eps_yoy': 'basic_eps_yoy',        # 基本每股收益同比增长率
    'dt_eps_yoy': 'diluted_eps_yoy',         # 稀释每股收益同比增长率
    'cfps_yoy': 'cfps_yoy',                  # 每股经营现金流同比增长率
    'op_yoy': 'operating_profit_yoy',        # 营业利润同比增长率
    'ebt_yoy': 'ebt_yoy',                    # 利润总额同比增长率
    'netprofit_yoy': 'net_profit_yoy',        # 归属母公司股东的净利润同比增长率
    'dt_netprofit_yoy': 'deducted_net_profit_yoy',  # 归属母公司股东的净利润-扣除非经常损益同比增长率
    'ocf_yoy': 'ocf_yoy',                    # 经营现金流同比增长率
    'roe_yoy': 'roe_yoy',                    # 净资产收益率(摊薄)同比增长率
    'bps_yoy': 'bps_yoy',                    # 每股净资产相对年初增长率
    'assets_yoy': 'total_assets_yoy',        # 资产总计相对年初增长率
    'eqt_yoy': 'equity_yoy',                 # 归属母公司的股东权益相对年初增长率
    'tr_yoy': 'total_revenue_yoy',          # 营业总收入同比增长率
    'or_yoy': 'operating_revenue_yoy',       # 营业收入同比增长率
    'q_gr_yoy': 'q_gross_revenue_yoy',       # 营业总收入同比增长率(单季度)
    'q_gr_qoq': 'q_gross_revenue_qoq',      # 营业总收入环比增长率(单季度)
    'q_sales_yoy': 'q_revenue_yoy',          # 营业收入同比增长率(单季度)
    'q_sales_qoq': 'q_revenue_qoq',          # 营业收入环比增长率(单季度)
    'q_op_yoy': 'q_operating_profit_yoy',     # 营业利润同比增长率(单季度)
    'q_op_qoq': 'q_operating_profit_qoq',     # 营业利润环比增长率(单季度)
    'q_profit_yoy': 'q_profit_yoy',          # 净利润同比增长率(单季度)
    'q_profit_qoq': 'q_profit_qoq',          # 净利润环比增长率(单季度)
    'q_netprofit_yoy': 'q_net_profit_yoy',   # 归属母公司股东的净利润同比增长率(单季度)
    'q_netprofit_qoq': 'q_net_profit_qoq',   # 归属母公司股东的净利润环比增长率(单季度)
    'equity_yoy': 'equity_yoy',              # 净资产同比增长率
    'rd_exp': 'rd_expense',                  # 研发费用

    # ----- 其他 -----
    'update_flag': 'update_flag',            # 更新标识
}
