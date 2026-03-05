"""Indicator Registry for managing financial indicators"""
from typing import Optional

from value_investment.data.mapper import CORE_FIELD_MAPPING
from value_investment.indicators.base import IndicatorMeta, IndicatorType


class IndicatorRegistry:
    """Singleton registry for managing financial indicators"""

    _instance: Optional["IndicatorRegistry"] = None
    _indicators: dict[str, IndicatorMeta] = {}

    def __init__(self) -> None:
        if IndicatorRegistry._instance is not None:
            raise RuntimeError("Use get_instance() to get singleton")
        self._indicators = {}

    @classmethod
    def get_instance(cls) -> "IndicatorRegistry":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._indicators = {}
        return cls._instance

    def register(self, meta: IndicatorMeta) -> None:
        """Register an indicator

        Args:
            meta: Indicator metadata
        """
        self._indicators[meta.name] = meta

    def get(self, name: str) -> IndicatorMeta | None:
        """Get indicator by name

        Args:
            name: Indicator name

        Returns:
            Indicator metadata or None if not found
        """
        return self._indicators.get(name)

    def list_all(self) -> list[IndicatorMeta]:
        """List all registered indicators

        Returns:
            List of all indicator metadata
        """
        return list(self._indicators.values())

    def list_by_type(self, indicator_type: IndicatorType) -> list[IndicatorMeta]:
        """List indicators by type

        Args:
            indicator_type: Type of indicators to filter

        Returns:
            List of matching indicators
        """
        return [
            meta
            for meta in self._indicators.values()
            if meta.type == indicator_type
        ]

    def list_by_market(self, market: str) -> list[IndicatorMeta]:
        """List indicators available for a market

        Args:
            market: Market name (e.g., "A股")

        Returns:
            List of indicators available for the market
        """
        return [
            meta
            for meta in self._indicators.values()
            if market in meta.market_fields or not meta.market_fields
        ]

    def clear(self) -> None:
        """Clear all registered indicators (mainly for testing)"""
        self._indicators.clear()


# ========================================================================
# 辅助函数：从 CORE_FIELD_MAPPING 生成指标定义
# ========================================================================

def _build_core_indicators() -> list[dict]:
    """从 CORE_FIELD_MAPPING 动态生成核心指标列表"""
    indicators = []
    for field_name, market_map in CORE_FIELD_MAPPING.items():
        field_names = list(set(market_map.values()))
        indicators.append({
            "name": field_name,
            "display_name": _get_display_name(field_name),
            "field_names": field_names,
            "market_fields": market_map,
            "description": _get_description(field_name),
            "unit": _get_unit(field_name),
        })
    return indicators


# Display name mapping for core fields
_DISPLAY_NAME_MAP = {
    "total_revenue": "营业收入",
    "net_profit": "净利润",
    "operating_profit": "营业利润",
    "gross_profit": "毛利润",
    "operating_cost": "营业成本",
    "total_assets": "总资产",
    "total_equity": "股东权益",
    "total_liabilities": "总负债",
    "current_assets": "流动资产",
    "current_liabilities": "流动负债",
    "cash_and_equivalents": "货币资金",
    "inventory": "存货",
    "accounts_receivable": "应收账款",
    "fixed_assets": "固定资产",
    "operating_cash_flow": "经营现金流",
    "investing_cash_flow": "投资现金流",
    "financing_cash_flow": "融资现金流",
    "capital_expenditure": "资本支出",
    "basic_eps": "每股收益",
    "diluted_eps": "稀释每股收益",
    "book_value_per_share": "每股净资产",
    "pe_ratio": "市盈率",
    "pb_ratio": "市净率",
    "market_cap": "总市值",
    "roe": "净资产收益率",
    "roa": "总资产收益率",
    "gross_margin": "毛利率",
    "net_profit_margin": "净利率",
    "current_ratio": "流动比率",
    "quick_ratio": "速动比率",
    "debt_ratio": "资产负债率",
    "asset_turnover": "资产周转率",
    "inventory_turnover": "存货周转率",
    "receivable_turnover": "应收账款周转率",
    "total_shares": "总股本",
}


def _get_display_name(field_name: str) -> str:
    """获取字段的中文显示名称"""
    return _DISPLAY_NAME_MAP.get(field_name, field_name)


def _get_description(field_name: str) -> str:
    """获取字段描述"""
    descriptions = {
        "total_revenue": "企业营业收入",
        "net_profit": "企业净利润",
        "total_assets": "企业总资产",
        "total_equity": "企业股东权益",
        "market_cap": "股票总市值",
    }
    return descriptions.get(field_name, f"字段: {field_name}")


def _get_unit(field_name: str) -> str:
    """获取字段单位"""
    units = {
        "total_revenue": "元",
        "net_profit": "元",
        "total_assets": "元",
        "total_equity": "元",
        "total_liabilities": "元",
        "basic_eps": "元",
        "diluted_eps": "元",
        "book_value_per_share": "元",
        "market_cap": "元/港元/美元",
        "roe": "%",
        "roa": "%",
        "gross_margin": "%",
        "net_profit_margin": "%",
    }
    return units.get(field_name, "")


