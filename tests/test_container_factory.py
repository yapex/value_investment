import pytest


def test_container_uses_factory():
    """Container should create providers via ProviderFactory"""
    from value_investment.core.container import Container
    from value_investment.data.providers.factory import ProviderFactory
    
    container = Container()
    # Verify ProviderFactory works with container's cache
    provider = ProviderFactory.create_provider(container.cache(), market="A")
    assert provider is not None
    assert provider.__class__.__name__ == "AShareProvider"
