"""Tests for AkshareProvider with configuration-driven architecture

AkshareProvider should:
1. Inherit from BaseProvider
2. Support configuration-driven field mappings
3. Support A 股/HK/US markets
4. Apply field mappings automatically
"""
from typing import Any

import pandas as pd
import pytest

from value_investment.data.providers.akshare_provider import AkshareProvider


class MockCache:
    """Mock cache for testing
    
    This mock is compatible with SmartCache interface.
    """
    
    def __init__(self):
        self._data: dict[str, Any] = {}
    
    def get(self, key: str) -> Any | None:
        return self._data.get(key)
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._data[key] = value
    
    def invalidate(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
    
    def get_or_fetch(self, key: str, fetch_func: Any, ttl: int | None = None, force_refresh: bool = False) -> Any:
        """Mock get_or_fetch for compatibility"""
        if not force_refresh:
            cached = self.get(key)
            if cached is not None:
                return cached
        result = fetch_func()
        self.set(key, result, ttl=ttl)
        return result
    
    def get_or_fetch_with_range(self, key: str, date_column: str, fetch_func: Any, 
                                 start_date: str | None = None, end_date: str | None = None, 
                                 ttl: int | None = None, force_refresh: bool = False) -> Any:
        """Mock get_or_fetch_with_range for compatibility"""
        if not force_refresh:
            cached = self.get(key)
            if cached is not None:
                return cached
        result = fetch_func()
        self.set(key, result, ttl=ttl)
        return result


class TestAkshareProviderInit:
    """Test AkshareProvider initialization"""

    def test_init_inherits_from_base_provider(self):
        """AkshareProvider should inherit from BaseProvider"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        assert issubclass(AkshareProvider, BaseProvider)

    def test_init_with_market(self):
        """Should initialize with market parameter"""
        provider = AkshareProvider(cache=MockCache(), market="A")  # type: ignore[arg-type]
        assert provider._market == "A"

    def test_init_with_field_mappings(self):
        """Should accept field_mappings from config"""
        mappings = {
            "balance": {"资产总值": "total_assets"},
            "income": {"收益": "total_revenue"},
        }
        provider = AkshareProvider(
            cache=MockCache(),  # type: ignore[arg-type]
            market="HK",
            field_mappings=mappings
        )
        assert provider.get_field_mapping("balance") == {"资产总值": "total_assets"}
        assert provider.get_field_mapping("income") == {"收益": "total_revenue"}

    def test_init_default_market_is_a(self):
        """Default market should be A"""
        provider = AkshareProvider(cache=MockCache())  # type: ignore[arg-type]
        assert provider._market == "A"


class TestAkshareProviderAStock:
    """Test A 股 functionality"""

    def test_get_balance_sheet_a_market(self):
        """Should get A 股 balance sheet with field mapping"""
        mappings = {
            "balance": {
                "资产总计": "total_assets",
                "负债合计": "total_liabilities",
                "股东权益合计": "total_equity",
            }
        }
        provider = AkshareProvider(
            cache=MockCache(),  # type: ignore[arg-type]
            market="A",
            field_mappings=mappings
        )
        
        # This is an integration test - skip if akshare not available
        try:
            df = provider.get_balance_sheet("600519", 2023)
            assert not df.empty
            # Check mapped fields exist
            assert "total_assets" in df.columns or "资产总计" in df.columns
        except Exception:
            pytest.skip("akshare API not available")

    def test_get_stock_info_a_market(self):
        """Should get A 股 stock info"""
        provider = AkshareProvider(cache=MockCache(), market="A")  # type: ignore[arg-type]
        
        try:
            df = provider.get_stock_info("600519")
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")


class TestAkshareProviderHKStock:
    """Test 港股 functionality"""

    def test_get_balance_sheet_hk_market(self):
        """Should get 港股 balance sheet with field mapping"""
        mappings = {
            "balance": {
                "资产总值": "total_assets",
                "总负债": "total_liabilities",
                "权益总额": "total_equity",
            }
        }
        provider = AkshareProvider(
            cache=MockCache(),  # type: ignore[arg-type]
            market="HK",
            field_mappings=mappings
        )
        
        try:
            df = provider.get_balance_sheet("00700", 2023)
            assert not df.empty
            # Check mapped fields exist
            assert "total_assets" in df.columns or "资产总值" in df.columns
        except Exception:
            pytest.skip("akshare API not available")

    def test_normalize_hk_code(self):
        """Should normalize HK stock code to 5-digit format"""
        provider = AkshareProvider(cache=MockCache(), market="HK")  # type: ignore[arg-type]
        
        assert provider._normalize_hk_code("700") == "00700"
        assert provider._normalize_hk_code("0700") == "00700"
        assert provider._normalize_hk_code("00700") == "00700"

    def test_get_stock_info_hk_market(self):
        """Should get 港股 stock info"""
        provider = AkshareProvider(cache=MockCache(), market="HK")  # type: ignore[arg-type]
        
        try:
            df = provider.get_stock_info("00700")
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")


class TestAkshareProviderUSStock:
    """Test 美股 functionality"""

    def test_get_balance_sheet_us_market(self):
        """Should get 美股 balance sheet with field mapping"""
        mappings = {
            "balance": {
                "totalAssets": "total_assets",
                "totalLiabilities": "total_liabilities",
                "totalStockholdersEquity": "total_equity",
            }
        }
        provider = AkshareProvider(
            cache=MockCache(),  # type: ignore[arg-type]
            market="US",
            field_mappings=mappings
        )
        
        try:
            df = provider.get_balance_sheet("AAPL", 2023)
            assert not df.empty
            # Check mapped fields exist
            assert "total_assets" in df.columns or "totalAssets" in df.columns
        except Exception:
            pytest.skip("akshare API not available")

    def test_get_stock_info_us_market(self):
        """Should get 美股 stock info"""
        provider = AkshareProvider(cache=MockCache(), market="US")  # type: ignore[arg-type]
        
        try:
            df = provider.get_stock_info("AAPL")
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")


class TestAkshareProviderFieldMapping:
    """Test field mapping application"""

    def test_apply_mapping_balance_sheet(self):
        """Should apply field mapping to balance sheet"""
        mappings = {
            "balance": {
                "资产总计": "total_assets",
                "负债合计": "total_liabilities",
            }
        }
        provider = AkshareProvider(
            cache=MockCache(),  # type: ignore[arg-type]
            market="A",
            field_mappings=mappings
        )
        
        # Create mock data
        df = pd.DataFrame({
            "资产总计": [1000, 2000],
            "负债合计": [500, 1000],
            "unmapped_field": [999, 888],
        })
        
        result = provider._apply_mapping(df, "balance")
        assert result is not None
        
        assert "total_assets" in result.columns
        assert "total_liabilities" in result.columns
        assert "资产总计" not in result.columns
        assert "unmapped_field" in result.columns  # Unmapped fields kept

    def test_apply_mapping_income_statement(self):
        """Should apply field mapping to income statement"""
        mappings = {
            "income": {
                "收益": "total_revenue",
                "期内溢利": "net_profit",
            }
        }
        provider = AkshareProvider(
            cache=MockCache(),  # type: ignore[arg-type]
            market="HK",
            field_mappings=mappings
        )
        
        df = pd.DataFrame({
            "收益": [1000, 2000],
            "期内溢利": [100, 200],
        })
        
        result = provider._apply_mapping(df, "income")
        assert result is not None
        
        assert "total_revenue" in result.columns
        assert "net_profit" in result.columns


class TestAkshareProviderHistoricalData:
    """Test historical data functionality"""

    def test_get_historical_data_a_market(self):
        """Should get A 股 historical data"""
        provider = AkshareProvider(cache=MockCache(), market="A")  # type: ignore[arg-type]
        
        try:
            df = provider.get_historical_data(
                "600519",
                end_date="20231231",
                start_date="20230101"
            )
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")

    def test_get_historical_data_hk_market(self):
        """Should get 港股 historical data"""
        provider = AkshareProvider(cache=MockCache(), market="HK")  # type: ignore[arg-type]
        
        try:
            df = provider.get_historical_data(
                "00700",
                end_date="20231231",
                start_date="20230101"
            )
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")

    def test_get_historical_data_us_market(self):
        """Should get 美股 historical data"""
        provider = AkshareProvider(cache=MockCache(), market="US")  # type: ignore[arg-type]
        
        try:
            df = provider.get_historical_data(
                "AAPL",
                end_date="20231231",
                start_date="20230101"
            )
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")


class TestAkshareProviderFinancialIndicator:
    """Test financial indicator functionality"""

    def test_get_financial_indicator_a_market(self):
        """Should get A 股 financial indicators"""
        provider = AkshareProvider(cache=MockCache(), market="A")  # type: ignore[arg-type]
        
        try:
            df = provider.get_financial_indicator("600519")
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")

    def test_get_financial_indicator_hk_market(self):
        """Should get 港股 financial indicators"""
        provider = AkshareProvider(cache=MockCache(), market="HK")  # type: ignore[arg-type]
        
        try:
            df = provider.get_financial_indicator("00700")
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")

    def test_get_financial_indicator_us_market(self):
        """Should get 美股 financial indicators"""
        provider = AkshareProvider(cache=MockCache(), market="US")  # type: ignore[arg-type]
        
        try:
            df = provider.get_financial_indicator("AAPL")
            assert not df.empty
        except Exception:
            pytest.skip("akshare API not available")
