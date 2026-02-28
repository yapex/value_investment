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
        financial_indicator = kwargs.get('financial_indicator')
        stock_code = kwargs.get('stock_code', '')
        
        if financial_indicator is None or financial_indicator.empty:
            return IndicatorResult(
                value=0.0,
                unit="",
                description="总市值 (无财务指标数据)",
                years=[],
                values=[]
            )
        
        finind = financial_indicator
        
        # 检测市场类型
        is_hk = len(stock_code) == 5 and stock_code.isdigit()
        is_us = stock_code.isalpha()
        
        market_cap = None
        market_name = ""
        unit = ""
        
        if is_hk:
            # 港股：优先使用内部标准字段
            for col in ['hk_market_cap', 'market_cap_hkd', '港股市值(港元)', '总市值(港元)']:
                if col in finind.columns:
                    market_cap = float(finind[col].iloc[0])
                    break
            market_name = "港股"
            unit = "港元"
        elif is_us:
            # 美股：优先使用内部标准字段
            for col in ['us_market_cap', 'market_cap_usd', '总市值(美元)']:
                if col in finind.columns:
                    market_cap = float(finind[col].iloc[0])
                    break
            market_name = "美股"
            unit = "美元"
        else:
            # A股：优先使用内部标准字段
            for col in ['a_market_cap', 'market_cap_cny', '总市值(元)', '总市值(人民币)']:
                if col in finind.columns:
                    market_cap = float(finind[col].iloc[0])
                    break
            market_name = "A股"
            unit = "人民币"
        
        if market_cap and market_cap > 0:
            return IndicatorResult(
                value=market_cap,
                unit=unit,
                description=f"总市值 ({market_name}, {unit})",
                years=[],
                values=[]
            )
        
        return IndicatorResult(
            value=0.0,
            unit="",
            description="总市值 (无法获取)",
            years=[],
            values=[]
        )

    def get_required_fields(self) -> List[str]:
        return []
