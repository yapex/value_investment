"""Pipeline validator - Full validation including dry run"""
from dataclasses import dataclass, field
from typing import Any

from value_investment.calculator_plugin import registry, get_calculators
from value_investment.domain.fields import ALL_FIELDS

# 构建 calculator 映射
_CALCULATOR_MAP = {calc.name: calc for calc in get_calculators()}


@dataclass
class FieldInconsistency:
    """字段不一致问题"""
    field_name: str
    severity: str  # "error" 或 "warning"
    description: str
    resolution: str | None = None


@dataclass
class FieldStatus:
    """单个字段的状态"""
    name: str
    category: str  # "registered", "calculator", "handler_only", "unknown"
    available: bool
    sources: list[str] = field(default_factory=list)
    required_by: list[str] = field(default_factory=list)
    issue: str | None = None


@dataclass
class HandlerStatus:
    """Handler 的处理状态"""
    name: str
    market: str
    will_handle: bool
    fields: list[str] = field(default_factory=list)


@dataclass
class CalculatorStatus:
    """计算器的状态"""
    name: str
    will_run: bool
    required_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    issue: str | None = None


@dataclass
class ValidationReport:
    """完整的验证报告"""
    fields_requested: list[str]
    market: str
    symbol: str
    dry_run: bool
    
    # 字段状态
    field_statuses: dict[str, FieldStatus] = field(default_factory=dict)
    
    # Handler 状态
    handler_statuses: list[HandlerStatus] = field(default_factory=list)
    
    # Calculator 状态
    calculator_statuses: dict[str, CalculatorStatus] = field(default_factory=dict)
    
    # 扩展后的字段列表
    fields_expanded: set[str] = field(default_factory=set)
    
    # 不一致性问题 (注册 vs Handler 声明)
    inconsistencies: list[FieldInconsistency] = field(default_factory=list)
    
    # 问题汇总 (只有严重问题)
    issues: list[str] = field(default_factory=list)
    
    # 警告 (不阻塞)
    warnings: list[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """是否可以通过验证 (只看错误，不看警告)"""
        return len(self.issues) == 0
    
    def summary(self) -> str:
        """生成摘要"""
        lines = [
            "=" * 70,
            f"Pipeline Validation Report (dry_run={self.dry_run})",
            "=" * 70,
            f"Symbol: {self.symbol}",
            f"Market: {self.market}",
            f"Requested: {self.fields_requested}",
            f"Expanded:  {sorted(self.fields_expanded)}",
            "",
        ]
        
        # 错误 (阻塞)
        if self.issues:
            lines.append("❌ Errors (blocking):")
            for issue in self.issues:
                lines.append(f"   • {issue}")
            lines.append("")
        
        # 警告 (非阻塞)
        if self.warnings:
            lines.append("⚠️  Warnings (non-blocking):")
            for warning in self.warnings:
                lines.append(f"   • {warning}")
            lines.append("")
        
        # 字段问题
        field_issues = [f for f in self.field_statuses.values() if f.issue]
        if field_issues:
            lines.append("❌ Field Issues:")
            for f in field_issues:
                lines.append(f"   {f.name}: {f.issue}")
            lines.append("")
        
        # Calculator 状态
        calc_issues = [c for c in self.calculator_statuses.values() if c.issue]
        if calc_issues:
            lines.append("❌ Calculator Issues:")
            for c in calc_issues:
                lines.append(f"   {c.name}: {c.issue}")
                if c.missing_fields:
                    lines.append(f"      Missing: {c.missing_fields}")
            lines.append("")
        
        # 不一致性问题
        if self.inconsistencies:
            lines.append("📋 Field Inconsistencies:")
            for inc in self.inconsistencies:
                icon = "❌" if inc.severity == "error" else "⚠️ "
                lines.append(f"   {icon} {inc.field_name}: {inc.description}")
                if inc.resolution:
                    lines.append(f"      → {inc.resolution}")
            lines.append("")
        
        # Handler 状态
        lines.append("📋 Handlers:")
        for h in self.handler_statuses:
            icon = "✓" if h.will_handle else " "
            fields_count = f"({len(h.fields)} fields)" if h.fields else ""
            lines.append(f"   {icon} {h.name} [{h.market}] {fields_count}")
        lines.append("")
        
        # 最终结论
        if self.is_valid:
            if self.warnings:
                lines.append("✅ Passed with warnings")
            else:
                lines.append("✅ All checks passed!")
        else:
            lines.append(f"❌ {len(self.issues)} error(s) found")
        
        lines.append("=" * 70)
        return "\n".join(lines)


def validate_fields_registration(
    fields: list[str],
) -> dict[str, FieldStatus]:
    """检查字段是否在 ALL_FIELDS 中注册"""
    from value_investment.calculator_plugin import get_calculators

    _CALCULATOR_MAP = {calc.name: calc for calc in get_calculators()}
    
    statuses = {}
    
    for field in fields:
        if field in ALL_FIELDS:
            statuses[field] = FieldStatus(
                name=field,
                category="registered",
                available=True,
            )
        elif field in _CALCULATOR_MAP:
            statuses[field] = FieldStatus(
                name=field,
                category="calculator",
                available=True,
                issue="Calculator field not registered in ALL_FIELDS",
            )
        else:
            statuses[field] = FieldStatus(
                name=field,
                category="unknown",
                available=False,
                issue=f"Unknown field: {field}",
            )
    
    return statuses


def check_field_consistency(
    container: Any,
    market: str,
) -> list[FieldInconsistency]:
    """
    检查字段注册与 Handler 声明的一致性
    
    检测两种不一致:
    1. Handler 声明了能力，但字段未在 ALL_FIELDS 中注册 (警告)
    2. 字段在 ALL_FIELDS 中注册，但没有任何 Handler 能处理 (错误)
    """
    from value_investment.calculator_plugin import get_calculators

    _CALCULATOR_MAP = {calc.name: calc for calc in get_calculators()}
    
    inconsistencies = []
    
    # 收集所有 Handler 能处理的字段
    handler_fields: set[str] = set()
    for handler in container.bus().handlers:
        handler_fields.update(handler.can_handle)
    
    # 检查 Handler 声明了但 ALL_FIELDS 没注册 (警告)
    handler_only = handler_fields - ALL_FIELDS
    for field in sorted(handler_only):
        # 排除 calculator 字段 (它们本来就不在 ALL_FIELDS 中)
        if field not in _CALCULATOR_MAP:
            inconsistencies.append(FieldInconsistency(
                field_name=field,
                severity="warning",
                description=f"Handler declares '{field}' but not registered in ALL_FIELDS",
                resolution="Add to ALL_FIELDS or remove from Handler",
            ))
    
    # 检查 ALL_FIELDS 注册了但 Handler 不能处理 (错误)
    # 只检查核心字段，不包括 calculator
    registered_but_no_handler = ALL_FIELDS - handler_fields - set(_CALCULATOR_MAP.keys())
    for field in sorted(registered_but_no_handler):
        inconsistencies.append(FieldInconsistency(
            field_name=field,
            severity="error",
            description=f"'{field}' registered in ALL_FIELDS but no Handler can provide it",
            resolution="Add field to a Handler or remove from ALL_FIELDS",
        ))
    
    return inconsistencies


def expand_required_fields(
    fields: list[str],
) -> tuple[set[str], list[str]]:
    """扩展字段以包含计算器依赖"""
    from value_investment.calculator_plugin import get_calculators

    _CALCULATOR_MAP = {calc.name: calc for calc in get_calculators()}
    
    expanded = set(fields)
    calculators_to_run = []
    
    for field in fields:
        if field in _CALCULATOR_MAP:
            calc = _CALCULATOR_MAP[field]
            expanded.update(calc.required_fields)
            calculators_to_run.append(field)
    
    return expanded, calculators_to_run


def validate_handlers(
    container: Any,
    fields: set[str],
    market: str,
) -> list[HandlerStatus]:
    """检查哪些 Handler 会处理这些字段"""
    statuses = []
    seen_handlers = set()
    
    for handler in container.bus().handlers:
        handler_name = type(handler).__name__
        
        if handler_name in seen_handlers:
            continue
        seen_handlers.add(handler_name)
        
        will_handle = (
            handler.target_market == market and
            bool(handler.can_handle & fields)
        )
        
        handled_fields = list(handler.can_handle & fields)
        
        statuses.append(HandlerStatus(
            name=handler_name,
            market=handler.target_market,
            will_handle=will_handle,
            fields=handled_fields,
        ))
    
    return statuses


def validate_calculators_fields(
    fields: set[str],
    calculator_fields: list[str],
    handler_fields: set[str],
) -> dict[str, CalculatorStatus]:
    """验证计算器是否能运行"""
    from value_investment.calculator_plugin import get_calculators

    _CALCULATOR_MAP = {calc.name: calc for calc in get_calculators()}
    
    statuses = {}
    
    for field in calculator_fields:
        calc = _CALCULATOR_MAP[field]
        required = calc.required_fields
        missing = required - handler_fields
        
        will_run = len(missing) == 0
        
        issue = None
        if missing:
            issue = f"Missing {len(missing)} required field(s)"
        
        statuses[field] = CalculatorStatus(
            name=field,
            will_run=will_run,
            required_fields=list(required),
            missing_fields=list(missing),
            issue=issue,
        )
    
    return statuses


def validate_pipeline(
    fields: list[str],
    symbol: str,
    market: str,
    dry_run: bool = True,
) -> ValidationReport:
    """
    完整 pipeline 验证
    """
    from value_investment.pipeline.container import Container
    from value_investment.calculator_plugin import get_calculators

    _CALCULATOR_MAP = {calc.name: calc for calc in get_calculators()}

    # 重置并获取 container
    Container._instance = None
    container = Container.create()

    # Step 1: 检查字段注册
    field_statuses = validate_fields_registration(fields)

    # Step 2: 检查一致性
    inconsistencies = check_field_consistency(container, market)

    # Step 3: 扩展字段
    fields_expanded, calculator_fields = expand_required_fields(fields)

    # Step 4: 检查 Handler
    handler_statuses = validate_handlers(container, fields_expanded, market)

    # 收集 Handler 能提供的字段（按市场）
    handler_fields: set[str] = set()
    for h in handler_statuses:
        if h.will_handle:
            handler_fields.update(h.fields)

    # Step 5: 验证 Calculator

    # Step 5.5: 检查该市场是否有有效的 Handler 能提供请求的字段
    market_handlers = [h for h in handler_statuses if h.market == market and h.will_handle]
    market_available: set[str] = set()
    for h in market_handlers:
        market_available.update(h.fields)

    # 标准字段（非 calculator）必须有 handler 能提供
    standard_fields = fields_expanded - set(_CALCULATOR_MAP.keys())
    missing_in_market = standard_fields - market_available
    if missing_in_market:
        inconsistencies.append(FieldInconsistency(
            field_name="market_coverage",
            severity="error",
            description=(
                f"Market '{market}': {len(missing_in_market)} field(s) cannot be fetched "
                f"({sorted(missing_in_market)}). "
                f"No working Handler with Provider found for this market."
            ),
            resolution="Implement Provider with fetch_financial_data for this market, "
                      "or ensure Handler has Provider injected",
        ))
    calculator_statuses = validate_calculators_fields(
        fields_expanded,
        calculator_fields,
        handler_fields,
    )
    
    # 收集问题 (只有错误)
    issues = []
    warnings = []
    
    # 字段问题
    for fs in field_statuses.values():
        if fs.issue:
            issues.append(f"Field {fs.name}: {fs.issue}")
    
    # Calculator 问题
    for cs in calculator_statuses.values():
        if cs.issue:
            issues.append(f"Calculator {cs.name}: {cs.issue}")
    
    # 一致性问题分类
    for inc in inconsistencies:
        if inc.severity == "error":
            issues.append(f"Field inconsistency: {inc.description}")
        else:
            warnings.append(f"Field inconsistency: {inc.description}")
    
    return ValidationReport(
        fields_requested=fields,
        market=market,
        symbol=symbol,
        dry_run=dry_run,
        field_statuses=field_statuses,
        handler_statuses=handler_statuses,
        calculator_statuses=calculator_statuses,
        fields_expanded=fields_expanded,
        inconsistencies=inconsistencies,
        issues=issues,
        warnings=warnings,
    )


def assert_pipeline_valid(
    fields: list[str],
    symbol: str,
    market: str,
) -> ValidationReport:
    """断言 pipeline 配置有效，如果无效则抛出异常"""
    report = validate_pipeline(fields, symbol, market)
    
    if not report.is_valid:
        raise AssertionError(f"Pipeline validation failed:\n{report.summary()}")
    
    return report


# ============================================================
# 旧版 API (保持向后兼容)
# ============================================================

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
    """旧版: 验证计算器依赖"""
    from value_investment.pipeline.container import Container
    from value_investment.calculator_plugin import get_calculators
    all_calcs = get_calculators()
    
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
    """旧版: 获取验证摘要"""
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
    """旧版: 断言所有计算器有效"""
    results = validate_calculators(calculators)
    missing = [r for r in results if r.status == "MISSING_DEPS"]
    
    if missing:
        raise AssertionError(f"{len(missing)} calculators have missing dependencies:\n{get_validation_summary(results)}")