# ========================================================================
# 市场特有指标 (港股/美股 特有字段，不在 CORE_FIELD_MAPPING 中)
# ========================================================================

HK_SPECIFIC_INDICATORS = [
    {
        "name": "hk_eps",
        "display_name": "每股收益(港币)",
        "field_names": ["基本每股收益(元)"],
        "market_fields": {
            "港股": "基本每股收益(元)",
        },
        "description": "基本每股收益(元)",
        "unit": "元",
    },
    {
        "name": "hk_bvps",
        "display_name": "每股净资产(港币)",
        "field_names": ["每股净资产(元)"],
        "market_fields": {
            "港股": "每股净资产(元)",
        },
        "description": "每股净资产(元)",
        "unit": "元",
    },
    {
        "name": "hk_legal_capital",
        "display_name": "法定股本",
        "field_names": ["法定股本(股)"],
        "market_fields": {
            "港股": "法定股本(股)",
        },
        "description": "法定股本(股)",
        "unit": "股",
    },
    {
        "name": "hk_dividend_per_share",
        "display_name": "每股股息",
        "field_names": ["每股股息TTM(港元)"],
        "market_fields": {
            "港股": "每股股息TTM(港元)",
        },
        "description": "每股股息TTM(港元)",
        "unit": "港元",
    },
    {
        "name": "hk_payout_ratio",
        "display_name": "派息比率",
        "field_names": ["派息比率(%)"],
        "market_fields": {
            "港股": "派息比率(%)",
        },
        "description": "派息比率(%)",
        "unit": "%",
    },
    {
        "name": "hk_issued_shares",
        "display_name": "已发行股本",
        "field_names": ["已发行股本(股)"],
        "market_fields": {
            "港股": "已发行股本(股)",
        },
        "description": "已发行股本(股)",
        "unit": "股",
    },
    {
        "name": "hk_h_shares",
        "display_name": "H股股本",
        "field_names": ["已发行股本-H股(股)"],
        "market_fields": {
            "港股": "已发行股本-H股(股)",
        },
        "description": "已发行股本-H股(股)",
        "unit": "股",
    },
    {
        "name": "hk_cfo_per_share",
        "display_name": "每股经营现金流",
        "field_names": ["每股经营现金流(元)"],
        "market_fields": {
            "港股": "每股经营现金流(元)",
        },
        "description": "每股经营现金流(元)",
        "unit": "元",
    },
    {
        "name": "hk_dividend_yield",
        "display_name": "股息率",
        "field_names": ["股息率TTM(%)"],
        "market_fields": {
            "港股": "股息率TTM(%)",
        },
        "description": "股息率TTM(%)",
        "unit": "%",
    },
    {
        "name": "hk_market_cap",
        "display_name": "港股市值",
        "field_names": ["港股市值(港元)"],
        "market_fields": {
            "港股": "港股市值(港元)",
        },
        "description": "港股市值(港元)",
        "unit": "港元",
    },
    {
        "name": "hk_revenue_growth",
        "display_name": "营收环比增长",
        "field_names": ["营业总收入滚动环比增长(%)"],
        "market_fields": {
            "港股": "营业总收入滚动环比增长(%)",
        },
        "description": "营业总收入滚动环比增长(%)",
        "unit": "%",
    },
    {
        "name": "hk_net_profit_margin",
        "display_name": "销售净利率",
        "field_names": ["销售净利率(%)"],
        "market_fields": {
            "港股": "销售净利率(%)",
        },
        "description": "销售净利率(%)",
        "unit": "%",
    },
    {
        "name": "hk_net_profit_growth",
        "display_name": "净利润环比增长",
        "field_names": ["净利润滚动环比增长(%)"],
        "market_fields": {
            "港股": "净利润滚动环比增长(%)",
        },
        "description": "净利润滚动环比增长(%)",
        "unit": "%",
    },
]


# Default raw financial indicators - 从 CORE_FIELD_MAPPING 动态生成 + 港股特有指标
# 注意: pe_ratio, pb_ratio 等共享指标已包含在 CORE_FIELD_MAPPING 中
DEFAULT_RAW_INDICATORS = _build_core_indicators() + HK_SPECIFIC_INDICATORS


