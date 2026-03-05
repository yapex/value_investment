"""Market enum and detection functions for multi-market support"""
from enum import Enum


class Market(str, Enum):
    """Supported markets for financial analysis"""

    A = "A股"
    HK = "港股"
    US = "美股"


def detect_market(code: str) -> str | None:
    """Detect market from stock code

    Args:
        code: Stock code (e.g., "600519", "00700", "AAPL")

    Returns:
        Market name string or None if invalid
    """
    if not code:
        return None

    code = code.strip()

    # A股: 6-digit codes starting with 0, 3, 6
    if code.isdigit() and len(code) == 6:
        if code[0] in ("0", "3", "6"):
            return Market.A.value

    # 港股: 5-digit codes
    if code.isdigit() and len(code) == 5:
        return Market.HK.value

    # 美股: alphabetic ticker symbols
    if code.isalpha():
        return Market.US.value

    return None
