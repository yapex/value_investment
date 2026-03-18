"""Tests for DI Container"""
import pytest
from value_investment.pipeline.container import Container


def test_container_creation():
    """Test container can be created"""
    container = Container.create()
    # 调用 bus() 获取实际实例
    assert container.bus() is not None
    assert len(container.bus().handlers) > 0


def test_container_provides_handlers():
    """Test container has handlers registered"""
    container = Container.create()
    # 应该有多个 handler 注册
    assert len(container.bus().handlers) >= 3
