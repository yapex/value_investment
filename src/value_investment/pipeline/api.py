"""Pipeline API - High-level interface for financial data pipeline"""
from typing import Any

from value_investment.pipeline.bus.message import Message
from value_investment.pipeline.container import Container
from value_investment.pipeline.fields import CustomFields


class PipelineAPI:
    """High-level API for financial data pipeline

    Usage:
        api = PipelineAPI()
        result = await api.get_indicator("600519", "roic", end="2024", years=10)
    """

    def __init__(self, container: Container | None = None):
        self._container = container or Container.create()

    @property
    def container(self) -> Container:
        return self._container

    async def get_indicator(
        self,
        symbol: str,
        indicator: str,
        end: str = "2024",
        years: int = 10,
        market: str | None = None,
    ) -> dict[int, float]:
        """Get financial indicator

        Args:
            symbol: Stock code
            indicator: Indicator name (e.g., "roic", "roe")
            end: End year
            years: Number of years
            market: Market (auto-detected if None)

        Returns:
            {year: indicator_value}

        Raises:
            ValueError: If indicator unknown or fields missing
        """
        # 自动检测市场
        if market is None:
            market = self._detect_market(symbol)

        # 获取计算器
        calculator = self._get_calculator(indicator)

        # 创建消息
        message = Message(
            symbol=symbol,
            market=market,
            end=end,
            years=years,
            require=calculator.required_fields.copy(),
        )

        # 通过消息总线获取数据
        await self._container.bus().process(message)

        # 检查是否所有字段都获取到了
        if message.require:
            missing = message.require
            raise ValueError(f"Missing fields: {missing}")

        # 计算指标
        return calculator.calculate(message.results)

    async def get_data(
        self,
        symbol: str,
        fields: list[str],
        end: str = "2024",
        years: int = 10,
        market: str | None = None,
    ) -> dict[str, dict[int, Any]]:
        """Get raw financial data (no calculation)

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

        # 通过消息总线获取数据
        await self._container.bus().process(message)

        # 检查是否所有字段都获取到了
        if message.require:
            missing = message.require
            raise ValueError(f"Missing fields: {missing}")

        return message.results

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

    def _get_calculator(self, name: str):
        """Get calculator by name"""
        from value_investment.pipeline.calculators.roic import ROICCalculator

        calculators = {
            CustomFields.ROIC: ROICCalculator,
        }

        if name not in calculators:
            raise ValueError(
                f"Unknown indicator: {name}. "
                f"Available: {list(calculators.keys())}"
            )

        return calculators[name]()
