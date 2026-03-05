import pytest
from unittest.mock import MagicMock
import pandas as pd


def test_us_share_provider_initialization():
    """USShareProvider should initialize with market='US'"""
    from value_investment.data.providers.us_share_provider import USShareProvider
    mock_cache = MagicMock()
    provider = USShareProvider(cache=mock_cache, market="US")
    assert provider._market == "US"
