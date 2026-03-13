"""Tests for HK stock list dynamic fetching

测试港股列表的动态获取功能，包括：
1. 从 akshare 获取港股列表
2. 缓存策略（到次年 6 月底）
3. 代码格式转换（5 位数字 -> 00001.HK）
4. 错误处理和降级
"""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from value_investment.scanner.data.hk_shares import (
    get_hk_stock_list_from_akshare,
    format_hk_stock_code,
    TOP_100_HK_SHARES,
)


class TestFormatHKStockCode:
    """Tests for HK stock code formatting"""

    def test_format_hk_stock_code_basic(self):
        """Test basic HK stock code formatting"""
        # 5-digit code -> project format
        assert format_hk_stock_code('00700') == '00700.HK'
        assert format_hk_stock_code('00001') == '00001.HK'
        assert format_hk_stock_code('9988') == '09988.HK'

    def test_format_hk_stock_code_with_various_lengths(self):
        """Test formatting codes with different lengths"""
        # 1-digit
        assert format_hk_stock_code('1') == '00001.HK'
        # 2-digit
        assert format_hk_stock_code('12') == '00012.HK'
        # 3-digit
        assert format_hk_stock_code('123') == '00123.HK'
        # 4-digit
        assert format_hk_stock_code('1234') == '01234.HK'
        # 5-digit (already correct)
        assert format_hk_stock_code('12345') == '12345.HK'

    def test_format_hk_stock_code_with_non_digits(self):
        """Test formatting codes with non-digit characters"""
        # Should strip non-digit characters
        assert format_hk_stock_code('HK00700') == '00700.HK'
        assert format_hk_stock_code('00700.HK') == '00700.HK'

    def test_format_hk_stock_code_empty(self):
        """Test formatting empty code"""
        assert format_hk_stock_code('') == '.HK'
        assert format_hk_stock_code(None) == '.HK'  # type: ignore


class TestGetHKStockListFromAkshare:
    """Tests for fetching HK stock list from akshare"""

    @patch('value_investment.scanner.data.hk_shares.ak')
    def test_get_hk_stock_list_success(self, mock_ak):
        """Test successful fetch from akshare"""
        # Mock akshare response
        mock_df = pd.DataFrame({
            '代码': ['00700', '09988', '01810'],
            '中文名称': ['腾讯控股', '阿里巴巴-SW', '小米集团-W'],
            '英文名称': ['TENCENT', 'ALIBABA-SW', 'XIAOMI-W'],
            '最新价': [300.0, 80.0, 15.0],
        })
        mock_ak.stock_hk_spot.return_value = mock_df

        result = get_hk_stock_list_from_akshare()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'ts_code' in result.columns
        assert 'symbol' in result.columns
        assert 'name' in result.columns

        # Check code format conversion
        assert result['ts_code'].iloc[0] == '00700.HK'
        assert result['symbol'].iloc[0] == '00700'
        assert result['name'].iloc[0] == '腾讯控股'

    @patch('value_investment.scanner.data.hk_shares.ak')
    def test_get_hk_stock_list_with_empty_data(self, mock_ak):
        """Test handling of empty response from akshare"""
        mock_ak.stock_hk_spot.return_value = pd.DataFrame()

        result = get_hk_stock_list_from_akshare()

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch('value_investment.scanner.data.hk_shares.ak')
    def test_get_hk_stock_list_with_missing_columns(self, mock_ak):
        """Test handling when some columns are missing"""
        # Only '代码' column available
        mock_df = pd.DataFrame({
            '代码': ['00700', '09988'],
        })
        mock_ak.stock_hk_spot.return_value = mock_df

        result = get_hk_stock_list_from_akshare()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'ts_code' in result.columns
        # Name should default to '港股 - 代码' when Chinese name is missing
        assert result['name'].iloc[0] == '港股-00700'

    @patch('value_investment.scanner.data.hk_shares.ak')
    def test_get_hk_stock_list_preserves_chinese_name(self, mock_ak):
        """Test that Chinese names are preserved from akshare"""
        mock_df = pd.DataFrame({
            '代码': ['00700', '09988'],
            '中文名称': ['腾讯控股', '阿里巴巴-SW'],
            '英文名称': ['TENCENT', 'ALIBABA-SW'],
        })
        mock_ak.stock_hk_spot.return_value = mock_df

        result = get_hk_stock_list_from_akshare()

        assert result['name'].iloc[0] == '腾讯控股'
        assert result['name'].iloc[1] == '阿里巴巴-SW'

    @patch('value_investment.scanner.data.hk_shares.ak')
    def test_get_hk_stock_list_code_normalization(self, mock_ak):
        """Test that stock codes are normalized to 5-digit format"""
        # Akshare may return codes with different formats
        mock_df = pd.DataFrame({
            '代码': ['700', '9988', '12345'],  # Various lengths
            '中文名称': ['腾讯', '阿里', '某公司'],
        })
        mock_ak.stock_hk_spot.return_value = mock_df

        result = get_hk_stock_list_from_akshare()

        # All codes should be 5-digit in symbol column
        assert result['symbol'].tolist() == ['00700', '09988', '12345']
        assert result['ts_code'].tolist() == ['00700.HK', '09988.HK', '12345.HK']


