import pytest
import pandas as pd
from value_investment.core.schemas import CoreFinancialSchema, CoreFinancialSchemaLite

def test_schema_valid_data():
    """Schema should pass with valid data"""
    data = pd.DataFrame({
        'year': [2024, 2023],
        'net_profit': [100.0, 90.0],
        'total_equity': [500.0, 450.0],
        'total_assets': [1000.0, 900.0],
        'revenue': [800.0, 700.0],
    })

    # Should not raise
    validated = CoreFinancialSchema.validate(data)
    assert not validated.empty

def test_schema_rejects_missing_required_fields():
    """Schema should fail with missing required fields"""
    data = pd.DataFrame({
        'year': [2024],
        'net_profit': [100.0],
        # Missing: total_equity, total_assets, revenue
    })

    with pytest.raises(Exception):
        CoreFinancialSchema.validate(data)
