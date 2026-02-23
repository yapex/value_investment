"""Tests for API analyze result formatting"""
import pytest
import pandas as pd
from value_investment.api import ValueInvestment


class TestAnalyzeFormatting:
    """测试 analyze 结果格式化"""

    def test_analyze_returns_formatted_result(self):
        """测试 analyze 返回格式化后的结果"""
        vi = ValueInvestment(market="A")
        result = vi.analyze("600519", years=5)
        # 验证返回包含必要字段
        assert "name" in result
        assert "year_range" in result
        assert "table" in result
        assert "summary" in result

    def test_analyze_table_has_columns(self):
        """测试表格数据包含正确列"""
        vi = ValueInvestment(market="A")
        result = vi.analyze("600519", years=5)
        table = result.get("table")
        assert isinstance(table, pd.DataFrame)
        if not table.empty:
            assert "年份" in table.columns

    def test_analyze_summary_has_labels(self):
        """测试汇总指标包含中文标签"""
        vi = ValueInvestment(market="A")
        result = vi.analyze("600519", years=5)
        summary = result.get("summary", [])
        # 验证有标签
        if summary:
            assert any("label" in item and "value" in item for item in summary)


class TestCacheStats:
    """测试缓存统计功能"""

    def test_get_cache_stats(self):
        """测试获取缓存统计"""
        vi = ValueInvestment()
        stats = vi.get_cache_stats()
        assert "memory_size" in stats
        assert "disk_cache_size" in stats
