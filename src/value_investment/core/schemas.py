import pandera.pandas as pa
from pandera import Field, Check
from typing import Optional

class CoreFinancialSchema(pa.DataFrameModel):
    """Core financial fields - required for 90% of indicators"""

    year: int = Field(gt=1990)

    # Required fields
    net_profit: float = Field()
    total_equity: float = Field(gt=0)
    total_assets: float = Field(gt=0)
    revenue: float = Field(gt=0)

    # Optional fields
    operating_cash_flow: Optional[float] = Field(nullable=True)
    operating_profit: Optional[float] = Field(nullable=True)
    total_liabilities: Optional[float] = Field(nullable=True)
    current_assets: Optional[float] = Field(nullable=True)
    current_liabilities: Optional[float] = Field(nullable=True)

    class Config:
        strict = False  # Allow extra columns

class CoreFinancialSchemaLite(pa.DataFrameModel):
    """Minimal schema - only year and one financial metric"""

    year: int = Field(gt=1990)

    # At least one of these must be present
    net_profit: Optional[float] = Field(nullable=True)
    revenue: Optional[float] = Field(nullable=True)
    total_assets: Optional[float] = Field(nullable=True)
