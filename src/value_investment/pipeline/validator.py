"""Pipeline validator utilities"""
from dataclasses import dataclass


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


def validate_calculators(calculators: list) -> list[ValidationResult]:
    """Validate Calculator dependencies can be satisfied by Handlers"""
    from value_investment.pipeline.container import Container
    
    Container._instance = None
    container = Container.create()
    
    # Build field -> Handler index
    field_sources = {}
    for handler in container.bus().handlers:
        for field in handler.can_handle:
            field_sources.setdefault(field, []).append(type(handler).__name__)
    
    results = []
    
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
