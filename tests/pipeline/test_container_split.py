"""Tests for Container handler registration"""


class TestContainerHandlerRegistration:
    def test_registers_9_handlers(self):
        """Container.create() 应注册 9 个 Handler（3 市场 × 3 数据类型）"""
        from value_investment.pipeline.container import Container

        # 重置 singleton 以便测试独立运行
        Container._instance = None
        container = Container.create()

        expected = [
            "AStockStatementHandler",
            "AStockIndicatorHandler",
            "AStockMarketHandler",
            "HKStockStatementHandler",
            "HKStockIndicatorHandler",
            "HKStockMarketHandler",
            "USStockStatementHandler",
            "USStockIndicatorHandler",
            "USStockMarketHandler",
        ]
        handler_names = [type(h).__name__ for h in container.bus().handlers]

        for name in expected:
            assert name in handler_names, f"Missing handler: {name}"

    def test_no_duplicate_handlers(self):
        """不应有重复 Handler"""
        from value_investment.pipeline.container import Container

        Container._instance = None
        container = Container.create()
        handler_names = [type(h).__name__ for h in container.bus().handlers]

        assert len(handler_names) == len(set(handler_names)), "Duplicate handlers found"
