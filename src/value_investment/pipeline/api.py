"""Pipeline API - High-level interface for financial data pipeline"""
import warnings
from typing import Any

from value_investment.core.types import Message
from value_investment.pipeline.container import Container
from value_investment.calculator_plugin import registry
from value_investment.domain.fields import ALL_FIELDS
from value_investment.pipeline.validator import validate_pipeline, ValidationReport

CALCULATOR_MAP = {calc.name: calc for calc in registry.get_all()}


class PipelineAPI:
    """High-level API for financial data pipeline

    Usage:
        api = PipelineAPI()
        result = await api.get_data("600519", ["roic", "roe"], end="2024", years=10)

    Dry Run:
        # Validate without fetching actual data
        report = api.validate("600519", ["implied_growth"], market="港股")
        print(report.summary())
    """

    def __init__(self, container: Container | None = None):
        self._container = container or Container.create()

    @property
    def container(self) -> Container:
        return self._container

    def validate(
        self,
        symbol: str,
        fields: list[str],
        market: str | None = None,
    ) -> ValidationReport:
        """
        Validate pipeline configuration without fetching actual data.
        
        This is a "dry run" that checks:
        1. All requested fields are registered
        2. Calculator dependencies can be satisfied
        3. Which Handlers will process the request
        
        Args:
            symbol: Stock code
            fields: List of field names to validate
            market: Market (auto-detected if None)
        
        Returns:
            ValidationReport with detailed status
        """
        if market is None:
            market = self._detect_market(symbol)
        
        return validate_pipeline(fields, symbol, market, dry_run=True)

    async def get_data(
        self,
        symbol: str,
        fields: list[str],
        end: str = "2024",
        years: int = 10,
        market: str | None = None,
    ) -> dict[str, dict[int, Any]]:
        """Get financial data with calculated fields

        Args:
            symbol: Stock code
            fields: List of field names
            end: End year
            years: Number of years
            market: Market (auto-detected if None)

        Returns:
            {field: {year: value}}

        Raises:
            ValueError: If fields missing
        """
        # 检测未知字段并警告
        unknown_fields = set(fields) - ALL_FIELDS
        if unknown_fields:
            warnings.warn(
                f"Unknown fields requested (will be ignored): {sorted(unknown_fields)}",
                UserWarning,
                stacklevel=2,
            )

        # 自动检测市场
        if market is None:
            market = self._detect_market(symbol)

        # 创建消息
        message = Message(
            symbol=symbol,
            market=market,
            end=end,
            years=years,
            require=set(fields),
        )

        # 扩展 require 以包含计算器所需的字段
        self._expand_required_fields(message)

        # 通过消息总线获取数据（Handler 自动路由）
        await self._container.bus().process(message)

        # 计算派生字段 (Calculator)
        self._apply_calculators(message)

        # 检查是否所有字段都获取到了
        if message.require:
            missing = message.require
            raise ValueError(f"Missing fields: {missing}")

        return message.results

    def _expand_required_fields(self, message: Message) -> None:
        """Expand require set to include calculator's required fields

        This ensures that when a calculated field is requested, the
        underlying data fields are also fetched.

        Args:
            message: Message with require set
        """
        # 首先收集所有需要扩展的字段
        fields_to_expand = []
        for field in message.require:
            if field in CALCULATOR_MAP:
                fields_to_expand.append(field)

        # 然后扩展 require
        for field in fields_to_expand:
            calculator = CALCULATOR_MAP[field]
            message.require.update(calculator.required_fields)

    def _apply_calculators(self, message: Message) -> None:
        """Apply calculators for derived fields

        Args:
            message: Message with require set and results dict
        """
        # 找出需要计算的字段
        fields_to_calculate = message.require & set(CALCULATOR_MAP.keys())

        for field in fields_to_calculate:
            calculator = CALCULATOR_MAP[field]
            # 检查 required_fields 是否都已获取
            missing_required = calculator.required_fields - set(message.results.keys())
            if missing_required:
                continue

            # 执行计算
            calculated = calculator.calculate(message.results)
            if calculated:
                message.results[field] = calculated
                message.require.discard(field)

    def _detect_market(self, symbol: str) -> str:
        """Detect market from symbol"""
        # 港股: 5位数字
        if len(symbol) == 5 and symbol.isdigit():
            return "港股"
        # A股: 6位数字 (0/3/6开头)
        elif len(symbol) == 6 and symbol.isdigit() and symbol.startswith(("0", "3", "6")):
            return "A股"
        # 美股: 字母
        else:
            return "美股"