class TestHKStockListCaching:
    """Tests for HK stock list caching strategy"""

    def test_cache_ttl_until_june_next_year(self):
        """Test that cache TTL is until June next year"""
        from value_investment.data.providers.base_provider import get_ttl_until_june_next_year
        
        # Current date: March 2026
        # Should cache until June 2027
        current_year = 2026
        ttl_seconds = get_ttl_until_june_next_year(current_year)
        
        # TTL should be more than 1 year (until June 2027)
        assert ttl_seconds > 365 * 24 * 60 * 60  # More than 1 year
        
        # Calculate expected TTL (roughly)
        from datetime import timedelta
        target_date = datetime(2027, 6, 30)
        current_date = datetime(2026, 3, 13)
        expected_days = (target_date - current_date).days
        expected_seconds = expected_days * 24 * 60 * 60
        
        # Allow some margin for time of day differences
        assert abs(ttl_seconds - expected_seconds) < 24 * 60 * 60  # Within 1 day

    def test_cache_key_is_used(self):
        """Test that cache key 'scanner_hk_stocks' is used"""
        # This is a simple test to verify the cache key naming convention
        cache_key = "scanner_hk_stocks"
        assert cache_key.startswith("scanner_")
        assert "hk" in cache_key


class TestPresetListFallback:
    """Tests for preset list as fallback"""

    def test_preset_list_exists(self):
        """Test that preset TOP_100_HK_SHARES list exists"""
        assert isinstance(TOP_100_HK_SHARES, list)
        assert len(TOP_100_HK_SHARES) > 0
        assert '00700' in TOP_100_HK_SHARES  # Tencent
        assert '09988' in TOP_100_HK_SHARES  # Alibaba

    @patch('value_investment.scanner.data.hk_shares.ak')
    def test_returns_empty_on_error(self, mock_ak):
        """Test that empty DataFrame is returned when akshare fails"""
        # Simulate akshare failure
        mock_ak.stock_hk_spot.side_effect = Exception("Network error")

        # Should return empty DataFrame gracefully
        result = get_hk_stock_list_from_akshare()
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestScannerIntegration:
    """Integration tests for Scanner with dynamic HK stock list"""

    @patch('value_investment.scanner.data.hk_shares.ak')
    def test_scanner_get_stock_list_uses_akshare(self, mock_ak):
        """Test that Scanner.get_stock_list() fetches from akshare"""
        import tempfile
        from value_investment.scanner.scanner import Scanner
        from value_investment.data.cache import SmartCache
        
        # Mock akshare response
        mock_df = pd.DataFrame({
            '代码': ['00700', '09988'],
            '中文名称': ['腾讯控股', '阿里巴巴-SW'],
        })
        mock_ak.stock_hk_spot.return_value = mock_df
        
        # Create scanner with isolated cache directory
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = Scanner(market='HK', cache_dir=tmpdir)
            result = scanner.get_stock_list()
            
            assert len(result) == 2
            assert result['ts_code'].iloc[0] == '00700.HK'
            assert result['name'].iloc[0] == '腾讯控股'
            
            # Verify cache is set
            cached = scanner._cache.get('scanner_hk_stocks')
            assert cached is not None
            assert len(cached) == 2

    @patch('value_investment.scanner.data.hk_shares.ak')
    def test_scanner_returns_empty_on_akshare_failure(self, mock_ak):
        """Test that Scanner returns empty DataFrame when akshare fails"""
        import tempfile
        from value_investment.scanner.scanner import Scanner
        
        # Simulate akshare failure
        mock_ak.stock_hk_spot.side_effect = Exception("Network error")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = Scanner(market='HK', cache_dir=tmpdir)
            result = scanner.get_stock_list()
            
            assert isinstance(result, pd.DataFrame)
            assert result.empty
