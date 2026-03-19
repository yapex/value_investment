"""Optional decorator for Calculator registration

Usage (optional - auto-discovery works without it):
    from value_investment.pipeline.calculators import calculator

    @calculator
    class ROICCalculator:
        name = "roic"
        required_fields = {...}
        ...

Or without decorator (auto-discovery still works):
    class ROICCalculator:
        name = "roic"
        ...
"""
from typing import TypeVar, Type

T = TypeVar('T')


def calculator(cls: Type[T]) -> Type[T]:
    """Decorator to explicitly mark a class as a Calculator
    
    This is OPTIONAL. Auto-discovery will find Calculator classes
    even without this decorator.
    
    Benefits:
    - Makes intent explicit
    - IDE autocomplete support
    - Documentation clarity
    
    Args:
        cls: Calculator class to register
        
    Returns:
        Same class (no modification)
    """
    # Mark the class for clarity (no actual registration needed)
    setattr(cls, '_is_calculator', True)
    return cls
