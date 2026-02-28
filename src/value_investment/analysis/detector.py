"""Detector module - abnormal signal detection for financial indicators"""

from typing import Tuple, List, Dict, Any


def detect_warnings(indicators: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Detect warnings from financial indicators.
    
    Args:
        indicators: Dictionary containing financial indicator values.
            Expected keys:
            - ROE: Return on equity (%)
            - gross_margin: Gross margin (%)
            - net_profit_margin: Net profit margin (%)
            - current_ratio: Current ratio
            - cfo_to_netprofit_sum: Operating cash flow / Net profit ratio
            - gross_margin_3y_avg: 3-year average gross margin (optional)
    
    Returns:
        Tuple of (warnings, notes):
            - warnings: List of warning messages
            - notes: List of informational notes
    """
    warnings = []
    notes = []
    
    if not indicators:
        return warnings, notes
    
    # ROE detection
    roe = indicators.get("ROE")
    if roe is not None:
        if roe < 5:
            warnings.append(f"ROE 偏低: {roe}%，低于5%门槛")
        elif roe > 30:
            warnings.append(f"ROE 偏高: {roe}%，超过30%需验证真实性")
        # Normal ROE (5-30%) is fine, no warning
    
    # Gross margin detection
    gross_margin = indicators.get("gross_margin")
    if gross_margin is not None:
        if gross_margin < 10:
            warnings.append(f"毛利率异常偏低: {gross_margin}%，低于10%")
        
        # Check for declining gross margin
        gross_margin_3y_avg = indicators.get("gross_margin_3y_avg")
        if gross_margin_3y_avg is not None and gross_margin < gross_margin_3y_avg * 0.8:
            warnings.append(f"毛利率下降: 当前{gross_margin}% vs 3年均值{gross_margin_3y_avg}%")
    
    # Cash flow detection
    cfo_ratio = indicators.get("cfo_to_netprofit_sum")
    if cfo_ratio is not None:
        if cfo_ratio < 0:
            warnings.append(f"现金流为负: 经营现金流/净利润 = {cfo_ratio}")
        elif cfo_ratio < 0.8:
            warnings.append(f"现金流异常: 经营现金流/净利润 = {cfo_ratio}，低于0.8")
    
    # Liquidity detection
    current_ratio = indicators.get("current_ratio")
    if current_ratio is not None:
        if current_ratio < 1.0:
            warnings.append(f"流动比率偏低: {current_ratio}，低于1.0")
    
    return warnings, notes
