"""Tests for API list_indicators with market filter"""
import pytest


class TestAPIListIndicators:
    """Test ValueInvestment API list_indicators with market filter"""

    def test_list_indicators_all(self):
        """list_indicators should return all indicators by default"""
        from value_investment.api import ValueInvestment

        api = ValueInvestment()
        indicators = api.list_indicators()

        assert isinstance(indicators, list)
        assert len(indicators) > 0

    def test_list_indicators_by_market(self):
        """list_indicators should filter by market"""
        from value_investment.api import ValueInvestment

        api = ValueInvestment()

        # Should accept market parameter
        abc_indicators = api.list_indicators(market="A股")
        assert isinstance(abc_indicators, list)

        hk_indicators = api.list_indicators(market="港股")
        assert isinstance(hk_indicators, list)

        us_indicators = api.list_indicators(market="美股")
        assert isinstance(us_indicators, list)

    def test_list_indicators_by_type(self):
        """list_indicators should filter by type"""
        from value_investment.api import ValueInvestment

        api = ValueInvestment()

        # Should accept type parameter
        raw_indicators = api.list_indicators(indicator_type="RAW")
        assert isinstance(raw_indicators, list)
