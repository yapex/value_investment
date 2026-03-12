"""速率限制器 - 控制 API 调用频率"""
import time
from typing import Dict


class RateLimiter:
    """速率限制器 - 限制每分钟调用次数

    用于控制 Tushare API 等有限速的接口调用频率。
    默认每分钟最多 200 次调用（Tushare 免费版限制）。

    Example:
        >>> limiter = RateLimiter(max_calls_per_minute=200)
        >>> for code in stock_codes:
        ...     limiter.wait_if_needed()
        ...     data = api.get_data(code)
    """

    def __init__(self, max_calls_per_minute: int = 200):
        """初始化速率限制器

        Args:
            max_calls_per_minute: 每分钟最大调用次数
        """
        self.max_calls = max_calls_per_minute
        self._calls: list[float] = []  # 记录每次调用的时间戳

    def wait_if_needed(self) -> None:
        """检查是否需要等待，确保不超过速率限制

        如果当前分钟内已达到调用上限，会等待直到下一分钟开始。
        """
        now = time.time()
        # 清理 1 分钟前的记录
        self._calls = [t for t in self._calls if now - t < 60]

        # 如果已达到限制，等待
        if len(self._calls) >= self.max_calls:
            oldest_call = min(self._calls)
            wait_time = 60 - (now - oldest_call) + 0.1
            if wait_time > 0:
                time.sleep(wait_time)
            # 重新清理
            now = time.time()
            self._calls = [t for t in self._calls if now - t < 60]

        # 记录本次调用
        self._calls.append(time.time())

    def get_status(self) -> Dict[str, int]:
        """获取当前速率状态

        Returns:
            Dict with keys:
                - calls_in_last_minute: 最近 1 分钟内的调用次数
                - remaining: 剩余可用调用次数
        """
        now = time.time()
        self._calls = [t for t in self._calls if now - t < 60]
        return {
            'calls_in_last_minute': len(self._calls),
            'remaining': self.max_calls - len(self._calls)
        }
