import pytest
from unittest.mock import MagicMock
from value_investment.api import ValueInvestment

def test_api_uses_registry_for_needs():
    """API should resolve needs through DependencyRegistry"""
    api = ValueInvestment()

    # Check that api has registry
    assert hasattr(api, '_registry'), "ValueInvestment must have _registry"

def test_calculate_indicator_injects_dependencies():
    """calculate_indicator should inject dependencies from needs"""
    api = ValueInvestment()

    # Mock the registry
    api._registry = MagicMock()
    api._registry.resolve.return_value = {'quarterly': 'test_data'}

    # This should call registry.resolve
    try:
        api.calculate_indicator('PEPct', '600519')
    except:
        pass

    api._registry.resolve.assert_called()
