"""RateLimiter 工具类测试"""
import time
import pytest
from value_investment.core.rate_limiter import RateLimiter


class TestRateLimiter:
    """RateLimiter 测试类"""

    def test_rate_limiter_basic(self):
        """测试基本速率限制功能"""
        limiter = RateLimiter(max_calls_per_minute=10)

        # 前 10 次应该无需等待
        start = time.time()
        for _ in range(10):
            limiter.wait_if_needed()
        elapsed = time.time() - start
        assert elapsed < 1  # 应该很快完成

    def test_rate_limiter_status(self):
        """测试状态查询"""
        limiter = RateLimiter(max_calls_per_minute=10)

        # 初始状态
        status = limiter.get_status()
        assert status['calls_in_last_minute'] == 0
        assert status['remaining'] == 10

        # 调用 3 次后
        for _ in range(3):
            limiter.wait_if_needed()

        status = limiter.get_status()
        assert status['calls_in_last_minute'] == 3
        assert status['remaining'] == 7
