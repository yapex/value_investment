"""Tests for Fields Registry"""
import pytest
from value_investment.pipeline.fields.registry import (
    FieldRegistry,
    get_registry,
    RAW_FIELDS,
    CALCULATED_FIELDS,
)


def test_field_registry_singleton():
    """Test registry is singleton"""
    registry1 = get_registry()
    registry2 = get_registry()
    assert registry1 is registry2


def test_raw_fields_exist():
    """Test raw fields are defined"""
    assert len(RAW_FIELDS) > 0
    assert "net_profit" in RAW_FIELDS
    assert "total_assets" in RAW_FIELDS


def test_calculated_fields_exist():
    """Test calculated fields are defined"""
    assert len(CALCULATED_FIELDS) > 0
    assert "roic" in CALCULATED_FIELDS
    assert "roe" in CALCULATED_FIELDS


def test_roic_depends_on():
    """Test ROIC field declares its dependencies"""
    registry = get_registry()
    roic_meta = registry.get_field("roic")
    assert roic_meta is not None
    # ROIC depends on operating_profit (as EBIT substitute), total_assets, cash_and_equivalents, current_liabilities
    assert "operating_profit" in roic_meta.depends_on
    assert "total_assets" in roic_meta.depends_on
    assert "cash_and_equivalents" in roic_meta.depends_on
    assert "current_liabilities" in roic_meta.depends_on
