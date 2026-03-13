"""Tests for indicator factory"""
import pandas as pd
import pytest

from value_investment.indicators.factory import IndicatorFactory


class TestIndicatorFactory:
    """Test IndicatorFactory"""
    
    def test_create(self):
        """Test factory creation"""
        factory = IndicatorFactory()
        assert factory is not None
    
    def test_register_and_get(self):
        """Test register and get indicator"""
        from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType
        
        class CustomIndicator(BaseIndicator):
            name = "custom_test"
            description = "Custom indicator"
            type = IndicatorType.CALCULATED
            
            def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
                return IndicatorResult(value=1.0, unit='%', description='Custom')
        
        factory = IndicatorFactory()
        factory.register(CustomIndicator())
        indicator = factory.get("custom_test")
        assert indicator is not None
