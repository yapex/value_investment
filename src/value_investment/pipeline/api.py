"""Pipeline API - High-level interface for financial data pipeline"""
import warnings
from typing import Any

from value_investment.pipeline.bus.message import Message
from value_investment.pipeline.container import Container
from value_investment.pipeline.calculators import CALCULATOR_MAP
from value_investment.pipeline.fields import ALL_FIELDS


class PipelineAPI:
    """High-level API for financial data pipeline

    Usage:
        api = PipelineAPI()
        result = await api.get_data("600519", ["roic", "roe"], end="2024", years=10)
    """

    def __init__(self, container: Container | None = None):
        self._container = container or Container.create()

    @property
    def container(self) -> Container:
        return self._container

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

        # 通过消息总线获取数据（Handler 自动路由）
        await self._container.bus().process(message)

        # 计算派生字段 (Calculator)
        self._apply_calculators(message)

        # 检查是否所有字段都获取到了
        if message.require:
            missing = message.require
            raise ValueError(f"Missing fields: {missing}")

        return message.results

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
