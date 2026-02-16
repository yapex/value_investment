import pytest
from value_investment.indicators.factory import IndicatorFactory


def test_indicator_factory_has_roic():
    factory = IndicatorFactory()
    indicator = factory.get("ROIC")
    assert indicator is not None


def test_indicator_factory_has_cagr():
    factory = IndicatorFactory()
    indicator = factory.get("CAGR")
    assert indicator is not None


def test_indicator_factory_has_dcf():
    factory = IndicatorFactory()
    indicator = factory.get("DCF")
    assert indicator is not None
