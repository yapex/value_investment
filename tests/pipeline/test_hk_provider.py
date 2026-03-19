"""Tests for HK Provider (pipeline/data/hk_provider.py)"""
import pytest
import warnings
from datetime import datetime
from unittest.mock import MagicMock, patch

from value_investment.providers.hk_share import HKProvider
from value_investment.providers.data_provider import DataProvider


class TestHKProviderProtocol:
    """验证 HKProvider 实现 DataProvider Protocol"""

    def test_has_supported_fields_property(self):
        """HKProvider 必须有 supported_fields 属性"""
        provider = HKProvider(cache=MagicMock())
        assert hasattr(provider, "supported_fields")
        assert isinstance(provider.supported_fields, set)

    def test_supported_fields_contains_core_fields(self):
        """supported_fields 应包含核心字段"""
        provider = HKProvider(cache=MagicMock())
        assert "total_revenue" in provider.supported_fields
        assert "net_profit" in provider.supported_fields
        assert "roe" in provider.supported_fields
        assert "market_cap" in provider.supported_fields

    def test_has_required_methods(self):
        """HKProvider 必须有必需的方法"""
        provider = HKProvider(cache=MagicMock())
        assert hasattr(provider, "fetch_financial_data")
        assert hasattr(provider, "fetch_indicators")
        assert hasattr(provider, "fetch_market_data")

    def test_inherits_base_provider(self):
        """HKProvider 应继承 BaseProvider"""
        from value_investment.providers.base import BaseProvider
        provider = HKProvider(cache=MagicMock())
        assert hasattr(provider, "_cache")
        assert hasattr(provider, "_get_from_cache")
        assert hasattr(provider, "_set_to_cache")
        assert hasattr(provider, "get_balance_sheet")
        assert hasattr(provider, "get_income_statement")
        assert hasattr(provider, "get_cash_flow_statement")


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def provider_with_mock_cache():
    """Provider with mocked cache using get_or_fetch"""
    mock_cache = MagicMock()

    def get_or_fetch_side_effect(key, fetch_fn, ttl=None, force_refresh=False):
        return fetch_fn()

    mock_cache.get_or_fetch.side_effect = get_or_fetch_side_effect
    return HKProvider(cache=mock_cache)


# ============================================================================
# Helper functions for mock data
# ============================================================================

def _empty_df():
    import pandas as pd
    return pd.DataFrame()


def _make_financial_df():
    """模拟多年财务报表 DataFrame（长表格式）"""
    import pandas as pd
    data = {
        "SECURITY_CODE": ["00700"] * 6,
        "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"] * 2,
        "STD_ITEM_NAME": [
            "营业额", "营业额", "营业额",
            "股东应占溢利", "股东应占溢利", "股东应占溢利",
        ],
        "AMOUNT": [
            751766000000, 660000000000, 550000000000,
            224842000000, 200000000000, 150000000000,
        ],
    }
    return pd.DataFrame(data)


def _partial_financial_df():
    """部分字段缺失的 DataFrame"""
    import pandas as pd
    data = {
        "SECURITY_CODE": ["00700"] * 2,
        "REPORT_DATE": ["2024-12-31", "2023-12-31"],
        "STD_ITEM_NAME": ["营业额", "营业额"],
        "AMOUNT": [751766000000, 660000000000],
    }
    return pd.DataFrame(data)


def _make_indicator_df():
    """模拟指标 DataFrame"""
    import pandas as pd
    data = {
        "基本每股收益(元)": [24.749],
        "每股净资产(元)": [126.548],
        "已发行股本(股)": [9106356125],
        "每股经营现金流(元)": [33.228],
        "股息率TTM(%)": [0.8696],
        "总市值(港元)": [5013049046812.5],
        "港股市值(港元)": [5013049046812.5],
        "营业总收入": [751766000000],
        "营业总收入滚动环比增长(%)": [3.004],
        "销售净利率(%)": [30.568],
        "净利润": [224842000000],
        "净利润滚动环比增长(%)": [3.183],
        "股东权益回报率(%)": [21.1347],
        "市盈率": [20.138],
        "市净率": [3.923],
        "总资产回报率(%)": [11.7719],
        "派息比率(%)": [16.818],
    }
    return pd.DataFrame(data)


# ============================================================================
# Tests
# ============================================================================

