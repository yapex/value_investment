"""Unit tests for TushareProvider code conversion"""
import pytest  # type: ignore[import-untyped]


class TestTsCodeConversion:
    """测试股票代码转换逻辑"""

    def test_to_ts_code_shanghai(self):
        """测试上海股票代码转换（6 开头）"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        # 使用 __new__ 创建实例，避免初始化需要 token
        provider = TushareProvider.__new__(TushareProvider)

        assert provider._to_ts_code("600519") == "600519.SH"
        assert provider._to_ts_code("601318") == "601318.SH"
        assert provider._to_ts_code("688981") == "688981.SH"

    def test_to_ts_code_shenzhen(self):
        """测试深圳股票代码转换（0/3 开头）"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        provider = TushareProvider.__new__(TushareProvider)

        # 0 开头
        assert provider._to_ts_code("000001") == "000001.SZ"
        assert provider._to_ts_code("000002") == "000002.SZ"

        # 3 开头
        assert provider._to_ts_code("300750") == "300750.SZ"
        assert provider._to_ts_code("300059") == "300059.SZ"

    def test_to_ts_code_already_formatted(self):
        """测试已经格式化的代码保持不变"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        provider = TushareProvider.__new__(TushareProvider)

        assert provider._to_ts_code("600519.SH") == "600519.SH"
        assert provider._to_ts_code("000001.SZ") == "000001.SZ"

    def test_to_ts_code_unknown_format(self):
        """测试未知格式的代码保持不变"""
        from value_investment.data.providers.tushare_provider import TushareProvider

        provider = TushareProvider.__new__(TushareProvider)

        # 非 6 位数字
        assert provider._to_ts_code("AAPL") == "AAPL"
        assert provider._to_ts_code("00700") == "00700"

        # 包含非数字字符
        assert provider._to_ts_code("600abc") == "600abc"
