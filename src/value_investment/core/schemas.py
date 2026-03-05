
import pandera.pandas as pa
from pandera import Field


class CoreFinancialSchema(pa.DataFrameModel):
    """Core financial fields - required for 90% of indicators"""

    year: int = Field(gt=1990)

    # Required fields
    net_profit: float = Field()
    total_equity: float = Field(gt=0)
    total_assets: float = Field(gt=0)
    revenue: float = Field(gt=0)

    # Optional fields
    operating_cash_flow: float | None = Field(nullable=True)
    operating_profit: float | None = Field(nullable=True)
    total_liabilities: float | None = Field(nullable=True)
    current_assets: float | None = Field(nullable=True)
    current_liabilities: float | None = Field(nullable=True)

    class Config:
        strict = False  # Allow extra columns

class CoreFinancialSchemaLite(pa.DataFrameModel):
    """Minimal schema - only year and one financial metric"""

    year: int = Field(gt=1990)

    # At least one of these must be present
    net_profit: float | None = Field(nullable=True)
    revenue: float | None = Field(nullable=True)
    total_assets: float | None = Field(nullable=True)
