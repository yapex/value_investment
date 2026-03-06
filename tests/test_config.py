"""Tests for data source configuration models (Pydantic)"""
import os

import pytest  # type: ignore
from pydantic import ValidationError


class TestProviderConfig:
    """Test ProviderConfig model"""

    def test_provider_config_basic(self):
        """ProviderConfig should accept basic fields"""
        from value_investment.core.config import ProviderConfig
        
        config = ProviderConfig(
            name="test_provider",
            module="value_investment.data.providers.test",
            class_name="TestProvider",
        )
        
        assert config.name == "test_provider"
        assert config.module == "value_investment.data.providers.test"
        assert config.class_name == "TestProvider"
        assert config.init_kwargs == {}
        assert config.field_mappings == {}

    def test_provider_config_with_kwargs(self):
        """ProviderConfig should accept init_kwargs"""
        from value_investment.core.config import ProviderConfig
        
        config = ProviderConfig(
            name="tushare",
            module="value_investment.data.providers.tushare_provider",
            class_name="TushareProvider",
            init_kwargs={"token": "test_token", "timeout": "30"},
        )
        
        assert config.init_kwargs["token"] == "test_token"
        assert config.init_kwargs["timeout"] == "30"

    def test_provider_config_with_field_mappings(self):
        """ProviderConfig should accept field_mappings"""
        from value_investment.core.config import ProviderConfig
        
        config = ProviderConfig(
            name="tushare",
            module="value_investment.data.providers.tushare_provider",
            class_name="TushareProvider",
            field_mappings={
                "income": {"total_revenue": "total_revenue"},
                "balance": {"total_assets": "total_assets"},
            }
        )
        
        assert "income" in config.field_mappings
        assert "balance" in config.field_mappings
        assert config.field_mappings["income"]["total_revenue"] == "total_revenue"

    def test_provider_config_env_var_expansion(self, monkeypatch):
        """ProviderConfig should expand environment variables in init_kwargs"""
        from value_investment.core.config import ProviderConfig
        
        monkeypatch.setenv("TEST_API_TOKEN", "expanded_token_123")
        
        config = ProviderConfig(
            name="test",
            module="test.module",
            class_name="TestProvider",
            init_kwargs={"token": "${TEST_API_TOKEN}"},
        )
        
        assert config.init_kwargs["token"] == "expanded_token_123"

    def test_provider_config_env_var_not_found(self):
        """ProviderConfig should handle missing environment variables"""
        from value_investment.core.config import ProviderConfig
        
        config = ProviderConfig(
            name="test",
            module="test.module",
            class_name="TestProvider",
            init_kwargs={"token": "${NONEXISTENT_VAR}"},
        )
        
        # Should be empty string if env var not found
        assert config.init_kwargs["token"] == ""

    def test_provider_config_env_var_literal(self):
        """ProviderConfig should keep non-env-var values as-is"""
        from value_investment.core.config import ProviderConfig
        
        config = ProviderConfig(
            name="test",
            module="test.module",
            class_name="TestProvider",
            init_kwargs={"token": "literal_token", "count": "100"},
        )
        
        assert config.init_kwargs["token"] == "literal_token"
        assert config.init_kwargs["count"] == "100"


class TestMarketDataSource:
    """Test MarketDataSource model"""

    def test_market_data_source_basic(self):
        """MarketDataSource should accept basic fields"""
        from value_investment.core.config import MarketDataSource
        
        ds = MarketDataSource(financial="tushare", market="tushare")
        
        assert ds.financial == "tushare"
        assert ds.market == "tushare"

    def test_market_data_source_different_providers(self):
        """MarketDataSource should support different providers for financial/market"""
        from value_investment.core.config import MarketDataSource
        
        ds = MarketDataSource(financial="akshare", market="yfinance")
        
        assert ds.financial == "akshare"
        assert ds.market == "yfinance"


