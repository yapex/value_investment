import pytest
import pandas as pd
from value_investment.core.validation import ValidationPipeline, ValidationError

def test_pipeline_passes_valid_data():
    pipeline = ValidationPipeline()
    data = pd.DataFrame({
        'year': [2024],
        'net_profit': [100.0],
        'total_equity': [500.0],
        'total_assets': [1000.0],
        'revenue': [800.0],
    })

    result = pipeline.validate(data)
    assert result is not None

def test_pipeline_raises_on_invalid_data():
    pipeline = ValidationPipeline()
    data = pd.DataFrame({
        'year': [2024],
        # Missing all required fields
    })

    with pytest.raises(ValidationError) as exc_info:
        pipeline.validate(data)

    assert 'net_profit' in str(exc_info.value)
