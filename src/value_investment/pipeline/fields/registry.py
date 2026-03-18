"""Fields Registry - Standard field definitions for financial data

This module provides a centralized registry of all standard fields used in the system.
All calculators and handlers should reference fields from this registry rather than
hardcoding field names.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldMeta:
    """Metadata for a field"""
    name: str
    display_name: str
    description: str
    unit: str  # "%", "CNY", "USD", "ratio", etc.
    depends_on: list[str] = field(default_factory=list)  # For calculated fields
    is_raw: bool = True  # True for data fields, False for calculated fields


class FieldRegistry:
    """Registry of all standard fields"""
    
    _instance = None
    
    def __init__(self):
        self._fields: dict[str, FieldMeta] = {}
        self._register_all_fields()
    
    @classmethod
    def get_instance(cls) -> "FieldRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _register_all_fields(self):
        """Register all standard fields"""
        # Raw fields (from financial statements)
        raw_fields = [
            # Income Statement
            FieldMeta(
                name="net_profit",
                display_name="净利润",
                description="Net profit after tax",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="operating_profit",
                display_name="营业利润",
                description="Operating profit",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="gross_profit",
                display_name="毛利",
                description="Gross profit",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="revenue",
                display_name="营业总收入",
                description="Total revenue",
                unit="CNY",
                is_raw=True,
            ),
            # Balance Sheet
            FieldMeta(
                name="total_assets",
                display_name="资产总计",
                description="Total assets",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="total_equity",
                display_name="股东权益合计",
                description="Total equity",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="cash_and_equivalents",
                display_name="货币资金",
                description="Cash and cash equivalents",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="current_liabilities",
                display_name="流动负债合计",
                description="Current liabilities",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="total_liabilities",
                display_name="负债合计",
                description="Total liabilities",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="current_assets",
                display_name="流动资产合计",
                description="Current assets",
                unit="CNY",
                is_raw=True,
            ),
            FieldMeta(
                name="non_current_assets",
                display_name="非流动资产合计",
                description="Non-current assets",
                unit="CNY",
                is_raw=True,
            ),
        ]
        
        # Calculated fields (indicators)
        calculated_fields = [
            FieldMeta(
                name="roe",
                display_name="净资产收益率",
                description="Return on Equity",
                unit="%",
                depends_on=["net_profit", "total_equity"],
                is_raw=False,
            ),
            FieldMeta(
                name="roa",
                display_name="总资产报酬率",
                description="Return on Assets",
                unit="%",
                depends_on=["operating_profit", "total_assets"],
                is_raw=False,
            ),
            FieldMeta(
                name="roic",
                display_name="投入资本回报率",
                description="Return on Invested Capital",
                unit="%",
                depends_on=["operating_profit", "total_assets", "cash_and_equivalents", "current_liabilities"],
                is_raw=False,
            ),
            FieldMeta(
                name="gross_profit_margin",
                display_name="销售毛利率",
                description="Gross Profit Margin",
                unit="%",
                depends_on=["gross_profit", "revenue"],
                is_raw=False,
            ),
            FieldMeta(
                name="net_profit_margin",
                display_name="销售净利率",
                description="Net Profit Margin",
                unit="%",
                depends_on=["net_profit", "revenue"],
                is_raw=False,
            ),
        ]
        
        for f in raw_fields + calculated_fields:
            self._fields[f.name] = f
    
    def get_field(self, name: str) -> FieldMeta | None:
        """Get field metadata by name"""
        return self._fields.get(name)
    
    def list_raw_fields(self) -> list[FieldMeta]:
        """List all raw fields"""
        return [f for f in self._fields.values() if f.is_raw]
    
    def list_calculated_fields(self) -> list[FieldMeta]:
        """List all calculated fields"""
        return [f for f in self._fields.values() if not f.is_raw]
    
    def get_dependencies(self, field_name: str) -> list[str]:
        """Get dependencies for a calculated field"""
        field = self.get_field(field_name)
        if field:
            return field.depends_on
        return []


def get_registry() -> FieldRegistry:
    """Get the global field registry instance"""
    return FieldRegistry.get_instance()


# Convenience constants for quick access
_registry = get_registry()
RAW_FIELDS = {f.name for f in _registry.list_raw_fields()}
CALCULATED_FIELDS = {f.name for f in _registry.list_calculated_fields()}