class TestDataSourcesConfig:
    """Test DataSourcesConfig model"""

    def test_datasources_config_basic(self):
        """DataSourcesConfig should accept basic configuration"""
        from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
        
        config = DataSourcesConfig(
            providers={
                "tushare": ProviderConfig(
                    name="tushare",
                    module="test.tushare",
                    class_name="TushareProvider",
                )
            },
            markets={
                "A": MarketDataSource(financial="tushare", market="tushare")
            }
        )
        
        assert "tushare" in config.providers
        assert "A" in config.markets
        assert config.markets["A"].financial == "tushare"

    def test_datasources_config_multiple_providers(self):
        """DataSourcesConfig should support multiple providers"""
        from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
        
        config = DataSourcesConfig(
            providers={
                "tushare": ProviderConfig(name="tushare", module="test.tushare", class_name="TushareProvider"),
                "yfinance": ProviderConfig(name="yfinance", module="test.yfinance", class_name="YFinanceProvider"),
                "akshare": ProviderConfig(name="akshare", module="test.akshare", class_name="AkshareProvider"),
            },
            markets={
                "A": MarketDataSource(financial="tushare", market="tushare"),
                "HK": MarketDataSource(financial="akshare", market="yfinance"),
                "US": MarketDataSource(financial="akshare", market="yfinance"),
            }
        )
        
        assert len(config.providers) == 3
        assert len(config.markets) == 3

    def test_datasources_config_validation_invalid_provider(self):
        """DataSourcesConfig should validate provider references"""
        from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
        
        with pytest.raises(ValidationError) as exc_info:
            DataSourcesConfig(
                providers={
                    "tushare": ProviderConfig(name="tushare", module="test.tushare", class_name="TushareProvider"),
                },
                markets={
                    "A": MarketDataSource(financial="unknown_provider", market="tushare")
                }
            )
        
        assert "unknown_provider" in str(exc_info.value)

    def test_datasources_config_get_provider(self):
        """DataSourcesConfig should provide get_provider method"""
        from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
        
        config = DataSourcesConfig(
            providers={
                "tushare": ProviderConfig(name="tushare", module="test.tushare", class_name="TushareProvider"),
            },
            markets={
                "A": MarketDataSource(financial="tushare", market="tushare")
            }
        )
        
        provider = config.get_provider("tushare")
        assert provider.name == "tushare"
        assert provider.class_name == "TushareProvider"

    def test_datasources_config_get_market_source(self):
        """DataSourcesConfig should provide get_market_source method"""
        from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
        
        config = DataSourcesConfig(
            providers={
                "tushare": ProviderConfig(name="tushare", module="test.tushare", class_name="TushareProvider"),
                "akshare": ProviderConfig(name="akshare", module="test.akshare", class_name="AkshareProvider"),
                "yfinance": ProviderConfig(name="yfinance", module="test.yfinance", class_name="YFinanceProvider"),
            },
            markets={
                "A": MarketDataSource(financial="tushare", market="tushare"),
                "HK": MarketDataSource(financial="akshare", market="yfinance"),
            }
        )
        
        ds_a = config.get_market_source("A")
        assert ds_a.financial == "tushare"
        
        ds_hk = config.get_market_source("HK")
        assert ds_hk.financial == "akshare"
        assert ds_hk.market == "yfinance"

    def test_datasources_config_get_market_source_fallback(self):
        """DataSourcesConfig should fallback to A market if not found"""
        from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
        
        config = DataSourcesConfig(
            providers={
                "tushare": ProviderConfig(name="tushare", module="test.tushare", class_name="TushareProvider"),
            },
            markets={
                "A": MarketDataSource(financial="tushare", market="tushare")
            }
        )
        
        # Unknown market should fallback to A
        ds = config.get_market_source("JP")
        assert ds.financial == "tushare"


class TestConfigIntegration:
    """Test configuration integration"""

    def test_full_config_creation(self):
        """Should create complete configuration"""
        from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
        
        config = DataSourcesConfig(
            providers={
                "tushare_a": ProviderConfig(
                    name="tushare_a",
                    module="value_investment.data.providers.tushare_provider",
                    class_name="TushareProvider",
                    init_kwargs={"token": "${TUSHARE_TOKEN}"},
                    field_mappings={
                        "income": {"total_revenue": "total_revenue"},
                        "balance": {"total_assets": "total_assets"},
                    }
                ),
                "akshare_hk": ProviderConfig(
                    name="akshare_hk",
                    module="value_investment.data.providers.akshare_provider",
                    class_name="AkshareProvider",
                ),
                "akshare_us": ProviderConfig(
                    name="akshare_us",
                    module="value_investment.data.providers.akshare_provider",
                    class_name="AkshareProvider",
                ),
                "yfinance": ProviderConfig(
                    name="yfinance",
                    module="value_investment.data.providers.yfinance_provider",
                    class_name="YFinanceProvider",
                    field_mappings={
                        "market": {"Close": "close"}
                    }
                ),
            },
            markets={
                "A": MarketDataSource(financial="tushare_a", market="tushare_a"),
                "HK": MarketDataSource(financial="akshare_hk", market="yfinance"),
                "US": MarketDataSource(financial="akshare_us", market="yfinance"),
            }
        )
        
        # Verify structure
        assert len(config.providers) == 4  # tushare_a, akshare_hk, akshare_us, yfinance
        assert len(config.markets) == 3
        
        # Verify tushare config
        tushare = config.get_provider("tushare_a")
        assert tushare.init_kwargs["token"] == ""  # Env var not set
        assert "income" in tushare.field_mappings
        
        # Verify market routing
        a_market = config.get_market_source("A")
        assert a_market.financial == "tushare_a"
        assert a_market.market == "tushare_a"
        
        hk_market = config.get_market_source("HK")
        assert hk_market.financial == "akshare_hk"
        assert hk_market.market == "yfinance"
