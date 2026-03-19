"""Tests for AShareProvider field mapping IoC"""
import pytest


class TestAShareProviderFieldMappings:
    """AShareProvider should declare FIELD_MAPPINGS"""

    def test_provider_declares_field_mappings(self):
        """TushareProvider should declare FIELD_MAPPINGS"""
        from value_investment.providers.a_share import TushareProvider

        assert hasattr(TushareProvider, "FIELD_MAPPINGS")
        assert isinstance(TushareProvider.FIELD_MAPPINGS, dict)
        assert "balance_sheet" in TushareProvider.FIELD_MAPPINGS
        assert "income_statement" in TushareProvider.FIELD_MAPPINGS
        assert "cash_flow" in TushareProvider.FIELD_MAPPINGS

    def test_field_mappings_structure(self):
        """FIELD_MAPPINGS values should be native→standard mappings"""
        from value_investment.providers.a_share import TushareProvider

        for statement_type, mapping in TushareProvider.FIELD_MAPPINGS.items():
            assert isinstance(mapping, dict)
            for native_field, standard_field in mapping.items():
                assert isinstance(native_field, str)
                assert isinstance(standard_field, str)
