"""Pipeline validator utilities"""
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DependencyStatus:
    field: str
    available: bool
    source: str


@dataclass
class ValidationResult:
    calculator: str
    status: str
    details: list[DependencyStatus]


def discover_calculators(package_file: str) -> list:
    """Discover all Calculator instances in a package directory"""
    import sys
    
    instances = []
    seen_names = set()
    
    package_path = Path(package_file).parent
    package_name = package_path.name  # e.g., "calculators"
    parent_path = str(package_path.parent)  # e.g., ".../pipeline"
    full_package = f"value_investment.pipeline.{package_name}"
    
    # Add parent to path if needed
    if parent_path not in sys.path:
        sys.path.insert(0, parent_path)
    
    for file in package_path.glob("*.py"):
        if file.name in ("__init__.py", "protocol.py"):
            continue
        if file.name.startswith("_"):
            continue
        
        module_name = file.stem
        full_module_name = f"{full_package}.{module_name}"
        
        try:
            module = importlib.import_module(full_module_name)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if not (inspect.isclass(attr) and attr.__module__ == full_module_name):
                    continue
                
                if not _implements_calculator(attr):
                    continue
                
                try:
                    instance = attr()
                    if instance.name not in seen_names:
                        instances.append(instance)
                        seen_names.add(instance.name)
                except Exception as e:
                    print(f"⚠️  Failed to instantiate {attr_name}: {e}")
                    
        except Exception as e:
            print(f"⚠️  Failed to import {full_module_name}: {e}")
    
    return instances


def _implements_calculator(cls) -> bool:
    """Check if a class implements Calculator Protocol (duck typing)"""
    # Must have these attributes
    if not hasattr(cls, "name"):
        return False
    if not hasattr(cls, "required_fields"):
        return False
    if not hasattr(cls, "calculate"):
        return False
    
    # calculate must be callable
    if not callable(getattr(cls, "calculate", None)):
        return False
    
    return True


def validate_calculators(calculators: list) -> list[ValidationResult]:
    """Validate Calculator dependencies can be satisfied by Handlers"""
    from value_investment.pipeline.container import Container
    
    Container._instance = None
    container = Container.create()
    
    # Build field -> Handler index
    field_sources: dict[str, list[str]] = {}
    for handler in container.bus().handlers:
        for field in handler.can_handle:
            field_sources.setdefault(field, []).append(type(handler).__name__)
    
    results: list[ValidationResult] = []
    
    for calc in calculators:
        details = []
        all_available = True
        
        for field in calc.required_fields:
            sources = field_sources.get(field, [])
            details.append(
                DependencyStatus(
                    field=field,
                    available=len(sources) > 0,
                    source=", ".join(sources) if sources else "MISSING",
                )
            )
            if not sources:
                all_available = False
        
        results.append(
            ValidationResult(
                calculator=calc.name,
                status="OK" if all_available else "MISSING_DEPS",
                details=details,
            )
        )
    
    return results


def get_validation_summary(results: list[ValidationResult]) -> str:
    """Get validation summary for display"""
    ok_count = sum(1 for r in results if r.status == "OK")
    missing_count = sum(1 for r in results if r.status == "MISSING_DEPS")
    
    lines = ["=" * 60, "Pipeline Calculator Validation", "=" * 60]
    
    for r in results:
        icon = "✅" if r.status == "OK" else "❌"
        lines.append(f"\n{icon} {r.calculator}")
        for d in r.details:
            mark = "✓" if d.available else "✗"
            source = d.source if d.available else "⚠️  No Handler"
            lines.append(f"    {mark} {d.field:35} → {source}")
    
    lines.extend(["", "=" * 60, f"Total: {ok_count} OK, {missing_count} Missing", "=" * 60])
    return "\n".join(lines)


def assert_all_valid(calculators: list) -> None:
    """Assert all calculators have valid dependencies"""
    results = validate_calculators(calculators)
    missing = [r for r in results if r.status == "MISSING_DEPS"]
    
    if missing:
        raise AssertionError(f"{len(missing)} calculators have missing dependencies:\n{get_validation_summary(results)}")
