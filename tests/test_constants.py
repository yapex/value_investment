"""测试核心常量定义"""
import pytest


class TestTimeConstants:
    """测试时间相关常量"""

    def test_one_day_seconds(self):
        """ONE_DAY_SECONDS 应该等于 86400"""
        from value_investment.core.constants import ONE_DAY_SECONDS

        assert ONE_DAY_SECONDS == 86400

    def test_one_year_seconds(self):
        """ONE_YEAR_SECONDS 应该等于 365 天"""
        from value_investment.core.constants import ONE_DAY_SECONDS, ONE_YEAR_SECONDS

        assert ONE_YEAR_SECONDS == 365 * ONE_DAY_SECONDS
        assert ONE_YEAR_SECONDS == 31536000

    def test_six_months_seconds(self):
        """SIX_MONTHS_SECONDS 应该等于 180 天"""
        from value_investment.core.constants import ONE_DAY_SECONDS, SIX_MONTHS_SECONDS

        assert SIX_MONTHS_SECONDS == 180 * ONE_DAY_SECONDS
        assert SIX_MONTHS_SECONDS == 15552000

    def test_two_years_seconds(self):
        """TWO_YEARS_SECONDS 应该等于 2 年"""
        from value_investment.core.constants import ONE_YEAR_SECONDS, TWO_YEARS_SECONDS

        assert TWO_YEARS_SECONDS == 2 * ONE_YEAR_SECONDS
        assert TWO_YEARS_SECONDS == 63072000


class TestDateFormatConstants:
    """测试日期格式常量"""

    def test_date_format(self):
        """DATE_FORMAT 应该是标准的日期格式"""
        from value_investment.core.constants import DATE_FORMAT
        from datetime import datetime

        assert DATE_FORMAT == "%Y-%m-%d"
        # 验证格式可用
        now = datetime(2024, 3, 9)
        assert now.strftime(DATE_FORMAT) == "2024-03-09"

    def test_date_format_compact(self):
        """DATE_FORMAT_COMPACT 应该是紧凑的日期格式"""
        from value_investment.core.constants import DATE_FORMAT_COMPACT
        from datetime import datetime

        assert DATE_FORMAT_COMPACT == "%Y%m%d"
        # 验证格式可用
        now = datetime(2024, 3, 9)
        assert now.strftime(DATE_FORMAT_COMPACT) == "20240309"


class TestMarketCodeConstants:
    """测试市场代码常量"""

    def test_a_share_code_prefixes(self):
        """A 股代码前缀应该是 0, 3, 6"""
        from value_investment.core.constants import A_SHARE_CODE_PREFIXES

        assert A_SHARE_CODE_PREFIXES == ("0", "3", "6")
        # 验证可以用于判断
        assert "6" in A_SHARE_CODE_PREFIXES
        assert "0" in A_SHARE_CODE_PREFIXES
        assert "3" in A_SHARE_CODE_PREFIXES
        assert "9" not in A_SHARE_CODE_PREFIXES

    def test_a_share_prefixes_immutable(self):
        """A 股前缀 tuple 应该是不可变的"""
        from value_investment.core.constants import A_SHARE_CODE_PREFIXES

        assert isinstance(A_SHARE_CODE_PREFIXES, tuple)

    def test_market_suffixes(self):
        """市场后缀常量"""
        from value_investment.core.constants import (
            SHANGHAI_SUFFIX,
            SHENZHEN_SUFFIX,
            HK_STOCK_SUFFIX,
        )

        assert SHANGHAI_SUFFIX == ".SH"
        assert SHENZHEN_SUFFIX == ".SZ"
        assert HK_STOCK_SUFFIX == ".HK"


class TestNumericConstants:
    """测试数值常量"""

    def test_billion(self):
        """BILLION 应该等于 1e9"""
        from value_investment.core.constants import BILLION

        assert BILLION == 1e9
        assert BILLION == 1_000_000_000

    def test_hundred_million(self):
        """HUNDRED_MILLION 应该等于 1e8（亿）"""
        from value_investment.core.constants import HUNDRED_MILLION

        assert HUNDRED_MILLION == 1e8
        assert HUNDRED_MILLION == 100_000_000

    def test_us_shares_multiplier(self):
        """US_SHARES_MULTIPLIER 应该等于 10000（美股股数转换）"""
        from value_investment.core.constants import US_SHARES_MULTIPLIER

        assert US_SHARES_MULTIPLIER == 10000

    def test_percentage_multiplier(self):
        """PERCENTAGE_MULTIPLIER 应该等于 100"""
        from value_investment.core.constants import PERCENTAGE_MULTIPLIER

        assert PERCENTAGE_MULTIPLIER == 100


class TestFinancialThresholds:
    """测试财务分析阈值常量"""

    def test_default_tax_rate(self):
        """DEFAULT_TAX_RATE 应该等于 0.25"""
        from value_investment.core.constants import DEFAULT_TAX_RATE

        assert DEFAULT_TAX_RATE == 0.25

    def test_growth_rate_thresholds(self):
        """增长率相关阈值"""
        from value_investment.core.constants import (
            MIN_GROWTH_RATE,
            GROWTH_SEARCH_RANGE,
            MAX_ITERATIONS,
            TOLERANCE,
        )

        assert MIN_GROWTH_RATE == -0.1
        assert GROWTH_SEARCH_RANGE == (-0.05, 0.30)
        assert MAX_ITERATIONS == 100
        assert TOLERANCE == 0.0001

    def test_default_year_span(self):
        """DEFAULT_YEAR_SPAN 应该等于 15 年"""
        from value_investment.core.constants import DEFAULT_YEAR_SPAN

        assert DEFAULT_YEAR_SPAN == 15


class TestCacheTTLConstants:
    """测试缓存 TTL 常量"""

    def test_default_cache_ttl(self):
        """DEFAULT_CACHE_TTL 应该等于 1 天"""
        from value_investment.core.constants import DEFAULT_CACHE_TTL, ONE_DAY_SECONDS

        assert DEFAULT_CACHE_TTL == ONE_DAY_SECONDS

    def test_historical_data_ttl(self):
        """HISTORICAL_DATA_TTL 应该等于 1 年"""
        from value_investment.core.constants import (
            HISTORICAL_DATA_TTL,
            ONE_YEAR_SECONDS,
        )

        assert HISTORICAL_DATA_TTL == ONE_YEAR_SECONDS

    def test_financial_data_ttl(self):
        """FINANCIAL_DATA_TTL 应该等于 2 年"""
        from value_investment.core.constants import (
            FINANCIAL_DATA_TTL,
            TWO_YEARS_SECONDS,
        )

        assert FINANCIAL_DATA_TTL == TWO_YEARS_SECONDS
