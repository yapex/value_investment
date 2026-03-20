"""Domain layer - core business logic"""
from value_investment.domain.fields import (
    IFRSFields,
    SourceFields,
    IndicatorFields,
    ALL_FIELDS,
    validate_fields,
    get_source_fields,
    get_indicator_fields,
)

# 向后兼容
CustomFields = SourceFields

__all__ = [
    "IFRSFields",
    "SourceFields",
    "IndicatorFields",
    "CustomFields",
    "ALL_FIELDS",
    "validate_fields",
    "get_source_fields",
    "get_indicator_fields",
]
