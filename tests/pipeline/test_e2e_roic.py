"""E2E tests for ROIC pipeline"""
import os
import pytest

from value_investment.pipeline.api import PipelineAPI
from value_investment.pipeline.fields import IFRSFields, CustomFields


@pytest.mark.skipif(not os.environ.get("TUSHARE_TOKEN"), reason="TUSHARE_TOKEN not set")
async def test_e2e_roic_full_flow():
    """E2E test: Get ROIC for Kweichow Moutai (600519)"""
    api = PipelineAPI()

    result = await api.get_indicator(
        symbol="600519",
        indicator=CustomFields.ROIC,
        end="2024",
        years=10,
    )

    assert isinstance(result, dict)
    assert len(result) > 0
    assert 2024 in result or 2023 in result  # Latest year may vary

    # ROIC should be positive for profitable companies
    # Allow higher values for exceptional companies like Moutai
    for year, value in result.items():
        assert value > 0, f"ROIC for {year} is {value}, should be positive"


@pytest.mark.skipif(not os.environ.get("TUSHARE_TOKEN"), reason="TUSHARE_TOKEN not set")
async def test_e2e_get_data():
    """E2E test: Get raw financial data"""
    api = PipelineAPI()

    result = await api.get_data(
        symbol="600519",
        fields=[IFRSFields.NET_PROFIT, IFRSFields.TOTAL_ASSETS],
        end="2024",
        years=5,
    )

    assert IFRSFields.NET_PROFIT in result
    assert IFRSFields.TOTAL_ASSETS in result
    assert len(result[IFRSFields.NET_PROFIT]) > 0
    assert len(result[IFRSFields.TOTAL_ASSETS]) > 0
