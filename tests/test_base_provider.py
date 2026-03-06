"""Tests for BaseProvider with field mapping support"""

import pandas as pd
import pytest  # type: ignore


class MockCache:
    """Mock cache for testing"""
    
    def __init__(self):
        self._data = {}
    
    def get(self, key):
        return self._data.get(key)
    
    def set(self, key, value, ttl=None):
        self._data[key] = value
    
    def invalidate(self, key):
        if key in self._data:
            del self._data[key]


class ConcreteTestProvider:
    """Concrete provider for testing BaseProvider functionality"""
    # Will be defined in each test that needs it
    pass


class TestBaseProviderInit:
    """Test BaseProvider initialization"""

    def test_base_provider_import(self):
        """BaseProvider should be importable"""
        from value_investment.data.providers.base_provider import BaseProvider
        assert BaseProvider is not None

    def test_base_provider_init_minimal(self):
        """BaseProvider should initialize with minimal config"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(cache=MockCache())
        
        assert provider._cache is not None
        assert provider._field_mappings == {}

    def test_base_provider_init_with_mappings(self):
        """BaseProvider should accept field_mappings"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        mappings = {
            "income": {"total_revenue": "total_revenue"},
            "balance": {"total_assets": "total_assets"},
        }
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(cache=MockCache(), field_mappings=mappings)
        
        assert provider._field_mappings == mappings
        assert provider.get_field_mapping("income") == {"total_revenue": "total_revenue"}

    def test_base_provider_init_with_kwargs(self):
        """BaseProvider should store init_kwargs"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(
            cache=MockCache(),
            token="test_token",
            timeout=30,
        )
        
        assert provider._init_kwargs["token"] == "test_token"
        assert provider._init_kwargs["timeout"] == 30


class TestBaseProviderFieldMapping:
    """Test BaseProvider field mapping functionality"""

    def test_get_field_mapping_exists(self):
        """get_field_mapping should return mapping for data type"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        mappings = {
            "income": {"ts_code": "stock_code", "total_revenue": "total_revenue"},
        }
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(cache=MockCache(), field_mappings=mappings)
        
        result = provider.get_field_mapping("income")
        assert result == {"ts_code": "stock_code", "total_revenue": "total_revenue"}

    def test_get_field_mapping_not_found(self):
        """get_field_mapping should return empty dict for unknown type"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(cache=MockCache(), field_mappings={"income": {}})
        
        result = provider.get_field_mapping("unknown")
        assert result == {}

    def test_apply_mapping_basic(self):
        """_apply_mapping should rename columns"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        mappings = {
            "income": {"ts_code": "stock_code", "total_revenue": "total_revenue"},
        }
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(cache=MockCache(), field_mappings=mappings)
        
        df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "total_revenue": [1000],
            "other_field": [999],
        })
        
        result = provider._apply_mapping(df, "income")
        assert result is not None  # Type guard
        
        assert "stock_code" in result.columns
        assert "total_revenue" in result.columns
        assert "ts_code" not in result.columns
        assert "other_field" in result.columns  # Unmapped fields kept

    def test_apply_mapping_no_mapping_for_type(self):
        """_apply_mapping should return df unchanged if no mapping for type"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(
            cache=MockCache(),
            field_mappings={"income": {"ts_code": "stock_code"}}
        )
        
        df = pd.DataFrame({"ts_code": ["000001.SZ"], "value": [100]})
        
        result = provider._apply_mapping(df, "balance")
        assert result is not None  # Type guard
        
        # Should be unchanged
        assert "ts_code" in result.columns
        assert list(result.columns) == list(df.columns)

    def test_apply_mapping_empty_df(self):
        """_apply_mapping should handle empty DataFrame"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(cache=MockCache(), field_mappings={"income": {}})
        
        df = pd.DataFrame()
        
        result = provider._apply_mapping(df, "income")
        assert result is not None  # Type guard
        
        assert result.empty

    def test_apply_mapping_none_df(self):
        """_apply_mapping should handle None"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(cache=MockCache(), field_mappings={"income": {}})
        
        result = provider._apply_mapping(None, "income")
        
        assert result is None

    def test_apply_mapping_partial_match(self):
        """_apply_mapping should only rename columns that exist"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        mappings = {
            "income": {
                "ts_code": "stock_code",
                "nonexistent_field": "standard_field",
            },
        }
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        provider = TestProvider(cache=MockCache(), field_mappings=mappings)
        
        df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "total_revenue": [1000],
        })
        
        result = provider._apply_mapping(df, "income")
        assert result is not None  # Type guard
        
        assert "stock_code" in result.columns
        assert "ts_code" not in result.columns
        # nonexistent_field should be ignored
        assert "standard_field" not in result.columns


class TestBaseProviderAbstractMethods:
    """Test BaseProvider abstract methods"""

    def test_base_provider_cannot_instantiate_without_implementation(self):
        """BaseProvider cannot be instantiated without implementing abstract methods"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        with pytest.raises(TypeError):
            BaseProvider(cache=MockCache())  # type: ignore

    def test_concrete_provider_implementation(self):
        """Concrete provider should implement abstract methods"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame({"stock_code": [stock_code], "year": [end_year]})
        
        provider = TestProvider(cache=MockCache())
        
        df = provider.get_balance_sheet("000001.SZ", 2023)
        
        assert not df.empty
        assert df.iloc[0]["stock_code"] == "000001.SZ"
        assert df.iloc[0]["year"] == 2023

    def test_concrete_provider_with_mapping(self):
        """Concrete provider should apply mapping automatically"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                df = pd.DataFrame({
                    "ts_code": [stock_code],
                    "end_date": [f"{end_year}-12-31"],
                    "total_assets": [1000],
                })
                result = self._apply_mapping(df, "balance")
                assert result is not None  # Type guard
                return result
        
        mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
            }
        }
        
        provider = TestProvider(cache=MockCache(), field_mappings=mappings)
        
        df = provider.get_balance_sheet("000001.SZ", 2023)
        
        assert "stock_code" in df.columns
        assert "report_date" in df.columns
        assert "ts_code" not in df.columns
        assert "end_date" not in df.columns


class TestBaseProviderCache:
    """Test BaseProvider cache integration"""

    def test_base_provider_has_cache(self):
        """BaseProvider should have cache attribute"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                return pd.DataFrame()
        
        cache = MockCache()
        provider = TestProvider(cache=cache)
        
        assert provider._cache is cache

    def test_base_provider_cache_methods(self):
        """BaseProvider should provide cache helper methods"""
        from value_investment.data.providers.base_provider import BaseProvider
        
        class TestProvider(BaseProvider):
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                cache_key = self._get_cache_key("balance", stock_code, str(end_year))
                cached = self._get_from_cache(cache_key)
                if cached is not None:
                    return cached
                
                df = pd.DataFrame({"data": [1]})
                self._set_to_cache(cache_key, df)
                return df
        
        cache = MockCache()
        provider = TestProvider(cache=cache)
        
        # First call - cache miss
        df1 = provider.get_balance_sheet("000001.SZ", 2023)
        
        # Second call - cache hit
        df2 = provider.get_balance_sheet("000001.SZ", 2023)
        
        # Should return same data
        assert len(df1) == len(df2)
