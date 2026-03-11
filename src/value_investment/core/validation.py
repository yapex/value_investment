from dataclasses import dataclass

import pandas as pd

from value_investment.core.schemas import CoreFinancialSchema


@dataclass
class ValidationError(Exception):
    """Validation error with details"""
    message: str
    missing_fields: list = None

    def __str__(self):
        return self.message

class ValidationPipeline:
    """Pipeline that validates data through schemas"""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.schema = CoreFinancialSchema

    def validate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate DataFrame through schema"""
        if data is None or data.empty:
            raise ValidationError("Empty DataFrame provided")

        try:
            validated = self.schema.validate(data)
            return validated
        except Exception as e:
            # Extract missing fields from error
            missing = []
            error_str = str(e)
            if 'net_profit' in error_str:
                missing.append('net_profit')
            if 'total_equity' in error_str:
                missing.append('total_equity')
            if 'total_assets' in error_str:
                missing.append('total_assets')
            if 'revenue' in error_str:
                missing.append('revenue')

            raise ValidationError(
                message=f"Validation failed: {str(e)}",
                missing_fields=missing
            )
