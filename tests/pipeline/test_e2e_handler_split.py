"""End-to-end tests for handler split architecture"""
import pytest
from unittest.mock import MagicMock

from value_investment.pipeline.container import Container
from value_investment.core.types import Message


class TestE2EHandlerSplit:
    """端到端测试：验证 9 个 Handler 的路由正确性"""

    @pytest.fixture(autouse=True)
    def reset_container(self):
        """每个测试前重置 Container singleton"""
        Container._instance = None
        yield
        Container._instance = None

    @pytest.fixture
    def mock_tushare(self):
        """Mock Tushare provider for A股 testing"""
        provider = MagicMock()
        provider.supported_fields = {
            "total_revenue", "net_profit", "total_assets",  # Statement
            "roe", "roa", "gross_margin",  # Indicator
            "market_cap", "pe_ratio", "pb_ratio",  # Market
        }
        provider.fetch_financial_data = MagicMock(
            return_value={
                "total_revenue": {2024: 100e9, 2023: 90e9},
                "net_profit": {2024: 50e9, 2023: 45e9},
            }
        )
        provider.fetch_indicators = MagicMock(
            return_value={
                "roe": {2024: 25.5, 2023: 24.8},
            }
        )
        provider.fetch_market_data = MagicMock(
            return_value={
                "market_cap": 2.5e12,
                "pe_ratio": 28.5,
            }
        )
        return provider

    @pytest.mark.asyncio
    async def test_a_stock_statement_fields_routed(self, mock_tushare):
        """A股 statement 字段只被 AShareStatementHandler 处理"""
        Container._instance = None
        container = Container.create()

        # 替换 A 股 Statement Handler 的 provider
        for handler in container.bus().handlers:
            if type(handler).__name__ == "AShareStatementHandler":
                handler._provider = mock_tushare

        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=5,
            require={"total_revenue", "net_profit"},
        )

        await container.bus().process(message)

        # Statement 数据应被获取
        assert "total_revenue" not in message.require
        assert 2024 in message.results.get("total_revenue", {})

    @pytest.mark.asyncio
    async def test_a_stock_indicator_fields_routed(self, mock_tushare):
        """A股 indicator 字段只被 AShareIndicatorHandler 处理"""
        Container._instance = None
        container = Container.create()

        for handler in container.bus().handlers:
            if type(handler).__name__ == "AShareIndicatorHandler":
                handler._provider = mock_tushare

        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=5,
            require={"roe"},
        )

        await container.bus().process(message)

        assert "roe" not in message.require
        assert message.results["roe"][2024] == 25.5

    @pytest.mark.asyncio
    async def test_hk_handler_ignores_a_stock_message(self, mock_tushare):
        """HK Handler 拒绝 A 股消息（快速拒绝），AShareStatementHandler 处理 A 股"""
        Container._instance = None
        container = Container.create()

        # Mock AShareStatementHandler provider
        for handler in container.bus().handlers:
            if type(handler).__name__ == "AShareStatementHandler":
                handler._provider = mock_tushare
            elif type(handler).__name__ in ("HKShareStatementHandler", "USShareStatementHandler"):
                handler._provider = None  # 确保 HK/US 没有 provider

        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=5,
            require={"total_revenue"},
        )

        await container.bus().process(message)

        # AShareStatementHandler 应处理此消息
        assert "total_revenue" not in message.require
        assert 2024 in message.results.get("total_revenue", {})

    @pytest.mark.asyncio
    async def test_mixed_fields_routed_to_correct_handlers(self, mock_tushare):
        """混合字段路由到正确的 Handler"""
        Container._instance = None
        container = Container.create()

        # 注入 mock provider
        for handler in container.bus().handlers:
            if type(handler).__name__ in ("AShareStatementHandler", "AShareIndicatorHandler", "AShareMarketHandler"):
                handler._provider = mock_tushare

        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=5,
            require={"total_revenue", "roe", "market_cap"},
        )

        await container.bus().process(message)

        # 所有字段都应被处理
        assert "total_revenue" not in message.require
        assert "roe" not in message.require
        assert "market_cap" not in message.require

    def test_all_9_handlers_in_bus(self):
        """验证 9 个 Handler 都在消息总线上"""
        Container._instance = None
        container = Container.create()

        handler_names = [type(h).__name__ for h in container.bus().handlers]
        expected = [
            "AShareStatementHandler", "AShareIndicatorHandler", "AShareMarketHandler",
            "HKShareStatementHandler", "HKShareIndicatorHandler", "HKShareMarketHandler",
            "USShareStatementHandler", "USShareIndicatorHandler", "USShareMarketHandler",
        ]
        assert set(handler_names) == set(expected)
