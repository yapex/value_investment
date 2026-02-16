import pytest
from value_investment.api import ValueInvestment


def test_financial_data_merge():
    vi = ValueInvestment(market="A")
    data = vi.get_financial_data("600519", 2020, 2024)

    # Verify merge contains key fields from all three statements
    assert "total_assets" in data.columns  # Balance sheet
    assert "total_revenue" in data.columns      # Income statement
    assert "operating_cash_flow" in data.columns  # Cash flow
    assert len(data) > 0
