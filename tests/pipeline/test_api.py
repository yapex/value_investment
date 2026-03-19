"""Tests for Pipeline API"""
import pytest

from value_investment.pipeline.api import PipelineAPI
from value_investment.domain.fields import IFRSFields, CustomFields


def test_api_detect_market():
    """Test market detection"""
    api = PipelineAPI()

    # A股: 6位数字 (0/3/6开头)
    assert api._detect_market("600519") == "A股"
    assert api._detect_market("000001") == "A股"
    assert api._detect_market("300001") == "A股"
    # 港股: 5位数字
    assert api._detect_market("00700") == "港股"
    assert api._detect_market("09988") == "港股"
    # 美股: 字母
    assert api._detect_market("AAPL") == "美股"
    assert api._detect_market("TSLA") == "美股"