class TestHKProviderFetchFinancialData:
    """fetch_financial_data 测试"""

    def test_fetch_multi_year_financial_data(self, provider_with_mock_cache):
        """能获取多年财务报表数据"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = _make_financial_df()

            result = provider_with_mock_cache.fetch_financial_data(
                stock_code="00700",
                fields={"total_revenue", "parent_net_profit"},
                end_year=2024,
                years=5,
            )

            assert "total_revenue" in result or "parent_net_profit" in result

    def test_fetch_financial_data_no_data(self, provider_with_mock_cache):
        """无数据时返回空字典"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = _empty_df()

            result = provider_with_mock_cache.fetch_financial_data(
                stock_code="00700",
                fields={"total_revenue"},
                end_year=2024,
                years=5,
            )

            assert result == {}

    def test_fetch_financial_data_missing_fields(self, provider_with_mock_cache):
        """部分字段缺失时，发出警告"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
                mock_ak.stock_financial_hk_report_em.return_value = _partial_financial_df()

                result = provider_with_mock_cache.fetch_financial_data(
                    stock_code="00700",
                    fields={"total_revenue", "parent_net_profit"},
                    end_year=2024,
                    years=5,
                )

            user_warnings = [warning for warning in w if issubclass(warning.category, UserWarning)]
            assert len(user_warnings) > 0
            warning_text = str(user_warnings[0].message)
            assert "parent_net_profit" in warning_text or "无数据" in warning_text


class TestHKProviderFetchIndicators:
    """fetch_indicators 测试"""

    def test_fetch_indicators_returns_latest_year(self, provider_with_mock_cache):
        """AkShare 指标 API 只返回最新一年数据"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_hk_financial_indicator_em.return_value = _make_indicator_df()

            result = provider_with_mock_cache.fetch_indicators(
                stock_code="00700",
                fields={"roe", "roa", "basic_eps"},
                end_year=2024,
                years=10,
            )

            assert "roe" in result
            assert "roa" in result
            assert "basic_eps" in result
            current_year = datetime.now().year
            assert current_year in result["roe"]
            assert result["roe"][current_year] == pytest.approx(21.1347)

    def test_fetch_indicators_issues_warning(self, provider_with_mock_cache):
        """应发出警告：API 只返回一年数据"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
                mock_ak.stock_hk_financial_indicator_em.return_value = _make_indicator_df()

                provider_with_mock_cache.fetch_indicators(
                    stock_code="00700",
                    fields={"roe"},
                    end_year=2024,
                    years=10,
                )

            user_warnings = [w_item for w_item in w if issubclass(w_item.category, UserWarning)]
            assert len(user_warnings) > 0
            assert any("一年" in str(w_item.message) for w_item in user_warnings)


class TestHKProviderFetchMarketData:
    """fetch_market_data 测试"""

    def test_fetch_market_data(self, provider_with_mock_cache):
        """能获取市值相关字段"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_hk_financial_indicator_em.return_value = _make_indicator_df()

            result = provider_with_mock_cache.fetch_market_data(
                stock_code="00700",
                fields={"market_cap", "pe_ratio", "pb_ratio"},
            )

            assert "market_cap" in result or "pe_ratio" in result
            if "pe_ratio" in result:
                assert result["pe_ratio"] == pytest.approx(20.138)


class TestHKProviderErrorHandling:
    """异常处理测试"""

    def test_handles_api_error(self, provider_with_mock_cache):
        """API 异常时返回空数据"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.side_effect = Exception("Network error")

            result = provider_with_mock_cache.fetch_financial_data(
                stock_code="00700",
                fields={"total_revenue"},
                end_year=2024,
                years=5,
            )

            assert result == {}

    def test_handles_empty_response(self, provider_with_mock_cache):
        """API 返回空 DataFrame 时返回空字典"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = _empty_df()

            result = provider_with_mock_cache.fetch_financial_data(
                stock_code="00700",
                fields={"total_revenue"},
                end_year=2024,
                years=5,
            )

            assert result == {}


class TestHKProviderBaseProviderMethods:
    """BaseProvider Template Method 测试"""

    def test_get_balance_sheet_uses_template_method(self, provider_with_mock_cache):
        """get_balance_sheet 使用 Template Method"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = _make_financial_df()

            result = provider_with_mock_cache.get_balance_sheet("00700", 2024)

            provider_with_mock_cache._cache.get_or_fetch.assert_called()
            assert not result.empty

    def test_get_income_statement_uses_template_method(self, provider_with_mock_cache):
        """get_income_statement 使用 Template Method"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = _make_financial_df()

            result = provider_with_mock_cache.get_income_statement("00700", 2024)

            provider_with_mock_cache._cache.get_or_fetch.assert_called()
            assert not result.empty

    def test_get_cash_flow_statement_uses_template_method(self, provider_with_mock_cache):
        """get_cash_flow_statement 使用 Template Method"""
        with patch.object(provider_with_mock_cache, "_ak") as mock_ak:
            mock_ak.stock_financial_hk_report_em.return_value = _make_financial_df()

            result = provider_with_mock_cache.get_cash_flow_statement("00700", 2024)

            provider_with_mock_cache._cache.get_or_fetch.assert_called()
