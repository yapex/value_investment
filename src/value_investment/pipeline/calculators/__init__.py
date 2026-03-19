"""Calculators module - Auto-discovery and registration

All .py files in this directory (except __init__.py) are automatically
discovered and registered. No manual registration needed.

Usage:
    from value_investment.pipeline.calculators import CALCULATOR_MAP
    
    # Use a calculator
    calc = CALCULATOR_MAP["gross_profit"]
"""
import importlib
import pkgutil
from pathlib import Path

from value_investment.pipeline.calculators.gross_profit import GrossProfitCalculator
from value_investment.pipeline.calculators.implied_growth import ImpliedGrowthCalculator
from value_investment.pipeline.calculators.inventory_turnover import InventoryTurnoverCalculator

# Core calculators (always available)
CORE_CALCULATORS = [
    GrossProfitCalculator(),
    ImpliedGrowthCalculator(),
    InventoryTurnoverCalculator(),
]


def _discover_calculators() -> list:
    """Auto-discover all Calculator classes in this directory
    
    Scans all .py files (except __init__.py) and instantiates classes
    that have 'Calculator' in their name.
    
    Validates required_fields against IFRSFields.all().
    
    Returns:
        List of Calculator instances (deduplicated by name)
    """
    from value_investment.pipeline.fields import ALL_FIELDS
    
    calculators = []
    seen_names = set()
    
    # Get current package path
    package_path = Path(__file__).parent
    package_name = __name__
    
    # Scan all .py files
    for file in package_path.glob("*.py"):
        if file.name in ("__init__.py",):
            continue
        if file.name.startswith("_"):
            continue
        
        # Import module
        module_name = file.stem
        full_module_name = f"{package_name}.{module_name}"
        
        try:
            module = importlib.import_module(full_module_name)
            
            # Find Calculator classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a Calculator class (not imported)
                if (isinstance(attr, type) and 
                    "Calculator" in attr_name and
                    attr.__module__ == full_module_name):
                    
                    # Instantiate and validate
                    try:
                        calc = attr()
                        
                        # Validate required_fields
                        invalid_fields = set(calc.required_fields) - ALL_FIELDS
                        if invalid_fields:
                            raise ValueError(
                                f"Calculator '{calc.name}' has invalid required_fields: {invalid_fields}. "
                                f"Valid fields are in IFRSFields or CustomFields."
                            )
                        
                        if calc.name not in seen_names:
                            calculators.append(calc)
                            seen_names.add(calc.name)
                            
                    except ValueError:
                        # Re-raise validation errors
                        raise
                    except Exception as e:
                        print(f"⚠️  Warning: Failed to instantiate {attr_name}: {e}")
                        
        except Exception as e:
            # Re-raise import/validation errors
            if "invalid required_fields" in str(e):
                raise
            print(f"⚠️  Warning: Failed to import {full_module_name}: {e}")
    
    return calculators


# Auto-discover and register all calculators
ALL_CALCULATORS = _discover_calculators()

# name -> calculator 映射
CALCULATOR_MAP = {calc.name: calc for calc in ALL_CALCULATORS}

# Export core calculators for direct import
__all__ = [
    "GrossProfitCalculator",
    "ImpliedGrowthCalculator", 
    "InventoryTurnoverCalculator",
    "ALL_CALCULATORS",
    "CALCULATOR_MAP",
]
