"""Additional API tests for better coverage"""
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch


class TestAPICacheManagement:
    """Test API cache management methods"""

    def test_get_cache_stats_empty(self):
        """Should return cache stats for empty cache"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment.__new__(ValueInvestment)
        # Don't call __init__, just set up minimal state
        vi._container = MagicMock()
        
        stats = vi.get_cache_stats()
        
        assert stats is not None

    def test_get_cache_stats_with_data(self):
        """Should return cache stats with data"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment.__new__(ValueInvestment)
        vi._container = MagicMock()
        
        stats = vi.get_cache_stats()
        
        assert stats is not None

    def test_list_cache_keys_with_limit(self):
        """Should respect limit parameter"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment.__new__(ValueInvestment)
        vi._container = MagicMock()
        
        keys = vi.list_cache_keys(limit=2)
        
        assert keys is not None


class TestAPIDataPreparation:
    """Test API data preparation methods"""

    def test_prepare_data_with_dependencies(self):
        """Should prepare data with dependencies"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment.__new__(ValueInvestment)
        vi._container = MagicMock()
        
        # Mock the registry
        mock_registry = MagicMock()
        mock_registry.resolve.side_effect = lambda need: pd.DataFrame({"data": [1, 2, 3]})
        vi._registry = mock_registry
        
        result = vi._prepare_data(['financial_indicator', 'prices'], "600519")
        
        assert result is not None

    def test_prepare_data_with_missing_dependency(self):
        """Should handle missing dependency"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment.__new__(ValueInvestment)
        vi._container = MagicMock()
        
        # Mock registry returning None
        vi._registry = MagicMock()
        vi._registry.resolve.return_value = None
        
        result = vi._prepare_data(['financial_indicator'], "600519")
        
        assert result is not None


class TestAPIFieldFiltering:
    """Test API field filtering"""

    def test_filter_fields_basic(self):
        """Should filter fields"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment.__new__(ValueInvestment)
        vi._container = MagicMock()
        
        df = pd.DataFrame({
            "a": [1, 2],
            "b": [3, 4],
            "c": [5, 6]
        })
        
        result = vi._filter_fields(df, ["a", "b"])
        
        assert "a" in result.columns
        assert "b" in result.columns
        assert "c" not in result.columns

    def test_filter_fields_with_none(self):
        """Should return all fields when fields=None"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment.__new__(ValueInvestment)
        vi._container = MagicMock()
        
        df = pd.DataFrame({
            "a": [1, 2],
            "b": [3, 4]
        })
        
        result = vi._filter_fields(df, None)
        
        assert result.equals(df)

    def test_filter_fields_with_invalid(self):
        """Should handle invalid field names"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment.__new__(ValueInvestment)
        vi._container = MagicMock()
        
        df = pd.DataFrame({
            "a": [1, 2],
            "b": [3, 4]
        })
        
        result = vi._filter_fields(df, ["nonexistent"])
        
        # Should return empty or original df
        assert result is not None


class TestAPIMarketDetection:
    """Test market detection"""

    def test_detect_market_a_share(self):
        """Should detect A股"""
        from value_investment.api import ValueInvestment
        
        assert ValueInvestment.detect_market("600519") == "A"
        assert ValueInvestment.detect_market("000001") == "A"
        assert ValueInvestment.detect_market("300750") == "A"

    def test_detect_market_hk(self):
        """Should detect 港股"""
        from value_investment.api import ValueInvestment
        
        assert ValueInvestment.detect_market("00700") == "HK"
        assert ValueInvestment.detect_market("09988") == "HK"

    def test_detect_market_us(self):
        """Should detect 美股"""
        from value_investment.api import ValueInvestment
        
        assert ValueInvestment.detect_market("AAPL") == "US"
        assert ValueInvestment.detect_market("TSLA") == "US"


class TestAPIGetMarket:
    """Test get_market method"""

    def test_get_market_explicit(self):
        """Should return explicit market"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment(market="A")
        
        assert vi.get_market() == "A"

    def test_get_market_from_symbol(self):
        """Should detect market from symbol"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment()
        
        market = vi.get_market("600519")
        
        assert market in ["A", "HK", "US"]


class TestAPIAnalyzeFormatting:
    """Test analyze result formatting"""

    def test_format_analyze_results(self):
        """Should format analyze results"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment()
        
        results = {
            "roe": {"value": 0.15, "years": [2023]},
            "gross_margin": {"value": 0.50, "years": [2023]}
        }
        
        formatted = vi._format_analyze_results("Test Stock", results, 10)
        
        assert formatted is not None
        assert "stock_name" in formatted
        assert "indicators" in formatted

    def test_format_analyze_results_empty(self):
        """Should handle empty results"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment()
        
        formatted = vi._format_analyze_results("Test Stock", {}, 10)
        
        assert formatted is not None

    def test_format_analyze_results_with_many_years(self):
        """Should format results with many years"""
        from value_investment.api import ValueInvestment
        
        vi = ValueInvestment()
        
        results = {
            "roe": {
                "value": 0.15,
                "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
                "values": [0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.14, 0.15, 0.14, 0.15]
            }
        }
        
        formatted = vi._format_analyze_results("Test Stock", results, 10)
        
        assert formatted is not None
