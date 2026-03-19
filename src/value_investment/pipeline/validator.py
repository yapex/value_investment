"""Pipeline dependency validator

Validates that all Calculator dependencies can be satisfied by registered Handlers.
"""
from dataclasses import dataclass
from typing import TypedDict


@dataclass
class DependencyStatus:
    field: str
    available: bool
    source: str  # Handler name or "MISSING"


@dataclass
class ValidationResult:
    calculator: str
    status: str  # "OK" or "MISSING_DEPS"
    details: list[DependencyStatus]


def validate_calculators() -> list[ValidationResult]:
    """Validate all Calculator dependencies can be satisfied by Handlers

    Returns:
        List of validation results for each Calculator
    """
    from value_investment.pipeline.container import Container
    from value_investment.pipeline.calculators import ALL_CALCULATORS

    Container._instance = None
    container = Container.create()

    # Build field -> Handler index
    field_sources: dict[str, list[str]] = {}
    for handler in container.bus().handlers:
        for field in handler.can_handle:
            field_sources.setdefault(field, []).append(type(handler).__name__)

    # Validate each Calculator
    results = []
    for calc in ALL_CALCULATORS:
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
    """Get a summary string for test assertions"""
    ok_count = sum(1 for r in results if r.status == "OK")
    missing_count = sum(1 for r in results if r.status == "MISSING_DEPS")

    lines = [
        "=" * 60,
        "Pipeline Calculator Dependency Validation",
        "=" * 60,
    ]

    for r in results:
        status_icon = "✅" if r.status == "OK" else "❌"
        lines.append(f"\n{status_icon} {r.calculator}")

        for d in r.details:
            icon = "✓" if d.available else "✗"
            source = d.source if d.available else "⚠️  No Handler supports this field"
            lines.append(f"    {icon} {d.field:35} → {source}")

    lines.append("")
    lines.append("=" * 60)
    lines.append(f"Total: {ok_count} OK, {missing_count} Missing")
    lines.append("=" * 60)

    return "\n".join(lines)


def assert_all_calculators_valid() -> None:
    """Assert all Calculators have valid dependencies

    Raises:
        AssertionError: If any Calculator has missing dependencies
    """
    results = validate_calculators()
    missing = [r for r in results if r.status == "MISSING_DEPS"]

    if missing:
        summary = get_validation_summary(results)
        raise AssertionError(
            f"{len(missing)} Calculator(s) have missing dependencies:\n{summary}"
        )
