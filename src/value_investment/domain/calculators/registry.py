"""Calculator registry and decorator

All calculators must be decorated with @calculator to be discovered.
This makes registration explicit and avoids implicit conventions.

Usage:
    from value_investment.domain.calculators import calculator

    @calculator
    class ROICCalculator:
        name = "roic"
        required_fields = {...}
        
        def calculate(self, results):
            return {...}
"""
from typing import Any


# Global registry for calculators
_calculators: list = []


def calculator(cls):
    """Decorator to register a Calculator
    
    Must be used on all Calculator classes. Without this decorator,
    the class will NOT be discovered.
    
    Args:
        cls: Calculator class to register
        
    Returns:
        Same class (unchanged)
        
    Raises:
        ValueError: If class doesn't have required attributes
    """
    # Validate required attributes
    required_attrs = ["name", "required_fields", "calculate"]
    for attr in required_attrs:
        if not hasattr(cls, attr):
            raise ValueError(
                f"Calculator class '{cls.__name__}' is missing required attribute '{attr}'. "
                f"Calculator must have: {', '.join(required_attrs)}"
            )
    
    # Validate 'calculate' is callable
    if not callable(getattr(cls, "calculate", None)):
        raise ValueError(
            f"Calculator class '{cls.__name__}' has 'calculate' attribute but it's not callable"
        )
    
    # Register the class (not instance - instantiation happens later)
    _calculators.append(cls)
    
    return cls


def get_registered_calculators() -> list:
    """Get all registered Calculator classes"""
    return list(_calculators)


def clear_registry() -> None:
    """Clear registry (for testing)"""
    _calculators.clear()


def instantiate_calculators() -> list:
    """Instantiate all registered calculators"""
    instances = []
    for cls in _calculators:
        try:
            instances.append(cls())
        except Exception as e:
            print(f"⚠️  Failed to instantiate {cls.__name__}: {e}")
    return instances