# Default calculated financial indicators (SIMPLE)
DEFAULT_CALCULATED_INDICATORS = [
    # Profitability indicators
    {
        "name": "gross_margin",
        "display_name": "毛利率",
        "type": IndicatorType.CALCULATED,
        "description": "毛利率 (毛利润/营业收入)",
        "unit": "%",
        "market_fields": {
            "A股": "销售毛利率(%)",
            "港股": "毛利率",
        },
    },
    {
        "name": "roe",
        "display_name": "净资产收益率",
        "type": IndicatorType.CALCULATED,
        "description": "净资产收益率 ROE (净利润/股东权益)",
        "unit": "%",
        "market_fields": {
            "A股": "净资产收益率(%)",
            "港股": "股东权益回报率(%)",
        },
    },
    {
        "name": "roa",
        "display_name": "总资产收益率",
        "type": IndicatorType.CALCULATED,
        "description": "总资产收益率 ROA (净利润/总资产)",
        "unit": "%",
        "market_fields": {
            "A股": "总资产收益率(%)",
            "港股": "总资产回报率(%)",
        },
    },
    {
        "name": "net_profit_margin",
        "display_name": "净利率",
        "type": IndicatorType.CALCULATED,
        "description": "净利率 (净利润/营业收入)",
        "unit": "%",
        "market_fields": {
            "A股": "净利率(%)",
            "港股": "销售净利率(%)",
        },
    },
    # Liquidity indicators
    {
        "name": "current_ratio",
        "display_name": "流动比率",
        "type": IndicatorType.CALCULATED,
        "description": "流动比率 (流动资产/流动负债)",
        "unit": "ratio",
        "market_fields": {
            "A股": "流动比率",
            "港股": "流动比率",
        },
    },
    {
        "name": "quick_ratio",
        "display_name": "速动比率",
        "type": IndicatorType.CALCULATED,
        "description": "速动比率 ((流动资产-存货)/流动负债)",
        "unit": "ratio",
        "market_fields": {
            "A股": "速动比率",
            "港股": "速动比率",
        },
    },
    # Leverage indicators
    {
        "name": "debt_ratio",
        "display_name": "资产负债率",
        "type": IndicatorType.CALCULATED,
        "description": "资产负债率 (负债合计/资产总计)",
        "unit": "%",
        "market_fields": {
            "A股": "资产负债率(%)",
            "港股": "资产负债率",
        },
    },
    # Efficiency indicators
    {
        "name": "inventory_turnover",
        "display_name": "存货周转率",
        "type": IndicatorType.CALCULATED,
        "description": "存货周转率 (营业成本/平均存货)",
        "unit": "ratio",
        "market_fields": {
            "A股": "存货周转率(次)",
            "港股": "存货周转率",
        },
    },
    {
        "name": "receivable_turnover",
        "display_name": "应收账款周转率",
        "type": IndicatorType.CALCULATED,
        "description": "应收账款周转率 (营业收入/平均应收账款)",
        "unit": "ratio",
        "market_fields": {
            "A股": "应收账款周转率(次)",
            "港股": "应收账款周转率",
        },
    },
    {
        "name": "asset_turnover",
        "display_name": "总资产周转率",
        "type": IndicatorType.CALCULATED,
        "description": "总资产周转率 (营业收入/平均总资产)",
        "unit": "ratio",
        "market_fields": {
            "A股": "总资产周转率(次)",
            "港股": "总资产周转率",
        },
    },
    {
        "name": "payable_turnover",
        "display_name": "应付账款周转率",
        "type": IndicatorType.CALCULATED,
        "description": "应付账款周转率 (营业成本/平均应付账款)",
        "unit": "ratio",
        "market_fields": {
            "A股": "应付账款周转率",
            "港股": "应付账款周转率",
        },
    },
    # Cash flow indicators
    {
        "name": "cfo_to_netprofit_sum",
        "display_name": "累计净现比",
        "type": IndicatorType.CALCULATED,
        "description": "经营现金流累计/净利润累计 (盈利质量验证)",
        "unit": "%",
        "market_fields": {},
    },
    # Complex indicators
    {
        "name": "ROIC",
        "display_name": "投资资本回报率",
        "type": IndicatorType.CALCULATED,
        "description": "ROIC = NOPAT / 投入资本",
        "unit": "%",
        "market_fields": {},
    },
    {
        "name": "CAGR",
        "display_name": "复合增长率",
        "type": IndicatorType.CALCULATED,
        "description": "复合增长率，支持 revenue/net_profit",
        "unit": "%",
        "market_fields": {},
    },
    {
        "name": "ImpliedGrowth",
        "display_name": "市场隐含增长率",
        "type": IndicatorType.CALCULATED,
        "description": "基于DCF模型反推增长率",
        "unit": "%",
        "market_fields": {},
    },
    {
        "name": "PEPct",
        "display_name": "PE历史百分位",
        "type": IndicatorType.CALCULATED,
        "description": "当前PE在历史PE序列中的位置",
        "unit": "%",
        "market_fields": {},
    },
]


def register_defaults() -> None:
    """Register default raw financial indicators"""
    registry = IndicatorRegistry.get_instance()

    # Register RAW indicators
    for indicator_data in DEFAULT_RAW_INDICATORS:
        meta = IndicatorMeta(
            name=indicator_data["name"],
            display_name=indicator_data["display_name"],
            type=IndicatorType.RAW,
            field_names=indicator_data.get("field_names", []),
            market_fields=indicator_data.get("market_fields", {}),
            description=indicator_data["description"],
            unit=indicator_data["unit"],
        )
        registry.register(meta)

    # Register calculated (SIMPLE) indicators
    for indicator_data in DEFAULT_CALCULATED_INDICATORS:
        meta = IndicatorMeta(
            name=indicator_data["name"],
            display_name=indicator_data["display_name"],
            type=indicator_data["type"],
            field_names=indicator_data.get("field_names", []),
            market_fields=indicator_data.get("market_fields", {}),
            description=indicator_data["description"],
            unit=indicator_data["unit"],
        )
        registry.register(meta)
