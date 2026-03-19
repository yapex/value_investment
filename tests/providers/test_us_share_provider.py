"""Tests for USProvider field mapping IoC"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


class TestUSProviderFieldMappings:
    """USProvider should declare FIELD_MAPPINGS and provide fetch_raw_* methods"""

    def test_provider_declares_field_mappings(self):
        """USProvider should declare FIELD_MAPPINGS at class level"""
        from value_investment.providers.us_share import USProvider

        assert hasattr(USProvider, "FIELD_MAPPINGS")
        assert isinstance(USProvider.FIELD_MAPPINGS, dict)
        assert "balance_sheet" in USProvider.FIELD_MAPPINGS
        assert "income_statement" in USProvider.FIELD_MAPPINGS
        assert "cash_flow" in USProvider.FIELD_MAPPINGS

    @patch("value_investment.providers.us_share.ak")
    def test_fetch_raw_returns_native_fields(self, mock_ak):
        """fetch_raw_balance_sheet should return data with native field names"""
        from value_investment.providers.us_share import USProvider

        mock_ak.stock_financial_us_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2023-12-31", "2022-12-31"],
            "STD_ITEM_NAME": ["总资产", "总资产"],
            "AMOUNT": [1000, 900],
        })

        provider = USProvider(MagicMock())
        df = provider.fetch_raw_balance_sheet("AAPL", 2024, 2020)

        assert "year" in df.columns
        assert 2023 in df["year"].values
        assert 2022 in df["year"].values

    def test_supported_fields_includes_standard_names(self):
        """supported_fields should include standard field names"""
        from value_investment.providers.us_share import USProvider

        provider = USProvider(MagicMock())
        fields = provider.supported_fields

        assert "total_assets" in fields
        assert "total_revenue" in fields
        assert "operating_cash_flow" in fields
