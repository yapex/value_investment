"""Data mapper for converting A股 fields to IFRS standard fields"""
from typing import Any

import pandas as pd

# ============================================================================
# 核心财务字段映射 (Core Field Mapping) - 唯一数据源
# ============================================================================
# 结构：标准字段名 → {市场: 市场字段名}
# 用途：统一管理 A股/港股/美股 的字段映射

CORE_FIELD_MAPPING: dict[str, dict[str, str]] = {
    # ----- 利润表 (Income Statement) -----
    "total_revenue": {
        "A股": "营业总收入",
        "港股": "收益",
        "美股": "totalRevenue",
    },
    "net_profit": {
        "A股": "净利润",
        "港股": "期内溢利",
        "美股": "netIncome",
    },
    "operating_profit": {
        "A股": "营业利润",
        "港股": "营业溢利",
        "美股": "operatingIncome",
    },
    "gross_profit": {
        "A股": "毛利",
        "港股": "毛利",
        "美股": "grossProfit",
    },
    "operating_cost": {
        "A股": "营业成本",
        "港股": "已售存货成本",
        "美股": "costOfRevenue",
    },

    # ----- 资产负债表 (Balance Sheet) -----
    "total_assets": {
        "A股": "资产总计",
        "港股": "资产总值",
        "美股": "totalAssets",
    },
    "total_equity": {
        "A股": "股东权益合计",
        "港股": "权益总额",
        "美股": "totalStockholdersEquity",
    },
    "total_liabilities": {
        "A股": "负债合计",
        "港股": "总负债",
        "美股": "totalLiabilities",
    },
    "current_assets": {
        "A股": "流动资产合计",
        "港股": "流动资产合计",
        "美股": "totalCurrentAssets",
    },
    "current_liabilities": {
        "A股": "流动负债合计",
        "港股": "流动负债合计",
        "美股": "totalCurrentLiabilities",
    },
    "cash_and_equivalents": {
        "A股": "货币资金",
        "港股": "现金及等价物",
        "美股": "cashAndCashEquivalents",
    },
    "inventory": {
        "A股": "存货",
        "港股": "存货",
        "美股": "inventory",
    },
    "accounts_receivable": {
        "A股": "应收账款",
        "港股": "应收帐款",
        "美股": "accountsReceivable",
    },
    "fixed_assets": {
        "A股": "固定资产",
        "港股": "固定资产",
        "美股": "propertyPlantEquipment",
    },

    # ----- 现金流量表 (Cash Flow Statement) -----
    "operating_cash_flow": {
        "A股": "经营活动产生的现金流量净额",
        "港股": "经营业务现金净额",
        "美股": "operatingCashFlow",
    },
    "investing_cash_flow": {
        "A股": "投资活动产生的现金流量净额",
        "港股": "投资业务现金净额",
        "美股": "investingCashFlow",
    },
    "financing_cash_flow": {
        "A股": "筹资活动产生的现金流量净额",
        "港股": "融资业务现金净额",
        "美股": "financingCashFlow",
    },
    "capital_expenditure": {
        "A股": "购建固定资产支付的现金",
        "港股": "购建固定资产",
        "美股": "capitalExpenditure",
    },

    # ----- 每股指标 (Per Share Metrics) -----
    "basic_eps": {
        "A股": "基本每股收益",
        "港股": "基本每股收益(元)",
        "美股": "basicEps",
    },
    "diluted_eps": {
        "A股": "稀释每股收益",
        "港股": "稀释每股收益(元)",
        "美股": "dilutedEps",
    },
    "book_value_per_share": {
        "A股": "每股净资产",
        "港股": "每股净资产(元)",
        "美股": "bookValuePerShare",
    },

    # ----- 估值指标 (Valuation Metrics) -----
    "pe_ratio": {
        "A股": "市盈率",
        "港股": "市盈率",
        "美股": "peRatio",
    },
    "pb_ratio": {
        "A股": "市净率",
        "港股": "市净率",
        "美股": "pbRatio",
    },
    "market_cap": {
        "A股": "总市值(元)",
        "港股": "总市值(港元)",
        "美股": "总市值(美元)",
    },

    # ----- 盈利能力指标 (Profitability Metrics) -----
    "roe": {
        "A股": "净资产收益率(%)",
        "港股": "股东权益回报率(%)",
        "美股": "returnOnEquity",
    },
    "roa": {
        "A股": "总资产收益率(%)",
        "港股": "总资产回报率(%)",
        "美股": "returnOnAssets",
    },
    "gross_margin": {
        "A股": "gross_profit_margin",
        "港股": "毛利率",
        "美股": "grossMargin",
    },
    "net_profit_margin": {
        "A股": "销售净利率",
        "港股": "销售净利率(%)",
        "美股": "netProfitMargin",
    },

    # ----- 流动性指标 (Liquidity Metrics) -----
    "current_ratio": {
        "A股": "流动比率",
        "港股": "流动比率",
        "美股": "currentRatio",
    },
    "quick_ratio": {
        "A股": "速动比率",
        "港股": "速动比率",
        "美股": "quickRatio",
    },

    # ----- 杠杆指标 (Leverage Metrics) -----
    "debt_ratio": {
        "A股": "资产负债率(%)",
        "港股": "资产负债率",
        "美股": "debtToAssetsRatio",
    },

    # ----- 效率指标 (Efficiency Metrics) -----
    "asset_turnover": {
        "A股": "总资产周转率(次)",
        "港股": "总资产周转率",
        "美股": "assetTurnover",
    },
    "inventory_turnover": {
        "A股": "存货周转率(次)",
        "港股": "存货周转率",
        "美股": "inventoryTurnover",
    },
    "receivable_turnover": {
        "A股": "应收账款周转率(次)",
        "港股": "应收账款周转率",
        "美股": "receivablesTurnover",
    },

    # ----- 股本指标 (Share Capital) -----
    "total_shares": {
        "A股": "总股本",
        "港股": "已发行股本(股)",
        "美股": "sharesOutstanding",
    },
}


