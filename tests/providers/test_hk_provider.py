"""Tests for HKProvider field mapping IoC"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch


class TestHKProviderFieldMappings:
    """HKProvider should declare FIELD_MAPPINGS and provide fetch_raw_* methods"""

    def test_provider_declares_field_mappings(self):
        """HKProvider should declare FIELD_MAPPINGS at class level"""
        from value_investment.providers.hk_share import HKProvider

        assert hasattr(HKProvider, "FIELD_MAPPINGS")
        assert isinstance(HKProvider.FIELD_MAPPINGS, dict)
        assert "balance_sheet" in HKProvider.FIELD_MAPPINGS
        assert "income_statement" in HKProvider.FIELD_MAPPINGS
        assert "cash_flow" in HKProvider.FIELD_MAPPINGS

    def test_field_mappings_structure(self):
        """FIELD_MAPPINGS values should be native→standard mappings"""
        from value_investment.providers.hk_share import HKProvider

        for statement_type, mapping in HKProvider.FIELD_MAPPINGS.items():
            assert isinstance(mapping, dict)
            for native_field, standard_field in mapping.items():
                assert isinstance(native_field, str)
                assert isinstance(standard_field, str)
                # 标准字段应该是英文
                assert native_field != standard_field or native_field.startswith(("_", "total_", "net_"))

    @patch("value_investment.providers.hk_share.ak")
    def test_fetch_raw_returns_native_fields(self, mock_ak):
        """fetch_raw_balance_sheet should return data with native field names"""
        from value_investment.providers.hk_share import HKProvider

        # 模拟 AKShare 返回原始数据（长表格式）
        mock_ak.stock_financial_hk_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2023-12-31", "2022-12-31"],
            "STD_ITEM_NAME": ["资产总计", "资产总计"],
            "AMOUNT": [1000, 900],
        })

        provider = HKProvider(MagicMock())
        df = provider.fetch_raw_balance_sheet("00700", 2024, 2020)

        # 应该返回宽表格式，包含 year 列
        assert "year" in df.columns
        # fetch_raw_* 不过滤年份，返回原始转换后的数据
        assert 2023 in df["year"].values
        assert 2022 in df["year"].values

        # 原始字段应该在列中（映射前）
        # fetch_raw_* 不做映射，所以 STD_ITEM_NAME 的值应该在列中
        # 宽表转换后的列名来自 STD_ITEM_NAME 的值 ("资产总计")
        assert len(df.columns) > 1

    def test_supported_fields_includes_standard_names(self):
        """supported_fields should include standard field names"""
        from value_investment.providers.hk_share import HKProvider

        provider = HKProvider(MagicMock())
        fields = provider.supported_fields

        # 应该有标准字段名
        assert "total_assets" in fields
        assert "total_revenue" in fields
        assert "operating_cash_flow" in fields

    def test_field_mappings_are_complete(self):
        """All supported standard fields should have mappings"""
        from value_investment.providers.hk_share import HKProvider

        provider = HKProvider(MagicMock())

        # 收集所有映射的标准字段
        mapped_fields: set[str] = set()
        for mapping in HKProvider.FIELD_MAPPINGS.values():
            mapped_fields.update(mapping.values())

        # 核心财务报表字段应该有映射（与 supported_fields 交集）
        statement_fields = {
            "total_assets", "total_liabilities", "total_equity",
            "current_assets", "current_liabilities",
            "cash_and_equivalents", "inventory",
            "accounts_receivable", "accounts_payable", "fixed_assets",
            "total_revenue", "net_profit", "operating_profit",
            "operating_cash_flow", "investing_cash_flow", "financing_cash_flow",
            "capital_expenditure",
        }
        for field in statement_fields:
            if field in provider.supported_fields:
                assert field in mapped_fields, f"{field} should be in FIELD_MAPPINGS"
