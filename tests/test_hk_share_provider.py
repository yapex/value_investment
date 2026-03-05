import pytest
from unittest.mock import MagicMock
import pandas as pd


def test_hk_share_provider_initialization():
    """HKShareProvider should initialize with market='HK'"""
    from value_investment.data.providers.hk_share_provider import HKShareProvider
    mock_cache = MagicMock()
    provider = HKShareProvider(cache=mock_cache, market="HK")
    assert provider._market == "HK"
