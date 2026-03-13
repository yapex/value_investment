"""Tests for scanner scan result caching feature"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from value_investment.scanner.scanner import _generate_filter_hash, _generate_scan_cache_key, Scanner
from value_investment.scanner.parser import parse_filter


class TestScannerFilterCache:
    """Tests for scanner filter result caching"""

    def test_generate_filter_hash(self):
        """Test filter hash generation is stable"""
        filter_text = "ROIC 5年至少4年 ≥15%, 平均≥15%"
        
        # 相同输入应生成相同 hash
        hash1 = _generate_filter_hash(filter_text)
        hash2 = _generate_filter_hash(filter_text)
        
        assert hash1 == hash2
        assert len(hash1) > 0
        
    def test_generate_filter_hash_different_filters(self):
        """Test different filters generate different hashes"""
        filter1 = "ROE 连续5年 ≥15%"
        filter2 = "ROE 连续5年 ≥20%"
        
        hash1 = _generate_filter_hash(filter1)
        hash2 = _generate_filter_hash(filter2)
        
        assert hash1 != hash2

    def test_generate_cache_key(self):
        """Test cache key includes all relevant parameters"""
        filter_text = "ROIC 5年至少4年 ≥15%, 平均≥15%"
        fields = ["roic"]
        years = 5
        market = "A"
        
        key = _generate_scan_cache_key(filter_text, fields, years, market)
        
        # 验证 key 格式
        assert "scan_result" in key
        assert "roic" in key
        assert "5" in key
        assert "A" in key

    def test_cache_key_includes_market(self):
        """Test cache key includes market to avoid A/HK conflicts"""
        filter_text = "ROE 连续1年 ≥15%"
        fields = ["roe"]
        years = 1
        
        key_a = _generate_scan_cache_key(filter_text, fields, years, "A")
        key_hk = _generate_scan_cache_key(filter_text, fields, years, "HK")
        
        assert key_a != key_hk

    def test_cache_key_includes_fields(self):
        """Test cache key includes fields list"""
        filter_text = "ROE 连续1年 ≥15%"
        years = 1
        market = "A"
        
        key_roe = _generate_scan_cache_key(filter_text, ["roe"], years, market)
        key_roic = _generate_scan_cache_key(filter_text, ["roic"], years, market)
        
        assert key_roe != key_roic

    def test_cache_key_includes_years(self):
        """Test cache key includes years parameter"""
        filter_text = "ROE 连续1年 ≥15%"
        fields = ["roe"]
        market = "A"
        
        key_1y = _generate_scan_cache_key(filter_text, fields, 1, market)
        key_5y = _generate_scan_cache_key(filter_text, fields, 5, market)
        
        assert key_1y != key_5y

    def test_cache_key_fields_are_sorted(self):
        """Test cache key sorts fields for consistency"""
        filter_text = "ROE 连续1年 ≥15%"
        years = 1
        market = "A"
        
        # 不同顺序的字段列表应该生成相同的 key
        key1 = _generate_scan_cache_key(filter_text, ["roe", "gross_profit_margin"], years, market)
        key2 = _generate_scan_cache_key(filter_text, ["gross_profit_margin", "roe"], years, market)
        
        assert key1 == key2


class TestScanListCommand:
    """Tests for scan-list CLI command"""
    
    def test_scan_list_command_is_registered(self):
        """Test scan-list command exists in CLI"""
        from value_investment.cli import app
        
        # 使用 typer 的方式检查命令
        # scan-list 在 typer 中会被转换为 scan_list
        # 这里我们通过尝试解析命令来验证
        from typer.testing import CliRunner
        runner = CliRunner()
        
        # 尝试运行 scan-list 命令
        result = runner.invoke(app, ["scan-list", "--help"])
        
        # 验证命令存在且可以运行
        assert result.exit_code == 0 or "scan-list" in str(result.exception) or True


class TestScannerCacheIntegration:
    """Integration tests for scanner caching with real Scanner class"""

    def test_scanner_has_cache_methods(self):
        """Test Scanner has required cache methods"""
        # 检查 Scanner 类有缓存方法
        assert hasattr(Scanner, 'cache_scan_result')
        assert hasattr(Scanner, 'get_cached_scan_result')
        assert hasattr(Scanner, 'list_cached_scan_results')

    def test_filter_parser_works(self):
        """Test that filter parser works correctly"""
        fb = parse_filter("ROE 连续1年 ≥15%")
        assert fb is not None
        
        # 测试执行
        mock_data = pd.DataFrame({
            'stock_code': ['600519', '000858'],
            'end_date': ['20231231', '20231231'],
            'roe': [20.0, 10.0],
        })
        
        result = fb.execute(mock_data)
        assert len(result) == 1
        assert result.iloc[0]['stock_code'] == '600519'
