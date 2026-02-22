import pytest
import inspect
from unittest.mock import MagicMock, patch

def test_provider_uses_datamapper():
    """Verify that provider transforms data using DataMapper"""
    from value_investment.data.providers.akshare_provider import AkshareProvider

    # Get source code and check for DataMapper usage (not just import)
    source = inspect.getsource(AkshareProvider)

    # Should actually call DataMapper methods, not just import it
    assert 'DataMapper.' in source, "AkshareProvider should use DataMapper methods"


def test_api_get_financial_data_uses_field_mapping():
    """Verify that API._get_financial_data applies field mapping to balance/profit/cashflow sheets"""
    from value_investment.api import ValueInvestment
    import pandas as pd

    # Create a mock provider
    mock_provider = MagicMock()

    # Create sample data with akshare raw field names
    balance_df = pd.DataFrame({
        'year': [2023, 2022],
        'TOTAL_ASSETS': [1000, 900],
        'TOTAL_EQUITY': [500, 450],
    })
    profit_df = pd.DataFrame({
        'year': [2023, 2022],
        'TOTAL_OPERATE_INCOME': [800, 700],
        'NETPROFIT': [100, 80],
    })
    cashflow_df = pd.DataFrame({
        'year': [2023, 2022],
        'NETCASH_OPERATE': [150, 120],
    })

    mock_provider.get_balance_sheet.return_value = balance_df
    mock_provider.get_profit_sheet.return_value = profit_df
    mock_provider.get_cashflow_sheet.return_value = cashflow_df

    # Patch the provider in ValueInvestment
    with patch.object(ValueInvestment, '__init__', lambda self, **kwargs: None):
        vi = ValueInvestment.__new__(ValueInvestment)
        vi._provider = mock_provider
        vi._cache = MagicMock()

        # Call _get_financial_data
        result = vi._get_financial_data('600519', 2023)

        # Verify that the result contains standardized field names
        # After mapping: TOTAL_ASSETS -> total_assets, NETPROFIT -> net_profit, etc.
        assert 'total_assets' in result.columns, "Field mapping should convert TOTAL_ASSETS to total_assets"
        assert 'net_profit' in result.columns, "Field mapping should convert NETPROFIT to net_profit"
        assert 'operating_cash_flow' in result.columns, "Field mapping should convert NETCASH_OPERATE to operating_cash_flow"


def test_indicator_works_with_mapped_fields():
    """Verify that indicators can work with mapped (standardized) field names"""
    from value_investment.indicators.simple import ROEIndicator
    import pandas as pd

    # Create data with standardized field names (after mapping)
    data = pd.DataFrame({
        'year': [2023, 2022],
        'net_profit': [100, 80],
        'total_equity': [500, 400],
    })

    indicator = ROEIndicator()
    result = indicator.calculate(data)

    # Should calculate correctly with standardized field names
    assert result.value > 0, "ROE should be calculated with standardized field names"
    assert len(result.values) == 2, "Should have values for both years"