# ============================================================================
# 反向索引：市场字段 → 标准字段 (自动生成)
# ============================================================================
_REVERSE_FIELD_INDEX: dict[str, dict[str, str]] = {}


def _build_reverse_index() -> None:
    """构建反向索引：市场字段名 → 标准字段名"""
    global _REVERSE_FIELD_INDEX

    for market in ["A股", "港股", "美股"]:
        _REVERSE_FIELD_INDEX[market] = {}

    for standard_field, market_map in CORE_FIELD_MAPPING.items():
        for market, market_field in market_map.items():
            if market in _REVERSE_FIELD_INDEX:
                _REVERSE_FIELD_INDEX[market][market_field] = standard_field


# 模块加载时构建索引
_build_reverse_index()


# ============================================================================
# 财务指标映射 (Financial Indicator Mapping)
# 分层结构: IFRS标准字段 (通用) + Custom字段 (按市场)
#
# 命名规范:
# - IFRS标准字段: 纯英文 (如 net_profit, total_revenue)
# - 市场特有字段: 带市场前缀 (如 a_market_cap, hk_market_cap, us_market_cap)
# ============================================================================

FINANCIAL_INDICATOR_MAPPING = {
    # ----- IFRS标准字段 (通用) -----
    # 利润表
    '净利润': 'net_profit',
    'NETPROFIT': 'net_profit',
    '扣非净利润': 'deducted_net_profit',
    '营业总收入': 'total_revenue',
    'TOTAL_OPERATE_INCOME': 'total_revenue',
    '经营溢利': 'operating_profit',  # 港股
    '毛利': 'gross_profit',  # 港股
    '除税前溢利': 'profit_before_tax',  # 港股
    '除税后溢利': 'profit_after_tax',  # 港股
    '股东应占溢利': 'parent_net_profit',  # 港股
    '期内溢利': 'net_profit',  # 港股

    # 现金流量
    '经营业务现金净额': 'operating_cash_flow',  # 港股
    'NETCASH_OPERATE': 'operating_cash_flow',

    # 每股指标
    '基本每股收益': 'basic_eps',
    'BASIC_EPS': 'basic_eps',
    '基本每股收益(元)': 'basic_eps',  # 港股
    '每股净资产': 'book_value_per_share',
    '每股经营现金流': 'operating_cash_flow_per_share',
    '每股经营现金流(元)': 'operating_cash_flow_per_share',  # 港股
    '每股股息TTM(港元)': 'hk_dividend_per_share',  # 港股

    # 比率指标
    '净资产收益率': 'roe',
    '净资产收益率-摊薄': 'roe_diluted',
    'WEIGHTED_AVG_ROE': 'roe',
    '股东权益回报率(%)': 'roe',  # 港股
    '销售净利率': 'net_profit_margin',
    '销售净利率(%)': 'net_profit_margin',  # 港股
    '销售毛利率': 'gross_profit_margin',
    '总资产回报率(%)': 'roa',  # 港股

    # 股本指标
    '已发行股本(股)': 'total_shares',
    '法定股本(股)': 'hk_legal_shares',  # 港股

    # 估值指标
    '市盈率': 'pe_ratio',
    '市净率': 'pb_ratio',

    # 港股特有扩展字段 (带 hk_ 前缀)
    # 注意：市值字段只在 Custom 部分映射，避免重复
    '营业总收入滚动环比增长(%)': 'hk_total_revenue_growth_qoq',
    '净利润滚动环比增长(%)': 'hk_net_profit_growth_qoq',
    '派息比率(%)': 'hk_dividend_payout_ratio',
    '股息率TTM(%)': 'hk_dividend_yield_ttm',

    # ----- Custom字段 (按市场, 带市场前缀) -----
    # 注意：A 股财务指标优先使用 Tushare (fina_indicator 接口)
    'A': {
        # 市值字段
        '总市值(元)': 'a_market_cap',
        '总市值(人民币)': 'a_market_cap',

        # ----- Tushare A 股财务指标 (fina_indicator) -----
        # 每股指标
        'eps': 'basic_eps',
        'dt_eps': 'diluted_eps',
        'total_revenue_ps': 'total_revenue_per_share',
        'revenue_ps': 'revenue_per_share',
        'capital_rese_ps': 'capital_reserve_per_share',
        'surplus_rese_ps': 'surplus_reserve_per_share',
        'undist_profit_ps': 'undistributed_profit_per_share',
        'extra_item': 'extraordinary_item',
        'profit_dedt': 'deducted_net_profit',
        'bps': 'book_value_per_share',
        'ocfps': 'operating_cash_flow_per_share',
        'cfps': 'cash_flow_per_share',
        'retainedps': 'retained_earnings_per_share',
        'ebit_ps': 'ebit_per_share',
        'fcff_ps': 'fcff_per_share',
        'fcfe_ps': 'fcfe_per_share',
        'diluted2_eps': 'diluted_eps_2',

        # 盈利能力
        'gross_margin': 'gross_profit_margin',
        'netprofit_margin': 'net_profit_margin',
        'cogs_of_sales': 'cost_of_sales_ratio',
        'expense_of_sales': 'sales_expense_ratio',
        'profit_to_gr': 'profit_to_gross_revenue',
        'saleexp_to_gr': 'sales_expense_to_gr',
        'adminexp_of_gr': 'admin_expense_to_gr',
        'finaexp_of_gr': 'financial_expense_to_gr',
        'impai_ttm': 'impairment_to_gr',
        'gc_of_gr': 'total_cost_to_gr',
        'op_of_gr': 'operating_profit_to_gr',
        'ebit_of_gr': 'ebit_to_gr',
        'roe': 'roe',
        'roe_waa': 'roe_weighted_avg',
        'roe_dt': 'roe_diluted',
        'roa': 'roa',
        'npta': 'net_profit_to_assets',
        'roic': 'roic',
        'roe_yearly': 'roe_yearly',
        'roa2_yearly': 'roa_yearly_2',
        'roe_avg': 'roe_avg',

        # 偿债能力
        'current_ratio': 'current_ratio',
        'quick_ratio': 'quick_ratio',
        'cash_ratio': 'cash_ratio',
        'debt_to_assets': 'debt_ratio',
        'assets_to_eqt': 'equity_multiplier',
        'dp_assets_to_eqt': 'equity_multiplier_dupont',
        'ca_to_assets': 'current_assets_ratio',
        'nca_to_assets': 'non_current_assets_ratio',
        'tbassets_to_totalassets': 'tangible_assets_ratio',
        'int_to_talcap': 'interest_debt_to_capital',
        'eqt_to_talcapital': 'equity_to_capital',
        'currentdebt_to_debt': 'current_debt_ratio',
        'longdeb_to_debt': 'long_term_debt_ratio',
        'ocf_to_shortdebt': 'ocf_to_current_debt',
        'debt_to_eqt': 'debt_to_equity',
        'eqt_to_debt': 'equity_to_debt',
        'eqt_to_interestdebt': 'equity_to_interest_debt',
        'tangibleasset_to_debt': 'tangible_asset_to_debt',
        'tangasset_to_intdebt': 'tangible_asset_to_interest_debt',
        'tangibleasset_to_netdebt': 'tangible_asset_to_net_debt',
        'ocf_to_debt': 'ocf_to_debt',
        'ocf_to_interestdebt': 'ocf_to_interest_debt',
        'ocf_to_netdebt': 'ocf_to_net_debt',
        'ebit_to_interest': 'ebit_to_interest',
        'longdebt_to_workingcapital': 'long_debt_to_working_capital',
        'ebitda_to_debt': 'ebitda_to_debt',

        # 营运效率
        'invturn_days': 'inventory_turnover_days',
        'arturn_days': 'receivables_turnover_days',
        'inv_turn': 'inventory_turnover',
        'ar_turn': 'receivables_turnover',
        'ca_turn': 'current_assets_turnover',
        'fa_turn': 'fixed_assets_turnover',
        'assets_turn': 'total_assets_turnover',
        'turn_days': 'operating_cycle_days',
        'total_fa_trun': 'fixed_assets_total_turnover',

        # 现金流
        'op_income': 'operating_income',
        'valuechange_income': 'value_change_income',
        'interst_income': 'interest_expense',
        'daa': 'depreciation_amortization',
        'ebit': 'ebit',
        'ebitda': 'ebitda',
        'fcff': 'fcff',
        'fcfe': 'fcfe',
        'current_exint': 'interest_free_current_liabilities',
        'noncurrent_exint': 'interest_free_non_current_liabilities',
        'interestdebt': 'interest_bearing_debt',
        'netdebt': 'net_debt',
        'tangible_asset': 'tangible_assets',
        'working_capital': 'working_capital',
        'networking_capital': 'net_working_capital',
        'invest_capital': 'invested_capital',
        'retained_earnings': 'retained_earnings',
        'fixed_assets': 'fixed_assets',

        # 现金流比率
        'opincome_of_ebt': 'operating_income_to_ebt',
        'investincome_of_ebt': 'investment_income_to_ebt',
        'n_op_profit_of_ebt': 'non_operating_profit_to_ebt',
        'tax_to_ebt': 'tax_to_ebt',
        'dtprofit_to_profit': 'deducted_profit_to_profit',
        'salescash_to_or': 'sales_cash_to_operating_revenue',
        'ocf_to_or': 'ocf_to_operating_revenue',
        'ocf_to_opincome': 'ocf_to_operating_income',
        'capitalized_to_da': 'capitalized_to_da',

        # 利润分析
        'profit_prefin_exp': 'profit_before_financial_expense',
        'non_op_profit': 'non_operating_profit',
        'op_to_ebt': 'operating_profit_to_ebt',
        'nop_to_ebt': 'non_operating_profit_to_ebt',
        'ocf_to_profit': 'ocf_to_profit',
        'cash_to_liqdebt': 'cash_to_current_liabilities',
        'cash_to_liqdebt_withinterest': 'cash_to_interest_bearing_liabilities',
        'op_to_liqdebt': 'operating_profit_to_current_liabilities',
        'op_to_debt': 'operating_profit_to_debt',
        'roic_yearly': 'roic_yearly',
        'profit_to_op': 'profit_to_operating_revenue',

        # 单季度指标
        'q_opincome': 'q_operating_income',
        'q_investincome': 'q_investment_income',
        'q_dtprofit': 'q_deducted_net_profit',
        'q_eps': 'q_basic_eps',
        'q_netprofit_margin': 'q_net_profit_margin',
        'q_gsprofit_margin': 'q_gross_profit_margin',
        'q_exp_to_sales': 'q_expense_to_sales',
        'q_profit_to_gr': 'q_profit_to_gross_revenue',
        'q_saleexp_to_gr': 'q_sales_expense_to_gr',
        'q_adminexp_to_gr': 'q_admin_expense_to_gr',
        'q_finaexp_to_gr': 'q_financial_expense_to_gr',
        'q_impair_to_gr_ttm': 'q_impairment_to_gr',
        'q_gc_to_gr': 'q_total_cost_to_gr',
        'q_op_to_gr': 'q_operating_profit_to_gr',
        'q_roe': 'q_roe',
        'q_dt_roe': 'q_roe_diluted',
        'q_npta': 'q_net_profit_to_assets',
        'q_opincome_to_ebt': 'q_operating_income_to_ebt',
        'q_investincome_to_ebt': 'q_investment_income_to_ebt',
        'q_dtprofit_to_profit': 'q_deducted_profit_to_profit',
        'q_salescash_to_or': 'q_sales_cash_to_revenue',
        'q_ocf_to_sales': 'q_ocf_to_sales',
        'q_ocf_to_or': 'q_ocf_to_revenue',

        # 增长指标
        'basic_eps_yoy': 'basic_eps_yoy',
        'dt_eps_yoy': 'diluted_eps_yoy',
        'cfps_yoy': 'cfps_yoy',
        'op_yoy': 'operating_profit_yoy',
        'ebt_yoy': 'ebt_yoy',
        'netprofit_yoy': 'net_profit_yoy',
        'dt_netprofit_yoy': 'deducted_net_profit_yoy',
        'ocf_yoy': 'ocf_yoy',
        'roe_yoy': 'roe_yoy',
        'bps_yoy': 'bps_yoy',
        'assets_yoy': 'total_assets_yoy',
        'eqt_yoy': 'equity_yoy',
        'tr_yoy': 'total_revenue_yoy',
        'or_yoy': 'operating_revenue_yoy',
        'q_gr_yoy': 'q_gross_revenue_yoy',
        'q_gr_qoq': 'q_gross_revenue_qoq',
        'q_sales_yoy': 'q_revenue_yoy',
        'q_sales_qoq': 'q_revenue_qoq',
        'q_op_yoy': 'q_operating_profit_yoy',
        'q_op_qoq': 'q_operating_profit_qoq',
        'q_profit_yoy': 'q_profit_yoy',
        'q_profit_qoq': 'q_profit_qoq',
        'q_netprofit_yoy': 'q_net_profit_yoy',
        'q_netprofit_qoq': 'q_net_profit_qoq',
        'equity_yoy': 'equity_yoy',
        'rd_exp': 'rd_expense',

        # 其他
        'update_flag': 'update_flag',
    },
    'HK': {
        # 市值字段
        '总市值(港元)': 'hk_market_cap',
        '港股市值(港元)': 'hk_market_cap',
        # 每股指标
        '基本每股收益 (元)': 'basic_eps',
        '每股净资产 (元)': 'book_value_per_share',
        '每股经营现金流 (元)': 'operating_cash_flow_per_share',
        '每股股息 TTM(港元)': 'hk_dividend_per_share',
        # 盈利能力
        '股东权益回报率 (%)': 'roe',
        '销售净利率 (%)': 'net_profit_margin',
        '总资产回报率 (%)': 'roa',
        # 估值指标
        '市盈率': 'pe_ratio',
        '市净率': 'pb_ratio',
        '股息率 TTM(%)': 'hk_dividend_yield_ttm',
        # 增长指标
        '营业总收入滚动环比增长 (%)': 'hk_total_revenue_growth_qoq',
        '净利润滚动环比增长 (%)': 'hk_net_profit_growth_qoq',
        # 其他
        '派息比率 (%)': 'hk_dividend_payout_ratio',
        # 标准字段映射
        '营业总收入': 'total_revenue',
        '净利润': 'net_profit',
    },
    'US': {
        '总市值(美元)': 'us_market_cap',
    },

    # ----- 美股特有字段 -----
    # 利润表字段 (stock_financial_us_analysis_indicator_em 返回)
    'TOTAL_INCOME': 'total_revenue',
    'PARENT_HOLDER_NETPROFIT': 'net_profit',
    'PARENT_HOLDER_NETPROFIT_YOY': 'net_profit_yoy',
    'BASIC_EPS_CS': 'basic_eps',
    'BASIC_EPS_CS_YOY': 'basic_eps_yoy',
    'DILUTED_EPS_CS': 'diluted_eps',

    # 比率指标
    'ROE': 'roe',
    'ROE_AVG': 'roe',  # 美股年报使用 ROE_AVG 字段
    'ROE_YOY': 'roe_yoy',
    'ROA': 'roa',
    'ROA_YOY': 'roa_yoy',
    'DEBT_RATIO': 'debt_ratio',
    'DEBT_RATIO_YOY': 'debt_ratio_yoy',
    'EQUITY_RATIO': 'equity_ratio',

    # 营收相关
    'TOTAL_INCOME_YOY': 'total_revenue_yoy',
}


