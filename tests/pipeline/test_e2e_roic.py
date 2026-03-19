"""E2E tests for ROIC pipeline"""
import os
import pytest

from value_investment.pipeline.api import PipelineAPI
from value_investment.domain.fields import IFRSFields, CustomFields


@pytest.mark.skipif(not os.environ.get("TUSHARE_TOKEN"), reason="TUSHARE_TOKEN not set")
async def test_e2e_roic_full_flow():
    """E2E test: Get ROIC for Kweichow Moutai (600519)"""
    api = PipelineAPI()

    # ROIC is now fetched from fina_indicator API as a pre-calculated indicator
    result = await api.get_data(
        symbol="600519",
        fields=["roic"],
        end="2024",
        years=10,
    )

    assert "roic" in result
    assert len(result["roic"]) > 0
    # Latest year may vary
    assert 2024 in result["roic"] or 2023 in result["roic"]


@pytest.mark.skipif(not os.environ.get("TUSHARE_TOKEN"), reason="TUSHARE_TOKEN not set")
async def test_e2e_get_data():
    """E2E test: Get raw financial data"""
    api = PipelineAPI()
    
    # Just call api.get_data directly
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
