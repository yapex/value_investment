"""Market Capitalization Indicator - fetch market cap from financial indicators"""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class MarketCapIndicator(BaseIndicator):
    """
    市值指标
    
    从财务指标直接获取市值，自动检测市场类型。
    - 港股: hk_market_cap (港元)
    - A股: a_market_cap (人民币)
    - 美股: us_market_cap (美元)
    """
    
    name = "market_cap"
    needs = ['financial_indicator']
    description = "总市值 (从财务指标获取)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # TODO: 实现计算逻辑
        return IndicatorResult(
            value=0.0,
            unit="",
            description="总市值",
            years=[],
            values=[]
        )

    def get_required_fields(self) -> List[str]:
        return []