# ============================================================================
# 季度指标映射 (Quarterly Mapping)
# ============================================================================

QUARTERLY_MAPPING = {
    # ----- 日期字段 -----
    '报告期': 'report_date',
    'end_date': 'report_date',  # Tushare 报告期截止日

    # ----- 利润表字段 -----
    '净利润': 'net_profit',
    'NETPROFIT': 'net_profit',
    '扣非净利润': 'deducted_net_profit',
    '营业总收入': 'total_revenue',
    'TOTAL_OPERATE_INCOME': 'total_revenue',
    '经营溢利': 'operating_profit',
    '毛利': 'gross_profit',
    '股东应占溢利': 'parent_net_profit',
    '除税后溢利': 'profit_after_tax',
    '基本每股收益': 'basic_eps',
    'BASIC_EPS': 'basic_eps',
    '每股净资产': 'book_value_per_share',
    '净资产收益率': 'roe',
    '净资产收益率-摊薄': 'roe_diluted',
    '销售净利率': 'net_profit_margin',
    '销售毛利率': 'gross_profit_margin',

    # 港股特有
    'DATE_TYPE_CODE': 'date_type_code',
    '股东应占溢利': 'parent_net_profit',

    # ----- 美股季度数据字段 -----
    # stock_financial_us_analysis_indicator_em 单季度报
    'OPERATE_INCOME': 'operating_income',
    'OPERATE_INCOME_YOY': 'operating_income_yoy',
    'GROSS_PROFIT': 'gross_profit',
    'GROSS_PROFIT_YOY': 'gross_profit_yoy',
    'PARENT_HOLDER_NETPROFIT': 'parent_net_profit',
    'PARENT_HOLDER_NETPROFIT_YOY': 'parent_net_profit_yoy',
    'BASIC_EPS': 'basic_eps',
    'DILUTED_EPS': 'diluted_eps',
    'GROSS_PROFIT_RATIO': 'gross_profit_margin',
    'NET_PROFIT_RATIO': 'net_profit_margin',
    'ROE_AVG': 'roe',
    'ROA': 'roa',
    'CURRENT_RATIO': 'current_ratio',
    'SPEED_RATIO': 'quick_ratio',
    'OCF_LIQDEBT': 'ocf_to_debt',
    'DEBT_ASSET_RATIO': 'debt_ratio',
    'EQUITY_RATIO': 'equity_ratio',
    'BASIC_EPS_YOY': 'basic_eps_yoy',
    'GROSS_PROFIT_RATIO_YOY': 'gross_profit_margin_yoy',
    'NET_PROFIT_RATIO_YOY': 'net_profit_margin_yoy',
    'ROE_AVG_YOY': 'roe_yoy',
    'ROA_YOY': 'roa_yoy',
    'DEBT_ASSET_RATIO_YOY': 'debt_ratio_yoy',
    'CURRENT_RATIO_YOY': 'current_ratio_yoy',
    'SPEED_RATIO_YOY': 'quick_ratio_yoy',
    'REPORT_DATE': 'report_date',
    'DATE_TYPE': 'date_type',
    'DATE_TYPE_CODE': 'date_type_code',
    # 美股特有 - 保留原始字段以便 PEPct 指标使用
    'DATE_TYPE_CODE_original': 'DATE_TYPE_CODE',
}


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
        "NOTE_RECE": "notes_receivable",
        "TOTAL_OTHER_RECE": "other_receivables",
        "INVENTORY": "inventory",
        "FIXED_ASSET": "fixed_assets",
        "INTANGIBLE_ASSET": "intangible_assets",
        "USERIGHT_ASSET": "right_of_use_assets",
        "LONG_EQUITY_INVEST": "long_term_equity_invest",
        "CONSTRUCT_PROGRESS": "construction_in_progress",
        "PROJECT_MATERIAL": "project_materials",
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
        "LEASE_LIAB": "lease_liability",
        "NONCURRENT_LIAB_1YEAR": "noncurrent_liability_due_1y",
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
        # 美股字段 (stock_financial_us_report_em 返回)
        "总资产": "total_assets",
        "总负债": "total_liabilities",
        "流动资产合计": "current_assets",
        "非流动资产合计": "non_current_assets",
        "流动负债合计": "current_liabilities",
        "非流动负债合计": "non_current_liabilities",
        "现金及现金等价物": "cash_and_equivalents",
        "应收账款": "accounts_receivable",
        "应收税项": "tax_receivable",
        "存货": "inventory",
        "预付款项(流动)": "prepaid_expenses",
        "其他流动资产": "other_current_assets",
        "有价证券投资(流动)": "marketable_securities_current",
        "物业、厂房及设备": "fixed_assets",
        "无形资产": "intangible_assets",
        "商誉": "goodwill",
        "递延所得税资产(流动)": "deferred_tax_assets_current",
        "递延所得税资产(非流动)": "deferred_tax_assets_non_current",
        "其他投资": "other_investments",
        "有价证券投资(非流动)": "marketable_securities_non_current",
        "预付款项(非流动)": "prepaid_expenses_non_current",
        "其他非流动资产": "other_non_current_assets",
        "应付账款": "accounts_payable",
        "应付税项(流动)": "tax_payable_current",
        "预收及预提费用": "accrued_expenses",
        "其他应付款及应计费用": "other_payable_accrued",
        "短期债务": "short_term_debt",
        "递延收入(流动)": "deferred_revenue_current",
        "应付薪酬和福利": "accrued_payroll",
        "资本租赁债务(流动)": "capital_lease_liability_current",
        "递延所得税负债(非流动)": "deferred_tax_liabilities_non_current",
        "递延收入(非流动)": "deferred_revenue_non_current",
        "应付税项(非流动)": "tax_payable_non_current",
        "长期负债": "long_term_debt",
        "其他非流动负债": "other_non_current_liabilities",
        "资本租赁债务(非流动)": "capital_lease_liability_non_current",
        "普通股": "common_stock",
        "优先股": "preferred_stock",
        "留存收益": "retained_earnings",
        "股本溢价": "share_premium",
        "其他综合收益": "other_comprehensive_income",
        "归属于母公司股东权益": "parent_equity",
        "股东权益合计": "total_equity",
        "负债及股东权益合计": "total_liabilities_and_equity",
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
        "INTEREST_EXPENSE": "interest_expense",
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
        # 美股字段 (stock_financial_us_report_em 综合损益表)
        "主营收入": "total_revenue",
        "主营成本": "cost_of_revenue",
        "毛利润": "gross_profit",
        "净利润": "net_profit",
        "归属于普通股股东净利润": "parent_net_profit",
        "已终止或非持续经营净利润": "discontinued_operations_profit",
        "利息收入": "interest_income",
        "利息费用": "interest_expense",
        "一般及行政费用": "general_administrative_expenses",
        "其他收入(支出)": "other_income_expense",
        "其他营业费用": "other_operating_expenses",
        "全面收益总额": "total_comprehensive_income",
        "其他全面收益合计项": "other_comprehensive_income_total",
        "其他全面收益其他项目": "other_comprehensive_income_other",
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
        # 美股字段 (stock_financial_us_report_em 现金流量表)
        "经营活动产生的现金流量净额": "operating_cash_flow",
        "投资活动产生的现金流量净额": "investing_cash_flow",
        "筹资活动产生的现金流量净额": "financing_cash_flow",
        "净利润": "net_profit",
        "折旧及摊销": "depreciation_amortization",
        "基于股票的补偿费": "stock_based_compensation",
        "递延所得税": "deferred_tax",
        "资产处置损益": "gain_loss_on_asset_disposal",
        "投资损益": "investment_income_loss",
        "权益性投资损益": "equity_investment_income_loss",
        "应收账款及票据": "accounts_receivable_notes",
        "待摊费用及其他资产": "prepaid_expenses_other_assets",
        "应付账款及票据": "accounts_payable_notes",
        "递延收入": "deferred_revenue",
        "应付税项": "taxes_payable",
        "预提费用及其他负债": "accrued_expenses_other_liabilities",
        "购买固定资产": "capital_expenditure",
        "处置固定资产": "disposal_of_fixed_assets",
        "购建无形资产及其他资产": "capital_expenditure_intangible",
        "投资支付现金": "cash_investments",
        "发行股份": "stock_issuance",
        "回购股份": "stock_repurchase",
        "发行债券": "bond_issuance",
        "赎回债券": "bond_redemption",
        "股息支付": "dividend_paid",
        "行使股票期权所得": "stock_option_exercise_proceeds",
        "偿还借款": "debt_repayment",
    }

    # 基础字段（不映射）
    BASE_FIELDS = ["year", "SECURITY_CODE", "REPORT_DATE"]

    # ========================================================================
    # 核心字段映射方法 (Core Field Mapping Methods)
    # ========================================================================

    @classmethod
    def get_market_field(cls, standard_field: str, market: str) -> str | None:
        """
        正向查找：标准字段名 → 市场字段名

        Args:
            standard_field: 标准字段名 (如 "total_revenue")
            market: 市场名称 ("A股", "港股", "美股")

        Returns:
            市场特定字段名，不存在则返回 None
        """
        if standard_field in CORE_FIELD_MAPPING:
            return CORE_FIELD_MAPPING[standard_field].get(market)
        return None

    @classmethod
    def get_standard_field(cls, market_field: str, market: str) -> str | None:
        """
        反向查找：市场字段名 → 标准字段名

        Args:
            market_field: 市场特定字段名 (如 "营业总收入")
            market: 市场名称 ("A股", "港股", "美股")

        Returns:
            标准字段名，不存在则返回 None
        """
        if market in _REVERSE_FIELD_INDEX:
            return _REVERSE_FIELD_INDEX[market].get(market_field)
        return None

    @classmethod
    def list_core_fields(cls) -> list[str]:
        """
        列出所有核心标准字段名

        Returns:
            排序后的标准字段名列表
        """
        return sorted(CORE_FIELD_MAPPING.keys())

    # ========================================================================
    # 财务报表映射方法 (Financial Statement Mapping Methods)
    # ========================================================================

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
        # 如果 operating_income 不存在但 total_revenue 存在，使用 total_revenue 作为 operating_income
        # 这对港股和美股特别重要，因为它们的利润表没有单独的 operating_income 字段
        if "operating_income" not in df.columns and "total_revenue" in df.columns:
            df["operating_income"] = df["total_revenue"]

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
        for old_field in rename_map:
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

    # =========================================================================
    # 分层映射方法 (Financial Indicator & Quarterly)
    # =========================================================================

    @classmethod
    def apply_hierarchical_mapping(
        cls,
        df,
        mapping: dict[str, Any],
        market: str = 'A',
        keep_original: bool = False
    ):
        """
        Apply hierarchical mapping: IFRS standard + Market-specific Custom

        Args:
            df: Source DataFrame with provider fields
            mapping: The mapping dictionary (FINANCIAL_INDICATOR_MAPPING or QUARTERLY_MAPPING)
            market: Market code ('A', 'HK', 'US')
            keep_original: Whether to preserve original fields (default False - strict mode)

        Returns:
            DataFrame with mapped internal standard fields only
        """
        # Handle non-DataFrame inputs (e.g., mock returns string)
        if df is None:
            return df
        if hasattr(df, 'empty'):
            if df.empty:
                return df
        else:
            # Not a DataFrame, return as-is
            return df

        result = df.copy()
        rename_map = {}

        # Step 1: Build rename map, avoiding conflicts
        # Track which target fields are already mapped
        mapped_targets = set()

        # First pass: Apply IFRS standard fields (not market-specific)
        for old_field, new_field in mapping.items():
            if isinstance(old_field, str) and isinstance(new_field, str):
                if old_field in result.columns and new_field not in mapped_targets:
                    rename_map[old_field] = new_field
                    mapped_targets.add(new_field)

        # Second pass: Apply market-specific Custom fields (only if not already mapped)
        custom_mapping = mapping.get(market, {})
        if custom_mapping:
            for old_field, new_field in custom_mapping.items():
                if old_field in result.columns and new_field not in mapped_targets:
                    rename_map[old_field] = new_field
                    mapped_targets.add(new_field)

        # Apply renaming
        if rename_map:
            result = result.rename(columns=rename_map)

        # Step 3: Filter out unmapped fields (strict mode)
        # Collect all mapped target field names (including custom market mappings)
        mapped_field_values = set()

        # Standard fields
        for old_field, new_field in mapping.items():
            if isinstance(old_field, str) and isinstance(new_field, str):
                mapped_field_values.add(new_field)

        # Custom market fields (A, HK, US)
        for market_code in ['A', 'HK', 'US']:
            custom_mapping = mapping.get(market_code, {})
            for old_field, new_field in custom_mapping.items():
                if isinstance(new_field, str):
                    mapped_field_values.add(new_field)

        # Keep only mapped columns
        cols_to_keep = [col for col in result.columns if col in mapped_field_values]
        result = result[cols_to_keep]

        return result

    @classmethod
    def map_financial_indicator(
        cls,
        df: pd.DataFrame,
        market: str = 'A'
    ) -> pd.DataFrame:
        """
        Map financial_indicator fields to internal standard fields

        Args:
            df: Raw financial indicator DataFrame from provider
            market: Market code ('A', 'HK', 'US')

        Returns:
            DataFrame with internal standard fields only
        """
        return cls.apply_hierarchical_mapping(
            df, FINANCIAL_INDICATOR_MAPPING, market, keep_original=False
        )

    @classmethod
    def map_quarterly(
        cls,
        df: pd.DataFrame,
        market: str = 'A'
    ) -> pd.DataFrame:
        """
        Map quarterly fields to internal standard fields

        Args:
            df: Raw quarterly DataFrame from provider
            market: Market code ('A', 'HK', 'US')

        Returns:
            DataFrame with internal standard fields only
        """
        return cls.apply_hierarchical_mapping(
            df, QUARTERLY_MAPPING, market, keep_original=False
        )

    # =========================================================================
    # Self-description methods (for CLI introspection)
    # =========================================================================

    # Registry of report types to mapping names (extensible without CLI changes)
    REPORT_MAPPINGS = {
        'balance': 'BALANCE_MAPPING',
        'income': 'INCOME_MAPPING',
        'cashflow': 'CASHFLOW_MAPPING',
        'finind': 'FINANCIAL_INDICATOR_MAPPING',
        'quarterly': 'QUARTERLY_MAPPING',
    }

    @classmethod
    def get_standard_fields(cls, report: str, market: str = 'A') -> list:
        """
        Get list of standard internal fields for a given report type and market.

        Only returns IFRS standard fields (without market prefix like a_, hk_, us_).

        Args:
            report: Report type (see REPORT_MAPPINGS for valid options)
            market: Market code ('A', 'HK', 'US')

        Returns:
            Sorted list of standard field names
        """
        report = report.lower()
        market = market.upper()

        if report not in cls.REPORT_MAPPINGS:
            valid_options = ', '.join(cls.REPORT_MAPPINGS.keys())
            raise ValueError(f"Unknown report type: {report}. Valid options: {valid_options}")

        mapping_name = cls.REPORT_MAPPINGS[report]

        # Check class attributes first (BALANCE_MAPPING, INCOME_MAPPING, etc.)
        if hasattr(cls, mapping_name):
            mapping = getattr(cls, mapping_name)
            return cls._extract_standard_fields(mapping)
        # Fall back to module-level mappings (FINANCIAL_INDICATOR_MAPPING, QUARTERLY_MAPPING)
        else:
            import sys
            module = sys.modules.get(__name__)
            if module and hasattr(module, mapping_name):
                mapping = getattr(module, mapping_name)
                return cls._extract_standard_fields_hierarchical(mapping, market)
            else:
                raise ValueError(f"Mapping '{mapping_name}' not found for report '{report}'")

    @classmethod
    def _extract_standard_fields(cls, mapping: dict) -> list:
        """Extract unique standard field names from a flat mapping dict."""
        fields = set()
        for value in mapping.values():
            if isinstance(value, str):
                fields.add(value)
        return sorted(fields)

    @classmethod
    def _extract_standard_fields_hierarchical(cls, mapping: dict, market: str) -> list:
        """
        Extract standard field names from hierarchical mapping.

        Only returns fields without market prefix (a_, hk_, us_).
        """
        fields = set()
        market_prefixes = ('a_', 'hk_', 'us_')

        for key, value in mapping.items():
            # Skip market-specific sub-dicts
            if isinstance(key, str) and key in ('A', 'HK', 'US'):
                continue
            if isinstance(value, str):
                # Only include if not a market-specific field
                if not any(value.lower().startswith(prefix) for prefix in market_prefixes):
                    fields.add(value)

        return sorted(fields)
